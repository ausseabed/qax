import logging
import os

from PySide2 import QtWidgets

from hyo2.abc.app.qt_progress import QtProgress

logger = logging.getLogger(__name__)


class AbstractWidget(QtWidgets.QMainWindow):

    abstract_here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # to be overloaded

    def __init__(self, main_win):
        QtWidgets.QMainWindow.__init__(self)

        self.main_win = main_win
        self.media = self.main_win.media

        self.setContentsMargins(0, 0, 0, 0)

        # add a frame
        self.frame = QtWidgets.QFrame()
        self.setCentralWidget(self.frame)

        # progress dialog
        self.progress = QtProgress(parent=self)

    def change_tabs(self, index):
        self.tabs.setCurrentIndex(index)
        self.tabs.currentWidget().setFocus()

    def change_info_url(self, url):
        self.main_win.change_info_url(url)
