from PySide2.QtWidgets import QApplication, QDialog, QLineEdit, \
    QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QWidget, \
    QSizePolicy, QComboBox, QFileDialog, QPlainTextEdit, QProgressBar, \
    QFrame
from PySide2.QtGui import QFont, QIntValidator
from PySide2 import QtCore
from typing import Any
import logging

from hyo2.qax.app import qta
from hyo2.qax.app.gui_settings import GuiSettings
from hyo2.qax.app import gui_settings_const
from hyo2.qax.lib.logging import set_logging

GRIDPROCESSING_TILE_SIZE_MIN = 2000
GRIDPROCESSING_TILE_SIZE_MAX = 200000
GRIDPROCESSING_TILE_SIZE_DEFAULT = 40000


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

        self._add_gridprocessing()
        self._add_logging()

        self.layout.addStretch()

        close_layout = QHBoxLayout()
        close_layout.addStretch()
        button_close = QPushButton("Close")
        button_close.clicked.connect(self.close_dialog)
        close_layout.addWidget(button_close)
        self.layout.addLayout(close_layout)

        self._load_data_from_config()

    def __get_gridprocessing_tile_size(self, cfg_var_name: str) -> int:
        val = GuiSettings.settings().value(cfg_var_name)
        return self.__sanitise_tile_size(val)

    def __sanitise_tile_size(self, val: Any) -> int:
        if val is None:
            return GRIDPROCESSING_TILE_SIZE_DEFAULT
        try:
            ival = int(val)
            if ival < GRIDPROCESSING_TILE_SIZE_MIN:
                return GRIDPROCESSING_TILE_SIZE_MIN
            elif ival > GRIDPROCESSING_TILE_SIZE_MAX:
                return GRIDPROCESSING_TILE_SIZE_MAX
            else:
                return ival
        except ValueError:
            return GRIDPROCESSING_TILE_SIZE_DEFAULT

    def _load_data_from_config(self) -> None:
        gp_t_x = self.__get_gridprocessing_tile_size(
            gui_settings_const.gridprocessing_tile_x
        )
        self.processingtile_x.setText(str(gp_t_x))
        gp_t_y = self.__get_gridprocessing_tile_size(
            gui_settings_const.gridprocessing_tile_y
        )
        self.processingtile_y.setText(str(gp_t_y))


        log_qax_val = GuiSettings.settings().value(gui_settings_const.logging_qax)
        log_qt_val = GuiSettings.settings().value(gui_settings_const.logging_qt)
        log_other_val = GuiSettings.settings().value(gui_settings_const.logging_other)

        log_qax_val = gui_settings_const.logging_qax_default if log_qax_val is None else log_qax_val
        log_qt_val = gui_settings_const.logging_qt_default if log_qt_val is None else log_qt_val
        log_other_val = gui_settings_const.logging_other_default if log_other_val is None else log_other_val

        log_qax_index = [y[0] for y in gui_settings_const.LOG_LEVELS].index(log_qax_val)
        log_qt_index = [y[0] for y in gui_settings_const.LOG_LEVELS].index(log_qt_val)
        log_other_index = [y[0] for y in gui_settings_const.LOG_LEVELS].index(log_other_val)

        self.cb_qax_logging.setCurrentIndex(log_qax_index)
        self.cb_qt_logging.setCurrentIndex(log_qt_index)
        self.cb_other_logging.setCurrentIndex(log_other_index)

    def _add_gridprocessing(self) -> None:
        # Grid Processing config options
        gridprocessing_groupbox = QGroupBox("Grid Processing")
        gridprocessing_groupbox.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed)
        gridprocessing_layout = QVBoxLayout()
        gridprocessing_layout.setSpacing(4)
        gridprocessing_groupbox.setLayout(gridprocessing_layout)
        self.layout.addWidget(gridprocessing_groupbox)

        bold_font = QFont()
        bold_font.setBold(True)
        processingtile_label_0 = QLabel(
            "Processing tile dimensions"
        )
        processingtile_label_0.setFont(bold_font)
        processingtile_label_1 = QLabel(
            "When grid checks are run by QAX the "
            "data is loaded by tiles. Smaller tile sizes allow these checks to "
            "be run on machines with limited memory. When the dataset "
            "size exceeds tile size the detailed spatial outputs will be split "
            "into multiple tiles."
        )
        processingtile_label_1.setWordWrap(True)
        processingtile_label_1.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Minimum)
        processingtile_label_1.setStyleSheet("background: none")
        processingtile_label_2 = QLabel(
            "Note: only change these values if experiencing out of memory errors"
        )
        gridprocessing_layout.addWidget(processingtile_label_0)
        gridprocessing_layout.addWidget(processingtile_label_1)
        gridprocessing_layout.addWidget(processingtile_label_2)

        processingtile_layout = QHBoxLayout()
        gridprocessing_layout.addLayout(processingtile_layout)
        processingtile_layout.setSpacing(32)

        processingtile_size_validator = QIntValidator(
            GRIDPROCESSING_TILE_SIZE_MIN, GRIDPROCESSING_TILE_SIZE_MAX
        )

        processingtile_layout_x = QHBoxLayout()
        processingtile_layout.addLayout(processingtile_layout_x)
        processingtile_layout_x.setSpacing(4)
        processingtile_layout_y = QHBoxLayout()
        processingtile_layout.addLayout(processingtile_layout_y)
        processingtile_layout_y.setSpacing(4)

        self.processingtile_x = QLineEdit()
        self.processingtile_x.setValidator(processingtile_size_validator)
        self.processingtile_y = QLineEdit()
        self.processingtile_y.setValidator(processingtile_size_validator)
        self.processingtile_x.textChanged.connect(
            self._on_processingtile_x_changed)
        self.processingtile_y.textChanged.connect(
            self._on_processingtile_y_changed)
        self.processingtile_x.setMinimumWidth(200)
        self.processingtile_y.setMinimumWidth(200)
        self.processingtile_x.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding)
        self.processingtile_y.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding)
        processingtile_layout_x.addWidget(QLabel('x tile size: '))
        processingtile_layout_x.addWidget(self.processingtile_x)
        processingtile_layout_y.addWidget(QLabel('y tile size:'))
        processingtile_layout_y.addWidget(self.processingtile_y)

    def _on_processingtile_x_changed(self, x):
        GuiSettings.settings().setValue(
            gui_settings_const.gridprocessing_tile_x,
            self.__sanitise_tile_size(x)
        )

    def _on_processingtile_y_changed(self, y):
        GuiSettings.settings().setValue(
            gui_settings_const.gridprocessing_tile_y,
            self.__sanitise_tile_size(y)
        )

    def __add_log_levels(self, cb: QComboBox) -> None:
        for (name, level) in gui_settings_const.LOG_LEVELS:
            cb.addItem(name, level)

    def _add_logging(self) -> None:
        # Grid Processing config options
        logging_groupbox = QGroupBox("Logging")
        logging_groupbox.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred)
        logging_layout = QVBoxLayout()
        logging_layout.setSpacing(4)
        logging_groupbox.setLayout(logging_layout)
        self.layout.addWidget(logging_groupbox)

        label_1 = QLabel(
            "The following settings modify the level of detail that is output to the "
            "QAX console window and the log window on the run tab. Setting log levels "
            "to the most severe category will reduce the volume of log messages."
        )
        label_1.setWordWrap(True)
        label_1.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Minimum)
        logging_layout.addWidget(label_1)
        label_1.setStyleSheet("background: none")
        label_2 = QLabel(
            "Setting the QAX Logging level to INFO may produce some information relative "
            "to the checks being performed. QT and Other logging options will likely only "
            "produce information required to support development and debugging."
        )
        label_2.setWordWrap(True)
        label_2.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Minimum)
        logging_layout.addWidget(label_2)
        label_2.setStyleSheet("background: none")

        label_width = 80
        cb_width = 80
        layout_qax_logging = QHBoxLayout()
        logging_layout.addLayout(layout_qax_logging)
        l = QLabel("QAX logging:")
        l.setFixedWidth(label_width)
        layout_qax_logging.addWidget(l)
        self.cb_qax_logging = QComboBox()
        self.__add_log_levels(self.cb_qax_logging)
        self.cb_qax_logging.currentIndexChanged.connect(self._on_logging_changed)
        self.cb_qax_logging.setFixedWidth(cb_width)
        layout_qax_logging.addWidget(self.cb_qax_logging)
        layout_qax_logging.addStretch()

        layout_qt_logging = QHBoxLayout()
        logging_layout.addLayout(layout_qt_logging)
        l = QLabel("QT logging:")
        l.setFixedWidth(label_width)
        layout_qt_logging.addWidget(l)
        self.cb_qt_logging = QComboBox()
        self.__add_log_levels(self.cb_qt_logging)
        self.cb_qt_logging.currentIndexChanged.connect(self._on_logging_changed)
        self.cb_qt_logging.setFixedWidth(cb_width)
        layout_qt_logging.addWidget(self.cb_qt_logging)
        layout_qt_logging.addStretch()

        layout_other_logging = QHBoxLayout()
        logging_layout.addLayout(layout_other_logging)
        l = QLabel("Other logging:")
        l.setFixedWidth(label_width)
        layout_other_logging.addWidget(l)
        self.cb_other_logging = QComboBox()
        self.__add_log_levels(self.cb_other_logging)
        self.cb_other_logging.currentIndexChanged.connect(self._on_logging_changed)
        self.cb_other_logging.setFixedWidth(cb_width)
        layout_other_logging.addWidget(self.cb_other_logging)
        layout_other_logging.addStretch()

    def _on_logging_changed(self):
        GuiSettings.settings().setValue(
            gui_settings_const.logging_qax,
            self.cb_qax_logging.currentText()
        )
        GuiSettings.settings().setValue(
            gui_settings_const.logging_qt,
            self.cb_qt_logging.currentText()
        )
        GuiSettings.settings().setValue(
            gui_settings_const.logging_other,
            self.cb_other_logging.currentText()
        )

        log_qax_int = [item[1] for item in gui_settings_const.LOG_LEVELS if item[0] == self.cb_qax_logging.currentText()][0]
        log_qt_int = [item[1] for item in gui_settings_const.LOG_LEVELS if item[0] == self.cb_qt_logging.currentText()][0]
        log_other_int = [item[1] for item in gui_settings_const.LOG_LEVELS if item[0] == self.cb_other_logging.currentText()][0]

        set_logging(
            default_logging=log_other_int,
            qax_logging=log_qax_int,
            qt_logging=log_qt_int
        )

    def close_dialog(self):
        self.close()
