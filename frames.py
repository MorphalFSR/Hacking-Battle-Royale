from clientbase import *
from tkinter import *
from constants import *
from protocol import *


class LoginFrame(MainFrame):

    def __init__(self, parent, root):
        super().__init__(master=parent, root=root)

        self.attempts = dict()

        self.password_label = Label(self, text="Enter Password:", font=INTERACTABLE_FONT)

        pass_var = StringVar(root)
        pass_var.trace('w', lambda *args: pass_var.set(pass_var.get().replace(" ", "")))
        self.password_box = Entry(self, textvariable=pass_var, width=25, bg=WHITE, font=INTERACTABLE_FONT)
        self.entries.append(self.password_box)

        self.username_label = Label(self, text="Enter Username:", font=INTERACTABLE_FONT)

        self.username_box = Entry(self, width=25, bg=WHITE, font=INTERACTABLE_FONT)
        self.entries.append(self.username_box)

        self.password_box.bind('<Return>', lambda event: self.try_login(username=self.username_box.get(),
                                                                        password=self.password_box.get()))

        self.sign_in_button = Button(self, width=8, height=1, font=INTERACTABLE_FONT, text="Sign in",
                                     command=lambda: self.try_login(username=self.username_box.get(),
                                                                    password=self.password_box.get()))

        self.logo_label = Label(self, image=self.root.logo)
        self.logo_label.place(relx=0.5, rely=0.5, y=-1.5 * self.password_box.winfo_height() - 2 * WIDGET_SPACE,
                              anchor=S)

        self.info_button = Button(self, text="Game Info", font=INTERACTABLE_FONT, command=lambda: self.root.show_frame(MetaFrame.__name__))

        self.hints_container = BaseFrame(self, root)

        self.assets = [self.logo_label, self.username_label, self.username_box, self.password_label, self.password_box,
                       self. sign_in_button, self.info_button, self.hints_container]

        self.construct_window()

    def try_login(self, username, password):
        self.root.try_login(username, password)

    def add_hint(self, username, hint):
        if username not in self.attempts.keys():
            self.attempts[username] = []
        self.attempts[username].append(hint)
        self.display_hints(username)

    def display_hints(self, username):
        self.hints_container.clear_screen()
        if username in self.attempts.keys():
            for k in range(len(self.attempts[username])):
                attempt = self.attempts[username][k]
                for i in range(len(attempt)):
                    char = attempt[i][0]
                    colors = [COLORS[c] for c in attempt[i][1:]]
                    print(char)
                    char_box = Label(self.hints_container, bg=WHITE if len(colors) == 0 else colors[0], font=INTERACTABLE_FONT, height=1,
                                     width=1, text=char)

                    char_box.grid(row=k, column=i, pady=PADY)
                    self.hints_container.columnconfigure(i, weight=0)
                    self.hints_container.rowconfigure(k, weight=0)

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


class InAppFrame(MainFrame):

    def __init__(self, parent, root):
        super().__init__(master=parent, root=root)

        self.username = None

        self.logo_label = Label(self, image=self.root.logo)

        self.username_label = Label(self, height=1, font=INTERACTABLE_FONT)

        self.logout_button = Button(self, font=INTERACTABLE_FONT,
                                    text="Log out of all other devices",
                                    command=lambda: self.root.socket.send(construct_message(LOGOUT, self.username)))

        self.change_password_button = Button(self, font=INTERACTABLE_FONT, text="Change Password",
                                             command=multi_func(lambda: self.root.frames[ChangePasswordFrame.__name__].set_user(self.username),
                                                                lambda: self.root.show_frame(ChangePasswordFrame.__name__)))

        self.back_button = Button(self, width=5, height=1, font=INTERACTABLE_FONT, text="Back",
                                  command=lambda: self.root.show_frame(LoginFrame.__name__))

        self.assets = [self.logo_label, self.username_label, self.logout_button, self.change_password_button,
                       self.back_button]

        self.construct_window()

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


class SignUpFrame(MainFrame):

    def __init__(self, parent, root):
        super().__init__(master=parent, root=root)

        self.attempts = dict()

        self.username_label = Label(self, text="Enter Username:", font=INTERACTABLE_FONT)

        self.username_box = Entry(self, width=25, bg=WHITE, font=INTERACTABLE_FONT)
        self.entries.append(self.username_box)

        self.password_label = Label(self, text="Enter Password:", font=INTERACTABLE_FONT)

        self.password_box = Entry(self, width=25, bg=WHITE, font=INTERACTABLE_FONT)
        self.entries.append(self.password_box)

        self.sign_up_button = Button(self, width=8, height=1, font=INTERACTABLE_FONT, text="Sign Up",
                                     command=lambda: self.create_account(username=self.username_box.get(),
                                                                         password=self.password_box.get()))

        self.back_button = Button(self, font=INTERACTABLE_FONT, text="Back",
                                  command=lambda: self.root.show_frame(LobbyFrame.__name__))

        self.invalid_label = Label(self, fg="#ff0000")

        self.logo_label = Label(self, image=self.root.logo)

        self.assets = [self.logo_label, self.username_label, self.username_box, self.password_label, self.password_box,
                       self.sign_up_button, self.back_button, self.invalid_label]

        self.construct_window()

    def create_account(self, username, password):
        self.root.create_account(username, password)

    def display_message(self, message):
        self.invalid_label.config(text=message)

    def load(self):
        self.invalid_label.config(text='')
        self.attempts = {user: [] for user in self.attempts.keys()}
        super().load()


class LobbyFrame(MainFrame):

    def __init__(self, parent, root):
        super().__init__(master=parent, root=root)

        self.lobby_buttons = dict()
        self.test_label = Label(self, text="Choose A Lobby", font=TITLE_FONT)
        self.test_label.grid(row=0, column=0, columnspan=LOBBY_COLUMNS)

        self.create_lobby_button = Button(self, text="Create Lobby", font=INTERACTABLE_FONT, command=self.open_creator)
        self.create_lobby_button.grid(row=1, column=0, columnspan=LOBBY_COLUMNS)

        self.entry_open = False
        self.lobby_name_entry = Entry(self, width=10, font=INTERACTABLE_FONT)

        for i in range(LOBBY_COLUMNS):
            self.columnconfigure(i, weight=1)

        self.rowconfigure(0, weight=3)
        for i in range(1, 8):
            self.rowconfigure(i, weight=1)

        self.entries.append(self.lobby_name_entry)

    def add_lobbies(self, lobbies):
        for lobby in lobbies:
            if lobby[0] in self.lobby_buttons.keys():
                self.lobby_buttons[lobby[0]].config(text=f"{lobby[0]}\n{lobby[1]}/{lobby[2]}")
            else:
                self.lobby_buttons[lobby[0]] = (Button(self, text=f"{lobby[0]}\n{lobby[1]}/{lobby[2]}", font=INTERACTABLE_FONT,
                                                       command=(lambda l: lambda: self.root.join_lobby(l[0]))(lobby)))
                row = 1 + int((len(self.lobby_buttons) - 1) / LOBBY_COLUMNS)
                self.rowconfigure(row, weight=1)
                self.lobby_buttons[lobby[0]].grid(row=row, column=(len(self.lobby_buttons) - 1) % LOBBY_COLUMNS, sticky=NSEW, padx=PADX, pady=PADY)

        self.create_lobby_button.grid_remove()
        new_button_row = 2 + int((len(self.lobby_buttons) - 1) / LOBBY_COLUMNS)
        self.rowconfigure(new_button_row, weight=3)
        self.create_lobby_button.grid(row=new_button_row, column=0, columnspan = LOBBY_COLUMNS)

    def remove_lobbies(self, lobbies):
        for lobby in lobbies:
            if lobby[0] in self.lobby_buttons.keys():
                self.lobby_buttons[lobby[0]].destroy()
                del self.lobby_buttons[lobby[0]]
        self.update_lobby_display()

    def update_lobbies(self, lobbies):
        self.add_lobbies(lobbies)

        lobby_names = [l[0] for l in lobbies]
        self.remove_lobbies([l for l in self.lobby_buttons.keys() if l not in lobby_names])

        self.update_lobby_display()

    def update_lobby_display(self):
        i = 0
        for name in self.lobby_buttons.keys():
            row = 1 + int(i / LOBBY_COLUMNS)
            self.lobby_buttons[name].grid(row=row, column=i % LOBBY_COLUMNS, sticky=NSEW, padx=PADX, pady=PADY)
            self.rowconfigure(row, weight=1)
            i += 1

        new_min_row = 2 + int((len(self.lobby_buttons) - 1) / LOBBY_COLUMNS)

        if self.entry_open:
            new_button_row = new_min_row + 1
            self.lobby_name_entry.grid_remove()
            self.lobby_name_entry.grid(row=new_min_row, column=0, columnspan=LOBBY_COLUMNS)
        else:
            new_button_row = new_min_row

        self.create_lobby_button.grid_remove()
        self.rowconfigure(new_button_row, weight=3)
        self.create_lobby_button.grid(row=new_button_row, column=0, columnspan=LOBBY_COLUMNS)

    def open_creator(self):
        self.entry_open = True
        self.create_lobby_button.grid_remove()
        new_button_row = 3 + int((len(self.lobby_buttons) - 1) / LOBBY_COLUMNS)
        self.create_lobby_button.grid(row=new_button_row, column=0, columnspan=LOBBY_COLUMNS)
        self.lobby_name_entry.grid(row=new_button_row - 1, column=0, columnspan=LOBBY_COLUMNS)
        self.create_lobby_button.config(command=lambda: self.create_lobby(self.lobby_name_entry.get()))

    def close_creator(self):
        self.entry_open = False
        self.create_lobby_button.grid_remove()
        self.lobby_name_entry.grid_remove()
        new_button_row = 2 + int((len(self.lobby_buttons) - 1) / LOBBY_COLUMNS)
        self.create_lobby_button.grid(row=new_button_row, column=0, columnspan=LOBBY_COLUMNS)
        self.create_lobby_button.config(command=self.open_creator)

    def create_lobby(self, name):
        self.root.socket.send(construct_message(CREATELOBBY, name))

    def load(self):
        self.close_creator()
        self.root.socket.send(construct_message(LOBBIES))
        super().load()


class ChangePasswordFrame(MainFrame):

    def __init__(self, parent, root):
        super().__init__(master=parent, root=root)

        self.username = None

        self.logo_label = Label(self, image=self.root.logo)

        self.username_label = Label(self, height=1, font=INTERACTABLE_FONT)

        self.pass_label = Label(self, font=INTERACTABLE_FONT, text="Enter new password:")
        self.pass_entry = Entry(self, width=10, font=INTERACTABLE_FONT)

        self.repeat_label = Label(self, font=INTERACTABLE_FONT, text="Repeat password:")
        self.repeat_entry = Entry(self, width=10, font=INTERACTABLE_FONT)

        self.change_button = Button(self, font=INTERACTABLE_FONT, text="Set New Password", command=self.change_password)

        self.back_button = Button(self, width=5, height=1, font=INTERACTABLE_FONT, text="Back",
                                  command=multi_func(lambda: self.root.frames[InAppFrame.__name__].set_user(self.username),
                                                     lambda: self.root.show_frame(InAppFrame.__name__)))

        self.message_label = Label(self, font=MESSAGE_FONT)

        self.assets = [self.logo_label, self.username_label, self.pass_label, self.pass_entry,
                       self.repeat_label, self.repeat_entry, self.change_button, self.back_button, self.message_label]

        self.construct_window()

    def set_user(self, username):
        self.username = username
        self.username_label.config(text="Signed in to account: " + self.username)

    def display_message(self, message, color="#ff0000"):
        self.message_label.config(text=message, fg=color)

    def change_password(self):
        self.root.change_password(self.username, self.pass_entry.get(), self.repeat_entry.get())

    def load(self):
        self.message_label.config(text='')
        super().load()


class MetaFrame(MainFrame):

    def __init__(self, parent, root):
        super().__init__(master=parent, root=root)

        self.state = 0  # 0 for pre-game, 1 for during game, 2 for loss

        self.title_label = Label(self, font=TITLE_FONT)
        self.title_label.grid(row=0, column=0)

        self.exit_button = Button(self, font=INTERACTABLE_FONT, text="Exit Lobby", command=self.exit_lobby)
        self.exit_button.grid(row=1, column=0, sticky=W, padx=PADX)

        self.start_button = Button(self, font=INTERACTABLE_FONT, text="Start Game", command=self.start_game)
        self.admin = False

        self.back_button = Button(self, font=INTERACTABLE_FONT, text="Back to Game", command=lambda: self.root.show_frame(LoginFrame.__name__))

        self.player_data = []

        self.labels = []

    def update_data(self, original_name, cur_hacking, accessible):
        # data = list of (original username, currently hacking, accessible)
        usernames = [p[0] for p in self.player_data]
        if original_name in usernames:
            p_i = usernames.index(original_name)
            self.player_data[p_i] = (original_name, cur_hacking, accessible)
        else:
            self.player_data.append((original_name, cur_hacking, accessible))

    def remove_player(self, username):
        self.columnconfigure(len(self.player_data) - 1, weight=0)
        usernames = [p[0] for p in self.player_data]
        print(usernames)
        if username in usernames:
            p_i = usernames.index(username)
            self.player_data.pop(p_i)

    def display_data(self):

        for l in self.labels:
            l.grid_remove()

        for i in range(N_PLAYERS):
            self.columnconfigure(i, weight=0)

        for i in range(len(self.player_data)):
            p = self.player_data[i]
            self.columnconfigure(i, weight=1)

            if i >= len(self.labels):
                self.labels.append(Label(self))

            self.labels[i].grid(row=2, column=i)

            self.labels[i].config(text=p[0] + ("\n\nLOST" if len(p[2]) == 0 else
                                               "\n\nCurrently Hacking: " + p[1] + "\n\nHeld accounts:\n" + '\n'.join(p[2])))

        if self.admin and self.state == 0:
            self.start_button.grid_remove()
            self.start_button.grid(row=1, column=max(0, len(self.player_data) - 1), sticky=E, padx=PADX)

        self.title_label.grid(row=0, column=0, columnspan=max(len(self.player_data), 1))

    def set_state(self, state):
        self.state = state
        if state == 0:
            self.title_label.config(text="Lobby: " + self.root.lobby)
            self.back_button.grid_remove()
            self.exit_button.grid(row=1, column=0, sticky=W, padx=PADX)
            if self.admin:
                self.start_button.grid(row=1, column=max(0, len(self.player_data) - 1), sticky=E, padx=PADX)
            else:
                self.start_button.grid_remove()
        elif state == 1:
            self.title_label.config(text="Get Hacking!")
            self.start_button.grid_remove()
            self.exit_button.grid_remove()
            self.back_button.grid(row=1, column=max(0, len(self.player_data) - 1), sticky=E, padx=PADX)
        elif state == 2:
            self.title_label.config(text="You Lost...")
            self.start_button.grid_remove()
            self.back_button.grid_remove()
            self.exit_button.grid(row=1, column=0, sticky=W, padx=PADX)
        elif state == 3:
            self.title_label.config(text="You Won!")
            self.start_button.grid_remove()
            self.back_button.grid_remove()
            self.exit_button.grid(row=1, column=0, sticky=W, padx=PADX)

    def show_start(self):
        self.admin = True
        self.display_data()

    def hide_start(self):
        self.admin = False
        self.display_data()

    def exit_lobby(self):
        self.root.exit_lobby()

    def start_game(self):
        self.root.start_game()

    def load(self):
        super().load()
        self.display_data()


class ConnectingFrame(MainFrame):

    def __init__(self, parent, root):
        super().__init__(master=parent, root=root)

        self.connecting_label = Label(self, text="Connecting to Server...", font=TITLE_FONT)
        self.connecting_label.place(relx=0.5, rely=0.5, anchor=CENTER)

    def display(self, message):
        self.connecting_label.config(text=message)
