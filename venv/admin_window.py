import tkinter as tk
from tkinter import ttk
from VendingMachine import VendingMachine

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

        try:
            if current_user.idHotel:
                self.vending = VendingMachine()
                self.vending.idMachine = db.get_idVending(current_user.idHotel)
                self.vending_icon = tk.PhotoImage(file="venv/icons/vending_icon.png")
                vending_frame = AdminVending(notebook, db, self.vending)
                notebook.add(vending_frame, text="Торговый автомат", image=self.vending_icon, compound=tk.LEFT)
        except Exception as e:
            print('vending error: ', e)

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

class AdminVending(tk.Frame):
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
        for r in range(4): self.vend.rowconfigure(index=r, weight=1)

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

        self.buy_btn = tk.Button(self.vend, text='Купить', command=self.buy_items)
        self.buy_btn.grid(row=4, column=0, pady=10)

        self.cancel_btn = tk.Button(self.vend, text='Отмена', command=self.clear_cart)
        self.cancel_btn.grid(row=4, column=1, pady=10)

        self.cart = ttk.Treeview(self)
        self.cart['columns'] = ('Product Name', 'Price')
        self.cart.heading('#0', text='№')
        self.cart.column('#0', width=50)
        self.cart.heading('Product Name', text='Название товара')
        self.cart.column('Product Name', width=150)
        self.cart.heading('Price', text='Цена')
        self.cart.column('Price', width=100)
        self.cart.grid(row=0,column=3, columnspan=2, padx=10, pady=10)
        self.update_cart_display()

    def draw_products_table(self):
        self.products_table = ttk.Treeview(self)
        self.products_table['columns'] = ('Product Name', 'Price', 'Quantity')
        self.products_table.heading('#0', text='№')
        self.products_table.column('#0', width=50)
        self.products_table.heading('Product Name', text='Название товара')
        self.products_table.column('Product Name', width=150)
        self.products_table.heading('Price', text='Цена')
        self.products_table.column('Price', width=100)
        self.products_table.heading('Quantity', text='Количество')
        self.products_table.column('Quantity', width=100)
        self.products_table.grid(row=4, column=7, columnspan=2, padx=10, pady=10)
        self.update_products_table()

        # Добавление поля для ввода нового количества товара
        self.new_quantity_entry = tk.Entry(self)
        self.new_quantity_entry.grid(row=5, column=7, padx=5, pady=5)
        self.change_quantity_btn = tk.Button(self, text='Изменить количество', command=self.change_quantity)
        self.change_quantity_btn.grid(row=5, column=8, padx=5, pady=5)

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
        self.draw_products_table()

    def update_products_table(self):
        for item in self.products_table.get_children():
            self.products_table.delete(item)

        for index, product in enumerate(self.products, start=1):
            product_name = product['product_name']
            product_price = product['product_price']
            product_quantity = product['quantity']
            self.products_table.insert('', 'end', text=str(index),
                                       values=(product_name, f"{str(product_price)}р.", product_quantity))

    def change_quantity(self):
        selected_item = self.products_table.focus()
        if selected_item:
            new_quantity = self.new_quantity_entry.get()
            try:
                new_quantity = int(new_quantity)
                if new_quantity >= 0:
                    item = self.products_table.item(selected_item)
                    product_name = item['values'][0]
                    for product in self.products:
                        if product['product_name'] == product_name:
                            product['quantity'] = new_quantity
                            self.db.buy_products(self.vending.idMachine, self.products)
                    self.update_products_table()
                else:
                    tk.messagebox.showwarning(title="Ошибка", message="Количество не может быть отрицательным")
            except ValueError:
                tk.messagebox.showwarning(title="Ошибка", message="Введите корректное число")

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


