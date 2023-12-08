import tkinter as tk
from tkinter import ttk
import tkcalendar
from datetime import timedelta,date,datetime


class GuestAccount(tk.Frame):
    def __init__(self, parent, controller, db, current_user):

        tk.Frame.__init__(self, parent)
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        info_frame = AccountInfo(notebook, db, current_user)
        reservation_frame = GuestReservation(notebook, db, current_user)

        self.user_icon = tk.PhotoImage(file="venv/icons/user_icon.png")
        self.booking_icon = tk.PhotoImage(file="venv/icons/booking_icon.png")
        notebook.add(info_frame, text="Личный кабинет", image=self.user_icon, compound=tk.LEFT)
        notebook.add(reservation_frame, text="Бронирование", image=self.booking_icon, compound=tk.LEFT)

class AccountInfo(tk.Frame):
    def __init__(self, notebook, db, current_user):
        tk.Frame.__init__(self, notebook)
        self.db = db
        self.user_reservaions = self.get_reservations(current_user.phone)
        #self.current_user = current_user
        welcome_label = tk.Label(self, text='Добро пожаловать!')
        welcome_label.grid(row=1, column=0, padx=20)
        #print("telefon", current_user.phone, current_user.email)
        name_label = tk.Label(self, text = f'Имя: {current_user.name} {current_user.surname}')
        name_label.grid(row=2, column=0, padx=20)

        colums = ['Отель', 'Дата заезда', 'Дата выезда']
        self.reservations = ttk.Treeview(self, columns=colums, show='headings')
        self.reservations.grid(row=1, column=5)
        self.reservations.heading("Отель", text="Отель")
        self.reservations.heading("Дата заезда", text="Дата заезда")
        self.reservations.heading("Дата выезда", text="Дата выезда")
        for r in self.user_reservaions:
            self.reservations.insert("", tk.END, values=r)

    def get_reservations(self, phone):
        try:
            user_reservation = []
            reservations = self.db.get_users_reservaion(phone)
            for r in reservations:
                #print(str(f"{r['country']}, {r['city']}, {r['adress']}"))
                adress_str = str(f"{r['country']}, {r['city']}, {r['adress']}")
                user_reservation.append((adress_str, str(r['start_date']), str(r['end_date'])))
            #print(user_reservation)
            return user_reservation
        except Exception as e:
            print(e)



        print(reservations)


class GuestReservation(tk.Frame):
    def __init__(self, notebook, db, current_user):
        tk.Frame.__init__(self, notebook)
        self.db = db
        self.current_user = current_user
        self.full_adresses = []
        self.combobox_adresses = []
        self.idHotel = 0
        self.rooms = []
        self.full_rooms=[]
        self.price = 0
        self.rooms_var = tk.Variable(value=self.rooms)
        self.roomType=0

        adress_label = tk.Label(self, text = 'Страна или город')
        adress_label.grid(row=1, column=0, padx=20)

        self.adress_entry = tk.Entry(self, validate="key", validatecommand=(self.register(self.get_hotels), "%P"))
        self.adress_entry.grid(row=3, column=0, padx=20)

        self.hotel_list = ttk.Combobox(self, values=self.combobox_adresses, state="readonly", width=50)
        self.hotel_list.grid(row=4, column=0, padx=30, pady=20)
        self.hotel_list.bind("<<ComboboxSelected>>", self.get_idHotel)

        self.rooms_listbox = tk.Listbox(self, listvariable=self.rooms_var, width=80)
        self.rooms_listbox.grid(row=6, column=0, padx=30)
        self.rooms_listbox.bind("<<ListboxSelect>>", self.calc_price)

        start_label = tk.Label(self, text = 'Начало бронирования:')
        start_label.grid(row=1, column=2, padx=20)
        self.date1 = tkcalendar.DateEntry(self, mindate=datetime.now(),
                                          maxdate=(datetime.now() + timedelta(days=365)))
        self.date1.grid(row=1, column=3, padx=10)
        self.date1.bind("<<DateEntrySelected>>", self.calc_price)

        end_label = tk.Label(self, text = 'Окончание бронирования:')
        end_label.grid(row=4, column=2, padx=20)
        self.date2 = tkcalendar.DateEntry(self, mindate=(datetime.now() + timedelta(days=1)),
                                          maxdate=(datetime.now() + timedelta(days=365)))
        self.date2.grid(row=4, column=3, padx=10)
        self.date2.bind("<<DateEntrySelected>>", self.calc_price)

        self.price_label = tk.Label(self, text = f'Итоговая стоимость бронирования: {self.price}$')
        self.price_label.grid(row=1, column=4, padx=10)

        self.reservate_btn = tk.Button(self, text = 'Забронировать', command=self.create_reservation)
        self.reservate_btn.grid(row=3, column=4, padx=10)

    def get_hotels(self, adress):
        self.full_adresses = self.db.get_hotels(adress)
        self.combobox_adresses = [f"{hotel['country']}, {hotel['city']}, {hotel['adress']}" for hotel in self.full_adresses]
        self.hotel_list['values'] = self.combobox_adresses
        return 1

    def get_idHotel(self, event):
        #print("getigHotel")
        try:
            selection = self.hotel_list.get()
            #print(selection)
            selection = selection.split(', ')[2]
            #print(selection)
            for adr in self.full_adresses:
                for key, value in adr.items():
                    if value == selection:
                        self.idHotel = adr['idHotel']
                        print("ID HOTEL", adr['idHotel'])
                        self.get_rooms()
        except Exception as e:
            print(e)

    def get_rooms(self):
        try:
            #print(self.date1.get_date())
            self.full_rooms = []
            for type in [1, 3, 4]:
                #print("TYPE", type)
                try:
                    self.full_rooms.append(self.db.get_rooms(self.idHotel, type, self.date1.get_date(), self.date2.get_date())[0])
                    #print(self.full_rooms)
                except Exception as e:
                    print("Get rooms from db error:", e)
            self.rooms = [f"Тип комнаты: {room['type_name']}. " \
                          f"{room['facilities']}, {room['price']}$. Колличество: {room['count']}" for room in self.full_rooms]
            #print(self.rooms)
            self.rooms_listbox['listvariable'] = tk.Variable(value=self.rooms)
            self.calc_price("<<ListboxSelect>>")
        except Exception as e:
            print("get_rooms error:", e)

    def calc_price(self, event):
        try:
            selection = self.rooms_listbox.curselection()
            delta = (self.date2.get_date() - self.date1.get_date()).days
            #print('DELTA:', delta)
            self.price = self.full_rooms[selection[0]]['price'] * delta
            self.roomType = self.full_rooms[selection[0]]['type_name']
            self.price_label['text'] = f'Итоговая стоимость бронирования: {self.price}$'
            #print(f"Price = {self.price}, {delta}")
        except Exception as e:
            print(e)

    def create_reservation(self):
        try:
            self.db.reservate(self.current_user.phone, self.idHotel, self.roomType, self.date1.get_date(), self.date2.get_date())
        except Exception as e:
            print(e)









