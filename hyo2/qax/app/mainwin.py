import os
import ssl
import sys
import traceback
from urllib.request import urlopen
from urllib.error import URLError
import socket
import logging
from PySide2 import QtCore, QtGui, QtWidgets

from hyo2.abc.app.dialogs.exception.exception_dialog import ExceptionDialog
from hyo2.abc.app.tabs.info.info_tab import InfoTab
from hyo2.abc.lib.helper import Helper
from hyo2.qax.lib import lib_info
from hyo2.qax.app import app_info
from hyo2.qax.app.widgets.qax.widget import QAXWidget
from hyo2.qax.app.gui_settings import GuiSettings

logger = logging.getLogger(__name__)


class MainWin(QtWidgets.QMainWindow):

    here = os.path.abspath(os.path.dirname(__file__))
    media = os.path.join(here, "media")

    exception_signal = QtCore.Signal(list)

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)

        logger.info("current configuration:\n%s" % Helper(lib_info=lib_info).package_info())

        # set the application name
        self.name = app_info.app_name
        self.version = app_info.app_version
        self.setWindowTitle('{} {}'.format(self.name, self.version))
        self.setMinimumSize(QtCore.QSize(500, 800))
        self.resize(QtCore.QSize(920, 840))

        self.exception_signal.connect(self.show_exception_dialog)

        # noinspection PyArgumentList
        _app = QtCore.QCoreApplication.instance()
        _app.setApplicationName('%s' % self.name)
        _app.setOrganizationName("HydrOffice")
        _app.setOrganizationDomain("hydroffice.org")

        # set icons
        icon_info = QtCore.QFileInfo(app_info.app_icon_path)
        self.setWindowIcon(QtGui.QIcon(icon_info.absoluteFilePath()))
        if Helper.is_windows():

            try:
                # This is needed to display the app icon on the taskbar on Windows 7
                import ctypes
                app_id = '%s v.%s' % (self.name, self.version)
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

            except AttributeError as e:
                logger.debug("Unable to change app icon: %s" % e)

        self.qax_widget = QAXWidget(main_win=self)
        self.qax_widget.setDocumentMode(True)

        self.setCentralWidget(self.qax_widget)

    def initialize(self):
        self.qax_widget.initialize()

        self.settings = GuiSettings.settings()
        self.resize(QtCore.QSize(
            int(self.settings.value("qax_app_width", defaultValue=920)),
            int(self.settings.value("qax_app_height", defaultValue=840)),
        ))

    def exception_hook(self, ex_type: type, ex_value: BaseException, tb: traceback) -> None:
        sys.__excepthook__(ex_type, ex_value, tb)

        # first manage case of not being an exception (e.g., keyboard interrupts)
        if not issubclass(ex_type, Exception):
            msg = str(ex_value)
            if not msg:
                msg = ex_value.__class__.__name__
            logger.info(msg)
            self.close()
            return

        # Exceptions may be raised from background threads. So use signals
        # and slots to pass the information that will be presented in the
        # GUI dialog. It is not possible (causes seg fault) to show a dialog
        # from a background thread (definately the case on macOS)
        self.exception_signal.emit(
            [app_info, lib_info, ex_type, ex_value, tb]
        )

    @QtCore.Slot(list)
    def show_exception_dialog(self, params):
        _app_info, _lib_info, ex_type, ex_value, tb = params

        dlg = ExceptionDialog(
            app_info=_app_info,
            lib_info=_lib_info,
            ex_type=ex_type,
            ex_value=ex_value,
            tb=tb
        )
        ret = dlg.exec_()
        if ret == QtWidgets.QDialog.Rejected:
            if not dlg.user_triggered:
                self.close()
        else:
            logger.warning("ignored exception")

    # Quitting #

    def do_you_really_want(self, title="Quit", text="quit"):
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setIconPixmap(QtGui.QPixmap(app_info.app_icon_path).scaled(QtCore.QSize(60, 60)))
        msg_box.setText('Do you really want to %s?' % text)
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msg_box.setDefaultButton(QtWidgets.QMessageBox.No)
        return msg_box.exec_()

    def closeEvent(self, event):
        """ actions to be done before close the app """
        reply = self.do_you_really_want("Quit", "quit %s" % self.name)

        if reply == QtWidgets.QMessageBox.Yes:
            # store window size
            self.settings.setValue("qax_app_width", self.size().width())
            self.settings.setValue("qax_app_height", self.size().height())
            event.accept()
            super().closeEvent(event)
        else:
            event.ignore()

    def do(self):
        logger.warning("DEV MODE")
        from ausseabed.qajson.parser import QajsonParser
        print(QajsonParser.example_paths()[-1])
        from pathlib import Path
        qajsonparser = QajsonParser(Path(QajsonParser.example_paths()[-1]))
        self.qax_widget.tab_run.prj.qa_json = qajsonparser.root
        # self.qax_widget.tab_inputs._add_json(QajsonParser.example_paths()[-1])
        # self.qax_widget.tab_qc_tools.display_json()
