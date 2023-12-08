import tkinter as tk
from guest_account import GuestAccount

class Login(tk.Frame):
    def __init__(self, parent, controller, db, current_user):
        tk.Frame.__init__(self, parent)
        #self.db = db

        self.email = tk.StringVar()
        self.password = tk.StringVar()

        label_email = tk.Label(self, text="Почта:")
        label_email.grid(row=1, column=0, padx=20)

        email_entry = tk.Entry(self, textvariable=self.email)
        email_entry.grid(row=2, column=0, padx=20)

        label = tk.Label(self, text="Пароль:")
        label.grid(row=3, column=0, padx=20)

        pwd_entry = tk.Entry(self, textvariable=self.password, show="*")
        pwd_entry.grid(row=4, column=0, padx=20)

        def login_user():
            user_info = db.login(email_entry.get(), pwd_entry.get())
            #print(user_info)
            if user_info:
                current_user.set_user_info(user_info)
                controller.show_guest_account(current_user)
                #print('succes')

        login = tk.Button(self, text="Войти", command=login_user)
        login.grid(row=5, column=0, padx=20)

        gotoreg = tk.Button(self, text="Создать аккаунт", command = lambda: controller.show_frame(Registration))
        gotoreg.grid(row=6, column=0, padx=20)

class Registration(tk.Frame):
    def __init__(self, parent, controller,db):
        tk.Frame.__init__(self, parent)

        self.email = tk.StringVar()
        self.phone = tk.StringVar()
        self.name = tk.StringVar()
        self.surname = tk.StringVar()
        self.password = tk.StringVar()
        self.password2 = tk.StringVar()
        self.errmsg = tk.StringVar()

        self.password.trace("w", self.validate_password)
        self.password2.trace("w", self.validate_password)

        label = tk.Label(self, text = "Имя:")
        label.pack(anchor=tk.NW, padx=6, pady=6)
        name_entry = tk.Entry(self, textvariable=self.name)
        name_entry.pack(anchor=tk.NW, padx=6, pady=6)

        label = tk.Label(self, text = "Фамилия:")
        label.pack(anchor=tk.NW, padx=6, pady=6)
        surname_entry = tk.Entry(self, textvariable=self.surname)
        surname_entry.pack(anchor=tk.NW, padx=6, pady=6)

        label = tk.Label(self, text = "Номер телефона:")
        label.pack(anchor=tk.NW, padx=6, pady=6)
        phone_entry = tk.Entry(self, validate="key",
                                    validatecommand=(self.register(self.validate_phone), "%P"))
        phone_entry.pack(anchor=tk.NW, padx=6, pady=6)
        phone_label = tk.Label(self, text = "")
        phone_label.pack(anchor=tk.NW, padx=3, pady=3)

        label = tk.Label(self, text = "Почта:")
        label.pack(anchor=tk.NW, padx=6, pady=6)
        email_entry = tk.Entry(self, validate="key",
                                    validatecommand=(self.register(self.validate_email), "%P"))
        email_entry.pack(anchor=tk.NW, padx=6, pady=6)
        email_label = tk.Label(self, text = "")
        email_label.pack(anchor=tk.NW, padx=3, pady=3)

        label = tk.Label(self, text = "Пароль:")
        label.pack(anchor=tk.NW, padx=6, pady=6)
        pwd_entry = tk.Entry(self, textvariable=self.password, show="*")
        pwd_entry.pack(anchor=tk.NW, padx=6, pady=6)

        label = tk.Label(self, text = "Повторите пароль:")
        label.pack(anchor=tk.NW, padx=6, pady=6)
        pwd2_entry = tk.Entry(self, textvariable=self.password2, show="*")
        pwd2_entry.pack(anchor=tk.NW, padx=6, pady=6)

        error_label = tk.Label(self, foreground="red", textvariable=self.errmsg, wraplength=250)
        error_label.pack(padx=5, pady=5, anchor=tk.NW)

        reg = tk.Button(self, text="Зарегистрироваться",
                             command=lambda: self.reg_user(self.phone_entry.get(), self.email_entry.get(),
                                                           self.name.get(), self.surname.get(), self.password.get()))
        reg.pack(anchor=tk.NW, padx=6, pady=6)

        reg = tk.Button(self, text="Уже есть аккаунт", command=lambda: controller.show_frame(Login))
        reg.pack(anchor=tk.NW, padx=6, pady=6)


    def validate_password(self, *args):
        if self.password.get() != self.password2.get():
            self.errmsg.set("Пароли не совпадают")
            return False
        else:
            self.errmsg.set("Пароли совпадают")
            return True

    def validate_phone(self, phone):
        if re.match(r'^\+\d{11}$', phone):
            self.phone_label['text'] = ''
        else:
            self.phone_label['text'] = 'Номер телефона должен быть в формате: +xxxxxxxxxxx'
        return True

    def validate_email(self, email):
        if re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            self.email_label['text'] = ''
        else:
            self.email_label['text'] = 'Неверный формат электронной почты'
        return True

    def reg_user(self, phone, email, name, surname, password):
        try:
            for arg in [phone, email, name, surname, password]:
                if self.checkSQLinjection(arg):
                    self.errmsg.set("Введён один из запрещённых символов: \"\'\\")
                    return 0
            if (self.validate_password()
                    and re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email)
                    and re.match(r'^\+\d{11}$', phone)):
                self.db.registration(phone, email, name, surname, password)
                controller.show_frame(Login)
            else:
                self.errmsg.set("Пароли не совпадают")
        except Exception as e:
            print(e)

    def checkSQLinjection(self, string):
        if re.findall(r'[\"\'\\]', string):
            return True
        else:
            return False
