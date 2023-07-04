import json
import logging
import os
import time
from typing import List, NoReturn, Dict
from pathlib import Path
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QApplication, QDialog, QLineEdit, \
    QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QWidget, \
    QSizePolicy, QComboBox, QFileDialog, QPlainTextEdit, QProgressBar, \
    QFrame, QCheckBox
from PySide2.QtGui import QFont
import multiprocessing as mp

from hyo2.abc.lib.helper import Helper

from hyo2.qax.app import qta
from hyo2.qax.app.gui_settings import GuiSettings
from hyo2.qax.app.widgets.qax.check_widget import CheckWidget
from hyo2.qax.lib.plugin import QaxCheckToolPlugin
from hyo2.qax.lib.check_options import CheckOption
from hyo2.qax.lib.check_executor import CheckExecutor, MultiprocessCheckExecutor, \
    ProgressQueueItem, CheckToolStartedQueueItem, StatusQueueItem, \
    QajsonChangedQueueItem, ChecksCompleteQueueItem
from ausseabed.qajson.model import QajsonRoot
from hyo2.qax.lib.project import QAXProject

logger = logging.getLogger(__name__)


class QtCheckExecutorThread(QtCore.QThread):
    """ QThread implementation that starts, and then watched a check executor
    that is run in another thread via Python's multiprocessing module. Running
    the checks from this run method thread does allow the UI to update while
    the check run, however it is still restricted to running on a single process.
    Hence, multiprocessing was introduced to get around this issue.
    """

    progress = QtCore.Signal(float)
    qajson_updated = QtCore.Signal()
    check_tool_started = QtCore.Signal(object)
    checks_complete = QtCore.Signal()
    status_changed = QtCore.Signal(str)

    def __init__(
            self,
            qa_json: QajsonRoot,
            profile_name: str,
            check_tool_class_names: List[str]):
        super(QtCheckExecutorThread, self).__init__()

        self.queue = mp.Queue()
        self.mp_checkexecutor = MultiprocessCheckExecutor(
            qa_json,
            profile_name,
            check_tool_class_names,
            self.queue
        )
        self.mp_running = False
        # options such as what output to generate, where to put it. Keys come
        # from check_options.py
        self.options = {}

    def run(self):
        self.mp_checkexecutor.options = self.options

        self.mp_running = True
        self.mp_checkexecutor.start()

        while self.mp_running:
            queue_item = self.queue.get()
            if queue_item is not None:
                if isinstance(queue_item, ProgressQueueItem):
                    self.progress.emit(queue_item.progress)
                elif isinstance(queue_item, CheckToolStartedQueueItem):
                    tpl = (
                        queue_item.check_tool_class_name,
                        queue_item.check_number,
                        queue_item.total_check_count
                    )
                    self.check_tool_started.emit(tpl)
                elif isinstance(queue_item, StatusQueueItem):
                    self.status = queue_item.status
                    self.status_changed.emit(queue_item.status)
                elif isinstance(queue_item, QajsonChangedQueueItem):
                    self.qa_json = queue_item.qajson
                    self.qajson_updated.emit()
                elif isinstance(queue_item, ChecksCompleteQueueItem):
                    self.checks_complete.emit()

        self.mp_checkexecutor.join()

    def stop(self):
        self.mp_checkexecutor.stop()


class RunTab(QtWidgets.QWidget):

    run_checks = QtCore.Signal()

    def __init__(self, prj: QAXProject):
        super(RunTab, self).__init__()
        self.prj = prj
        self.check_executor = None

        self.vbox = QtWidgets.QVBoxLayout()
        self.setLayout(self.vbox)

        self._add_check_outputs()
        self._add_process()

        # final setup
        self.set_run_stop_buttons_enabled(False)

    def _add_check_outputs(self):
        co_groupbox = QGroupBox("Check outputs")
        co_groupbox.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed)
        co_layout = QVBoxLayout()
        co_layout.setSpacing(16)
        co_groupbox.setLayout(co_layout)

        self.qajson_spatial_checkbox = QCheckBox(
            "Include summary spatial output in QAJSON. "
            "Supports QAX visualisation.")
        self.qajson_spatial_checkbox.setCheckState(
            QtCore.Qt.CheckState.Checked)
        co_layout.addWidget(self.qajson_spatial_checkbox)

        export_layout = QVBoxLayout()
        export_layout.setSpacing(4)
        self.export_spatial_checkbox = QCheckBox(
            "Export detailed spatial outputs to file. "
            "Supports visualisation in other geospatial applications.")
        self.export_spatial_checkbox.stateChanged.connect(
            self._on_export_spatial_changed)
        export_layout.addWidget(self.export_spatial_checkbox)

        output_folder_layout = QHBoxLayout()
        output_folder_layout.setSpacing(4)
        output_folder_layout.addSpacerItem(QtWidgets.QSpacerItem(37, 20))
        self.output_folder_label = QLabel(
            "Detailed spatial output folder location:")
        output_folder_layout.addWidget(self.output_folder_label)
        self.output_folder_input = QLineEdit()
        self.output_folder_input.setText(
            GuiSettings.settings().value("spatial_outputs"))
        self.output_folder_input.setMinimumWidth(300)
        self.output_folder_input.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding)
        output_folder_layout.addWidget(self.output_folder_input)

        self.open_output_folder_button = QPushButton()
        output_folder_layout.addWidget(self.open_output_folder_button)
        self.open_output_folder_button.setIcon(qta.icon('fa.folder-open'))
        self.open_output_folder_button.setToolTip(
            f"Select file containing data")
        self.open_output_folder_button.clicked.connect(
            self._click_open_spatial_export_folder)
        export_layout.addLayout(output_folder_layout)

        co_layout.addLayout(export_layout)

        self._on_export_spatial_changed()
        self.vbox.addWidget(co_groupbox)

    def _click_open_spatial_export_folder(self):
        output_folder = QFileDialog.getExistingDirectory(
            self,
            f"Select folder for spatial outputs",
            GuiSettings.settings().value("spatial_outputs"),
            QFileDialog.ShowDirsOnly)

        if os.path.exists(output_folder):
            GuiSettings.settings().setValue(
                "spatial_outputs", output_folder)

        self.output_folder_input.setText(output_folder)

    def _on_export_spatial_changed(self):
        is_export = self.export_spatial_checkbox.isChecked()
        self.output_folder_label.setEnabled(is_export)
        self.output_folder_input.setEnabled(is_export)
        self.open_output_folder_button.setEnabled(is_export)

    def _add_process(self):
        process_groupbox = QGroupBox("Process")
        process_groupbox.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding)
        process_layout = QVBoxLayout()
        process_layout.setSpacing(0)
        process_groupbox.setLayout(process_layout)

        pbar_frame = QFrame()
        pbar_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        pbar_hbox = QHBoxLayout()
        pbar_hbox.setContentsMargins(QtCore.QMargins(0, 0, 0, 16))
        pbar_hbox.setSpacing(16)

        # Run and stop buttons
        hbox = QHBoxLayout()
        hbox.setSpacing(8)
        self.run_button = QPushButton()
        # is only enabled when validation passes
        self.run_button.setEnabled(False)
        self.run_button.setText("Run")
        self.run_button.setToolTip("Start check execution")
        self.run_button.setFixedWidth(100)
        run_icon = qta.icon('fa.play', color='green')
        self.run_button.setIcon(run_icon)
        self.run_button.clicked.connect(self._click_run)
        hbox.addWidget(self.run_button)

        self.stop_button = QPushButton()
        self.stop_button.setEnabled(False)
        self.stop_button.setText("Stop")
        self.stop_button.setToolTip("Stop check execution")
        self.stop_button.setFixedWidth(100)
        stop_icon = qta.icon('fa.stop', color='red')
        self.stop_button.setIcon(stop_icon)
        self.stop_button.clicked.connect(self._click_stop)
        hbox.addWidget(self.stop_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(QtCore.Qt.AlignCenter)
        self.progress_bar.setValue(0)
        self.progress_bar.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding)

        pbar_hbox.addLayout(hbox)
        pbar_hbox.addWidget(self.progress_bar)
        pbar_frame.setLayout(pbar_hbox)
        process_layout.addWidget(pbar_frame)

        vbox = QVBoxLayout()
        vbox.setSpacing(8)
        vbox.setContentsMargins(QtCore.QMargins(0, 0, 0, 16))
        process_layout.addLayout(vbox)
        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        check_name_label = QLabel("Check:")
        check_name_label.setFixedWidth(80)
        hbox.addWidget(check_name_label)
        self.check_name_text_label = QLabel("n/a")
        hbox.addWidget(self.check_name_text_label)

        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        status_name_label = QLabel("Status:")
        status_name_label.setFixedWidth(80)
        hbox.addWidget(status_name_label)
        self.status_name_text_label = QLabel("Not started")
        hbox.addWidget(self.status_name_text_label)

        self.warning_frame = QFrame()
        self.warning_frame.setVisible(False)
        self.warning_frame.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed)
        hbox = QHBoxLayout()

        warning_icon_widget = qta.IconWidget('fa.warning', color='red')
        warning_icon_widget.setIconSize(QtCore.QSize(48, 48))
        warning_icon_widget.update()
        hbox.addWidget(warning_icon_widget)
        warning_label = QLabel(
            "Grid Transformer did not complete successfully. Please refer to "
            "log output.")
        warning_label.setStyleSheet("QLabel { color: red; }")
        warning_label.setWordWrap(True)
        warning_label.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred)
        hbox.addWidget(warning_label)
        self.warning_frame.setLayout(hbox)
        process_layout.addWidget(self.warning_frame)

        self.success_frame = QFrame()
        self.success_frame.setVisible(False)
        self.success_frame.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed)
        hbox = QHBoxLayout()

        success_icon_widget = qta.IconWidget('fa.check', color='green')
        success_icon_widget.setIconSize(QtCore.QSize(48, 48))
        success_icon_widget.update()
        hbox.addWidget(success_icon_widget)
        success_label = QLabel("All checks completed successfully.")
        success_label.setStyleSheet("QLabel { color: green; }")
        success_label.setWordWrap(True)
        success_label.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred)
        hbox.addWidget(success_label)
        self.success_frame.setLayout(hbox)
        process_layout.addWidget(self.success_frame)

        log_layout = QVBoxLayout()
        log_layout.setSpacing(4)
        log_label = QLabel("Log messages")
        log_label.setStyleSheet("QLabel { color: grey; }")
        log_layout.addWidget(log_label)

        self.log_messages = QPlainTextEdit()
        doc: QtGui.QTextDocument = self.log_messages.document()
        font = doc.defaultFont()
        font.setFamily("Courier New")
        doc.setDefaultFont(font)

        self.log_messages.setReadOnly(True)
        self.log_messages.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding)
        log_layout.addWidget(self.log_messages)
        process_layout.addLayout(log_layout)

        self.vbox.addWidget(process_groupbox)

    def set_run_stop_buttons_enabled(self, is_running: bool) -> NoReturn:
        if is_running:
            self.run_button.setEnabled(False)
            self.stop_button.setEnabled(True)
        else:
            self.run_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def _log_message(self, message):
        self.log_messages.appendPlainText(message)

    def run_executor(self, check_executor: QtCheckExecutorThread):
        # we pass the check_executor into the run tab as this is where the UI
        # components are that will display the execution status.
        self.set_run_stop_buttons_enabled(True)

        self._log_message("Check execution started")
        self.start_time = time.perf_counter()

        self.check_executor = check_executor
        self.check_executor.options = self.get_options()
        self.check_executor.check_tool_started.connect(
            self._on_check_tool_started)
        self.check_executor.progress.connect(self._on_progress)
        self.check_executor.qajson_updated.connect(self._on_qajson_update)
        self.check_executor.checks_complete.connect(self._on_checks_complete)
        self.check_executor.status_changed.connect(self._on_status_change)
        self.check_executor.start()

    def get_options(self) -> Dict:
        ''' Gets a list of options based on user entered data. eg; the spatial
        output specifications.
        '''
        return {
            CheckOption.spatial_output_qajson: self.qajson_spatial_checkbox.isChecked(),
            CheckOption.spatial_output_export: self.export_spatial_checkbox.isChecked(),
            CheckOption.spatial_output_export_location: self.output_folder_input.text()
        }

    def _click_run(self):
        self.run_checks.emit()

    def _click_stop(self):
        if self.check_executor is None:
            logger.warn("Check executor does not exist, cannot stop")
            return
        self._log_message("Stopping check execution")
        self.check_executor.stop()

    @QtCore.Slot(float)
    def _on_progress(self, progress):
        self.progress_bar.setValue(int(progress * 100))

    @QtCore.Slot()
    def _on_qajson_update(self):
        self.prj.qa_json = self.check_executor.qa_json

    @QtCore.Slot(object)
    def _on_check_tool_started(self, tpl):
        check_tool_name, check_number, total_check_count = tpl
        self.check_name_text_label.setText("{} ({}/{})".format(
            check_tool_name, check_number, total_check_count))

    @QtCore.Slot()
    def _on_checks_complete(self):
        run_time = time.perf_counter() - self.start_time
        self._log_message(
            f"Execution time for all checks = {run_time:.2f} sec")
        self._log_message("\n\n")

        self.set_run_stop_buttons_enabled(False)
        self.prj.qa_json = self.check_executor.qa_json

    @QtCore.Slot(str)
    def _on_status_change(self, status):
        self.status_name_text_label.setText(status)
