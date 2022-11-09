from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.uic import loadUi
from settings_window import SettingsWindow
from PyQt5 import QtCore, QtGui, QtWidgets
import database_connector as mongoConnector
from pymongo.errors import OperationFailure
from cryptography.fernet import Fernet

class LoginWindow(QMainWindow):
    def __init__(self,collection):
        super(LoginWindow, self).__init__()
        loadUi('UI/login_window.ui', self)
        self.register_button.clicked.connect(self.registrarUsuario) #no se esta usando.
        self.login_button.clicked.connect(self.open_settings_window)

        #self.client, dbPointer = mongoConnector.get_database()
        self.collection = collection

        self.encryptionKey = self.getKey()
        self.fernet = Fernet(self.encryptionKey)
        self.show()

    def go_to_register_page(self):
        print("reg page")

    def registrarUsuario(self):


        username = self.username_input.text()
        password = self.password_input.text()
        encryptedPassword = self.fernet.encrypt(password.encode())

        user = {"User":{
                    "username": username,
                    "password": encryptedPassword,
                    "lastDetection": 0,
                    "cameras": []
                }
            }

        if username == "" or password == "":
            self.collection.insert_one(user)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Usuario y Contraseña no pueden estar vacios")
            msg.setWindowTitle("¡Atención!")
            msg.exec_()
        else:
            try:
                if not self.existe(self.collection, username):
                    self.collection.insert_one(user)
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText(f"El usuario {username} fue registrado exitosamente en la base de datos")
                    msg.setWindowTitle("Registro Exitoso")
                    msg.exec_()
                else:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText(f"El usuario {username} ya se encuentra registrado en nuestra base de datos")
                    msg.setWindowTitle("¡Atención!")
                    msg.exec_()
            except OperationFailure as OF:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText(f"Hubo un problema en el registro del usuario {username}")
                msg.setWindowTitle("¡Atención!")
                msg.exec_()


    def existe(self,collection,username):
        if collection.count_documents({'User.username': username}, limit = 1) != 0: #existe el usuario
            #(f"Encontrado {collection.count_documents({'User.username': username}, limit = 1)}")
            return True
        else:
            #print(f"NO! Encontrado {collection.count_documents({'User.username': username}, limit = 1)}")
            return False

    def passwordCheck(self,collection,username, password):
        try:
            data = collection.find_one({"User.username": username})
            encryptedDBPass = data['User']['password']
            decryptedDBPass = self.fernet.decrypt(encryptedDBPass).decode()

            if decryptedDBPass == password:
                #print(f"Contrasena desencriptada es: {decryptedDBPass} y la contrasena que enviamos nosotros de login es: {password}")
                return True
            else:
                #print(f"Contrasena desencriptada es: {decryptedDBPass} y la contrasena que enviamos nosotros de login es: {password}")
                return False
        except OperationFailure:
            return False

    def open_settings_window(self):

        username = self.username_input.text()
        password = self.password_input.text()
        if username == "" or password == "":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Usuario y Contraseña no pueden estar vacios")
            msg.setWindowTitle("¡Atención!")
            msg.exec_()
        else:
            if self.passwordCheck(self.collection,username, password):
                self.settings_window = SettingsWindow(username, self.collection)
                self.settings_window.displayInfo()
                self.close()
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("Usuario o contraseña invalidos")
                msg.setWindowTitle("¡Atención!")
                msg.exec_()



    def getKey(self):
        with open('encryptionKey.txt', 'r') as f:
            lines = f.readlines()
            f.close()
            return lines[0].encode('UTF-8')
