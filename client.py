import socket
from tkinter import *
import threading
from frames import *
from constants import *

HOST = '127.0.0.1'
PORT = 25252


class ClientApp(Tk):

    def __init__(self):
        super().__init__()

        self.geometry("{}x{}".format(*WINDOW_SIZE))
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

        self.frames = dict()
        for F in (LoginFrame, InAppFrame):
            frame = F(parent=container, root=self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.frames[F.__name__] = frame

        self.dropdown = DropdownFrame(parent=container, root=self, usernames=self.accounts)
        self.dropdown.grid(row=0, column=0, sticky="nsew")
        self.dropdown.place(x=0, y=0, anchor=NW)
        self.top_widgets.append(self.dropdown)

        self.protocol(QUIT_EVENT, self.on_close)

        self.show_frame(LoginFrame.__name__)

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
        self.socket.send(f"LOGIN {username} {password}".encode())
        while not self.got_login_response(username):
            pass
        key, args = self.messages.pop([message[1][0] for message in self.messages].index(username))
        if key == APPROVED:
            self.login_successful(username)
        return key, args

    def login_successful(self, username):
        print("Logging in.")
        self.accounts.add(username)
        self.dropdown.update_buttons(self.accounts)
        self.frames[InAppFrame.__name__].set_user(username)
        self.show_frame(InAppFrame.__name__)

    def on_close(self):
        try:
            self.socket.send(QUIT.encode())
            self.do_listen = False
        except Exception as e:
            print(e)
        self.destroy()

    def listen(self):
        while self.do_listen:
            data = self.socket.recv(1024).decode()
            if len(data) > 0:
                split_message = data.split(' ')
                self.messages.append((split_message[0], split_message[1:]))
                hacked_args = self.get_response(HACKED)
                logout_args = self.get_response(LOGOUT)
                if hacked_args:
                    print(hacked_args)
                    print(f"Account {hacked_args[0]} was hacked!")
                if logout_args:
                    username = logout_args[0]
                    print(f"You were logged out of the account: {username}")
                    self.accounts.discard(username)
                    if self.frames[InAppFrame.__name__].username == username:
                        self.show_frame(LoginFrame.__name__)
                    self.dropdown.update_buttons(self.accounts)


if __name__ == "__main__":
    game = ClientApp()
    game.mainloop()
