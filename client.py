import socket
from tkinter import *
import threading

HOST = '127.0.0.1'
PORT = 25252

INTERACTABLE_FONT = ("Comic Sans MS", 12)
END = 'end'
WHITE = 'white'
CENTER = 'center'


class LoginFrame(Frame):

    def __init__(self, parent, root):
        super().__init__(master=parent)

        self.root = root

        self.input_box = Entry(self, width=25, bg=WHITE, font=INTERACTABLE_FONT)
        self.input_box.place(relx=0.5, rely=0.5, anchor=CENTER)

        self.master.update()

        self.sign_in_button = Button(self, width=8, height=1, font=INTERACTABLE_FONT, text="Sign in",
                                     command=lambda: self.root.socket.send("Pressed".encode()))
        self.sign_in_button.place(relx=0.5, rely=0.5, x=0, y=1.5 * self.input_box.winfo_height(), anchor=CENTER)


class BlankFrame(Frame):

    def __init__(self, parent, root):
        super().__init__(master=parent)

        self.root = root


class ClientApp(Tk):

    def __init__(self):
        super().__init__()

        self.geometry("1280x720")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((HOST, PORT))

        listen_thread = threading.Thread(target=self.listen)
        listen_thread.start()

        container = Frame(self)
        container.pack(side=TOP, fill=BOTH, expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = dict()
        for F in (LoginFrame, BlankFrame):
            frame = F(parent=container, root=self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.frames[F.__name__] = frame

        self.show_frame("LoginFrame")

    def show_frame(self, name):
        self.frames[name].tkraise()

    def listen(self):
        while True:
            data = self.socket.recv(1024)
            print(data.decode())


if __name__ == "__main__":
    game = ClientApp()
    game.mainloop()
