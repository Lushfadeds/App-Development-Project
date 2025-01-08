class User:
    def __init__(self, name: str, contact_number: str, email: str, password: str, role: str):
        self.__name = name
        self.contact_number = contact_number
        self.__email = email
        self.__password = password
        self.role = role

    # Getter for name
    def get_name(self):
        return self.__name

    # Setter for name
    def set_name(self, name):
        if not name.strip():
            raise ValueError("Name cannot be empty.")
        self.__name = name

    # Getter for email
    def get_email(self):
        return self.__email

    # Setter for email
    def set_email(self, email):
        if not self.validate_email(email):
            raise ValueError("Invalid email format.")
        self.__email = email

    # Getter for password (optional - for security, usually avoided)
    def get_password(self):
        return "Access Denied: Passwords are not retrievable."

    # Setter for password
    def set_password(self, password):
        if not self.validate_password(password):
            raise ValueError("Password must be at least 8 characters long and include a number.")
        self.__password = password

    # Validation methods
    def validate_password(self, password):
        return len(password) >= 8 and any(char.isdigit() for char in password)

    def validate_email(self, email):
        import re
        return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

    def validate_phone_number(self, phone_number):
        return len(phone_number) >= 8 and phone_number.isdigit()

    # Example methods (placeholders)
    def register_user(self, name, contact_number, email, password, role):
        pass

    def login_user(self, name, contact_number, email, password, role):
        pass
