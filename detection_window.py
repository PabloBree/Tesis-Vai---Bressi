from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QTimer
from PyQt5 import QtCore
from PyQt5.QtGui import QImage, QPixmap
from detection import Detection
from easygui import *
import cv2
import numpy as np
import time

#http://186.127.194.202:8080/shot.jpg

class DetectionWindow(QMainWindow):
    def __init__(self):
        super(DetectionWindow, self).__init__()
        loadUi('UI/detection_window.ui', self)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        self.stop_detection_button.clicked.connect(self.closeDetectionWindows)
        self.detectionCounter = 0

    #https://www.bocajuniors.com.ar/upload/images/thumbs/pl/ac/1920x794placa-escudo-de-boca_4867d.jpeg
    #https://static.educalingo.com/img/ms/800/pistol.jpg
    contadorCamarasLocales = 0
    camerasDict = dict()
    detectionClosing = pyqtSignal(bool)


    def create_detection_instance(self, listaCamara, username, collection):
        self.camerasDict = dict()
        self.username = username
        self.userFilter = {'User.username': self.username}
        self.collection = collection
        self.updateContadoresDB()

        for cam in listaCamara:
            #self.camerasDict[listaCamara.index(cam)+1] = Detection(cam,listaCamara.index(cam)+1, self.contadorCamarasLocales)
            self.camerasDict[cam["uuid_camera"]] = Detection(cam, self.contadorCamarasLocales)
            if not cam["URL"]:
                self.contadorCamarasLocales += 1



    def closeDetectionWindows(self):
        self.detectionClosing.emit(True)
        ##Update de valores
        newvalues = {"$set": {'User.lastDetection': self.detectionCounter}}
        self.collection.update_one(self.userFilter, newvalues)
        ##
        self.close()

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.label_detection.setPixmap(QPixmap.fromImage(image)) #el qpixmap va a manejar el frame de la camara, va a recibir el frame emitido de la clase DETECTION

    @pyqtSlot(QImage)
    def setImage2(self, image):
        self.label_detection2.setPixmap(QPixmap.fromImage(image))  # el qpixmap va a manejar el frame de la camara, va a recibir el frame emitido de la clase DETECTION

    @pyqtSlot(QImage)
    def setImage3(self, image):
        self.label_detection3.setPixmap(QPixmap.fromImage(image))  # el qpixmap va a manejar el frame de la camara, va a recibir el frame emitido de la clase DETECTION

    @pyqtSlot(QImage)
    def setImage4(self, image):
        self.label_detection4.setPixmap(QPixmap.fromImage(image))  # el qpixmap va a manejar el frame de la camara, va a recibir el frame emitido de la clase DETECTION


    def start_detection(self):
        for idx, camera in enumerate(self.camerasDict.values()):
            if idx == 0:
                #CODIGO NUEVO DIA 3/7/2022#
                camera.changePixmap.connect(self.setImage)
                camera.miSignal.connect(self.show_popUp)
                camera.start()
                self.show()

            elif idx == 1:
                #print(f"el indice es {idx} y la camara es {camera}")
                camera.changePixmap.connect(self.setImage2)
                camera.miSignal.connect(self.show_popUp)
                camera.start() ##ACA EMPIEZA EL HILO DE WORKER.
                self.show()
            elif idx == 2:
                camera.changePixmap.connect(self.setImage3)
                camera.miSignal.connect(self.show_popUp)
                camera.start() ##ACA EMPIEZA EL HILO DE WORKER.
                self.show()
            else:
                camera.changePixmap.connect(self.setImage4)
                camera.miSignal.connect(self.show_popUp)
                camera.start() ##ACA EMPIEZA EL HILO DE WORKER.
                self.show()
                # CODIGO NUEVO DIA 3/7/2022#


    def show_popUp(self, cameraName, frame, x, y, w, h):

        if self.confirmarDeteccion(cameraName): #si es positivo
            file_name = f"Deteccion{self.username}-{self.detectionCounter}.jpg"
            file_txt = f"Detecciones/Deteccion{self.username}-{self.detectionCounter}.txt"
            cv2.imwrite(f"Detecciones/{file_name}", frame)
            self.detectionCounter += 1

            with open(file_txt, 'w') as f:
                f.write(str(x) + " " + str(y) + " " + str(w) + " " + str(h))
                f.close()

            print("GUARDADO")
        else:
            print("Imagen no guardada.")



    #Funcion que lanza el popUp para seleccionar que tipo de evento es.
    def confirmarDeteccion(self, cameraName):
        text = "Hubo una deteccion de arma ¿Es correcta?:"
        title = f"Camera {cameraName}"
        option_list = []
        # Option 1
        button1 = "Si"
        # Option 2
        button2 = "No"
        # appending button to the button list
        option_list.append(button1)
        option_list.append(button2)
        output = buttonbox(text, title, option_list)
        if output == "Si":
           return True
        else:
           return False


    def closeEvent(self, event):
        for camera in self.camerasDict.values():
            camera.running = False
            event.accept()

    def updateContadoresDB(self):
        data = self.collection.find_one({"User.username": self.username})
        latestDetection = data['User']['lastDetection']
        self.detectionCounter = latestDetection

        # self.tiroteoCounter = detections['lastTiroteo']
        # self.asaltoCounter = detections['lastAsalto']
        # self.secuestroCounter = detections['lastSecuestro']

