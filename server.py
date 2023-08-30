import socket
import threading
from constants import *
from serverbase import *
from protocol import *
import datetime


class Server(threading.Thread):

    def __init__(self):
        super().__init__(target=self.handle_server)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.lobbies = []
        self.start()
        self.lobby_handler = threading.Thread(target=self.handle_lobbies)
        self.lobby_handler.start()

    def broadcast(self, message, clients=None, condition=None):
        condition = condition if condition else lambda x: True
        clients = clients if clients else self.clients
        for client in clients:
            if condition(client):
                try:
                    print(client.socket)
                    client.socket.send(message)
                except (ConnectionError, OSError):
                    pass

    def handle_server(self):
        with self.socket:
            self.socket.bind((IP, PORT))
            self.socket.listen()
            while True:
                client_socket, address = self.socket.accept()
                print(f"Connected to {client_socket}")
                new_client = Client(handle=self.handle_client, client_socket=client_socket)
                self.clients.append(new_client)
                new_client.start()

    def handle_lobbies(self):
        while True:
            for i in range(len(self.lobbies) - 1, -1, -1):
                lobby = self.lobbies[-i - 1]
                active_players = lobby.get_active_players()
                if len(active_players) == 1 and lobby.started:
                    active_players[0].in_game = False
                    try:
                        active_players[0].socket.send(construct_message(WIN, lobby.name))
                    except (ConnectionError, OSError):
                        pass
                if len(lobby.clients) == 0 and lobby.is_open:
                    self.broadcast(construct_message(REMLOBBIES, lobby.name), clients=self.clients)
                    self.lobbies.pop(i)
                if lobby.started:
                    lobby.update()
                    for client in lobby.clients:
                        if len(client.accessible) == 0 and client.in_game:
                            client.in_game = False
                            try:
                                client.socket.send(construct_message(LOSE, lobby.name))
                            except (ConnectionError, OSError):
                                pass

    def handle_client(self, client):
        maintain_connection = True
        pending_lobby = None
        try:
            while maintain_connection:
                data = client.socket.recv(1024).decode().split(BREAK)
                print("Got Message", *data)
                data = [message for message in data if len(message) > 0]

                for message in data:
                    command, args = deconstruct_message(message)

                    try:

                        # user trying to log in to an account
                        if command == LOGIN:

                            if client.lobby:
                                username, password = args

                                if username in client.lobby.accounts.keys():
                                    if username in client.accessible and password == "":
                                        client.socket.send(construct_message(APPROVED, username))
                                    elif client.get_attempts(username) < MAX_ATTEMPTS:
                                        if client.lobby.accounts[username].password == password:
                                            client.accessible.append(username)
                                            client.socket.send(construct_message(APPROVED, username))
                                            self.broadcast(construct_message(HACKED, username),
                                                           clients=client.lobby.clients,
                                                           condition=lambda c: c.lobby is client.lobby and c != client)

                                            for d in client.lobby.get_data():
                                                self.broadcast(construct_message(LOBBYDATA, *d))
                                        else:
                                            client.socket.send(construct_message(ICPASS, username, hint_password(client.lobby.accounts[username].password, password)))
                                            client.inc_attempts(username)
                                            self.broadcast(construct_message(HACKING, username),
                                                           clients=client.lobby.clients, condition=lambda c: c.lobby is client.lobby and c != client and username in c.accessible)

                                            self.broadcast(construct_message(LOBBYDATA, client.original_name, username, *client.accessible),
                                                           clients=client.lobby.clients,
                                                           condition=lambda c: c.lobby is client.lobby)
                                    else:
                                        if client.attempts[username] == MAX_ATTEMPTS:
                                            client.block_times[username] = datetime.datetime.now()
                                            unblock_thread = threading.Thread(target=multi_func(lambda: sleep(BLOCK_TIME),
                                                                                                lambda: client.clear_attempts(username),
                                                                                                lambda: client.socket.send(construct_message(UNBLOCKED, username))))
                                            unblock_thread.start()
                                        client.socket.send(construct_message(BLOCKED, username, BLOCK_TIME - (datetime.datetime.now() - client.block_times[username]).seconds))
                                        client.attempts[username] += 1
                                else:
                                    client.socket.send(construct_message(ICUSER, username))

                        # user is logging out an account form other devices
                        if command == LOGOUT:
                            if client.lobby:
                                username, = args
                                print(username)
                                for c in client.lobby.clients:
                                    if username in c.accessible and c is not client:
                                        c.accessible.remove(username)
                                        c.socket.send(construct_message(LOGOUT, username))
                                        for d in client.lobby.get_data():
                                            self.broadcast(construct_message(LOBBYDATA, *d))

                        # user is creating an account
                        if command == CREATEACCOUNT:
                            if pending_lobby:
                                username, password = args
                                if check_user_pass(username, password, pending_lobby, client):
                                    if username not in pending_lobby.accounts.keys():

                                        if pending_lobby.add_client(client):
                                            client.socket.send(construct_message(ADMIN, pending_lobby.name))
                                        client.lobby = pending_lobby
                                        client.socket.send(construct_message(JOINED2, client.lobby.name))
                                        self.broadcast(construct_message(LOBBIES, pending_lobby.name, len(pending_lobby.clients),
                                                                         pending_lobby.max_clients),
                                                       clients=self.clients, condition=lambda c: c.lobby is None)
                                        pending_lobby.open()

                                        client.set_name(username)
                                        client.lobby.accounts[username] = Account(username, password)
                                        client.accessible.append(username)

                                        for c in client.lobby.clients:
                                            client.socket.send(construct_message(LOBBYDATA, c.original_name, '-', *c.accessible))
                                        self.broadcast(construct_message(LOBBYDATA, username, '-', username), client.lobby.clients)

                                        pending_lobby = None
                                    else:
                                        client.socket.send(construct_message(TAKEN, username))

                        # user is requesting a list of lobbies
                        if command == LOBBIES:
                            client.socket.send(construct_message(LOBBIES, *[v for lobby in self.lobbies for v in
                                                                            (lobby.name, len(lobby.clients), lobby.max_clients)
                                                                            if lobby.is_open and not lobby.started]))

                        # user is requesting to join a lobby
                        if command == JOIN:
                            if client.lobby is None:
                                name, = args
                                for l in self.lobbies:
                                    if l.name == name:
                                        pending_lobby = l

                                if pending_lobby:
                                    if len(pending_lobby.clients) < pending_lobby.max_clients and client.lobby is None:
                                        client.socket.send(construct_message(JOINED1, pending_lobby.name))

                                    else:
                                        client.socket.send(construct_message(LOBBIES, *[v for lobby in self.lobbies for v in
                                                                                        [lobby.name, len(lobby.clients),
                                                                                         lobby.max_clients]]))
                                else:
                                    client.socket.send(construct_message(LOBBIES, *[v for lobby in self.lobbies for v in
                                                                                    [lobby.name, len(lobby.clients),
                                                                                     lobby.max_clients]]))

                        if command == CREATELOBBY:
                            if client.lobby is None:
                                name, = args
                                if name not in [l.name for l in self.lobbies]:
                                    pending_lobby = Lobby(name)
                                    self.lobbies.append(pending_lobby)
                                    client.socket.send(construct_message(JOINED1, name))

                        if command == EXIT:
                            if client.lobby:
                                self.broadcast(construct_message(EXITED, client.original_name), clients=client.lobby.clients)
                                if client.lobby.remove_client(client):
                                    client.lobby.clients[0].socket.send(construct_message(ADMIN, client.lobby.name))
                                client.exit_lobby()
                                pending_lobby = None

                        if command == START:
                            if client.lobby:
                                if client is client.lobby.admin:
                                    if len(client.lobby.clients) >= 2:
                                        client.lobby.start()
                                        self.broadcast(construct_message(REMLOBBIES, client.lobby.name), clients=self.clients, condition=lambda c: c.lobby is not client.lobby)
                                        self.broadcast(construct_message(START, client.lobby.name), clients=client.lobby.clients)
                                        for c in client.lobby.clients:
                                            c.socket.send(construct_message(APPROVED, c.original_name))

                        if command == CHANGEPASS:
                            if client.lobby:
                                username, password, repeat = args
                                if username in client.accessible:
                                    if password == repeat:
                                        if check_user_pass(username, password, client.lobby, client=client):
                                            client.lobby.accounts[username].password = password
                                            client.socket.send(construct_message(CHANGEPASS, username))
                                    else:
                                        client.socket.send(construct_message(IVPASS, "Passwords do not match."))

                        # user is disconnecting
                        if command == QUIT:
                            if client.lobby:
                                self.broadcast(construct_message(EXITED, client.original_name), clients=client.lobby.clients)
                                if client.lobby.remove_client(client):
                                    client.lobby.clients[0].socket.send(construct_message(ADMIN, client.lobby.name))
                                client.lobby = None

                            print(f"Disconnecting from {client.socket}")
                            maintain_connection = False
                    except ValueError:
                        print("Invalid arguments for " + command)

        except ConnectionError as e:
            print(f"Client {client} disconnected unexpectedly.")
        finally:
            if client.lobby:
                client.lobby.clients.remove(client)
                self.broadcast(construct_message(LOBBIES, client.lobby.name, len(client.lobby.clients), client.lobby.max_clients), condition=lambda c: c.lobby is None)
                self.broadcast(construct_message(EXITED, client.original_name), clients=client.lobby.clients, condition=lambda c: c is not client)
            self.clients.remove(client)
            client.socket.close()


if __name__ == "__main__":
    server = Server()
