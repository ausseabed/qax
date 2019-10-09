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

    def __init__(self, parent_win, prj):
        QtWidgets.QMainWindow.__init__(self)

        # store a project reference
        self.prj = prj
        self.parent_win = parent_win
        self.media = self.parent_win.media

        # aux variables
        self.has_raw = False
        self.has_dtm = False
        self.has_ff = False
        self.has_enc = False
        self.has_json = False

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
        self.savedData = QtWidgets.QGroupBox("Data outputs [drap-and-drop the desired output folder]")
        self.savedData.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        self.savedData.setMaximumHeight(GuiSettings.single_line_height() * 8)
        self.vbox.addWidget(self.savedData)

        vbox = QtWidgets.QVBoxLayout()
        self.savedData.setLayout(vbox)

        # set optional formats
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        text_set_formats = QtWidgets.QLabel("Formats:")
        hbox.addWidget(text_set_formats)
        text_set_formats.setFixedHeight(GuiSettings.single_line_height())
        text_set_formats.setMinimumWidth(left_space)
        self.output_pdf = QtWidgets.QCheckBox("PDF")
        self.output_pdf.setChecked(True)
        self.output_pdf.setDisabled(True)
        hbox.addWidget(self.output_pdf)
        self.output_s57 = QtWidgets.QCheckBox("S57")
        self.output_s57.setChecked(True)
        self.output_s57.setDisabled(True)
        hbox.addWidget(self.output_s57)
        self.output_shp = QtWidgets.QCheckBox("Shapefile")
        self.output_shp.setToolTip('Activate/deactivate the creation of Shapefiles in output')
        self.output_shp.setChecked(self.prj.params.write_shp)
        # noinspection PyUnresolvedReferences
        self.output_shp.clicked.connect(self.click_output_shp)
        hbox.addWidget(self.output_shp)
        self.output_kml = QtWidgets.QCheckBox("KML")
        self.output_kml.setToolTip('Activate/deactivate the creation of KML files in output')
        self.output_kml.setChecked(self.prj.params.write_kml)
        # noinspection PyUnresolvedReferences
        self.output_kml.clicked.connect(self.click_output_kml)
        hbox.addWidget(self.output_kml)

        hbox.addSpacing(36)

        text_set_prj_folder = QtWidgets.QLabel("Create project folder: ")
        hbox.addWidget(text_set_prj_folder)
        text_set_prj_folder.setFixedHeight(GuiSettings.single_line_height())
        self.output_prj_folder = QtWidgets.QCheckBox("")
        self.output_prj_folder.setToolTip('Create a sub-folder with project name')
        self.output_prj_folder.setChecked(self.prj.params.project_folder)
        # noinspection PyUnresolvedReferences
        self.output_prj_folder.clicked.connect(self.click_output_project_folder)
        hbox.addWidget(self.output_prj_folder)

        text_set_subfolders = QtWidgets.QLabel("Per-tool sub-folders: ")
        hbox.addWidget(text_set_subfolders)
        text_set_subfolders.setFixedHeight(GuiSettings.single_line_height())
        self.output_subfolders = QtWidgets.QCheckBox("")
        self.output_subfolders.setToolTip('Create a sub-folder for each tool')
        self.output_subfolders.setChecked(self.prj.params.subfolders)
        # noinspection PyUnresolvedReferences
        self.output_subfolders.clicked.connect(self.click_output_subfolders)
        hbox.addWidget(self.output_subfolders)

        hbox.addStretch()

        # add folder
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        text_add_folder = QtWidgets.QLabel("Folder:")
        hbox.addWidget(text_add_folder)
        text_add_folder.setMinimumWidth(left_space)
        self.output_folder = QtWidgets.QListWidget()
        hbox.addWidget(self.output_folder)
        self.output_folder.setMinimumHeight(GuiSettings.single_line_height())
        self.output_folder.setMaximumHeight(GuiSettings.single_line_height() * 2)
        self.output_folder.clear()
        new_item = QtWidgets.QListWidgetItem()
        new_item.setIcon(QtGui.QIcon(os.path.join(self.parent_win.media, 'folder.png')))
        new_item.setText("%s" % self.prj.outputs.output_folder)
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
        self.checksSuite.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        self.checksSuite.setMaximumHeight(GuiSettings.single_line_height() * 8)
        self.vbox.addWidget(self.checksSuite)

        vbox = QtWidgets.QVBoxLayout()
        self.checksSuite.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        hbox.addStretch()
        self.button_generate_checks = QtWidgets.QPushButton()
        hbox.addWidget(self.button_generate_checks)
        self.button_generate_checks.setFixedHeight(GuiSettings.single_line_height())
        # button_generate_checks.setFixedWidth(GuiSettings.single_line_height())
        self.button_generate_checks.setText("Generate")
        self.button_generate_checks.setToolTip('Generate the QA JSON checks based on the selected profile')
        self.button_generate_checks.setDisabled(True)
        # noinspection PyUnresolvedReferences
        self.button_generate_checks.clicked.connect(self.click_generate_checks)
        hbox.addStretch()

        # add folder
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        text_add_folder = QtWidgets.QLabel("QA JSON:")
        hbox.addWidget(text_add_folder)
        text_add_folder.setMinimumWidth(left_space)
        self.qa_json = QtWidgets.QListWidget()
        hbox.addWidget(self.qa_json)
        self.qa_json.setMinimumHeight(GuiSettings.single_line_height())
        self.qa_json.setMaximumHeight(GuiSettings.single_line_height() * 2)
        self.qa_json.clear()
        self.qa_json.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.qa_json.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # noinspection PyUnresolvedReferences
        self.qa_json.customContextMenuRequested.connect(self.make_json_context_menu)
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

    def _on_profile_selected(self, profile):
        # propogate event up
        self.profile_selected.emit(profile)

    def _on_check_tools_selected(self, check_tools):
        print("Selected check tools")
        print(check_tools)

        all_file_groups = []
        for check_tool in check_tools:
            check_tool_plugin = QaxPlugins.instance().get_plugin(
                check_tool.plugin_class)
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

    def click_output_kml(self):
        """ Set the KML output"""
        self.prj.params.write_kml = self.output_kml.isChecked()
        QtCore.QSettings().setValue("qax_export_kml", self.prj.params.write_kml)

    def click_output_shp(self):
        """ Set the Shapefile output"""
        self.prj.params.write_shp = self.output_shp.isChecked()
        QtCore.QSettings().setValue("qax_export_shp", self.prj.params.write_shp)

    def click_output_project_folder(self):
        """ Set the output project folder"""
        self.prj.params.project_folder = self.output_prj_folder.isChecked()
        QtCore.QSettings().setValue("qax_export_project_folder", self.prj.params.project_folder)

    def click_output_subfolders(self):
        """ Set the output in sub-folders"""
        self.prj.params.subfolders = self.output_subfolders.isChecked()
        QtCore.QSettings().setValue("qax_export_subfolders", self.prj.params.subfolders)

    def click_add_folder(self):
        """ Read the grids provided by the user"""
        logger.debug('set output folder ...')

        # ask the output folder
        # noinspection PyCallByClass
        selection = QtWidgets.QFileDialog.getExistingDirectory(self, "Set output folder",
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
            self.prj.outputs.output_folder = Path(selection)

        except Exception as e:  # more general case that catches all the exceptions
            msg = '<b>Error setting the output folder to \"%s\".</b>' % selection
            msg += '<br><br><font color=\"red\">%s</font>' % e
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.critical(self, "Output Folder Error", msg, QtWidgets.QMessageBox.Ok)
            logger.debug('output folder NOT set: %s' % selection)
            return

        self.output_folder.clear()
        new_item = QtWidgets.QListWidgetItem()
        new_item.setIcon(QtGui.QIcon(os.path.join(self.parent_win.media, 'folder.png')))
        new_item.setText("%s" % self.prj.outputs.output_folder)
        new_item.setFont(GuiSettings.console_font())
        new_item.setForeground(GuiSettings.console_fg_color())
        self.output_folder.addItem(new_item)

        QtCore.QSettings().setValue("qax_export_folder", self.prj.outputs.output_folder)

        logger.debug("new output folder: %s" % self.prj.outputs.output_folder)

    def click_default_output(self):
        """ Set default output data folder """
        self.prj.outputs.output_folder = self.prj.outputs.default_output_folder()
        self._add_folder(selection=self.prj.outputs.output_folder)

    def click_open_output(self):
        """ Open output data folder """
        logger.debug('open output folder: %s' % self.prj.outputs.output_folder)
        self.prj.outputs.open_output_folder()

    def click_generate_checks(self):
        """ Read the feature files provided by the user"""
        logger.debug('generate checks ...')
        from hyo2.qax.lib.qa_json import QAJson
        self.prj.inputs.json_path = QAJson.example_paths()[-1]
        self._update_json_list()
        self.json_loaded()

    # QA JSON methods

    def click_add_json(self):
        """ Read the feature files provided by the user"""
        logger.debug('adding feature files ...')

        # ask the file path to the user
        # noinspection PyCallByClass
        selections, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Add QA JSON Files",
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

        self.prj.inputs.json_path = selection

        self._update_json_list()
        self.json_loaded()

    def _update_json_list(self):
        """ update the FF list widget """
        self.qa_json.clear()
        if self.prj.inputs.json_path is not None:
            new_item = QtWidgets.QListWidgetItem()
            if os.path.splitext(self.prj.inputs.json_path)[-1] == ".json":
                new_item.setIcon(QtGui.QIcon(os.path.join(self.parent_win.media, 'json.png')))
            new_item.setText(str(self.prj.inputs.json_path))
            new_item.setFont(GuiSettings.console_font())
            new_item.setForeground(GuiSettings.console_fg_color())
            self.qa_json.addItem(new_item)

    def make_json_context_menu(self, pos):
        logger.debug('JSON context menu')

        remove_act = QtWidgets.QAction("Remove file", self, statusTip="Remove the JSON file",
                                       triggered=self.remove_json_file)

        menu = QtWidgets.QMenu(parent=self)
        # noinspection PyArgumentList
        menu.addAction(remove_act)
        # noinspection PyArgumentList
        menu.exec_(self.qa_json.mapToGlobal(pos))

    def remove_json_file(self):
        logger.debug("user want to remove JSON file")

        self.prj.inputs.json_path = None
        self.json_unloaded()
        self._update_json_list()

    # interaction methods

    def raw_loaded(self):
        logger.debug("raw loaded")
        self.has_raw = True
        self.button_generate_checks.setEnabled(True)

    def raw_unloaded(self):
        logger.debug("raw unloaded")
        self.has_raw = False
        if not self.has_ff and not self.has_dtm:
            self.button_generate_checks.setDisabled(True)

    def dtm_loaded(self):
        logger.debug("DTM loaded")
        self.has_dtm = True
        self.button_generate_checks.setEnabled(True)

    def dtm_unloaded(self):
        logger.debug("DTM unloaded")
        self.has_dtm = False
        if not self.has_ff and not self.has_ff:
            self.button_generate_checks.setDisabled(True)

    def ff_loaded(self):
        logger.debug("FF loaded")
        self.has_ff = True
        self.button_generate_checks.setEnabled(True)

    def ff_unloaded(self):
        logger.debug("FF unloaded")
        self.has_ff = False
        if not self.has_raw and not self.has_dtm:
            self.button_generate_checks.setDisabled(True)

    def enc_loaded(self):
        logger.debug("ENC loaded")
        self.has_enc = True

    def enc_unloaded(self):
        logger.debug("ENC unloaded")
        self.has_enc = False

    def json_loaded(self):
        logger.debug("JSON loaded")
        self.has_json = True
        self.parent_win.enable_mate()
        self.parent_win.enable_qc_tools()
        self.parent_win.enable_ca_tools()

    def json_unloaded(self):
        logger.debug("JSON unloaded")
        self.has_json = False
        self.parent_win.disable_mate()
        self.parent_win.disable_qc_tools()
        self.parent_win.disable_ca_tools()
