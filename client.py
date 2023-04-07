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
        for widget in self.top_widgets:
            widget.tkraise()

    def got_user_response(self, username):
        return username in ['' if message[0] not in LOGIN_RESPONSE_KEYS else message[1][0] for message in self.messages]

    def try_login(self, username, password=""):
        self.socket.send(f"LOGIN {username} {password}".encode())
        while not self.got_user_response(username):
            pass
        key, args = self.messages.pop([message[1][0] for message in self.messages].index(username))
        if key == APPROVED:
            print("Logging in.")
            self.accounts.add(username)
            self.dropdown.update_buttons(self.accounts)
            self.show_frame(InAppFrame.__name__)
        return key, args

    def login_successful(self, username):
        print("Logging in.")
        self.accounts.add(username)
        self.dropdown.update_buttons(self.accounts)
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
                # if len(self.messages) > 0:
                #     print(self.messages)
                if HACKED in [message[0] for message in self.messages]:
                    key, args = self.messages.pop([message[0] for message in self.messages].index(HACKED))
                    print(f"Account {args[0]} was hacked!")


if __name__ == "__main__":
    game = ClientApp()
    game.mainloop()
