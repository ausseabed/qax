import json
import logging
import os
from pathlib import Path
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QSizePolicy
from hyo2.abc.lib.helper import Helper

from hyo2.qax.app.gui_settings import GuiSettings
from hyo2.qax.app.widgets.qax.check_widget import CheckWidget
from hyo2.qax.lib.plugin import QaxCheckToolPlugin

logger = logging.getLogger(__name__)


class RunTab(QtWidgets.QMainWindow):

    def __init__(self):
        super(RunTab, self).__init__()

        # ui
        self.panel = QtWidgets.QFrame()
        self.setCentralWidget(self.panel)
        self.vbox = QtWidgets.QVBoxLayout()
        self.panel.setLayout(self.vbox)

        self.vbox.addWidget(QtWidgets.QLabel("Run stuff here"))
