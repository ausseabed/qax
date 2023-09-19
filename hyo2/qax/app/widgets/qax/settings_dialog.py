from PySide2.QtWidgets import QApplication, QDialog, QLineEdit, \
    QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QWidget, \
    QSizePolicy, QComboBox, QFileDialog, QPlainTextEdit, QProgressBar, \
    QFrame
from PySide2.QtGui import QFont, QIntValidator
from PySide2 import QtCore
from typing import Any

from hyo2.qax.app import qta
from hyo2.qax.app.gui_settings import GuiSettings
from hyo2.qax.app import gui_settings_const

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

    def close_dialog(self):
        self.close()
