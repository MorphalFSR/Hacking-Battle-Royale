import socket
from tkinter import *
import threading
from frames import *
from constants import *
from protocol import *
from PIL import ImageTk, Image

HOST = '127.0.0.1'
PORT = 25252


class ClientApp(Tk):

    def __init__(self):
        super().__init__()

        self.geometry("{}x{}".format(*WINDOW_SIZE))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((HOST, PORT))
        self.lobby = None
        self.messages = []

        self.do_listen = True
        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.start()

        self.accounts = set()

        self.top_widgets = []

        image = Image.open("logo.png")
        image = image.resize((int(LOGO_SCALING_FACTOR*d) for d in image.size))
        self.logo = ImageTk.PhotoImage(image=image)

        container = Frame(self)
        container.pack(side=TOP, fill=BOTH, expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # set up main frames
        self.frames = dict()
        for F in (LoginFrame, InAppFrame, SignUpFrame, LobbyFrame, ChangePasswordFrame, MetaFrame):
            frame = F(parent=container, root=self)
            self.frames[F.__name__] = frame

        self.login_frame = self.frames[LoginFrame.__name__]
        self.inapp_frame = self.frames[InAppFrame.__name__]
        self.signup_frame = self.frames[SignUpFrame.__name__]
        self.lobby_frame = self.frames[LobbyFrame.__name__]
        self.password_frame = self.frames[ChangePasswordFrame.__name__]
        self.meta_frame = self.frames[MetaFrame.__name__]

        # set up non-main frames
        self.dropdown_frame = DropdownFrame(parent=container, root=self, usernames=self.accounts)
        self.dropdown_frame.grid(row=0, column=0, sticky=NW)

        self.message_frame = MessagesFrame(parent=container, root=self)
        self.message_frame.grid(row=0, column=0, sticky=NE)

        self.top_widgets.append(self.message_frame)
        self.top_widgets.append(self.dropdown_frame)

        # set up quit message
        self.protocol(QUIT_EVENT, self.on_close)

        # show initial frame
        self.socket.send(construct_message(LOBBIES))
        self.show_frame(LobbyFrame.__name__)

    def show_frame(self, name):
        self.frames[name].load()
        if name != InAppFrame.__name__:
            self.frames[InAppFrame.__name__].username = None
        for widget in self.top_widgets:
            widget.tkraise()

    def get_response(self, key):
        """searches for the first instance of a response associated with the given key
        if found, returns its args component (list)
        if not found, returns None"""
        if key in [message[0] for message in self.messages]:
            return self.messages.pop([message[0] for message in self.messages].index(key))[1]
        else:
            return None

    def try_login(self, username, password=""):
        self.socket.send(construct_message(LOGIN, username, password))

    def create_account(self, username, password):
        self.socket.send(construct_message(CREATEACCOUNT, username, password))

    def login_successful(self, username):
        self.display_message(f"Logging in to account {username}.")
        self.accounts.add(username)
        self.dropdown_frame.update_buttons(self.accounts)
        self.frames[InAppFrame.__name__].set_user(username)
        self.show_frame(InAppFrame.__name__)

    def join_lobby(self, name):
        self.socket.send(construct_message(JOIN, name))

    def on_close(self):
        try:
            self.socket.send(QUIT.encode())
            self.do_listen = False
        except Exception as e:
            print(e)
        finally:
            self.socket.close()
            self.do_listen = False
            self.destroy()
            del self

    def display_message(self, message):
        self.message_frame.add_message(message)

    def exit_lobby(self):
        self.socket.send(construct_message(EXIT, self.lobby))
        self.lobby_frame.load()

    def start_game(self):
        self.socket.send(construct_message(START, self.lobby))

    def change_password(self, username, password, repeat):
        self.socket.send(construct_message(CHANGEPASS, username, password, repeat))

    def listen(self):
        while self.do_listen:
            print("listening")
            try:
                data = self.socket.recv(1024).decode()
            except socket.timeout:
                data = ''
            print("GOT MESSAGE!")
            print(data)
            if len(data) > 0:
                for message in data.split(BREAK):
                    cmd, args = deconstruct_message(message)
                    if cmd in CLIENT_RESPONSE_KEYS:
                        self.messages.append((cmd, args))
                # dict of arguments passed for each keyword
                argss = {c: [] for c in CLIENT_RESPONSE_KEYS}
                print(self.messages)
                for i in range(len(self.messages)):
                    message = self.messages.pop(0)
                    argss[message[0]].append(message[1])

                for args in argss[HACKED]:
                    print(f"Account {args[0]} was hacked!")
                    self.display_message(f"Account {args[0]} was hacked!")
                for args in argss[LOGOUT]:
                    username = args[0]
                    print(f"You were logged out of the account: {username}")
                    self.display_message(f"You were logged out of the account: {username}")
                    self.accounts.discard(username)
                    if self.inapp_frame.username == username:
                        self.show_frame(LoginFrame.__name__)
                    self.dropdown_frame.update_buttons(self.accounts)
                for args in argss[APPROVED]:
                    username = args[0]
                    self.login_successful(username)
                for args in argss[ICPASS]:
                    username = args[0]
                    hint = args[1:]
                    self.login_frame.add_hint(username, hint)
                for args in argss[ICUSER]:
                    username = args[0]
                    self.display_message(f"User {username} does not exist")
                for args in argss[BLOCKED]:
                    username, time = args
                    print(f"You have been blocked from logging in to {username} for {time} seconds")
                    self.display_message(f"You have been blocked from logging in to {username} for {time} seconds")
                    self.login_frame.attempts[username] = []
                for args in argss[UNBLOCKED]:
                    username, = args
                    print(f"You are no longer blocked from logging in to {username}")
                    self.display_message(f"You are no longer blocked from logging in to {username}")
                for args in argss[MONEY]:
                    username, money = args
                    if self.inapp_frame.username == username:
                        self.inapp_frame.money_var.set(money)
                for args in argss[HACKING]:
                    username = args[0]
                    self.display_message(f"Someone is hacking {username}!")
                for args in argss[LOBBIES]:
                    lobbies = [(args[i], int(args[i + 1]), int(args[i + 2])) for i in range(0, len(args), 3)]
                    self.lobby_frame.update_lobbies(lobbies)
                for args in argss[ADDLOBBIES]:
                    lobbies = [(args[i], int(args[i + 1]), int(args[i + 2])) for i in range(0, len(args), 3)]
                    self.lobby_frame.add_lobbies(lobbies)
                for args in argss[REMLOBBIES]:
                    self.lobby_frame.remove_lobbies(args)
                for args in argss[JOINED1]:
                    name, = args
                    self.lobby = name
                    self.signup_frame.load()
                for args in argss[JOINED2]:
                    name, = args
                    self.lobby = name
                    self.meta_frame.load()
                for args in argss[LOBBYDATA]:
                    original_name, cur_hacking, *accessible = args
                    self.meta_frame.update_data(original_name, cur_hacking, accessible)
                    self.meta_frame.display_data()
                for args in argss[IVUSER]:
                    message, = args
                    self.signup_frame.display_message(message)
                for args in argss[IVPASS]:
                    message, = args
                    self.signup_frame.display_message(message)
                for args in argss[EXITED]:
                    username, = args
                    self.meta_frame.remove_player(username)
                    self.meta_frame.display_data()
                for args in argss[ADMIN]:
                    lobby, = args
                    if self.lobby == lobby:
                        self.meta_frame.show_start = True
                        self.meta_frame.display_data()
                for args in argss[START]:
                    lobby, = args
                    if self.lobby == lobby:
                        self.meta_frame.state = 1
                        self.show_frame(LoginFrame.__name__)
                for args in argss[LOSE]:
                    print("Lost the game!")


if __name__ == "__main__":
    game = ClientApp()
    game.mainloop()
