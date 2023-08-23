import socket
import tkinter
from tkinter import *
import threading
from frames import *
from constants import *
from protocol import *

HOST = '127.0.0.1'
PORT = 25252


class ClientApp(Tk):

    def __init__(self):
        super().__init__()

        self.geometry("{}x{}".format(*WINDOW_SIZE))
        # self.grid_propagate(False)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((HOST, PORT))
        self.messages = []

        self.do_listen = True
        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.start()

        self.accounts = set()

        self.top_widgets = []

        container = Frame(self)
        container.pack(side=TOP, fill=BOTH, expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # set up main frames
        self.frames = dict()
        for F in (LoginFrame, InAppFrame, SignUpFrame):
            frame = F(parent=container, root=self)
            self.frames[F.__name__] = frame

        self.login_frame = self.frames[LoginFrame.__name__]
        self.inapp_frame = self.frames[InAppFrame.__name__]
        self.signup_frame = self.frames[SignUpFrame.__name__]

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
        print("ADASD")
        self.show_frame(SignUpFrame.__name__)

    def show_frame(self, name):
        self.frames[name].load()
        if name != InAppFrame.__name__:
            self.frames[InAppFrame.__name__].username = None
        for widget in self.top_widgets:
            widget.tkraise()

    def got_login_response(self, username):
        return username in ['' if message[0] not in LOGIN_RESPONSE_KEYS else message[1][0] for message in self.messages]

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
        self.socket.send(construct_message(CREATE, username, password))

    def login_successful(self, username):
        self.display_message(f"Logging in to account {username}.")
        self.accounts.add(username)
        self.dropdown_frame.update_buttons(self.accounts)
        self.frames[InAppFrame.__name__].set_user(username)
        self.show_frame(InAppFrame.__name__)

    def on_close(self):
        try:
            self.socket.send(QUIT.encode())
            self.do_listen = False
        except Exception as e:
            print(e)
        self.destroy()

    def display_message(self, message):
        self.message_frame.add_message(message)

    def listen(self):
        while self.do_listen:
            data = self.socket.recv(1024).decode()
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
                print(argss)

                for args in argss[HACKED]:
                    print(args)
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
                    print("AAAAAAAAAAAAAAAA")
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


if __name__ == "__main__":
    game = ClientApp()
    game.mainloop()
