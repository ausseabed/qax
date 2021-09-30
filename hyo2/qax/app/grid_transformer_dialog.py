from PySide2.QtWidgets import QApplication, QDialog, QLineEdit, \
    QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QWidget, \
    QSizePolicy, QComboBox, QFileDialog, QPlainTextEdit, QProgressBar, \
    QFrame
from PySide2.QtGui import QFont
from PySide2 import QtCore
import os
import time
import multiprocessing as mp

from ausseabed.mbesgc.lib.grid_transformer import GridTransformer

from hyo2.qax.app import qta
from hyo2.qax.app.gui_settings import GuiSettings
from hyo2.qax.lib.data import RasterFileInfo


class ProgressQueueItem:

    def __init__(self, progress: float):
        self.progress = progress


class MessageQueueItem:

    def __init__(self, message: str):
        self.message = message


class CompleteQueueItem:

    def __init__(self, successful: bool):
        self.successful = successful


class MultiprocessGridTransformerExecutor(mp.Process):
    ''' Implementation of multiprocessing Process class for the QAX CheckExecutor.
    Allows the checks to be processed in a background thread (to keep UI
    responsive). Communication with parent thread is handled by the Queue object
    passed into __init__
    '''

    def __init__(
            self,
            inputs: dict,
            queue: mp.Queue):
        super(MultiprocessGridTransformerExecutor, self).__init__()
        self.inputs = inputs
        self.queue = queue
        self.stop_event = mp.Event()

    def run(self):

        gt = GridTransformer()
        gt.process(
            self.inputs['Density'],
            self.inputs['Depth'],
            self.inputs['Uncertainty'],
            self.inputs['output'],
            self._progress_callback,
            self.is_stopped,
            self._complete_callback,
            self._message_callback
        )

    def stop(self):
        self.stop_event.set()

    def is_stopped(self) -> bool:
        return self.stop_event.is_set()

    def _progress_callback(self, progress):
        progress_item = ProgressQueueItem(progress)
        self.queue.put(progress_item)

    def _message_callback(self, message):
        message_item = MessageQueueItem(message)
        self.queue.put(message_item)

    def _complete_callback(self, successful: bool):
        complete_item = CompleteQueueItem(successful)
        self.queue.put(complete_item)


class QtGridTransformerThread(QtCore.QThread):

    progress = QtCore.Signal(float)
    message = QtCore.Signal(str)
    complete = QtCore.Signal(bool)

    def __init__(
            self,
            inputs: dict):
        super(QtGridTransformerThread, self).__init__()
        self.grid_transformer_inputs = inputs

    def run(self):
        self.queue = mp.Queue()
        self.mp_running = True

        self.gt_executor = MultiprocessGridTransformerExecutor(
            self.grid_transformer_inputs,
            self.queue,
        )

        self.gt_executor.start()

        while self.mp_running:
            queue_item = self.queue.get()
            if queue_item is not None:
                if isinstance(queue_item, ProgressQueueItem):
                    self.progress.emit(queue_item.progress)
                elif isinstance(queue_item, MessageQueueItem):
                    self.message.emit(queue_item.message)
                elif isinstance(queue_item, CompleteQueueItem):
                    self.complete.emit(queue_item.successful)

        self.gt_executor.join()

    def stop(self):
        self.gt_executor.stop()


input_band_names = [
    "Density",
    "Depth",
    "Uncertainty"
]

# names used in config file to remember locations user last opened file from
input_folder_settings = 'grid_transformer_input_folder'
output_folder_settings = 'grid_transformer_output_folder'


class GridTransformerInputBand(QWidget):
    ''' Widget for specification of filename and band '''

    log_message = QtCore.Signal(str)
    # tuple with band name, filename, band index
    band_selected = QtCore.Signal(object)

    def __init__(self, band_name: str, parent=None):
        QWidget.__init__(self, parent=parent)
        self.band_name = band_name
        self.filename = None
        self.file_info = None

        self.layout = QHBoxLayout()
        self.layout.setSpacing(16)
        self.layout.setMargin(8)
        self.setLayout(self.layout)

        label = QLabel(self.band_name)
        label.setMinimumWidth(125)
        self.layout.addWidget(label)

        input_file_layout = QHBoxLayout()
        input_file_layout.setSpacing(4)
        self.input_file_input = QLineEdit()
        # can only be set by file selection dialog
        self.input_file_input.setReadOnly(True)
        self.input_file_input.setMinimumWidth(300)
        self.input_file_input.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding)
        input_file_layout.addWidget(self.input_file_input)

        self.open_file_button = QPushButton()
        input_file_layout.addWidget(self.open_file_button)
        self.open_file_button.setIcon(qta.icon('fa.folder-open'))
        self.open_file_button.setToolTip(
            f"Select file containing {self.band_name} data")
        self.open_file_button.clicked.connect(self._click_open)
        self.layout.addLayout(input_file_layout)

        self.band_select = QComboBox()
        self.band_select.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding)
        self.band_select.setMinimumWidth(180)
        self.band_select.setMaximumWidth(240)
        self.band_select.setToolTip(
            f"Select band containing {self.band_name} data")
        self.band_select.currentIndexChanged.connect(self._band_selected)

        self.band_select.setDisabled(True)
        self.layout.addWidget(self.band_select)

    def _band_selected(self, index):
        tpl = (self.band_name, self.filename, self.selected_band_index)
        self.band_selected.emit(tpl)

    @property
    def selected_band_index(self) -> int:
        ''' Gets the band index that has been selected by the user. This is the
        index used by gdal, not the 0 based index of the combobox selection'''
        if self.file_info is None or len(self.file_info.bands) == 0:
            return None
        selected_band = self.file_info.bands[self.band_select.currentIndex()]
        return selected_band.index

    def _update_bands(self):
        self.band_select.clear()
        if self.file_info is None or len(self.file_info.bands) == 0:
            self.band_select.setDisabled(True)
            return

        self.band_select.setDisabled(False)

        for band in self.file_info.bands:
            self.band_select.addItem(band.display_name)

        # try to find a matching band. Obviously not needed if there is only one
        # band, but wont hurt.
        index = 0
        for i, band in enumerate(self.file_info.bands):
            if self.band_name.lower() in band.display_name.lower():
                index = i
        self.band_select.setCurrentIndex(index)

    def _set_filename(self, filename):
        self.filename = filename
        self.file_info = RasterFileInfo()
        self.file_info.open(self.filename)
        self.input_file_input.setText(self.filename)
        self._update_bands()

        self.log_message.emit(str(self.file_info) + "\n")

    def _click_open(self):
        filters = (
            "GeoTIFF (*.tif *.tiff);;"
            "Bathymetry Attributed Grid BAG (*.bag);;"
            "All files (*.*)"
        )
        selections, _ = QFileDialog.getOpenFileNames(
            self,
            f"Open {self.band_name} file",
            GuiSettings.settings().value(input_folder_settings),
            filters)
        if len(selections) == 0:
            return
        last_open_folder = os.path.dirname(selections[0])
        if os.path.exists(last_open_folder):
            GuiSettings.settings().setValue(
                input_folder_settings, last_open_folder)

        self._set_filename(selections[0])


class GridTransformerDialog(QDialog):

    def __init__(self, parent=None):
        super(
            GridTransformerDialog,
            self).__init__(
            parent,
            QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitle("Grid Transformer")

        self.setWindowIcon(qta.icon('fa.th'))

        # dict to store inputs that will get passed to the grid transformer
        # this gets validated to ensure all the bits of info are in it before
        # the run button gets enabled
        self.grid_transformer_inputs = {}

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self._add_inputs()
        self._add_output()
        self._add_process()

        close_layout = QHBoxLayout()
        close_layout.addStretch()
        button_close = QPushButton("Close")
        button_close.clicked.connect(self.close_dialog)
        close_layout.addWidget(button_close)
        self.layout.addLayout(close_layout)

    def _add_inputs(self):
        inputs_groupbox = QGroupBox("Inputs")
        inputs_groupbox.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed)
        inputs_layout = QVBoxLayout()
        inputs_layout.setSpacing(0)
        inputs_groupbox.setLayout(inputs_layout)

        for input_band_name in input_band_names:
            inputband = GridTransformerInputBand(input_band_name)
            inputs_layout.addWidget(inputband)
            inputband.band_selected.connect(self._band_selected)
            inputband.log_message.connect(self._log_message)

        self.layout.addWidget(inputs_groupbox)

    def _band_selected(self, band_details):
        band_name, filename, band_index = band_details
        self.grid_transformer_inputs[band_name] = (filename, band_index)
        self.validate()

    def validate(self):
        self.run_button.setEnabled(self._is_valid())

    def _is_valid(self) -> bool:
        '''Is this ready to run, as in has the user specified all inputs needed
        for the grid transformer'''
        for band_name in input_band_names:
            if band_name not in self.grid_transformer_inputs:
                return False
            if self.grid_transformer_inputs[band_name] is None:
                return False
        if 'output' not in self.grid_transformer_inputs:
            return False

        return True

    def _log_message(self, message):
        self.log_messages.appendPlainText(message)

    def _add_output(self):
        output_groupbox = QGroupBox("Output")
        output_groupbox.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed)
        output_layout = QVBoxLayout()
        output_layout.setSpacing(0)
        output_groupbox.setLayout(output_layout)

        output_file_layout = QHBoxLayout()
        output_file_layout.setSpacing(4)
        self.output_file_input = QLineEdit()
        self.output_file_input.textChanged.connect(
            self._on_output_filename_changed)
        self.output_file_input.setMinimumWidth(400)
        self.output_file_input.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding)
        output_file_layout.addWidget(self.output_file_input)
        output_layout.addLayout(output_file_layout)

        self.open_output_file_button = QPushButton()
        output_file_layout.addWidget(self.open_output_file_button)
        self.open_output_file_button.setIcon(qta.icon('fa.folder-open'))
        self.open_output_file_button.setToolTip("Select output file location")
        self.open_output_file_button.clicked.connect(self._click_open_output)

        self.layout.addWidget(output_groupbox)

    def _on_output_filename_changed(self, filename):
        self.grid_transformer_inputs['output'] = filename
        self.validate()

    def _set_output_filename(self, filename):
        self.output_file_input.setText(filename)
        self.grid_transformer_inputs['output'] = filename
        self.validate()

    def _click_open_output(self):
        filters = (
            "GeoTIFF (*.tif *.tiff)"
        )
        filename, _ = QFileDialog.getSaveFileName(
            self,
            f"Select output file",
            GuiSettings.settings().value(output_folder_settings),
            filters)
        if filename is None:
            return
        last_open_folder = os.path.dirname(filename)
        if os.path.exists(last_open_folder):
            GuiSettings.settings().setValue(
                output_folder_settings, last_open_folder)

        self._set_output_filename(filename)

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
        self.run_button.setFixedWidth(100)
        run_icon = qta.icon('fa.play', color='green')
        self.run_button.setIcon(run_icon)
        self.run_button.clicked.connect(self._click_run)
        hbox.addWidget(self.run_button)

        self.stop_button = QPushButton()
        self.stop_button.setEnabled(False)
        self.stop_button.setText("Stop")
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
        success_label = QLabel("Grid Transformer completed successfully.")
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
        log_font = QFont("monospace")
        log_font.setStyleHint(QFont.TypeWriter)
        self.log_messages.setFont(log_font)
        self.log_messages.setReadOnly(True)
        self.log_messages.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding)
        # self.log_messages.sizePolicy.setVerticalStretch(1)
        log_layout.addWidget(self.log_messages)
        process_layout.addLayout(log_layout)

        self.layout.addWidget(process_groupbox)

    def _on_progress(self, progress):
        self.progress_bar.setValue(int(progress * 100))

    def _on_complete(self, successful: bool):
        self.warning_frame.setVisible(not successful)
        self.success_frame.setVisible(successful)
        self.stop_button.setEnabled(False)
        self.run_button.setEnabled(True)

        run_time = time.perf_counter() - self.start_time
        self._log_message(
            f"Total grid transformation time = {run_time:.2f} sec")
        self._log_message("\n\n")

    def _click_run(self):
        self.warning_frame.setVisible(False)
        self.success_frame.setVisible(False)
        self.stop_button.setEnabled(True)
        self.run_button.setEnabled(False)

        self.gt_executor = QtGridTransformerThread(
            self.grid_transformer_inputs)

        self.gt_executor.progress.connect(self._on_progress)
        self.gt_executor.message.connect(self._log_message)
        self.gt_executor.complete.connect(self._on_complete)

        self.start_time = time.perf_counter()
        self._log_message("\n\nStarting Grid Transformer process")
        self.gt_executor.start()

    def _click_stop(self):
        if self.gt_executor is not None:
            self.gt_executor.stop()

    def close_dialog(self):
        self.close()
