from PySide2.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout
from PySide2.QtCore import QRect

""" utility widgets for including horizontal and vertical lines in components.
"""


class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFixedHeight(1)
        # self.setFrameShadow(QFrame.Sunken)

        self.setStyleSheet(
            "QFrame { background-color: rgb(210, 216, 219); }")
        # hbox = QHBoxLayout()
        #
        # self.setLayout(hbox)
        # hbox.addStretch()
        #
        # label_name = QLabel("foo")
        # vbox.addWidget(label_name)


class QVLine(QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)
