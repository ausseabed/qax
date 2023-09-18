from PySide2.QtWidgets import QApplication, QDialog, QLineEdit, \
    QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QWidget, \
    QSizePolicy, QComboBox, QFileDialog, QPlainTextEdit, QProgressBar, \
    QFrame
from PySide2.QtGui import QFont
from PySide2 import QtCore

from hyo2.qax.app import qta
from hyo2.qax.app.gui_settings import GuiSettings


class SettingsDialog(QDialog):

    def __init__(self, parent=None):
        super(
            SettingsDialog,
            self).__init__(
            parent,
            QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitle("Settings")

        self.setWindowIcon(qta.icon('fa.cog'))

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # TODO: add other controls

        close_layout = QHBoxLayout()
        close_layout.addStretch()
        button_close = QPushButton("Close")
        button_close.clicked.connect(self.close_dialog)
        close_layout.addWidget(button_close)
        self.layout.addLayout(close_layout)

    def close_dialog(self):
        self.close()