import json
import logging
import os
from typing import List, NoReturn
from pathlib import Path
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QSizePolicy
from hyo2.abc.lib.helper import Helper

from hyo2.qax.app.gui_settings import GuiSettings
from hyo2.qax.app.widgets.qax.check_widget import CheckWidget
from hyo2.qax.lib.plugin import QaxCheckToolPlugin
from hyo2.qax.lib.check_executor import CheckExecutor
from hyo2.qax.lib.qa_json import QaJsonRoot

logger = logging.getLogger(__name__)


class QtCheckExecutor(QtCore.QThread, CheckExecutor):
    """ Implementation of the CheckExecutor using QThread to run the checks in
    a background thread. This allows the UI to remain responsive, and accept
    other user events (eg; stop button). Signals and slots are used to
    communicate status to the UI main thread.
    """

    progress = QtCore.Signal(float)
    check_tool_started = QtCore.Signal(object)
    checks_complete = QtCore.Signal()
    status_changed = QtCore.Signal(str)

    def __init__(
            self,
            qa_json: QaJsonRoot,
            check_tools: List[QaxCheckToolPlugin]):
        super(QtCheckExecutor, self).__init__()
        CheckExecutor.__init__(self, qa_json, check_tools)

    def run(self):
        # seems ugly, but is required
        # expect this is related to the fact both the QThread and CheckExecutor
        # classes implement a `runs` function.
        CheckExecutor.run(self)

    def _progress_callback(self, check_tool, progress):
        self.progress.emit(progress)

    def _check_tool_started(self, check_tool, check_number, total_check_count):
        tpl = (check_tool.name, check_number, total_check_count)
        self.check_tool_started.emit(tpl)

    def _checks_complete(self):
        self.checks_complete.emit()

    def _set_status(self, status: str):
        self.status = status
        self.status_changed.emit(status)


class RunTab(QtWidgets.QMainWindow):

    run_checks = QtCore.Signal()

    def __init__(self):
        super(RunTab, self).__init__()

        self.check_executor = None

        self.panel = QtWidgets.QFrame()
        self.setCentralWidget(self.panel)
        self.vbox = QtWidgets.QVBoxLayout()
        self.panel.setLayout(self.vbox)

        # title
        label_name = QtWidgets.QLabel("Run checks")
        label_name.setStyleSheet(GuiSettings.stylesheet_plugin_tab_titles())
        self.vbox.addWidget(label_name)

        # Run and stop buttons
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch()
        self.run_button = QtWidgets.QPushButton()
        self.run_button.setText("Run")
        self.run_button.setFixedWidth(100)
        self.run_button.setIcon(QtGui.QIcon(
            GuiSettings.icon_path("play.png")))
        self.run_button.clicked.connect(self.click_run)
        hbox.addWidget(self.run_button)

        self.stop_button = QtWidgets.QPushButton()
        self.stop_button.setText("Stop")
        self.stop_button.setFixedWidth(100)
        self.stop_button.clicked.connect(self.click_stop)
        hbox.addWidget(self.stop_button)

        hbox.addStretch()
        self.vbox.addLayout(hbox)

        # progress section
        self.progress_groupbox = QtWidgets.QGroupBox("Check execution status")
        self.progress_groupbox.setStyleSheet(
            "QGroupBox::title { color: rgb(155, 155, 155); }")
        vbox = QtWidgets.QVBoxLayout()
        self.progress_groupbox.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        check_name_label = QtWidgets.QLabel("Check:")
        check_name_label.setFixedWidth(80)
        hbox.addWidget(check_name_label)
        self.check_name_text_label = QtWidgets.QLabel("n/a")
        hbox.addWidget(self.check_name_text_label)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        status_name_label = QtWidgets.QLabel("Status:")
        status_name_label.setFixedWidth(80)
        hbox.addWidget(status_name_label)
        self.status_name_text_label = QtWidgets.QLabel("Not started")
        hbox.addWidget(self.status_name_text_label)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        progress_label = QtWidgets.QLabel("Progress:")
        progress_label.setFixedWidth(80)
        hbox.addWidget(progress_label)
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setStyleSheet(
            "QProgressBar::chunk { background-color: lightgrey; }")
        hbox.addWidget(self.progress_bar)

        self.vbox.addWidget(self.progress_groupbox)

        self.vbox.addStretch()

        # final setup
        self.set_run_stop_buttons_enabled(False)

    def set_run_stop_buttons_enabled(self, is_running: bool) -> NoReturn:
        if is_running:
            self.run_button.setEnabled(False)
            self.stop_button.setEnabled(True)
        else:
            self.run_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def run_executor(self, check_executor: QtCheckExecutor):
        # we pass the check_executor into the run tab as this is where the UI
        # components are that will display the execution status.
        self.set_run_stop_buttons_enabled(True)

        self.check_executor = check_executor
        self.check_executor.check_tool_started.connect(
            self._on_check_tool_started)
        self.check_executor.progress.connect(self._on_progress)
        self.check_executor.checks_complete.connect(self._on_checks_complete)
        self.check_executor.status_changed.connect(self._on_status_change)
        self.check_executor.start()

    def click_run(self):
        self.run_checks.emit()

    def click_stop(self):
        if self.check_executor is None:
            logger.warn("Check executor does not exist, cannot stop")
            return
        self.check_executor.stop()

    @QtCore.Slot(float)
    def _on_progress(self, progress):
        self.progress_bar.setValue(int(progress * 100))

    @QtCore.Slot(object)
    def _on_check_tool_started(self, tpl):
        check_tool_name, check_number, total_check_count = tpl
        self.check_name_text_label.setText("{} ({}/{})".format(
            check_tool_name, check_number, total_check_count))

    @QtCore.Slot()
    def _on_checks_complete(self):
        self.set_run_stop_buttons_enabled(False)

    @QtCore.Slot(str)
    def _on_status_change(self, status):
        self.status_name_text_label.setText(status)
