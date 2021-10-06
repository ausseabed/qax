from ausseabed.qajson.model import QajsonRoot
from pathlib import Path
from PySide2 import QtCore, QtGui, QtWidgets
from typing import List, NoReturn
import logging
import os
import re

from hyo2.qax.app import qta
from hyo2.qax.app.gui_settings import GuiSettings
from hyo2.qax.lib.plugin import QaxFileGroup


logger = logging.getLogger(__name__)


class FileGroupWidget(QtWidgets.QWidget):
    """ Widget to support selection of one or more files for a *single* survey
    product. """

    # emitted when a new file is selected
    files_added = QtCore.Signal(QaxFileGroup)
    # emitted when a list of selected files is cleared
    files_removed = QtCore.Signal(QaxFileGroup)

    def __init__(self, file_group: QaxFileGroup, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)
        self.setMinimumHeight(40)

        self.file_group = file_group
        hbox = QtWidgets.QHBoxLayout()
        hbox.setAlignment(QtCore.Qt.AlignTop)
        hbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(hbox)

        self.selected_files = []

        left_space = 100

        label_layout = QtWidgets.QVBoxLayout()
        label_layout.setAlignment(QtCore.Qt.AlignTop)
        label = QtWidgets.QLabel("{}:".format(file_group.name))
        label.setWordWrap(True)
        label.setMinimumWidth(left_space)
        label.setMaximumWidth(left_space)
        label_layout.addWidget(label)
        hbox.addLayout(label_layout)

        self.file_list = QtWidgets.QListWidget()
        self.file_list.setMinimumHeight(40)
        hbox.addWidget(self.file_list)
        self.file_list.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)
        self.file_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(
            self.__make_context_menu)
        self.file_list.setAlternatingRowColors(True)
        # Enable dropping onto the input ss list
        self.file_list.setAcceptDrops(True)
        self.file_list.installEventFilter(self)

        button_layout = QtWidgets.QVBoxLayout()
        hbox.addLayout(button_layout)
        button_layout.setAlignment(QtCore.Qt.AlignTop)

        self.add_file_button = QtWidgets.QPushButton()
        button_layout.addWidget(self.add_file_button)
        self.add_file_button.setIcon(qta.icon('fa.folder-open'))
        self.add_file_button.setToolTip(
            "Add (or drag-and-drop) the survey {} files"
            .format(file_group.name))
        self.add_file_button.clicked.connect(self._click_add)

        self.clear_files_button = QtWidgets.QPushButton()
        button_layout.addWidget(self.clear_files_button)
        self.clear_files_button.setIcon(qta.icon('fa.close'))
        self.clear_files_button.setToolTip(
            "Clear {} files".format(file_group.name))
        self.clear_files_button.clicked.connect(self._click_clear)

    def eventFilter(self, obj, e):
        """ Captures events for the purpose of supporting drag and drop of
        files onto the appropriate file lists
        """
        # note for a drop event to be handled, the drag enter or drag move
        # events must be accepted.

        # drag events
        if (
            (e.type() == QtCore.QEvent.DragEnter) or
            (e.type() == QtCore.QEvent.DragMove)
        ):
            if (obj is not self.file_list) and (not e.mimeData().hasUrls):
                e.ignore()
                return False

            for url in e.mimeData().urls():
                dropping_file = str(url.toLocalFile())
                extension = os.path.splitext(dropping_file)[-1].lower()
                extension = extension.lstrip('.')
                acceptable_extensions = [
                    ft.extension for ft in self.file_group.file_types]
                if extension in acceptable_extensions:
                    e.accept()
                    return True
                e.ignore()
                return True

        # drop events
        if (
            e.type() == QtCore.QEvent.Drop and
            obj is self.file_list and
            e.mimeData().hasUrls()
        ):
            e.setDropAction(QtCore.Qt.CopyAction)
            e.accept()
            for url in e.mimeData().urls():
                dropped_file = str(url.toLocalFile())

                logger.debug("dropped file: %s" % dropped_file)
                extension = os.path.splitext(dropped_file)[-1].lower()
                extension = extension.lstrip('.')
                acceptable_extensions = [
                    ft.extension for ft in self.file_group.file_types]
                if extension in acceptable_extensions:
                    self.selected_files.append(dropped_file)
                    self._update_file_list()
                    self.files_added.emit(self.file_group)
                else:
                    # note: the following code is never called as only
                    # accepted drag events (enter and move) will make it here.
                    # And we validate for valid extensions in the enter and
                    # move handlers above. non acceptable_extensions events
                    # are ignored.
                    names = [
                        "- {}".format(ft.formatted_name())
                        for ft in self.file_group.file_types]
                    msg = (
                        'Drag-and-drop is only possible with the ' +
                        'following file extensions:\n' +
                        '{}\n'.format("\n".join(names)) +
                        'Dropped file:\n'
                        '{}'.format(dropped_file))
                    # noinspection PyCallByClass,PyArgumentList
                    QtWidgets.QMessageBox.critical(
                        self, "Drag-and-drop Error", msg,
                        QtWidgets.QMessageBox.Ok)
            return True

        # if event not handled defer to default event handler
        return QtWidgets.QMainWindow.eventFilter(self, obj, e)

    def _click_clear(self):
        self.selected_files.clear()
        self._update_file_list()

    def _click_add(self):
        """ Add files selected by user. Opens file selection dialog
        """
        import_folder_name = "{}_import_folder".format(
            self.file_group.clean_name())

        filters = []
        if len(self.file_group.file_types) > 0:
            all_ext = [
                "*.{}".format(ft.extension)
                for ft in self.file_group.file_types]
            all_formats = "Supported formats ({})".format(" ".join(all_ext))
            filters.append(all_formats)
            for ft in self.file_group.file_types:
                filters.append("{} (*.{})".format(ft.name, ft.extension))
        filters.append("All files (*.*)")

        # ask the file path to the user
        # noinspection PyCallByClass
        selections, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            "Add {} file".format(self.file_group.name.lower()),
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
        self.selected_files.extend(new_selected_files)
        self._update_file_list()
        self.files_added.emit(self.file_group)

    def __make_context_menu(self, pos):
        remove_action = QtWidgets.QAction(
            "Remove files",
            self,
            statusTip="Remove {} files".format(
                self.file_group.name.lower()),
            triggered=self.remove_files)

        menu = QtWidgets.QMenu(parent=self)
        menu.addAction(remove_action)
        menu.exec_(self.file_list.mapToGlobal(pos))

    def remove_files(self) -> NoReturn:
        """ Clears the list of selected files """
        logger.debug("user want to remove raw files")
        self.file_list.clear()
        self.selected_files.clear()
        self.files_removed.emit(self.file_group)

    def _update_file_list(self) -> NoReturn:
        self.file_list.clear()
        for selected_file in self.selected_files:
            file_item = QtWidgets.QListWidgetItem()
            file_item.setText(selected_file)
            file_item.setFont(GuiSettings.console_font())
            # file_item.setForeground(GuiSettings.console_fg_color())

            path = Path(selected_file)
            matching_file_type = self.file_group.matching_file_type(path)
            if (
                (matching_file_type is not None) and
                (matching_file_type.icon is not None)
            ):
                file_type_icon = QtGui.QIcon(
                    GuiSettings.icon_path(matching_file_type.icon))
                file_item.setIcon(file_type_icon)

            self.file_list.addItem(file_item)

    def update_ui(self, qajson: QajsonRoot) -> NoReturn:
        data_levels = ['raw_data', 'survey_products', 'chart_adequacy']

        # build list of all checks from all data levels
        all_checks = []
        for dl in data_levels:
            data_level = getattr(qajson.qa, dl, None)
            if data_level is None:
                continue
            all_checks.extend(data_level.checks)

        all_inputs = []
        for check in all_checks:
            all_inputs.extend(check.inputs.files)

        self.selected_files.clear()
        for input in all_inputs:
            if (input.file_type == self.file_group.name and
                    input.path not in self.selected_files):
                self.selected_files.append(input.path)
                dirty = True

        self._update_file_list()


class FileGroupGroupBox(QtWidgets.QGroupBox):
    """ Widget to support selection of survey products (the input files) that
    will be passed to the check tools. Widget includes multiple
    `FileGroupWidget` instances.
    """

    # emitted when a new file is selected, in one of the file group widgets
    files_added = QtCore.Signal(QaxFileGroup)
    # emitted when a list or all file group lists of files are cleared
    files_removed = QtCore.Signal(QaxFileGroup)

    def __init__(self, parent_win, prj):
        QtWidgets.QGroupBox.__init__(self, "Survey Products")
        self.prj = prj
        self.parent_win = parent_win
        self.file_group_widgets = []
        self.no_checks_selected_layout = None

        main_layout = QtWidgets.QVBoxLayout()
        self.file_groups_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(self.file_groups_layout)

        self.setLayout(main_layout)

        # clear data
        hbox = QtWidgets.QHBoxLayout()
        main_layout.addLayout(hbox)
        hbox.addStretch()
        self.clear_button = QtWidgets.QPushButton()
        hbox.addWidget(self.clear_button)

        self.clear_button.setText("Clear all selected files")
        self.clear_button.setToolTip('Clear all selected files')
        self.clear_button.setStyleSheet(
            "padding-left: 20px; padding-right: 20px;"
            "padding-top: 10px; padding-bottom: 10px;")
        # noinspection PyUnresolvedReferences
        self.clear_button.clicked.connect(self._click_clear_data)
        hbox.addStretch()

    def _click_clear_data(self):
        logger.debug("clearing selected input files")
        for sp_widget in self.file_group_widgets:
            sp_widget.remove_files()

    def _on_files_added(self, file_group: QaxFileGroup):
        # propogate events up GUI component tree to parent
        self.files_added.emit(file_group)

    def _on_files_removed(self, file_group: QaxFileGroup):
        # propogate events up GUI component tree to parent
        self.files_removed.emit(file_group)

    def update_file_groups(
            self, file_groups: List[QaxFileGroup]
            ) -> NoReturn:
        """ Updates the various lists of files based on the `file_groups`
        list
        """
        self.setMinimumHeight(40 + 40 * len(file_groups))

        if self.no_checks_selected_layout is not None:
            self.no_checks_selected_layout.setParent(None)
            self.no_checks_selected_layout = None

        # clear all items from survey products layout
        for sp_widget in self.file_group_widgets:
            sp_widget.setParent(None)
        self.file_group_widgets.clear()

        if len(file_groups) == 0:
            no_fgs = QtWidgets.QWidget()
            hbox = QtWidgets.QHBoxLayout()
            no_fgs.setLayout(hbox)
            hbox.addStretch()
            label_no_params = QtWidgets.QLabel(
                "Please select one or more check tools to enable input file "
                "selection")
            hbox.addWidget(label_no_params)
            hbox.addStretch()
            self.file_groups_layout.addWidget(no_fgs)
            self.no_checks_selected_layout = no_fgs
            return

        for file_group in file_groups:
            sp_widget = FileGroupWidget(file_group, self)
            sp_widget.files_added.connect(self._on_files_added)
            sp_widget.files_removed.connect(self._on_files_removed)
            self.file_groups_layout.addWidget(sp_widget)
            self.file_group_widgets.append(sp_widget)

    def get_files(self, file_groups: List[QaxFileGroup]) -> List[Path]:
        """ Gets a list of files that have been selected by the user, but only
        for the given file groups.
        """
        all_files = []
        for fgwidget in self.file_group_widgets:
            matching_fg = next(
                (
                    fg
                    for fg in file_groups
                    if fg.name == fgwidget.file_group.name
                ), None)
            if matching_fg is None:
                continue
            paths = ([
                (Path(fn), fgwidget.file_group.name)
                for fn in fgwidget.selected_files
            ])
            all_files.extend(paths)

        return all_files

    def update_ui(self, qajson: QajsonRoot) -> NoReturn:
        for fgw in self.file_group_widgets:
            fgw.update_ui(qajson)
