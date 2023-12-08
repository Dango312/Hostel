from dataclasses import dataclass

@dataclass
class User():
    phone: str = ''
    email: str = ''
    name: str = ''
    surname: str = ''
    in_hotel: str = 0

    def set_user_info(self, user_info):
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




        



