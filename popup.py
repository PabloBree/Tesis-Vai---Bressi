import sys
from PyQt5.QtWidgets import QApplication, QListWidget, QListWidgetItem, QLabel, QDialog


class AppDemo(QListWidget):
    def __init__(self):
        super().__init__()
        self.resize(1200, 800)
        self.setStyleSheet('font-size: 40px')

        companies = ['Microsoft', 'Facebook', 'Google', 'Apple']

        for company in companies:
            self.addItem(company)

        self.itemDoubleClicked.connect(self.launchPopup)

    def launchPopup(self, item):
        pop = Popup(item.text(), self)
        pop.show()


class Popup(QDialog):
    def __init__(self, name, parent):
        super().__init__(parent)
        self.resize(600, 300)
        self.label = QLabel(name, self)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    demo = AppDemo()
    demo.show()

    sys.exit(app.exec_())