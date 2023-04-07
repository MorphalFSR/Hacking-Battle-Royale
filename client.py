import socket
from tkinter import *
import threading
from frames import *

HOST = '127.0.0.1'
PORT = 25252

WIDGET_SPACE = 10
DROPDOWN_BOX_SIZE = (100, 24)

APPROVED = 'APPROVED'  # Correct username and password
ICUSER = 'ICUSER'  # InCorrect Username
ICPASS = 'ICPASS'  # InCorrect Password
QUIT = 'QUIT'

QUIT_EVENT = 'WM_DELETE_WINDOW'

INTERACTABLE_FONT = ("Comic Sans MS", 12)
END = 'end'
WHITE = 'white'
CENTER = 'center'

COLORS = {'g': "#00FF00",
          'y': "#FFFF00",
          'p': "#FF00FF",
          'r': "#FF0000"}


class ClientApp(Tk):

    def __init__(self):
        super().__init__()

        self.geometry("1280x720")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((HOST, PORT))

        container = Frame(self)
        container.pack(side=TOP, fill=BOTH, expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = dict()
        for F in (LoginFrame, InAppFrame):
            frame = F(parent=container, root=self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.frames[F.__name__] = frame

        self.protocol(QUIT_EVENT, self.on_close)

        self.show_frame(LoginFrame.__name__)

    def show_frame(self, name):
        self.frames[name].load()

    def try_login(self, username, password):
        self.socket.send(f"LOGIN {username} {password}".encode())
        response = self.socket.recv(1024).decode()
        if response == APPROVED:
            print("Logging in.")
            self.show_frame(InAppFrame.__name__)
        return response

    def on_close(self):
        try:
            self.socket.send(QUIT.encode())
        except Exception as e:
            print(e)
        self.destroy()


if __name__ == "__main__":
    game = ClientApp()
    game.mainloop()
