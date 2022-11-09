from PyQt5.QtCore import QThread, Qt, pyqtSignal, QObject
from PyQt5.QtGui import QImage
import cv2
import numpy as np
import time
import win32api
from easygui import *
import urllib.request



# url = 'http://186.127.194.202:8080/shot.jpg'


class Detection(QThread):
    def __init__(self, cameraInfo, totalCamaras, parent=None):  ##original es __init
        super(Detection, self).__init__()
        self.myCamera = cameraInfo

        self.LocalCamara = totalCamaras

    changePixmap = pyqtSignal(QImage)
    miSignal = pyqtSignal(str, np.ndarray, int, int, int, int)



    def run(self):
        counter = 0

        # Loads Yolov4
        net = cv2.dnn.readNet("weights/yolov4-obj_1000.weights", "cfg/yolov4.cfg")
        classes = []

        # Loads object names
        with open("obj.names", "r") as f:
            classes = [line.strip() for line in f.readlines()]

        layer_names = net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
        colors = np.random.uniform(0, 255, size=(len(classes), 3))

        font = cv2.FONT_HERSHEY_PLAIN
        starting_time = time.time() - 11

        self.running = True


        if not self.myCamera["URL"]:
                cap = cv2.VideoCapture(self.LocalCamara, cv2.CAP_DSHOW)


        while self.running:
            if not self.myCamera["URL"]: #Esto devuelve True o False, de ser True es local.. Sino es False porque lee el string de la URL
                ret, frame = cap.read()  ##WEBCAM
            else:
                ##Webcam iPhone
                vcap = cv2.VideoCapture(self.myCamera["URL"])
                ret, frame = vcap.read()
                stream = cv2.VideoCapture(self.myCamera["URL"])
                ret, frame = stream.read()
                ##Webcam Android
                #imgResp = urllib.request.urlopen(self.myCamera["URL"])  ##ONLINE
                #imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)  ##ONLINE
                #frame = cv2.imdecode(imgNp, -1)  ##ONLINE
                ###
            # if ret: ##WEBCAM
            if True:  ##ONLINE
                height, width, channels = frame.shape
                blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

                # PARA LA GPU#####
                net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
                net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
                #
                net.setInput(blob)

                outs = net.forward(output_layers)

                class_ids = []
                confidences = []
                boxes = []
                for out in outs:
                    for detection in out:
                        scores = detection[5:]
                        class_id = np.argmax(scores)
                        confidence = scores[class_id]

                        if confidence > 0.6:  # ACA PODEMOS ELEGIR EL TIPO DE PRECISION
                            center_x = int(detection[0] * width)
                            center_y = int(detection[1] * height)
                            w = int(detection[2] * width)
                            h = int(detection[3] * height)

                            x = int(center_x - w / 2)
                            y = int(center_y - h / 2)

                            boxes.append([x, y, w, h])
                            confidences.append(float(confidence))
                            class_ids.append(class_id)

                indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.8, 0.3)

                for i in range(len(boxes)):
                    if i in indexes:
                        x, y, w, h = boxes[i]
                        label = str(classes[class_ids[i]])
                        confidence = confidences[i]
                        color = (256, 0, 0)
                        redColor = (0,0,255)
                        copyPhoto = frame.copy() ##guardamos una copia limpia de la imagen del arma para guardar
                        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                        cv2.putText(frame, label + "{0:.1%}".format(confidence), (x, y - 20), font, 3, color, 3)
                        cv2.rectangle(frame, (0,0), (width, height), redColor, 20)
                        cv2.putText(frame, "ALERTA!", (20, height - 440), font, 2, redColor, 3)
                        elapsed_time = starting_time - time.time()
                        ##Prueba de variables x,y,w,h linea 105
                        if elapsed_time <= -10:  # aca guardamos el clip.
                            starting_time = time.time()
                            ###THREADS####
                            # x = threading.Thread(target=self.save_detection(), args=(self,))
                            # x.start()
                            self.save_detection(copyPhoto, x, y, w, h)
                            #
                            counter = counter + 1


                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                bytesPerLine = channels * width
                convertToQtFormat = QImage(rgbImage.data, width, height, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(550, 340, Qt.KeepAspectRatio)  ##ORIGINAL: 854x480
                cv2.waitKey(1)
                self.changePixmap.emit(p)

        if self.running == False:
            cv2.destroyAllWindows()

    def save_detection(self, copyPhoto, x, y, w, h):
        self.miSignal.emit(self.myCamera["nombre"], copyPhoto, x, y, w, h)
