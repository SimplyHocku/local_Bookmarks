import sys

import PyQt5
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QRect


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.animation_down = QtCore.QPropertyAnimation(self, b'geometry')
        self.animation_up = QtCore.QPropertyAnimation(self, b'geometry')
        self.setStyleSheet("background-color: black;")

    def enterEvent(self, event):
        print("y")
        super(MyWidget, self).enterEvent(event)
        self.animation_down.setDuration(900)
        self.animation_down.setStartValue(QRect(1, 5, 300, 1))
        self.animation_down.setEndValue(QRect(1, 5, 300, 300))
        self.animation_down.start()

    # def leaveEvent(self, a0: QtCore.QEvent) -> None:
    #     print("leave")
    #     self.animation_up.setDuration(900)
    #
    #     self.animation_up.setStartValue(QRect(1, 5, 300, 300))
    #     self.animation_up.setEndValue(QRect(1, 5, 300, 1))
    #     self

class Test(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.central = QtWidgets.QWidget()
        self.setCentralWidget(self.central)
        self.hbox = QtWidgets.QHBoxLayout()
        self.btn = QtWidgets.QPushButton("tesdt")
        self.btn.clicked.connect(self.test)

        self.qline = QtWidgets.QListWidget()
        self.qline.setMinimumSize(100, 50)
        self.qline.setMaximumSize(150, 100)
        self.web = QWebEngineView()
        self.web.setMinimumSize(840, 530)
        self.web.setMaximumHeight(400)

        self.hbox.addWidget(self.qline, alignment=QtCore.Qt.AlignTop)
        self.hbox.addWidget(self.web)
        self.hbox.setGeometry(QtCore.QRect(10, 10, 250, 250))

        self.test_wif = MyWidget()
        self.test_wif.setStyleSheet("background-color: black;")
        # self.test_wif.setGeometry(QtCore.QRect(100, 100, 10, 10))
        # self.test_wif.setMaximumSize(20, 20)
        self.hbox.addWidget(self.test_wif)
        self.hbox.addWidget(self.btn)

        self.central.setLayout(self.hbox)

        # QtWidgets.Are

    def test(self):
        self.test_wif.setGeometry(QtCore.QRect(100, 100, 500, 500))


app = QtWidgets.QApplication(sys.argv)
main = Test()
# main.
main.show()
sys.exit(app.exec_())
