#--Librerías--
from users import * 

#--Funciones--

def login_check(self, emailentry, passwdentry):
    sellsystem_users = [user1, user2, user3]  # List of users for the sellsystem interface
    inventorysystem_users = [user4, user5]  # List of users for the inventorysystem interface
    
    for user in sellsystem_users:
        if emailentry == user.get_email() and passwdentry == user.get_passwd():
            self.login_frame.pack_forget()
            self.sellsystem_frame.show()
            self.resizable(True, True)
            return
    
    for user in inventorysystem_users:
        if emailentry == user.get_email() and passwdentry == user.get_passwd():
            self.login_frame.pack_forget()
            self.inventorysystem_frame.show()
            self.resizable(True, True)
            return
    
    return self.loginerror_label.place(x=90, y=400)