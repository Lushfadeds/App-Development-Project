class User:
    def __init__(self,name:str, contact_number:str, email:str, password:str, role:str):
        self.__name = name
        self.contact_number = contact_number
        self.__email = email
        self.__password = password
        self.role = role
    def register_user(self):
        pass