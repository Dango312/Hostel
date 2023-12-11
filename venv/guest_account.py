import tkinter as tk
from tkinter import ttk
import tkcalendar
from datetime import timedelta,date,datetime
from VendingMachine import VendingMachine

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

        try:
            if current_user.in_hotel:
                self.vending = VendingMachine()
                self.vending.idMachine = db.get_idVending(current_user.in_hotel)
                self.vending_icon = tk.PhotoImage(file="venv/icons/vending_icon.png")
                vending_frame = GuestsVending(notebook, db, self.vending)
                notebook.add(vending_frame, text="Торговый автомат", image=self.vending_icon, compound=tk.LEFT)
        except Exception as e:
            print('vending error: ', e)




class AccountInfo(tk.Frame):
    def __init__(self, notebook, db, current_user):
        tk.Frame.__init__(self, notebook)
        self.db = db
        self.user_reservaions = self.get_reservations(current_user.phone)
        welcome_label = tk.Label(self, text='Добро пожаловать!')
        welcome_label.grid(row=1, column=0, padx=20)
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
                adress_str = str(f"{r['country']}, {r['city']}, {r['adress']}")
                user_reservation.append((adress_str, str(r['start_date']), str(r['end_date'])))
            return user_reservation
        except Exception as e:
            print(e)

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
        try:
            selection = self.hotel_list.get()
            selection = selection.split(', ')[2]
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
            self.full_rooms = []
            for type in [1, 3, 4]:
                try:
                    self.full_rooms.append(self.db.get_rooms(self.idHotel, type, self.date1.get_date(), self.date2.get_date())[0])
                except Exception as e:
                    print("Get rooms from db error:", e)
            self.rooms = [f"Тип комнаты: {room['type_name']}. " \
                          f"{room['facilities']}, {room['price']}$. Колличество: {room['count']}" for room in self.full_rooms]
            self.rooms_listbox['listvariable'] = tk.Variable(value=self.rooms)
            self.calc_price("<<ListboxSelect>>")
        except Exception as e:
            print("get_rooms error:", e)

    def calc_price(self, event):
        try:
            selection = self.rooms_listbox.curselection()
            delta = (self.date2.get_date() - self.date1.get_date()).days
            self.price = self.full_rooms[selection[0]]['price'] * delta
            self.roomType = self.full_rooms[selection[0]]['type_name']
            self.price_label['text'] = f'Итоговая стоимость бронирования: {self.price}$'
        except Exception as e:
            print(e)

    def create_reservation(self):
        try:
            self.db.reservate(self.current_user.phone, self.idHotel, self.roomType, self.date1.get_date(), self.date2.get_date())
        except Exception as e:
            print(e)

class GuestsVending(tk.Frame):
    def __init__(self, notebook, db, vending):
        tk.Frame.__init__(self, notebook)
        self.db = db
        self.vending = vending
        self.products = {}
        self.cart_items = []
        for c in range(7): self.columnconfigure(index=c, weight=1)
        for r in range(7): self.rowconfigure(index=r, weight=1)
        self.draw_vending()
        self.get_products()

    def draw_vending(self):
        'колаб вода сендвичб батончикб сок чипсы '
        self.vend = tk.Frame(self)
        self.vend.grid(sticky='ns')

        for c in range(2): self.vend.columnconfigure(index=c, weight=1)
        for r in range(3): self.vend.rowconfigure(index=r, weight=1)

        self.water_icon = tk.PhotoImage(file="venv/icons/water_icon.png")
        self.water_btn = tk.Button(self.vend, text='2', image=self.water_icon, compound="top", command=lambda: self.add_to_cart('вода', '70'))
        self.water_btn.grid(row=0, column=0)

        self.cola_icon = tk.PhotoImage(file="venv/icons/cola_icon.png")
        self.cola_btn = tk.Button(self.vend, text='3', image=self.cola_icon, compound="top", command=lambda: self.add_to_cart('кола', '80'))
        self.cola_btn.grid(row=0, column=1)

        self.juice_icon = tk.PhotoImage(file="venv/icons/juice_icon.png")
        self.juice_btn = tk.Button(self.vend, text='3', image=self.juice_icon, compound="top", command=lambda: self.add_to_cart('сок', '70'))
        self.juice_btn.grid(row=2, column=0)

        self.sandwich_icon = tk.PhotoImage(file="venv/icons/sandwich_icon.png")
        self.sandwich_btn = tk.Button(self.vend, text='3', image=self.sandwich_icon, compound="top", command=lambda: self.add_to_cart('сэндвич', '160'))
        self.sandwich_btn.grid(row=2, column=1)

        self.chips_icon = tk.PhotoImage(file="venv/icons/chips_icon.png")
        self.chips_btn = tk.Button(self.vend, text='3', image=self.chips_icon, compound="top", command=lambda: self.add_to_cart('чипсы', '80'))
        self.chips_btn.grid(row=3, column=0)

        self.bar_icon = tk.PhotoImage(file="venv/icons/bar_icon.png")
        self.bar_btn = tk.Button(self.vend, text='3', image=self.bar_icon, compound="top", command=lambda: self.add_to_cart('батончик', '60'))
        self.bar_btn.grid(row=3, column=1)

        self.buy_btn = tk.Button(self, text='Купить', command=self.buy_items)
        self.buy_btn.grid(row=4, column=0, pady=10)

        self.cancel_btn = tk.Button(self, text='Отмена', command=self.clear_cart)
        self.cancel_btn.grid(row=4, column=1, pady=10)

        self.cart = ttk.Treeview(self)
        self.cart['columns'] = ('Product Name', 'Price')
        self.cart.heading('#0', text='№')
        self.cart.column('#0', width=50)
        self.cart.heading('Product Name', text='Название товара')
        self.cart.column('Product Name', width=150)
        self.cart.heading('Price', text='Цена')
        self.cart.column('Price', width=100)
        self.cart.grid(row=1,column=5, columnspan=2, padx=10, pady=10)
        self.update_cart_display()

    def get_products(self):
        self.products = self.db.get_products(self.vending.idMachine)
        print(self.products)
        buttons_info = {
            'вода': self.water_btn,
            'кола': self.cola_btn,
            'сок': self.juice_btn,
            'сэндвич': self.sandwich_btn,
            'чипсы': self.chips_btn,
            'батончик': self.bar_btn
        }
        for product in self.products:
            product_name = product['product_name']
            quantity = product['quantity']
            product_price = product['product_price']

            # Проверяем, есть ли продукт на кнопке, и если есть, меняем текст кнопки
            if product_name in buttons_info:
                button = buttons_info[product_name]
                button['text'] = f'{product_price}р.'

    def add_to_cart(self, product_name, product_price):
        for product in self.products:
            if product['product_name'] == product_name:
                if product['quantity'] > 0:
                    self.cart_items.append({'product_name': product_name, 'product_price': product_price})
                    self.decrease_quantity(product_name)
                    self.update_cart_display()
                else:
                    tk.messagebox.showwarning(title="Предупреждение", message="Товар закончился")
                break

    def decrease_quantity(self, product_name):
        for product in self.products:
            if product['product_name'] == product_name:
                product['quantity'] -= 1
                if product['quantity'] < 0:
                    product['quantity'] = 0
                #self.update_button_text(product_name, product['quantity'])
                print(self.products)

    def buy_items(self):
        self.db.buy_products(self.vending.idMachine, self.products)
        children_count = len(self.cart.get_children())
        if children_count > 0:
            self.cart.delete(*self.cart.get_children())
            self.cart_items = []

    def clear_cart(self):
        children_count = len(self.cart.get_children())
        if children_count > 0:
            self.cart.delete(*self.cart.get_children())  # Удаляем все дочерние элементы
            for item in self.cart_items:
                product_name = item['product_name']
                for product in self.products:
                    if product['product_name'] == product_name:
                        product['quantity'] += 1  # Возвращаем товар в автомат
            self.cart_items = []  # Очищаем список товаров в корзине
            print('Корзина опустошена.')
        else:
            print('Корзина уже пуста.')

    def update_cart_display(self):
        for item in self.cart.get_children():
            self.cart.delete(item)

        for index, item in enumerate(self.cart_items, start=1):
            product_name = item['product_name']
            product_price = item['product_price']
            self.cart.insert('', 'end', text=str(index), values=(product_name, f"{str(product_price)}р."))








