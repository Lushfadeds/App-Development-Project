class User:
    count_id = 0

    def __init__(self,name:str, contact_number:str, email:str, password:str, role:str):
        User.count_id += 1
        self.__user_id = User.count_id
        self.__name = name
        self.contact_number = contact_number
        self.__email = email
        self.__password = password
        self.role = role

    def register_user(self):
        pass

    def get_name(self):
        return self.__name
