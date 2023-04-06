import socket
from tkinter import *
import threading

HOST = '127.0.0.1'
PORT = 25252

WIDGET_SPACE = 10

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


class BaseFrame(Frame):

    def __init__(self, master, root):
        super().__init__(master=master)

        self.root = root
        self.entries = []
        self.labels = []

    def load(self):
        for box in self.entries:
            box.delete(0, END)
        for i in range(len(self.labels)):
            self.labels[0].destroy()
            del(self.labels[0])
        self.tkraise()


class LoginFrame(BaseFrame):

    def __init__(self, parent, root):
        super().__init__(master=parent, root=root)

        self.attempts = 0

        self.password_box = Entry(self, width=25, bg=WHITE, font=INTERACTABLE_FONT)
        self.password_box.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.entries.append(self.password_box)

        self.update_idletasks()

        self.username_box = Entry(self, width=25, bg=WHITE, font=INTERACTABLE_FONT)
        self.username_box.place(relx=0.5, rely=0.5, y=-self.password_box.winfo_height() - WIDGET_SPACE, anchor=CENTER)
        self.entries.append(self.username_box)

        self.sign_in_button = Button(self, width=8, height=1, font=INTERACTABLE_FONT, text="Sign in",
                                     command=lambda: self.try_login(username=self.username_box.get(),
                                                                    password=self.password_box.get()))
        self.sign_in_button.place(relx=0.5, rely=0.5, y=0.5*self.password_box.winfo_height() + WIDGET_SPACE, anchor=N)

    def try_login(self, username, password):
        response = self.root.try_login(username, password).split(' ')
        key = response[0]
        args = response[1:]
        if key == ICPASS:
            for i in range(len(args)):
                char = args[i][0]
                colors = [COLORS[c] for c in args[i][1:]]
                char_box = Label(self, bg=WHITE if len(colors) == 0 else colors[0], font=INTERACTABLE_FONT, height=1,
                                 width=1, text=char)
                char_box.pack()
                self.update_idletasks()
                char_box.place(x=self.password_box.winfo_x() + i * char_box.winfo_width(),
                               y=self.sign_in_button.winfo_y() + self.sign_in_button.winfo_height() + WIDGET_SPACE + self.attempts * (char_box.winfo_height() + WIDGET_SPACE),
                               anchor=NW)
                self.labels.append(char_box)

            self.attempts += 1


class InAppFrame(BaseFrame):

    def __init__(self, parent, root):
        super().__init__(master=parent, root=root)

        self.back_button = Button(self, width=5, height=1, font=INTERACTABLE_FONT, text="Back",
                                  command=lambda: self.root.show_frame(LoginFrame.__name__))
        self.back_button.pack()


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
