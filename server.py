# TODO: add logged in users for each client + log out message when hacked

import socket
import threading
from constants import *
from serverbase import *


class Server(threading.Thread):

    def __init__(self):
        super().__init__(target=self.handle_server)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.accounts = {username: Account(username, PASSWORDS[username]) for username in PASSWORDS.keys()}
        self.start()
        # while True:
        #     username = input("Enter username: ")
        #     password = input("Enter password: ")
        #     self.accounts[username].password = password

    def broadcast(self, message, condition=None):
        condition = condition if condition else lambda x: True
        for client in self.clients:
            if condition(client):
                client.socket.send(message)

    def handle_server(self):
        with self.socket:
            self.socket.bind((IP, PORT))
            self.socket.listen(N_PLAYERS)
            while True:
                client_socket, address = self.socket.accept()
                print(f"Connected to {client_socket}")
                new_client = Client(handle=self.handle_client, client_socket=client_socket, accounts=self.accounts)
                self.clients.append(new_client)
                new_client.start()

    def handle_client(self, client):
        maintain_connection = True
        while maintain_connection:
            data = client.socket.recv(1024).decode().split(' ')
            command = data[0]
            args = data[1:]

            # user trying to log in to an account
            if command == LOGIN:
                username, password = args
                print(username, password)
                if username in self.accounts.keys():
                    if username in client.accessible and password == "":
                        client.socket.send(f"{APPROVED} {username}".encode())
                        client.socket.send(f"{MONEY} {username} {self.accounts[username].money}".encode())
                    elif client.attempts[username] < MAX_ATTEMPTS:
                        if self.accounts[username].password == password:
                            client.accessible.append(username)
                            client.socket.send(f"{APPROVED} {username}".encode())
                            client.socket.send(f"{MONEY} {username} {self.accounts[username].money}".encode())
                            self.broadcast(f"{HACKED} {username}".encode(), lambda c: c != client)
                        else:
                            print("pass")
                            client.socket.send((f"{ICPASS} {username}" + hint_password(self.accounts[username].password, password)).encode())
                            client.attempts[username] += 1
                    else:
                        if client.attempts[username] == MAX_ATTEMPTS:
                            print("hu")
                            unblock_thread = threading.Thread(target=multi_func(lambda: sleep(BLOCK_TIME),
                                                                                lambda: client.clear_attempts(username),
                                                                                lambda: client.socket.send(f"{UNBLOCKED} {username}".encode())))
                            print("ra!")
                            unblock_thread.start()
                        client.socket.send(f"{BLOCKED} {username} {BLOCK_TIME}".encode())
                        client.attempts[username] += 1
                else:
                    print("user")
                    client.socket.send(f"{ICUSER} {username}".encode())

            elif command == LOGOUT:
                if args[0] in client.accessible:
                    self.broadcast((' '.join(data)).encode(), lambda c: args[0] in c.accessible and c != client)
            elif command == TRANSFER:
                user_from, user_to, money = args
                money = int(money)
                if user_from in client.accessible:
                    if user_to in self.accounts.keys():
                        if money <= self.accounts[user_from].money:
                            self.accounts[user_from].money -= money
                            self.accounts[user_to].money += money
                            self.broadcast(f"{MONEY} {user_from} {self.accounts[user_from].money}".encode(), lambda c: user_from in c.accessible)
                            self.broadcast(f"{MONEY} {user_to} {self.accounts[user_to].money}".encode(), lambda c: user_to in c.accessible)
            elif command == QUIT:
                print(f"Disconnecting from {client.socket}")
                maintain_connection = False
        client.socket.close()
        self.clients.remove(client)


if __name__ == "__main__":
    server = Server()
