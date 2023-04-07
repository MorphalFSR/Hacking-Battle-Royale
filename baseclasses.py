from tkinter import *


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