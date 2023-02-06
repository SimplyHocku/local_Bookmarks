import sys

from PyQt5 import QtWidgets
from PyQt5 import QtCore


class Test(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # main = QtWidgets.QWidget()
        btn = QtWidgets.QPushButton("Ту")
        btn.clicked.connect(self.test)
        # btm.sh
        effect = QtWidgets.QGraphicsOpacityEffect(btn)
        btn.setGraphicsEffect(effect)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(btn)
        self.setLayout(vbox)

        self.animation = QtCore.QPropertyAnimation(effect, b"opacity")
        self.animation.setDuration(10000)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.start()

    def test(self):
        self.animation.start()


app = QtWidgets.QApplication(sys.argv)
main = Test()
main.setFixedSize(500,500)
main.show()
sys.exit(app.exec_())
