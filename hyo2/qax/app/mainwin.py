import os
import ssl
import sys
import traceback
from urllib.request import urlopen
from urllib.error import URLError
import socket
import logging
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtGui import QIcon, QKeySequence
from PySide2.QtWidgets import QAction
import qtawesome as qta

from hyo2.abc.lib.helper import Helper
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

        self._add_menu_bar()

        self.setCentralWidget(self.qax_widget)

    def _add_menu_bar(self):
        self.menuBar = QtWidgets.QMenuBar(parent=self)
        self.setMenuBar(self.menuBar)

        fileMenu = self.menuBar.addMenu('&File')

        # New QA JSON
        new_icon = qta.icon('ei.file-new')
        new_action = QAction(new_icon, "&New", self)
        new_action.setShortcuts(QKeySequence.New)
        new_action.setStatusTip("Create a new QA JSON")
        new_action.triggered.connect(self.new_qajson)
        fileMenu.addAction(new_action)

        save_icon = qta.icon('fa.save')
        save_action = QAction(save_icon, "&Save", self)
        save_action.setShortcuts(QKeySequence.Save)
        save_action.setStatusTip("Save QAJSON")
        save_action.triggered.connect(self.save_qajson)
        fileMenu.addAction(save_action)

        saveas_icon = qta.icon('fa.save')
        saveas_action = QAction(saveas_icon, "Save &As...", self)
        saveas_action.setShortcuts(QKeySequence.SaveAs)
        saveas_action.setStatusTip("Save QAJSON as")
        saveas_action.triggered.connect(self.saveas_qajson)
        fileMenu.addAction(saveas_action)

        open_action = QAction('&Open...', self)
        open_action.setShortcuts(QKeySequence.Open)
        open_action.setStatusTip("Open QAJSON")
        open_action.triggered.connect(self.open_qajson)
        fileMenu.addAction(open_action)

        fileMenu.addSeparator()

        quit_icon = qta.icon('fa.close')
        quit_action = QAction(quit_icon, "&Quit", self)
        quit_action.setShortcuts(QKeySequence.Quit)
        quit_action.setStatusTip("Quit QAX")
        quit_action.triggered.connect(self.quitAction)
        fileMenu.addAction(quit_action)

        helpMenu = self.menuBar.addMenu('&Help')

        manual_icon = qta.icon('fa.info-circle')
        manual_action = QAction(manual_icon, "&Manual", self)
        manual_action.setStatusTip("Open the manual page")
        manual_action.triggered.connect(self.open_manual)
        helpMenu.addAction(manual_action)

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

    def new_qajson(self):
        print("NEW")
        pass

    def save_qajson(self):
        print("save")
        pass

    def saveas_qajson(self):
        print("saveas")
        pass

    def open_qajson(self):
        print("open")
        pass

    def open_manual(self):
        logger.debug("open manual")
        Helper.explore_folder(
            "https://www.hydroffice.org/"
            "manuals/qax/user_manual_qax_data_inputs.html")

    def quitAction(self):
        reply = self.do_you_really_want("Quit", "quit %s" % self.name)
        if reply == QtWidgets.QMessageBox.Yes:
            # store window size
            self._persist_exit_settings()
            QtWidgets.qApp.quit()

    def closeEvent(self, event):
        """ actions to be done before close the app """
        reply = self.do_you_really_want("Quit", "quit %s" % self.name)

        if reply == QtWidgets.QMessageBox.Yes:
            # store window size
            self._persist_exit_settings()
            event.accept()
            super().closeEvent(event)
        else:
            event.ignore()

    def _persist_exit_settings(self):
        self.settings.setValue("qax_app_width", self.size().width())
        self.settings.setValue("qax_app_height", self.size().height())

    def do(self):
        logger.warning("DEV MODE")
        from ausseabed.qajson.parser import QajsonParser
        print(QajsonParser.example_paths()[-1])
        from pathlib import Path
        qajsonparser = QajsonParser(Path(QajsonParser.example_paths()[-1]))
        self.qax_widget.tab_run.prj.qa_json = qajsonparser.root
