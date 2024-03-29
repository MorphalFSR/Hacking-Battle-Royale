from tkinter import *
from constants import *


def multi_func(*args):
    return lambda: [f() for f in args]


def keep_only(text, chars):
    return "".join([c for c in text if c in chars])


class BaseFrame(Frame):

    def __init__(self, master, root, **kwargs):
        super().__init__(master=master, **kwargs)

        self.root = root
        self.entries = []
        self.temporaries = []

    def load(self):
        for box in self.entries:
            box.delete(0, END)
        self.clear_screen()
        self.tkraise()

    def clear_screen(self):
        for i in range(len(self.temporaries)):
            self.temporaries[0].grid_remove()
            self.temporaries[0].destroy()
            self.temporaries.pop(0)


class MainFrame(BaseFrame):

    def __init__(self, master, root, **kwargs):
        super().__init__(master=master, root=root, **kwargs)
        self.grid(row=0, column=0, sticky=NSEW)
        self.assets = []

    def construct_window(self):
        for i in range(len(self.assets)):
            self.rowconfigure(i + 1, weight=0)
            self.assets[i].grid(row=i + 1, column=1, sticky=N, pady=PADY)

        self.rowconfigure(0, weight=5)
        self.rowconfigure(len(self.assets) + 1, weight=5)

        for i in range(3):
            self.columnconfigure(i, weight=1)


class AccountButton(Button):

    def __init__(self, master, root, username, image=None):
        super().__init__(master=master, width=ACCOUNT_BUTTON_SIZE[0], height=ACCOUNT_BUTTON_SIZE[1], text=username,
                         font=INTERACTABLE_FONT, command=lambda: self.root.try_login(username))

        self.root = root
        self.image = image
