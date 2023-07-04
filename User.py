class User:
    def __init__(self, email, passwd):
        self.__email = email
        self.__passwd = passwd

    def get_email(self):
        return self.__email
    
    def set_email(self, email):
        self.__email = email
    
    def get_passwd(self):
        return self.__passwd
    
    def set_passwd(self, passwd):
        self.__passwd = passwd
