from tkinter import *
from constants import *


class BaseFrame(Frame):

    def __init__(self, master, root, **kwargs):
        super().__init__(master=master, **kwargs)

        self.root = root
        self.entries = []
        self.temporaries = []

    def load(self):
        for box in self.entries:
            box.delete(0, END)
        for i in range(len(self.temporaries)):
            self.temporaries[0].destroy()
            del(self.temporaries[0])
        self.tkraise()


class AccountButton(Button):

    def __init__(self, master, root, username, image=None):
        super().__init__(master=master, width=ACCOUNT_BUTTON_SIZE[0], height=ACCOUNT_BUTTON_SIZE[1], text=username,
                         font=INTERACTABLE_FONT, command=lambda: self.root.try_login(username))

        self.root = root
        self.image = image
