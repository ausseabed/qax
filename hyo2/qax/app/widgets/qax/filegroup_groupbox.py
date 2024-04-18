import logging
import os

from typing import Optional
from PySide2 import QtCore
from PySide2.QtWidgets import \
    QSizePolicy, QComboBox, QTableWidget, QGroupBox, QVBoxLayout, \
    QHBoxLayout, QTableWidgetItem, QPushButton, QFileDialog, QHeaderView, \
    QDialog, QDialogButtonBox, QLabel, QLineEdit, QAbstractItemView, QFrame

from hyo2.qax.app import qta
from hyo2.qax.app.gui_settings import GuiSettings
from hyo2.qax.lib.plugin_service import PluginService

from ausseabed.qajson.model import QajsonRoot, QajsonFile, QajsonDataLevel


logger = logging.getLogger(__name__)

class GroupRow:

    def __init__(
            self,
            filename: str,
            dataset: str,
            file_type: str,
            file_details:str
        ) -> None:
        self.filename = filename
        self._dataset = dataset
        self._user_set_dataset = False
        self._file_type = file_type
        self._file_details = file_details
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

    @property
    def file_details(self) -> str:
        return self._file_details

    def __str__(self) -> str:
        return (
            f"{self.filename_short} {self.dataset} "
            f"{self.file_type} {self.file_details}"
        )


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


class FileGroupGroupBox(QGroupBox):

    filenames_added = QtCore.Signal()
    filenames_removed = QtCore.Signal()
    dataset_changed = QtCore.Signal()
    filetype_changed = QtCore.Signal()

    def __init__(self, parent_win, prj):
        QGroupBox.__init__(self, "Survey Products")
        self.prj = prj
        self.parent_win = parent_win

        # for sorting
        self.sort_reversed = False
        self.last_sort_column = -1

        self.plugin_service:Optional[PluginService] = None
        self.no_checks_selected_layout = None

        self.rows:list[GroupRow] = []
        self.available_datasets: list[str] = []
        self.available_datasets.append("default")
        self.available_types: list[str] = []

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.table = QTableWidget()
        # hide the table row numbers
        self.table.verticalHeader().setVisible(False)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Filename", "Dataset", "Type", "Details" , ""])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        # don't highlight the column headers when one of them is clicked (for sorting)
        self.table.horizontalHeader().setHighlightSections(False)
        # there's no need to select any rows in this table
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        # for sorting
        self.table.horizontalHeader().sectionClicked.connect(self._click_header)
        main_layout.addWidget(self.table)

        self.cross_icon = qta.icon('fa.close')

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.add_file_button = QPushButton()
        button_layout.addWidget(self.add_file_button)
        self.add_file_button.setText("Add File")
        self.add_file_button.setIcon(qta.icon('fa.folder-open'))
        self.add_file_button.setToolTip("Add survey product files")
        self.add_file_button.clicked.connect(self._click_add_file)
        self.remove_all_files_button = QPushButton()
        self.remove_all_files_button.setText("Remove All Files")
        self.remove_all_files_button.setIcon(self.cross_icon)
        self.remove_all_files_button.setToolTip("Remove all survey product files")
        self.remove_all_files_button.clicked.connect(self._click_remove_all_files)
        button_layout.addWidget(self.remove_all_files_button)

        main_layout.addLayout(button_layout)

    def _click_header(self, header_index: int) -> None:
        # implement a very simple sort for the file list table. Qt provides a more
        # native/advanced method to do this,
        if self.last_sort_column == header_index:
            # if the user has clicked the same column header twice then reverse the
            # sort order for this column
            self.sort_reversed =  not self.sort_reversed

        # sort the rows list (in place) by whatever column the user has clicked
        if header_index == 0:
            self.rows.sort(key=lambda x: x.filename_short, reverse=self.sort_reversed)
        elif header_index == 1:
            self.rows.sort(key=lambda x: x.dataset, reverse=self.sort_reversed)
        elif header_index == 2:
            self.rows.sort(key=lambda x: x.file_type, reverse=self.sort_reversed)
        # remember what column was last sorted by so we can reverse it if the user
        # clicks again
        self.last_sort_column = header_index
        # once the list has been updated we need to update the table UI to match
        self.__update_table()

    def __update_table(self) -> None:
        # show and hide the little ^ char Qt uses to show sorting
        if (self.last_sort_column == -1):
            self.table.horizontalHeader().setSortIndicatorShown(False)
        else:
            self.table.horizontalHeader().setSortIndicatorShown(True)
        # update the order and column being sorted on (if any)
        if (self.last_sort_column != -1):
            order = (
                QtCore.Qt.SortOrder.DescendingOrder
                if self.sort_reversed
                else QtCore.Qt.SortOrder.AscendingOrder
            )
            self.table.horizontalHeader().setSortIndicator(self.last_sort_column, order)

        self.table.setRowCount(len(self.rows))
        for i, row in enumerate(self.rows):
            item_filename = QLabel(row.filename_short)
            item_filename.setToolTip(row.filename)
            item_filename_widget = QFrame()
            item_filename_widget.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Minimum)
            item_filename_widget.setLayout(QHBoxLayout())
            item_filename_widget.layout().addWidget(item_filename)
            item_filename_widget.layout().addStretch()
            item_filename_widget.layout().setAlignment(QtCore.Qt.AlignTop)
            item_filename_widget.layout().setContentsMargins(4, 2, 0, 0)
            self.table.setCellWidget(i, 0, item_filename_widget)

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
            item_dataset_widget = QFrame()
            item_dataset_widget.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Minimum)
            item_dataset_widget.setLayout(QHBoxLayout())
            item_dataset_widget.layout().addWidget(item_dataset)
            item_dataset_widget.layout().addStretch()
            item_dataset_widget.layout().setAlignment(QtCore.Qt.AlignTop)
            item_dataset_widget.layout().setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(i, 1, item_dataset_widget)

            item_type = QComboBox()
            item_type.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Minimum)
            for t in self.available_types:
                item_type.addItem(t)
            try:
                row_type_index = self.available_types.index(row.file_type)
            except ValueError as ex:
                row_type_index = self.available_types.index("Unknown")

            item_type.setCurrentIndex(row_type_index)
            item_type.currentIndexChanged.connect(
                lambda x, row=row: self._file_type_changed(x, row)
            )
            item_type_widget = QFrame()
            item_type_widget.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Minimum)
            item_type_widget.setLayout(QHBoxLayout())
            item_type_widget.layout().addWidget(item_type)
            item_type_widget.layout().addStretch()
            item_type_widget.layout().setAlignment(QtCore.Qt.AlignTop)
            item_type_widget.layout().setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(i, 2, item_type_widget)

            item_file_details = QTableWidgetItem(row.file_details)
            self.table.setItem(i, 3, item_file_details)

            item_remove_button = QPushButton()
            item_remove_button.setSizePolicy(
                QSizePolicy.Minimum, QSizePolicy.Minimum)
            item_remove_button.setText("")
            item_remove_button.setIcon(self.cross_icon)
            item_remove_button.clicked.connect(
                lambda x=1, row=row: self._remove_file(x, row)
            )
            item_remove_button_widget = QFrame()
            item_remove_button_widget.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Expanding)
            item_remove_button_widget.setLayout(QVBoxLayout())
            item_remove_button_widget.layout().addWidget(item_remove_button)
            item_remove_button_widget.layout().addStretch()
            item_remove_button_widget.layout().setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
            item_remove_button_widget.layout().setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(i, 4, item_remove_button_widget)

            self.table.verticalHeader().setSectionResizeMode(
                i, QHeaderView.ResizeMode.ResizeToContents
            )

        # we need to call this explicitly presumably because the table
        # doesn't correctly pick up that the qcombobox within this cell
        # has changed its size (as it has a dataset name with a new width)
        self.table.horizontalHeader().resizeSections()

    def _remove_file(self, x, row:GroupRow):
        self.rows.remove(row)
        self.__update_table()
        self.filenames_removed.emit()

    def _click_remove_all_files(self):
        self.rows.clear()
        self.__update_table()

    def __add_new_files(self, filenames: list[str]) -> None:
        for filename in filenames:
            ft = self.plugin_service.identify_file_group(filename)
            fd = self.plugin_service.get_file_details(filename)
            gr = GroupRow(
                filename=filename,
                dataset='default',
                file_type=ft,
                file_details=fd
            )
            self.rows.append(gr)

        # files won't be sorted when new ones are added
        self.last_sort_column = -1
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
            else:
                # we don't change anything (as the user has cancelled)
                # but updating the table will reselect whatever was selected
                # here before the user selected 'New...' from the list
                self.__update_table()
        else:
            # then user has selected from the existing list, just update the row
            row.dataset = self.available_datasets[index]
        self.dataset_changed.emit()

    def _file_type_changed(self, index: int, row:GroupRow):
        row.file_type = self.available_types[index]
        self.filetype_changed.emit()

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
        self.filenames_added.emit()

    def set_plugin_service(self, ps: PluginService):
        self.plugin_service = ps
        self.available_types = self.plugin_service.get_all_file_group_names()
        self.__update_table()

    def get_grouped_files(self) -> list[list[QajsonFile]]:
        """ Returns a list of lists containing QajsonFiles, each nested list
        is a grouping based on the 'Dataset' specified by the user.
        """
        # key is dataset name, value is list of files that belong to dataset
        group_dict: dict[str, list[QajsonFile]] = {}
        for row in self.rows:
            qf = QajsonFile(row.filename, row.file_type, None)
            if row.dataset in group_dict:
                # dataset already added to dict
                pass
            else:
                # need to create new file list for this row
                qf_list: list[QajsonFile] = []
                group_dict[row.dataset] = qf_list
            group_dict[row.dataset].append(qf)

        return list(group_dict.values())

    def __is_same_qajsonfile(self, a: QajsonFile, b: QajsonFile) -> bool:
        """ Compares two QajsonFile objects
        """
        # this should likely be a part of the qajson lib
        return a.file_type == b.file_type and a.path == b.path

    def __is_same_qajsonfile_group(self, a: list[QajsonFile], b: list[QajsonFile]) -> bool:
        """ Compares two lists of QajsonFile objects
        """
        # this should likely be a part of the qajson lib
        for i in a:
            found = False
            for j in b:
                if self.__is_same_qajsonfile(i, j):
                    found = True
            if not found:
                return False
        return True

    def update_ui(self, qajson: QajsonRoot) -> None:
        """ Updates this UI component to show the information within the qajson
        object. In this case the files, and their grouping.
        """
        # we need to build a list of the groups within the QAJSON. Groups will probably
        # be duplicated across the different checks so we need to de-duplicate them
        # before presenting to the user in the UI

        # first we build a list of all the groups across all check definitions in the
        # QAJSON, this *will* include duplicates
        all_groups: list[list[QajsonFile]] = []

        # create a list of all data levels, this makes it easier to iterate over
        all_dl: list[QajsonDataLevel] = []
        all_dl.append(qajson.qa.get_data_level('raw_data'))
        all_dl.append(qajson.qa.get_data_level('survey_products'))

        # for each data level and each check in these, grab the group of files
        for dl in all_dl:
            if dl is None:
                continue

            for c in dl.checks:
                if c.inputs is None:
                    continue

                all_groups.append(c.inputs.files)

        # now create a list of groups that doesn't include duplicates
        groups: list[list[QajsonFile]] = []
        for ag in all_groups:
            exists_already = False
            for g in groups:
                if self.__is_same_qajsonfile_group(ag, g):
                    exists_already = True
            if not exists_already:
                groups.append(ag)

        # now 'convert' these groups of files into the self.rows list used by this
        # UI component
        for g in groups:
            ds_name = self.__get_new_dataset_name()
            self.available_datasets.append(ds_name)
            for f in g:
                if f.file_type not in self.available_types:
                    self.available_types.append(f.file_type)
                self.rows.append(
                    GroupRow(
                        filename=f.path,
                        dataset=ds_name,
                        file_type=f.file_type,
                        file_details=self.plugin_service.get_file_details(f.path)
                    )
                )

        # recreate the table with this data derived from the QAJSON
        self.__update_table()
