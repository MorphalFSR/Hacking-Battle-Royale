from baseclasses import BaseFrame


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

    def load(self):
        self.attempts = 0
        super().load()


class InAppFrame(BaseFrame):

    def __init__(self, parent, root):
        super().__init__(master=parent, root=root)

        self.back_button = Button(self, width=5, height=1, font=INTERACTABLE_FONT, text="Back",
                                  command=lambda: self.root.show_frame(LoginFrame.__name__))
        self.back_button.pack()