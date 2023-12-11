import tkinter as tk
from tkinter import ttk

class AdminWindow(tk.Frame):
    def __init__(self, parent, controller, db, current_user):
        tk.Frame.__init__(self, parent)

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        hotelInfo = HotelInfo(notebook, db, current_user)
        hotelReservations =  HotelReservations(notebook, db, current_user)

        self.hotel_icon = tk.PhotoImage(file="venv/icons/hotel_icon.png")
        self.booking_icon = tk.PhotoImage(file="venv/icons/booking_icon.png")

        notebook.add(hotelInfo, text="Личный кабинет", image=self.hotel_icon, compound=tk.LEFT)
        notebook.add(hotelReservations, text="Бронирования", image=self.booking_icon, compound=tk.LEFT)

class HotelInfo(tk.Frame):
    def __init__(self, notebook, db, current_user):
        tk.Frame.__init__(self, notebook)
        self.db = db
        self.current_user = current_user

        welcome_lable = tk.Label(self, text = f"Добро пожаловать {current_user.name}!")
        welcome_lable.grid(row=1, column=0)

        self.hotel_lable = tk.Label(self, text=f"Отель: {self.employee_hotel(current_user.idHotel)}")
        self.hotel_lable.grid(row=2, column=0)

        self.update_btn = tk.Button(self, text='Обновить', command=self.update_tables)
        self.update_btn.grid(row=1, column=1, padx=20, pady=10)

        self.current_rooms_info(current_user.idHotel)

        colums = ['Имя', 'Номер комнаты', 'Статус', 'Тип комнаты']
        self.rooms = ttk.Treeview(self, columns=colums, show='headings')
        self.rooms.grid(row=4, column=2)
        self.rooms.heading("Имя", text="Имя", command=lambda: self.sort(0, False))
        self.rooms.heading("Номер комнаты", text="Номер комнаты", command=lambda: self.sort(1, False))
        self.rooms.heading("Статус", text="Статус", command=lambda: self.sort(2, False))
        self.rooms.heading("Тип комнаты", text="Тип комнаты", command=lambda: self.sort(3, False))
        for r in self.current_rooms_info(current_user.idHotel):
            self.rooms.insert("", tk.END, values=r)

    def employee_hotel(self, idHotel):
        info = self.db.select_hotel(idHotel)[0]
        info = str(f"{info['country']}, {info['city']}, {info['adress']}")
        return info

    def current_rooms_info(self, idHotel):
        hotel_rooms = []
        for room in self.db.select_rooms(idHotel):
            hotel_rooms.append((room['name'], room['room_number'], room['status_name'], room['type_name']))
        return hotel_rooms

    def sort(self, col, reverse):
        l = [(self.rooms.set(k, col), k) for k in self.rooms.get_children("")]
        l.sort(reverse=reverse)
        for index, (_, k) in enumerate(l):
            self.rooms.move(k, "", index)
        self.rooms.heading(col, command=lambda: self.sort(col, not reverse))

    def update_tables(self):
        for item in self.rooms.get_children():
            self.rooms.delete(item)

        new_rooms_info = self.current_rooms_info(self.current_user.idHotel)
        for r in new_rooms_info:
            self.rooms.insert("", tk.END, values=r)


class HotelReservations(tk.Frame):
    def __init__(self, notebook, db, current_user):
        tk.Frame.__init__(self, notebook)
        self.db = db
        self.current_user = current_user
        self.put_widgets()

    def put_widgets(self):
        self.selected_reservation = []

        self.checkin_btn = tk.Button(self, text = 'Заселить', command=self.check_in_guest)
        self.checkin_btn.grid(row=0, column=0, padx=10, pady=10)

        self.checkout_btn = tk.Button(self, text = 'Выселить', command=self.check_out_guest)
        self.checkout_btn.grid(row=1, column=0, padx=40, pady=10)

        self.update_btn = tk.Button(self, text='Обновить', command=self.update_tables)
        self.update_btn.grid(row=1, column=1, padx=20, pady=10)

        colums = ['ID','Телефон', 'Имя', '№ комнаты', 'Начало', 'Окончание', 'Заселился', 'Выселился']
        self.rooms = ttk.Treeview(self, columns=colums, show='headings', selectmode='browse')
        self.rooms.grid(row=10, column=0, pady = 40, columnspan=3)
        self.rooms.heading("ID", text="ID", command=lambda: self.sort(0, False))
        self.rooms.heading("Телефон", text="Телефон", command=lambda: self.sort(0, False))
        self.rooms.heading("Имя", text="Имя", command=lambda: self.sort(1, False))
        self.rooms.heading("№ комнаты", text="№ комнаты", command=lambda: self.sort(2, False))
        self.rooms.heading("Начало", text="Начало", command=lambda: self.sort(3, False))
        self.rooms.heading("Окончание", text="Окончание", command=lambda: self.sort(4, False))
        self.rooms.heading("Заселился", text="Заселился", command=lambda: self.sort(5, False))
        self.rooms.heading("Выселился", text="Выселился", command=lambda: self.sort(6, False))
        self.rooms.column("#1", stretch=False, width=40)
        self.rooms.column("#2", stretch=False, width=100)
        self.rooms.column("#3", stretch=False, width=100)
        self.rooms.column("#4", stretch=False, width=80)
        self.rooms.column("#5", stretch=False, width=100)
        self.rooms.column("#6", stretch=False, width=100)
        self.rooms.column("#7", stretch=False, width=70)
        self.rooms.column("#8", stretch=False, width=70)
        #Скролбар для таблицы
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.rooms.yview)
        self.rooms.configure(yscroll=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=1, sticky="ns")


        self.rooms.bind("<<TreeviewSelect>>", self.item_selected)

        for r in self.get_hotel_reservations(self.current_user.idHotel):
            self.rooms.insert("", tk.END, values=r)

    def get_hotel_reservations(self, idHotel):
        hotel_reservations = []
        for reservation in self.db.select_hotel_reservations(idHotel):
            hotel_reservations.append(tuple(v for v in reservation.values()))
        return hotel_reservations

    def sort(self, col, reverse):
        l = [(self.rooms.set(k, col), k) for k in self.rooms.get_children("")]
        l.sort(reverse=reverse)
        for index, (_, k) in enumerate(l):
            self.rooms.move(k, "", index)
        self.rooms.heading(col, command=lambda: self.sort(col, not reverse))

    def item_selected(self, event):
        self.selected_reservation = self.rooms.item(self.rooms.selection())['values']
        print(self.selected_reservation)

    def check_in_guest(self):
        self.db.check_in_guest(self.selected_reservation[0])
        self.update_tables()

    def check_out_guest(self):
        if self.selected_reservation and self.selected_reservation[6] == 1:  # Проверяем, заселился ли гость
            self.db.check_out_guest(self.selected_reservation[0])
            self.update_tables()
        else:
            tk.messagebox.showwarning(title="Предупреждение", message="Гость не заселён")

    def update_tables(self):
        for item in self.rooms.get_children():
            self.rooms.delete(item)

        new_reservations = self.get_hotel_reservations(self.current_user.idHotel)
        for r in new_reservations:
            self.rooms.insert("", tk.END, values=r)





