import sys

from PyQt5 import QtWidgets
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QIcon, QTransform, QPixmap


class Button(QtWidgets.QPushButton):
    def __init__(self, *args, **kwargs):
        super(Button, self).__init__(*args, **kwargs)

    def enterEvent(self, event):
        super(Button, self).enterEvent(event)
        print("R")

        # self.move(randint(0, 500), randint(0, 400))

class Test(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # main = QtWidgets.QWidget()
        btn = Button("Ту")
        # btn.enterEvent()
        # btn.clicked.connect(self.test)
        # btm.sh
        effect = QtWidgets.QGraphicsOpacityEffect(btn)
        btn.setGraphicsEffect(effect)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(btn)

        # pixmap = QPixmap()
        # transform_for_label = QTransform()
        # transform_for_label.rotate(0.5)
        # self.label_show_list = MyLabel()
        # self.label_show_list.show()
        # self.label_show_list.
        # self.label_show_list.setPixmap(pixmap.transformed(transform_for_label))

        # vbox.addWidget(self.label_show_list)
        self.setLayout(vbox)

        self.animation = QtCore.QPropertyAnimation(effect, b"opacity")
        self.animation.setDuration(10000)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        # self.animation.start()

    def test(self):
        self.animation.start()


app = QtWidgets.QApplication(sys.argv)
main = Test()
main.setFixedSize(500, 500)
main.show()
sys.exit(app.exec_())
