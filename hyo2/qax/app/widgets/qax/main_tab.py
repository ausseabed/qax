from ausseabed.qajson.model import QajsonRoot
from hyo2.abc.lib.helper import Helper
from pathlib import Path
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QSizePolicy
from typing import Optional, NoReturn, List
import logging
import os

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


class MainTab(QtWidgets.QWidget):

    here = os.path.abspath(os.path.dirname(__file__))

    profile_selected = QtCore.Signal(QaxConfigProfile)
    generate_checks = QtCore.Signal(Path)

    def __init__(self, parent_win, prj):
        QtWidgets.QWidget.__init__(self)

        # store a project reference
        self.prj = prj
        self.prj.qa_json_path_changed.connect(self._on_qa_json_path_changed)
        self.parent_win = parent_win

        self.selected_profile = None
        self.selected_check_tools = []

        # ui
        self.vbox = QtWidgets.QVBoxLayout()
        self.setLayout(self.vbox)

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
        self.file_group_selection.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.vbox.addWidget(self.file_group_selection)

        self._on_check_tools_selected(
            self.profile_selection.selected_check_tools())
        self.file_group_selection.files_added.connect(
            self._on_file_group_files_added)
        self.file_group_selection.files_removed.connect(
            self._on_file_group_files_removed)

    def initialize(self):
        self.profile_selection.initialize()

    def _on_profile_selected(self, profile):
        self.selected_profile = profile
        # propogate event up
        self.profile_selected.emit(profile)

    def _on_check_tools_selected(self, check_tools):
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

    def _on_qa_json_path_changed(self, new_path: Path):
        print("_update_json_list")
        print(new_path)

    def update_ui(self, qajson: QajsonRoot) -> NoReturn:
        self.profile_selection.update_ui(qajson)
        self.file_group_selection.update_ui(qajson)
