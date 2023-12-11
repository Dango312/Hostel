from dataclasses import dataclass

@dataclass
class User():
    phone: str = ''
    email: str = ''
    name: str = ''
    surname: str = ''
    in_hotel: int = 0
    # for employee
    idHotel: int = 1
    idEmployee: int = 0

    def set_guest_info(self, user_info):
        #print(user_info)
        try:
            self.phone = user_info[0]['phone_number']
            self.email = user_info[0]['guest_email']
            self.name = user_info[0]['guest_name']
            self.surname = user_info[0]['guest_surname']
            self.in_hotel = user_info[0]['in_hotel']
            #print(self.phone, self.email, self.name)
        except Exception as e:
            print(e)

    def set_admin_info(self, user_info):
        try:
            self.email = user_info[0]['employee_email']
            self.name = user_info[0]['employee_full_name']
            self.idHotel = user_info[0]['hotels_idHotel']
            self.idEmployee = user_info[0]['idEmployee']
            print(self.email, self.name, self.idHotel)
        except Exception as e:
            print(e)



        



