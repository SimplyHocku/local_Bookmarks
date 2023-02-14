import sys

from PyQt5 import QtWidgets
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QRect, QPropertyAnimation
from PyQt5.QtGui import QIcon, QTransform, QPixmap


class Button(QtWidgets.QListWidget):
    def __init__(self):
        super().__init__()
        self.animation_up = QPropertyAnimation(self, b'geometry')
        self.animation_down = QPropertyAnimation(self, b'geometry')
        size = QRect(100,5,300,1)
        self.setGeometry(size)
        self.resize(300,1)
        # self.setMaximumSize(300,300)

    def enterEvent(self, event):
        super(Button, self).enterEvent(event)
        print("enter")
        print(self.size())
        # self.resize(200,200)
        self.animation_down.setDuration(900)
        # QRect()
        self.animation_down.setStartValue(QRect(1, 5, 300, 1))
        self.animation_down.setEndValue(QRect(1, 5, 300, 300))
        # self.animation.start()
        # if self.height() == self.height():
        #     self.animation_up.start()
        self.setStyleSheet("background-color: black;")

        # self.move(randint(0, 500), randint(0, 400))
    #
    # def leaveEvent(self, a0: QtCore.QEvent) -> None:
    #     # print(self.size())
    #     print("leave")
    #     # self.resize(10, 10)
    #     self.animation_up.setDuration(900)
    #
    #     self.animation_up.setStartValue(QRect(1, 5, 300, 300))
    #     self.animation_up.setEndValue(QRect(1, 5, 300, 1))
    #     if self.height() == 300:
    #         self.animation_up.start()

class Test(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # main = QtWidgets.QWidget()
        # btn.enterEvent()
        # btn.clicked.connect(self.test)
        # btm.sh
        # self.cat = QtWidgets.QListWidget()
        # self.cat.resize(10, 10)
        btn = Button()
        # btn.resize(30, 1)
        # print(btn.size())
        #
        # effect = QtWidgets.QGraphicsOpacityEffect(btn)
        # btn.setGraphicsEffect(effect)
        vbox = QtWidgets.QVBoxLayout()
        lbel = QtWidgets.QLabel("test")
        vbox.addWidget(lbel)
        vbox.addWidget(btn)
        # self.setFixedSize(1900,1000)
        # vbox.addWidget(self.cat)

        # pixmap = QPixmap()
        # transform_for_label = QTransform()
        # transform_for_label.rotate(0.5)
        # self.label_show_list = MyLabel()
        # self.label_show_list.show()
        # self.label_show_list.
        # self.label_show_list.setPixmap(pixmap.transformed(transform_for_label))

        # vbox.addWidget(self.label_show_list)
        self.setLayout(vbox)

        # self.animation = QtCore.QPropertyAnimation(effect, b"opacity")
        # self.animation.setDuration(10000)
        # self.animation.setStartValue(1)
        # self.animation.setEndValue(0)
        # self.animation.start()

    def test(self):
        self.animation.start()


app = QtWidgets.QApplication(sys.argv)
main = Test()
# main.
main.showMaximized()
sys.exit(app.exec_())
