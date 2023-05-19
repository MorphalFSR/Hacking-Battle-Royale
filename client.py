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

        self.login_frame = self.frames[LoginFrame.__name__]
        self.inapp_frame = self.frames[InAppFrame.__name__]

        self.dropdown_frame = DropdownFrame(parent=container, root=self, usernames=self.accounts)
        self.dropdown_frame.grid(row=0, column=0, sticky="nsew")
        self.dropdown_frame.place(x=0, y=0, anchor=NW)

        self.message_frame = MessagesFrame(parent=container, root=self)
        self.message_frame.grid(row=0, column=0, sticky="nsew")
        self.message_frame.place(x=WINDOW_SIZE[0], y=0, anchor=NE)

        self.top_widgets.append(self.message_frame)
        self.top_widgets.append(self.dropdown_frame)

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

    def login_successful(self, username):
        print("Logging in.")
        self.display_message("Logging in.")
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
            if len(data) > 0:
                split_message = data.split(' ')
                self.messages.append((split_message[0], split_message[1:]))
                argss = {c: self.get_response(c) for c in CLIENT_RESPONSE_KEYS}
                if argss[HACKED]:
                    print(argss[HACKED])
                    print(f"Account {argss[HACKED][0]} was hacked!")
                    self.display_message(f"Account {argss[HACKED][0]} was hacked!")
                if argss[LOGOUT]:
                    username = argss[LOGOUT][0]
                    print(f"You were logged out of the account: {username}")
                    self.display_message(f"You were logged out of the account: {username}")
                    self.accounts.discard(username)
                    if self.inapp_frame.username == username:
                        self.show_frame(LoginFrame.__name__)
                    self.dropdown_frame.update_buttons(self.accounts)
                if argss[APPROVED]:
                    username = argss[APPROVED][0]
                    self.login_successful(username)
                if argss[ICPASS]:
                    username = argss[ICPASS][0]
                    hint = argss[ICPASS][1:]
                    self.login_frame.add_hint(username, hint)
                if argss[ICUSER]:
                    username = argss[ICUSER][0]
                    self.display_message(f"User {username} does not exist")
                if argss[BLOCKED]:
                    username, time = argss[BLOCKED]
                    print(f"You have been blocked from logging in to {username} for {time} seconds")
                    self.display_message(f"You have been blocked from logging in to {username} for {time} seconds")
                    self.login_frame.attempts[username] = []
                if argss[UNBLOCKED]:
                    username = argss[UNBLOCKED][0]
                    print(f"You are no longer blocked from logging in to {username}")
                    self.display_message(f"You are no longer blocked from logging in to {username}")
                if argss[MONEY]:
                    username, money = argss[MONEY]

                    if self.inapp_frame.username == username:
                        self.inapp_frame.money_var.set(money)
                print(self.messages)
                print(argss)


if __name__ == "__main__":
    game = ClientApp()
    game.mainloop()
