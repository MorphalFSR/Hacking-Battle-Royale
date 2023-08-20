from clientbase import *
from tkinter import *
from constants import *
from protocol import *


class LoginFrame(BaseFrame):

    def __init__(self, parent, root):
        super().__init__(master=parent, root=root)

        self.attempts = dict()

        pass_var = StringVar(root)
        pass_var.trace('w', lambda *args: pass_var.set(pass_var.get().replace(" ", "")))
        self.password_box = Entry(self, textvariable=pass_var, width=25, bg=WHITE, font=INTERACTABLE_FONT)
        self.password_box.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.entries.append(self.password_box)

        self.update_idletasks()

        user_var = StringVar(root)
        user_var.trace('w', lambda *args: self.display_hints(user_var.get()))
        self.username_box = Entry(self, textvariable=user_var, width=25, bg=WHITE, font=INTERACTABLE_FONT)
        self.username_box.place(relx=0.5, rely=0.5, y=-self.password_box.winfo_height() - WIDGET_SPACE, anchor=CENTER)
        self.entries.append(self.username_box)

        self.password_box.bind('<Return>', lambda event: self.try_login(username=self.username_box.get(),
                                                                        password=self.password_box.get()))

        self.sign_in_button = Button(self, width=8, height=1, font=INTERACTABLE_FONT, text="Sign in",
                                     command=lambda: self.try_login(username=self.username_box.get(),
                                                                    password=self.password_box.get()))
        self.sign_in_button.place(relx=0.5, rely=0.5, y=0.5 * self.password_box.winfo_height() + WIDGET_SPACE, anchor=N)

    # TODO: remove this
    def try_login(self, username, password):
        self.root.try_login(username, password)

    def add_hint(self, username, hint):
        if username not in self.attempts.keys():
            self.attempts[username] = []
        self.attempts[username].append(hint)
        self.display_hints(username)

    def display_hints(self, username):
        self.clear_screen()
        if username in self.attempts.keys():
            for k in range(len(self.attempts[username])):
                attempt = self.attempts[username][k]
                for i in range(len(attempt)):
                    char = attempt[i][0]
                    colors = [COLORS[c] for c in attempt[i][1:]]
                    char_box = Label(self, bg=WHITE if len(colors) == 0 else colors[0], font=INTERACTABLE_FONT, height=1,
                                     width=1, text=char)
                    char_box.place(x=self.password_box.winfo_x() + i * LETTER_WIDTH,
                                   y=self.sign_in_button.winfo_y() + self.sign_in_button.winfo_height() + WIDGET_SPACE + k * (
                                           LETTER_HEIGHT + WIDGET_SPACE),
                                   anchor=NW)
                    self.temporaries.append(char_box)

    def load(self):
        self.attempts = {user: [] for user in self.attempts.keys()}
        super().load()


class DropdownFrame(BaseFrame):

    def __init__(self, parent, root, usernames):
        super().__init__(parent, root, width=ACCOUNT_BUTTON_SIZE[0], height=WINDOW_SIZE[1])

        self.buttons = [AccountButton(self, self.root, user) for user in usernames]
        for button in self.buttons:
            button.pack(side=TOP)

    def update_buttons(self, usernames):
        for button in self.buttons:
            button.destroy()
        self.buttons = [AccountButton(self, self.root, user) for user in usernames]
        for button in self.buttons:
            button.pack(side=TOP)


class InAppFrame(BaseFrame):

    def __init__(self, parent, root):
        super().__init__(master=parent, root=root)

        self.username = None

        self.username_label = Label(self, height=1, font=INTERACTABLE_FONT)
        self.username_label.pack()

        self.money_var = IntVar(self)
        self.money_label = Label(self, height=1, width=5, textvariable=self.money_var, font=INTERACTABLE_FONT)
        self.money_label.pack()

        self.user_query_label = Label(self, height=1, width=12, font=INTERACTABLE_FONT, text="Transfer to:")
        self.user_query_label.pack()
        self.user_entry = Entry(self, width=10, font=INTERACTABLE_FONT)
        self.user_entry.pack()

        self.sum_query_label = Label(self, height=1, width=9, font=INTERACTABLE_FONT, text="How much:")
        self.sum_query_label.pack()
        self.sum_entry = Entry(self, width=5, font=INTERACTABLE_FONT)
        self.sum_entry.pack()

        self.transfer_button = Button(self, width=8, height=1, font=INTERACTABLE_FONT, text="Transfer",
                                      command=lambda: self.root.socket.send(construct_message(TRANSFER,
                                                                                              self.username,
                                                                                              self.user_entry.get(),
                                                                                              self.sum_entry.get())))
        self.transfer_button.pack()

        self.logout_button = Button(self, width=20, height=1, font=INTERACTABLE_FONT,
                                    text="Log out of all other devices",
                                    command=lambda: self.root.socket.send(construct_message(LOGOUT, self.username)))
        self.logout_button.pack()

        self.back_button = Button(self, width=5, height=1, font=INTERACTABLE_FONT, text="Back",
                                  command=lambda: self.root.show_frame(LoginFrame.__name__))
        self.back_button.pack()

    def set_user(self, username):
        self.username = username
        self.username_label.config(text="Signed in to account: " + self.username)


class MessagesFrame(BaseFrame):
    def __init__(self, parent, root):
        super().__init__(parent, root)

        self.display_text = StringVar()
        self.text_box = Label(self, textvariable=self.display_text, width=MESSAGE_FRAME_SIZE[0], height=0)
        self.text_box.pack(side=TOP)

    def add_message(self, message):
        self.text_box.config(height=len(self.display_text.get().split("\n")) + 1)
        self.display_text.set(self.display_text.get() + "\n" + message)
