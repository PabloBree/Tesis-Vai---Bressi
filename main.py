from PyQt5.QtWidgets import QApplication
import sys
from login_window import LoginWindow
import database_connector as mongoConnector

client, dbPointer = mongoConnector.get_database()
collection = dbPointer["usersData"]



app = QApplication(sys.argv)
mainwindows = LoginWindow(collection)

try:
    sys.exit(app.exec_()) #Aca empieza el Hilo principal...
except:
    print("Closing database connection..")
    client.close()
    print("Exiting..")
