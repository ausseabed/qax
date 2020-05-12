import os
import logging
from pathlib import Path
from PySide2 import QtCore, QtGui, QtWidgets
from hyo2.abc.lib.helper import Helper

from hyo2.qax.app.gui_settings import GuiSettings
from hyo2.qax.app.widgets.qax.profile_groupbox import ProfileGroupBox
from hyo2.qax.app.widgets.qax.filegroup_groupbox \
    import FileGroupGroupBox
from hyo2.qax.lib.config import QaxConfig, QaxConfigProfile
from hyo2.qax.lib.plugin import QaxPlugins, QaxFileGroup

# Use NSURL as a workaround to pyside/Qt4 behaviour for dragging and dropping
# on OSx
if Helper.is_darwin():
    # noinspection PyUnresolvedReferences
    from Foundation import NSURL

logger = logging.getLogger(__name__)


class MainTab(QtWidgets.QMainWindow):

    here = os.path.abspath(os.path.dirname(__file__))

    profile_selected = QtCore.Signal(QaxConfigProfile)
    generate_checks = QtCore.Signal(Path)

    def __init__(self, parent_win, prj):
        QtWidgets.QMainWindow.__init__(self)

        # store a project reference
        self.prj = prj
        self.prj.qa_json_path_changed.connect(self._on_qa_json_path_changed)
        self.parent_win = parent_win
        self.media = self.parent_win.media

        # aux variables
        self.has_raw = False
        self.has_dtm = False
        self.has_ff = False
        self.has_enc = False
        self.has_json = False

        self.selected_profile = None
        self.selected_check_tools = []

        # ui
        self.panel = QtWidgets.QFrame()
        self.setCentralWidget(self.panel)
        self.vbox = QtWidgets.QVBoxLayout()
        self.panel.setLayout(self.vbox)

        left_space = 100
        vertical_space = 1
        label_size = 160

        # Include widget for selecting profile and check tools to run
        self.profile_selection = ProfileGroupBox(
            self, self.prj, QaxConfig.instance())
        self.profile_selection.profile_selected.connect(
            self._on_profile_selected)
        self.profile_selection.check_tool_selection_change.connect(
            self._on_check_tools_selected)
        self.vbox.addWidget(self.profile_selection)

        self.file_group_selection = FileGroupGroupBox(self, self.prj)
        self.vbox.addWidget(self.file_group_selection)

        self._on_check_tools_selected(
            self.profile_selection.selected_check_tools())
        self.file_group_selection.files_added.connect(
            self._on_file_group_files_added)
        self.file_group_selection.files_removed.connect(
            self._on_file_group_files_removed)

        # data outputs
        self.savedData = QtWidgets.QGroupBox(
            "Data outputs [drap-and-drop the desired output folder]")
        self.savedData.setStyleSheet(
            "QGroupBox::title { color: rgb(155, 155, 155); }")
        self.vbox.addWidget(self.savedData)

        vbox = QtWidgets.QVBoxLayout()
        self.savedData.setLayout(vbox)

        # add folder
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        text_add_folder = QtWidgets.QLabel("Folder:")
        hbox.addWidget(text_add_folder)
        text_add_folder.setMinimumWidth(left_space)
        self.output_folder = QtWidgets.QListWidget()
        hbox.addWidget(self.output_folder)
        self.output_folder.setMinimumHeight(GuiSettings.single_line_height())
        self.output_folder.setMaximumHeight(GuiSettings.single_line_height())
        self.output_folder.clear()
        new_item = QtWidgets.QListWidgetItem()
        new_item.setIcon(
            QtGui.QIcon(os.path.join(self.parent_win.media, 'folder.png')))
        new_item.setText("{}".format(self.prj.output_folder))
        new_item.setFont(GuiSettings.console_font())
        new_item.setForeground(GuiSettings.console_fg_color())
        self.output_folder.addItem(new_item)
        # Enable dropping onto the input ss list
        self.output_folder.setAcceptDrops(True)
        self.output_folder.installEventFilter(self)
        button_add_folder = QtWidgets.QPushButton()
        hbox.addWidget(button_add_folder)
        button_add_folder.setFixedHeight(GuiSettings.single_line_height())
        button_add_folder.setFixedWidth(GuiSettings.single_line_height())
        button_add_folder.setText(" .. ")
        button_add_folder.setToolTip('Add (or drag-and-drop) output folder')
        # noinspection PyUnresolvedReferences
        button_add_folder.clicked.connect(self.click_add_folder)

        # open folder
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()

        text_set_prj_folder = QtWidgets.QLabel("Create project folder: ")
        hbox.addWidget(text_set_prj_folder)
        text_set_prj_folder.setFixedHeight(GuiSettings.single_line_height())
        self.output_prj_folder = QtWidgets.QCheckBox("")
        self.output_prj_folder.setToolTip(
            'Create a sub-folder with project name')
        self.output_prj_folder.setChecked(self.prj.create_project_folder)
        self.output_prj_folder.clicked.connect(
            self.click_output_project_folder)
        hbox.addWidget(self.output_prj_folder)

        text_set_subfolders = QtWidgets.QLabel("Per-tool sub-folders: ")
        hbox.addWidget(text_set_subfolders)
        text_set_subfolders.setFixedHeight(GuiSettings.single_line_height())
        self.output_subfolders = QtWidgets.QCheckBox("")
        self.output_subfolders.setToolTip('Create a sub-folder for each tool')
        self.output_subfolders.setChecked(self.prj.per_tool_folders)
        # noinspection PyUnresolvedReferences
        self.output_subfolders.clicked.connect(self.click_output_subfolders)
        hbox.addWidget(self.output_subfolders)

        hbox.addStretch()

        button_default_output = QtWidgets.QPushButton()
        hbox.addWidget(button_default_output)
        button_default_output.setFixedHeight(GuiSettings.single_line_height())
        # button_open_output.setFixedWidth(GuiSettings.single_line_height())
        button_default_output.setText("Use default")
        button_default_output.setToolTip('Use the default output folder')
        # noinspection PyUnresolvedReferences
        button_default_output.clicked.connect(self.click_default_output)

        button_open_output = QtWidgets.QPushButton()
        hbox.addWidget(button_open_output)
        button_open_output.setFixedHeight(GuiSettings.single_line_height())
        # button_open_output.setFixedWidth(GuiSettings.single_line_height())
        button_open_output.setText("Open folder")
        button_open_output.setToolTip('Open the output folder')
        # noinspection PyUnresolvedReferences
        button_open_output.clicked.connect(self.click_open_output)

        hbox.addStretch()

        self.vbox.addStretch()

        # data outputs
        self.checksSuite = QtWidgets.QGroupBox("Checks suite")
        self.checksSuite.setStyleSheet(
            "QGroupBox::title { color: rgb(155, 155, 155); }")
        self.vbox.addWidget(self.checksSuite)

        vbox = QtWidgets.QVBoxLayout()
        self.checksSuite.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        self.button_generate_checks = QtWidgets.QPushButton()
        hbox.addWidget(self.button_generate_checks)
        self.button_generate_checks.setFixedHeight(
            GuiSettings.single_line_height())
        self.button_generate_checks.setText("Generate")
        self.button_generate_checks.setToolTip(
            'Generate the QA JSON checks based on the selected profile')

        # noinspection PyUnresolvedReferences
        self.button_generate_checks.clicked.connect(self._on_generate_checks)
        hbox.addStretch()

        # add folder
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        text_add_folder = QtWidgets.QLabel("QA JSON:")
        hbox.addWidget(text_add_folder)
        text_add_folder.setMinimumWidth(left_space)
        self.qa_json = QtWidgets.QListWidget()
        hbox.addWidget(self.qa_json)
        self.qa_json.setFixedHeight(GuiSettings.single_line_height())
        # self.qa_json.setMinimumHeight(GuiSettings.single_line_height())
        # self.qa_json.setMaximumHeight(GuiSettings.single_line_height() * 2)
        self.qa_json.clear()
        self.qa_json.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)
        self.qa_json.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # noinspection PyUnresolvedReferences
        self.qa_json.customContextMenuRequested.connect(
            self.make_json_context_menu)
        # Enable dropping onto the input ss list
        self.qa_json.setAcceptDrops(True)
        self.qa_json.installEventFilter(self)
        button_add_json = QtWidgets.QPushButton()
        hbox.addWidget(button_add_json)
        button_add_json.setFixedHeight(GuiSettings.single_line_height())
        button_add_json.setFixedWidth(GuiSettings.single_line_height())
        button_add_json.setText(" .. ")
        button_add_json.setToolTip('Add (or drag-and-drop) QA JSON')
        # noinspection PyUnresolvedReferences
        button_add_json.clicked.connect(self.click_add_json)

        self.installEventFilter(self)

    def initialize(self):
        self.profile_selection.initialize()

    def _on_profile_selected(self, profile):
        self.selected_profile = profile
        # propogate event up
        self.profile_selected.emit(profile)

    def _on_check_tools_selected(self, check_tools):
        print("Selected check tools")
        print(check_tools)

        self.selected_check_tools = check_tools

        all_file_groups = []
        for check_tool in check_tools:
            check_tool_plugin = QaxPlugins.instance().get_plugin(
                self.selected_profile.name, check_tool.plugin_class)
            file_groups = check_tool_plugin.get_file_groups()
            all_file_groups.extend(file_groups)
        unique_file_groups = QaxFileGroup.merge(all_file_groups)

        if self.file_group_selection is not None:
            # it may be None during initialisation
            self.file_group_selection.update_file_groups(
                unique_file_groups)

    def _on_file_group_files_added(self, file_group):
        print("files added to: {}".format(file_group.name))

        # todo: call interaction functions such as `raw_loaded` based on
        # what check has had files selected

    def _on_file_group_files_removed(self, file_group):
        print("files removed from: {}".format(file_group.name))

        # todo: call interaction functions such as `raw_unloaded` based on
        # what check has had files cleared from

    def eventFilter(self, obj, e):

        # drag events
        if (e.type() == QtCore.QEvent.DragEnter) or (e.type() == QtCore.QEvent.DragMove):

            if obj in (self.output_folder,):

                if e.mimeData().hasUrls:

                    for url in e.mimeData().urls():

                        if Helper.is_darwin():
                            dropped_path = str(NSURL.URLWithString_(str(url.toString())).filePathURL().path())

                        else:
                            dropped_path = str(url.toLocalFile())

                        dropped_path = os.path.abspath(dropped_path)

                        if os.path.isdir(dropped_path):
                            e.accept()
                            return True

            elif obj in (self.qa_json,):

                if e.mimeData().hasUrls:

                    for url in e.mimeData().urls():

                        if Helper.is_darwin():
                            dropping_file = str(NSURL.URLWithString_(str(url.toString())).filePathURL().path())

                        else:
                            dropping_file = str(url.toLocalFile())

                        if os.path.splitext(dropping_file)[-1].lower() in (".json", ):
                            e.accept()
                            return True

            e.ignore()
            return True

        # drop events
        if e.type() == QtCore.QEvent.Drop:

            if obj is self.output_folder:

                if e.mimeData().hasUrls():

                    e.setDropAction(QtCore.Qt.CopyAction)
                    e.accept()
                    # Workaround for OSx dragging and dropping
                    for url in e.mimeData().urls():

                        if Helper.is_darwin():
                            dropped_path = str(NSURL.URLWithString_(str(url.toString())).filePathURL().path())

                        else:
                            dropped_path = str(url.toLocalFile())

                        dropped_path = os.path.abspath(dropped_path)

                        logger.debug("dropped file: %s" % dropped_path)
                        if os.path.isdir(dropped_path):
                            self._add_folder(selection=dropped_path)

                        else:
                            msg = 'Drag-and-drop is only possible with a single folder\n'
                            # noinspection PyCallByClass,PyArgumentList
                            QtWidgets.QMessageBox.critical(self, "Drag-and-drop Error", msg, QtWidgets.QMessageBox.Ok)

                    return True

            elif obj is self.qa_json:

                if e.mimeData().hasUrls():

                    e.setDropAction(QtCore.Qt.CopyAction)
                    e.accept()
                    # Workaround for OSx dragging and dropping
                    for url in e.mimeData().urls():
                        if Helper.is_darwin():
                            dropped_file = str(NSURL.URLWithString_(str(url.toString())).filePathURL().path())
                        else:
                            dropped_file = str(url.toLocalFile())

                        logger.debug("dropped file: %s" % dropped_file)
                        if os.path.splitext(dropped_file)[-1] in (".json",):
                            self._add_json(selection=dropped_file)
                        else:
                            msg = 'Drag-and-drop is only possible with the following file extensions:\n' \
                                  '- QA JSON Files: .json\n\n' \
                                  'Dropped file:\n' \
                                  '%s' % dropped_file
                            # noinspection PyCallByClass,PyArgumentList
                            QtWidgets.QMessageBox.critical(self, "Drag-and-drop Error", msg, QtWidgets.QMessageBox.Ok)
                    return True

            e.ignore()
            return True

        return QtWidgets.QMainWindow.eventFilter(self, obj, e)

    def click_output_project_folder(self):
        """ Set the output project folder"""
        self.prj.create_project_folder = self.output_prj_folder.isChecked()
        QtCore.QSettings().setValue(
            "qax_export_project_folder", self.prj.create_project_folder)

    def click_output_subfolders(self):
        """ Set the output in sub-folders"""
        self.prj.per_tool_folders = self.output_subfolders.isChecked()
        QtCore.QSettings().setValue(
            "qax_export_subfolders", self.prj.per_tool_folders)

    def click_add_folder(self):
        """ Read the grids provided by the user"""
        logger.debug('set output folder ...')

        # ask the output folder
        # noinspection PyCallByClass
        selection = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Set output folder",
            QtCore.QSettings().value("qa_export_folder"),)
        if selection == "":
            logger.debug('setting output folder: aborted')
            return
        logger.debug("selected path: %s" % selection)

        self._add_folder(selection)

    def _add_folder(self, selection):

        path_len = len(selection)
        logger.debug("folder path length: %d" % path_len)
        if path_len > 140:

            msg = 'The selected path is %d characters long. ' \
                  'This may trigger the filename truncation of generated outputs (max allowed path length: 260).\n\n' \
                  'Do you really want to use: %s?' % (path_len, selection)
            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setWindowTitle("Output folder")
            msg_box.setText(msg)
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            msg_box.setDefaultButton(QtWidgets.QMessageBox.No)
            reply = msg_box.exec_()

            if reply == QtWidgets.QMessageBox.No:
                return

        try:
            self.prj.output_folder = Path(selection)
        except Exception as e:
            # more general case that catches all the exceptions
            msg = '<b>Error setting the output folder to \"{}\".</b>'.format(
                selection)
            msg += '<br><br><font color=\"red\">%s</font>' % e
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(
                self, "Output Folder Error", msg, QtWidgets.QMessageBox.Ok)
            logger.debug('output folder NOT set: %s' % selection)
            return

        self.output_folder.clear()
        new_item = QtWidgets.QListWidgetItem()
        new_item.setIcon(
            QtGui.QIcon(os.path.join(self.parent_win.media, 'folder.png')))
        new_item.setText("{}".format(self.prj.output_folder))
        new_item.setFont(GuiSettings.console_font())
        new_item.setForeground(GuiSettings.console_fg_color())
        self.output_folder.addItem(new_item)

        QtCore.QSettings().setValue(
            "qax_export_folder", self.prj.output_folder)

        logger.debug("new output folder: {}".format(self.prj.output_folder))

    def click_default_output(self):
        """ Set default output data folder """
        self.prj.output_folder = self.prj.default_output_folder()
        self._add_folder(selection=self.prj.output_folder)

    def click_open_output(self):
        """ Open output data folder """
        logger.debug('open output folder: {}'.format(self.prj.output_folder))
        self.prj.open_output_folder()

    def _on_generate_checks(self):
        """ Read the feature files provided by the user"""
        logger.debug('generate checks ...')
        self.generate_checks.emit(Path(""))

    def click_add_json(self):
        """ Read the feature files provided by the user"""
        logger.debug('adding feature files ...')

        # ask the file path to the user
        # noinspection PyCallByClass
        selections, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self, "Add QA JSON Files",
            QtCore.QSettings().value("json_import_folder"),
            "QA JSON file (*.json);;All files (*.*)")
        if len(selections) == 0:
            logger.debug('adding json: aborted')
            return
        last_open_folder = os.path.dirname(selections[0])
        if os.path.exists(last_open_folder):
            QtCore.QSettings().setValue("json_import_folder", last_open_folder)

        for selection in selections:
            selection = os.path.abspath(selection).replace("\\", "/")
            self._add_json(selection=selection)

    def _add_json(self, selection):
        self.prj.qa_json_path = Path(selection)

    def _on_qa_json_path_changed(self, new_path: Path):
        self._update_json_list()

    def _update_json_list(self):
        """ update the FF list widget """
        self.qa_json.clear()
        if self.prj.qa_json_path is not None:
            new_item = QtWidgets.QListWidgetItem()
            if self.prj.qa_json_path.suffix == ".json":
                new_item.setIcon(QtGui.QIcon(
                    os.path.join(self.parent_win.media, 'json.png')))
            new_item.setText(str(self.prj.qa_json_path))
            new_item.setFont(GuiSettings.console_font())
            new_item.setForeground(GuiSettings.console_fg_color())
            self.qa_json.addItem(new_item)

    def make_json_context_menu(self, pos):
        logger.debug('JSON context menu')

        remove_act = QtWidgets.QAction(
            "Remove file",
            self,
            statusTip="Remove the JSON file",
            triggered=self.remove_json_file)

        menu = QtWidgets.QMenu(parent=self)
        menu.addAction(remove_act)
        menu.exec_(self.qa_json.mapToGlobal(pos))

    def remove_json_file(self):
        logger.debug("user want to remove JSON file")
        self.prj.qa_json_path = None
