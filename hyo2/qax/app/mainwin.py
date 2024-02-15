from ausseabed.qajson.model import QajsonRoot
from ausseabed.qajson.utils import minimal_qajson
from hyo2.qax.app.widgets.exception_dialog import ExceptionDialog
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QAction, QApplication
from pathlib import Path
from typing import Optional, NoReturn, List
import logging
import os
import sys
import traceback

from hyo2.qax.app import qta
from hyo2.qax.app.widgets.qax.manual import ManualWindow
from hyo2.qax.lib import lib_info
from hyo2.qax.app import app_info
from hyo2.qax.app.widgets.qax.widget import QAXWidget
from hyo2.qax.app.widgets.qax.settings_dialog import SettingsDialog
from hyo2.qax.app.gui_settings import GuiSettings
from hyo2.qax.app.grid_transformer_dialog import GridTransformerDialog

logger = logging.getLogger(__name__)


class MainWin(QtWidgets.QMainWindow):

    here = os.path.abspath(os.path.dirname(__file__))
    media = os.path.join(here, "media")

    exception_signal = QtCore.Signal(list)

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)

        # set the application name
        self.name = app_info.app_name
        self.version = app_info.app_version
        self.setWindowTitle('{} {}'.format(self.name, self.version))
        self.setMinimumSize(QtCore.QSize(500, 800))
        self.resize(QtCore.QSize(920, 1240))

        self.exception_signal.connect(self.show_exception_dialog)

        # noinspection PyArgumentList
        _app = QtCore.QCoreApplication.instance()
        _app.setApplicationName('%s' % self.name)
        _app.setOrganizationName("HydrOffice")
        _app.setOrganizationDomain("hydroffice.org")

        # set icons
        icon_info = QtCore.QFileInfo(app_info.app_icon_path)
        self.setWindowIcon(QtGui.QIcon(icon_info.absoluteFilePath()))

        self.qax_widget = QAXWidget(main_win=self)
        self.qax_widget.setDocumentMode(True)
        self.qax_widget.status_message.connect(self.update_status_bar)

        self._add_menu_bar()

        self.status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage('...')

        self.setCentralWidget(self.qax_widget)

    def update_status_bar(self, message: str, timeout=0):
        self.status_bar.showMessage(message, timeout=timeout)

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

        export_qajson_excel_icon = qta.icon('fa5s.file-export')
        export_qajson_excel_action = QAction(export_qajson_excel_icon, "Export to Excel...", self)
        export_qajson_excel_action.setShortcuts(QKeySequence.SaveAs)
        export_qajson_excel_action.setStatusTip("Export QAJSON as Excel file")
        export_qajson_excel_action.triggered.connect(self.export_qajson_excel)
        fileMenu.addAction(export_qajson_excel_action)

        open_action = QAction('&Open...', self)
        open_action.setShortcuts(QKeySequence.Open)
        open_action.setStatusTip("Open QAJSON")
        open_action.triggered.connect(self.open_qajson)
        fileMenu.addAction(open_action)

        fileMenu.addSeparator()

        settings_icon = qta.icon('fa5s.cog')
        settings_action = QAction(settings_icon, "Settings...", self)
        settings_action.setStatusTip("View/Edit QAX settings")
        settings_action.triggered.connect(self.open_settings)
        fileMenu.addAction(settings_action)

        fileMenu.addSeparator()

        quit_icon = qta.icon('fa.close')
        quit_action = QAction(quit_icon, "&Quit", self)
        quit_action.setShortcuts(QKeySequence.Quit)
        quit_action.setStatusTip("Quit QAX")
        quit_action.triggered.connect(self.quitAction)
        fileMenu.addAction(quit_action)

        utilities_menu = self.menuBar.addMenu('&Utilities')
        gridtransformer_icon = qta.icon('fa.th')
        gridtransformer_action = QAction(
            gridtransformer_icon, "&Grid Transformer", self)
        gridtransformer_action.setStatusTip(
            "Convert grid files to check input specification")
        gridtransformer_action.triggered.connect(self.open_gridtransformer)
        utilities_menu.addAction(gridtransformer_action)

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

    def exception_hook(
            self,
            ex_type: type,
            ex_value: BaseException, tb: traceback) -> None:
        sys.__excepthook__(ex_type, ex_value, tb)

        # first manage case of not being an exception (e.g., keyboard
        # interrupts)
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

        dlg = ExceptionDialog(ex_type, ex_value, tb)
        ret = dlg.exec_()
        if ret == QtWidgets.QDialog.Rejected:
            self.close()
        else:
            logger.warning("ignored exception")

    def do_you_really_want(self, title="Quit", text="quit"):
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setIconPixmap(
            QtGui.QPixmap(
                app_info.app_icon_path).scaled(
                QtCore.QSize(
                    60, 60)))
        msg = (
            f"Do you really want to {text}?"
            "<br><br>"
            f"If you would like to provide feedback on {self.name}, please open the following "
            f"link <a href='{app_info.app_support_link}'>{self.name}</a>."
        )
        msg_box.setText(msg)
        msg_box.setStandardButtons(
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msg_box.setDefaultButton(QtWidgets.QMessageBox.No)
        return msg_box.exec_()

    def update_ui(self, qajson: QajsonRoot) -> NoReturn:
        self.qax_widget.update_ui(qajson)

    def new_qajson(self):
        self.qax_widget.prj.qa_json_path = None
        self.qax_widget.prj.qa_json = minimal_qajson()
        self.update_ui(self.qax_widget.prj.qa_json)

    def _save_qajson(self):
        self.qax_widget.prj.save_qa_json()
        base_name = os.path.basename(self.qax_widget.prj.qa_json_path)
        self.update_status_bar("Saved {}".format(base_name), 1500)

    def _export_qajson_excel(self, output: Path):
        success = self.qax_widget.prj.export_qajson_excel(output_file=output)
        if success:
            self.update_status_bar("Saved {}".format(output.name), 1500)
        else:
            self.update_status_bar("Failed to export QAJSON to Excel", 1500)

    def save_qajson(self):
        if self.qax_widget.prj.qa_json_path is None:
            # we don't know what file was saved, or opened, so do "Save as..."
            self.saveas_qajson()
        else:
            self._save_qajson()

    def saveas_qajson(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptMode.AcceptSave)
        dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dialog.setNameFilter("QAJSON (*.json)")
        if dialog.exec_():
            file_names = dialog.selectedFiles()
            if len(file_names) == 0:
                return
            file_name = file_names[0]
            self.qax_widget.prj.qa_json_path = file_name
            self._save_qajson()

    def export_qajson_excel(self):
        # Save the QAJSON as an XLSX file (Excel)
        dialog = QtWidgets.QFileDialog(self)
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptMode.AcceptSave)
        dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dialog.setNameFilter("Microsoft Excel (*.xlsx)")
        if dialog.exec_():
            file_names = dialog.selectedFiles()
            if len(file_names) == 0:
                return
            file_name = file_names[0]
            self._export_qajson_excel(Path(file_name))

    def open_qajson(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptMode.AcceptOpen)
        dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dialog.setNameFilter("QAJSON (*.json)")
        if dialog.exec_():
            file_names = dialog.selectedFiles()
            if len(file_names) == 0:
                return
            file_name = file_names[0]
            self.qax_widget.prj.qa_json_path = file_name
            self.qax_widget.prj.open_qa_json()
            base_name = os.path.basename(self.qax_widget.prj.qa_json_path)
            self.update_ui(self.qax_widget.prj.qa_json)
            self.update_status_bar("Opened {}".format(base_name), 1500)

    def open_manual(self):
        ManualWindow.show_manual()

    def open_gridtransformer(self):
        gt_dialog = GridTransformerDialog()
        gt_dialog.show()
        gt_dialog.exec_()

    def open_settings(self):
        settings_dialog = SettingsDialog()
        settings_dialog.show()
        settings_dialog.exec_()

    def quitAction(self):
        reply = self.do_you_really_want("Quit", f"quit {self.name}")
        if reply == QtWidgets.QMessageBox.Yes:
            # store window size
            self._persist_exit_settings()
            QApplication.instance().quit()

    def closeEvent(self, event):
        """ actions to be done before close the app """
        reply = self.do_you_really_want("Quit", f"quit {self.name}")

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
        self.qax_widget.persist_exit_settings()

    def do(self):
        logger.warning("DEV MODE")
        from ausseabed.qajson.parser import QajsonParser
        print(QajsonParser.example_paths()[-1])
        from pathlib import Path
        qajsonparser = QajsonParser(Path(QajsonParser.example_paths()[-1]))
        self.qax_widget.tab_run.prj.qa_json = qajsonparser.root
