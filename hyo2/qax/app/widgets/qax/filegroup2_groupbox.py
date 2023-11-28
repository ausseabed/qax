import logging
import os

from typing import Optional
from PySide2 import QtCore, QtGui
from PySide2.QtWidgets import \
    QSizePolicy, QComboBox, QTableWidget, QGroupBox, QVBoxLayout, \
    QHBoxLayout, QTableWidgetItem, QPushButton, QFileDialog, QHeaderView, \
    QDialog, QDialogButtonBox, QLabel, QLineEdit

from hyo2.qax.app import qta
from hyo2.qax.app.gui_settings import GuiSettings
from hyo2.qax.lib.plugin import QaxFileGroup
from hyo2.qax.lib.plugin_service import PluginService

from ausseabed.qajson.model import QajsonRoot


logger = logging.getLogger(__name__)

class GroupRow:

    def __init__(self, filename: str, dataset: str, file_type: str) -> None:
        self.filename = filename
        self._dataset = dataset
        self._user_set_dataset = False
        self._file_type = file_type
        self._user_set_file_type = False

    @property
    def filename_short(self) -> str:
        return os.path.basename(self.filename)

    @property
    def dataset(self) -> str:
        return self._dataset

    @dataset.setter
    def dataset(self, val: str) -> None:
        self._user_set_dataset = True
        self._dataset = val

    @property
    def file_type(self) -> str:
        return self._file_type

    @file_type.setter
    def file_type(self, val: str) -> None:
        self._user_set_file_type = True
        self._file_type = val

    def __str__(self) -> str:
        return f"{self.filename_short} {self.dataset} {self.file_type}"


class NewDatasetDialog(QDialog):
    """ Simple dialog window to prompt user for a new dataset name
    """

    def __init__(self, parent=None, default_name="new dataset"):
        super().__init__(parent)

        self.setWindowTitle("New dataset")

        self.layout = QVBoxLayout()
        message = QLabel("Enter name for new dataset")
        self.layout.addWidget(message)

        self.name_field = QLineEdit()
        self.name_field.setText(default_name)
        self.layout.addWidget(self.name_field)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(QBtn)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

    def get_name(self) -> str:
        """ Get the name entered by the user in the dialog
        """
        return self.name_field.text()


class FileGroup2GroupBox(QGroupBox):

    filenames_added = QtCore.Signal(list[str])

    def __init__(self, parent_win, prj):
        QGroupBox.__init__(self, "Survey Products")
        self.prj = prj
        self.parent_win = parent_win

        self.plugin_service:Optional[PluginService] = None
        self.no_checks_selected_layout = None

        self.rows:list[GroupRow] = []
        self.available_datasets: list[str] = []
        self.available_datasets.append("default")
        self.available_types: list[str] = []


        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # colors = [("Red", "#FF0000"),
        #   ("Green", "#00FF00"),
        #   ("Blue", "#0000FF"),
        #   ("Black", "#000000"),
        #   ("White", "#FFFFFF"),
        #   ("Electric Green", "#41CD52"),
        #   ("Dark Blue", "#222840"),
        #   ("Yellow", "#F9E56d")
        # ]

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Filename", "Dataset", "Type"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)



        main_layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.add_file_button = QPushButton()
        button_layout.addWidget(self.add_file_button)
        self.add_file_button.setText("Add File")
        self.add_file_button.setIcon(qta.icon('fa.folder-open'))
        self.add_file_button.setToolTip("Add survey product files")
        self.add_file_button.clicked.connect(self._click_add_file)
        self.clear_file_button = QPushButton()
        button_layout.addWidget(self.clear_file_button)
        self.clear_file_button.setText("Clear Files")
        self.clear_file_button.setToolTip("Clear all survey product files")
        self.clear_file_button.clicked.connect(self._click_clear_files)

        main_layout.addLayout(button_layout)

    def __update_table(self):
        self.table.setRowCount(len(self.rows))
        for i, row in enumerate(self.rows):
            item_filename = QTableWidgetItem(row.filename_short)
            item_filename.setToolTip(row.filename)
            self.table.setItem(i, 0, item_filename)

            item_dataset = QComboBox()
            item_dataset.setSizePolicy(
                QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
            for ds in self.available_datasets:
                item_dataset.addItem(ds)
            item_dataset.addItem("New...")
            item_dataset.setCurrentIndex(self.available_datasets.index(row.dataset))
            item_dataset.currentIndexChanged.connect(
                lambda x, row=row: self._dataset_changed(x, row)
            )
            self.table.setCellWidget(i, 1, item_dataset)

            item_type = QComboBox()
            item_type.setSizePolicy(
                QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
            for t in self.available_types:
                item_type.addItem(t)
            item_type.setCurrentIndex(self.available_types.index(row.file_type))
            item_type.currentIndexChanged.connect(
                lambda x, row=row: self._file_type_changed(x, row)
            )
            self.table.setCellWidget(i, 2, item_type)

    def __add_new_files(self, filenames: list[str]) -> None:
        for filename in filenames:
            ft = self.plugin_service.identify_file_group(filename)
            gr = GroupRow(
                filename=filename,
                dataset='default',
                file_type=ft
            )
            self.rows.append(gr)

        self.__update_table()

    def __get_new_dataset_name(self, count=1) -> str:
        """ Generates a new default name based on a simple number
        sequence
        """
        test_name = f"dataset {count:02}"
        if test_name in self.available_datasets:
            return self.__get_new_dataset_name(count=count+1)
        return test_name

    def _dataset_changed(self, index: int, row:GroupRow):
        if index >= len(self.available_datasets):
            # then 'New...' has been selected
            ndd = NewDatasetDialog(self, self.__get_new_dataset_name())
            if ndd.exec_():
                new_ds_name = ndd.get_name()
                self.available_datasets.append(new_ds_name)
                row.dataset = new_ds_name
                self.__update_table()
                # we need to call this explicitly presumably because the table
                # doesn't correctly pick up that the qcombobox within this cell
                # has changed its size (as it has a dataset name with a new width)
                self.table.horizontalHeader().resizeSections()
            else:
                # we don't change anything (as the user has cancelled)
                # but updating the table will reselect whatever was selected
                # here before the user selected 'New...' from the list
                self.__update_table()
        else:
            # then user has selected from the existing list, just update the row
            row.dataset = self.available_datasets[index]
        print(row)

    def _file_type_changed(self, index: int, row:GroupRow):
        row.file_type = self.available_types[index]
        print(row)

    def _click_add_file(self):
        import_folder_name = "import_folder_all"
        filters:list[str] = []
        all_ext:list[str] = []
        for file_group in self.plugin_service.get_all_file_groups():
            all_fg_ext = [
                "*.{}".format(ft.extension)
                for ft in file_group.file_types
            ]
            all_ext.extend(all_fg_ext)
            all_fg_ext_str = " ".join(all_fg_ext)
            all_fg_formats = f"{file_group.name} ({all_fg_ext_str})"
            filters.append(all_fg_formats)

        all_ext_str = " ".join(all_ext)
        filters.insert(0, f"All Supported Files ({all_ext_str})")

        filters.append("All files (*.*)")

        # ask the file path to the user
        # noinspection PyCallByClass
        selections, _ = QFileDialog.getOpenFileNames(
            self,
            "Add File",
            GuiSettings.settings().value(import_folder_name),
            ";; ".join(filters))
        if len(selections) == 0:
            logger.debug('adding raw: aborted')
            return

        last_open_folder = os.path.dirname(selections[0])
        if os.path.exists(last_open_folder):
            GuiSettings.settings().setValue(
                import_folder_name, last_open_folder)

        new_selected_files = [
            os.path.abspath(selection).replace("\\", "/")
            for selection in selections
        ]

        self.__add_new_files(new_selected_files)
        # self.filenames_added.emit(new_selected_files)


    def _click_clear_files(self):
        print("files clear")


    def get_rgb_from_hex(self, code):
        code_hex = code.replace("#", "")
        rgb = tuple(int(code_hex[i:i+2], 16) for i in (0, 2, 4))
        
        return QtGui.QColor.fromRgb(rgb[0], rgb[1], rgb[2])

    def set_plugin_service(self, ps: PluginService):
        self.plugin_service = ps
        self.available_types = self.plugin_service.get_all_file_group_names()
        self.__update_table()

    # def update_file_groups(
    #         self, file_groups: list[QaxFileGroup]
    #     ) -> None:
    #     """ Update what file groups should be open'able in this file
    #     selection widget
    #     """
    #     self.file_groups = file_groups
    #     self.available_types = [fg.name for fg in self.file_groups]
    #     self.__update_table()


    def update_ui(self, qajson: QajsonRoot) -> None:
        pass



