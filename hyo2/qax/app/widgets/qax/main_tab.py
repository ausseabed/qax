from ausseabed.qajson.model import QajsonRoot
from pathlib import Path
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QSizePolicy
from typing import Optional, NoReturn, List
import logging
import os

from hyo2.qax.app.widgets.qax.profile_groupbox import ProfileGroupBox
from hyo2.qax.app.widgets.qax.filegroup_groupbox \
    import FileGroupGroupBox
from hyo2.qax.lib.config import QaxConfig, QaxConfigProfile, QaxConfigSpecification
from hyo2.qax.lib.plugin import QaxPlugins, QaxFileGroup, QaxCheckToolPlugin
from hyo2.qax.lib.plugin_service import PluginService


logger = logging.getLogger(__name__)


class MainTab(QtWidgets.QWidget):

    here = os.path.abspath(os.path.dirname(__file__))

    profile_selected = QtCore.Signal(QaxConfigProfile)
    specification_selected = QtCore.Signal(QaxConfigSpecification)
    check_inputs_changed = QtCore.Signal()

    def __init__(self, parent_win, prj):
        QtWidgets.QWidget.__init__(self)

        # store a project reference
        self.prj = prj
        self.parent_win = parent_win

        self.selected_check_tools = []

        # ui
        self.vbox = QtWidgets.QVBoxLayout()
        self.setLayout(self.vbox)

        # Include widget for selecting profile and check tools to run
        self.profile_selection = ProfileGroupBox(
            self, self.prj, QaxConfig.instance())
        self.profile_selection.profile_selected.connect(
            self._on_profile_selected)
        self.profile_selection.specification_selected.connect(
            self._on_specification_selected)
        self.profile_selection.check_tool_selection_change.connect(
            self._on_check_tools_selected)
        self.vbox.addWidget(self.profile_selection)

        self.file_group_selection = FileGroupGroupBox(self, self.prj)
        self.file_group_selection.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.vbox.addWidget(self.file_group_selection)

        self._on_check_tools_selected(
            self.profile_selection.selected_check_tools())
        self.file_group_selection.filenames_added.connect(
            self._on_file_group_files_changed)
        self.file_group_selection.filenames_removed.connect(
            self._on_file_group_files_changed)
        self.file_group_selection.dataset_changed.connect(
            self._on_file_group_files_changed)
        self.file_group_selection.filetype_changed.connect(
            self._on_file_group_files_changed)

    def initialize(self):
        self.profile_selection.initialize()

    def _on_profile_selected(self, profile):
        self.prj.profile = profile
        # propogate event up
        self.profile_selected.emit(profile)
        self.check_inputs_changed.emit()

    def _on_specification_selected(self, specification: QaxConfigSpecification):
        # propogate event up
        self.specification_selected.emit(specification)

    def _on_check_tools_selected(self, check_tools):
        self.selected_check_tools = check_tools

        plugins: list[QaxCheckToolPlugin] = []
        for check_tool in check_tools:
            check_tool_plugin = QaxPlugins.instance().get_plugin(
                self.prj.profile.name, check_tool.plugin_class)

            plugins.append(check_tool_plugin)
        self.file_group_selection.set_plugin_service(PluginService(plugins))

        self.check_inputs_changed.emit()

    def _on_file_group_files_added(self, file_group):
        self.check_inputs_changed.emit()

    def _on_file_group_files_changed(self):
        self.check_inputs_changed.emit()

    def _on_file_group_files_removed(self, file_group):
        self.check_inputs_changed.emit()

    def update_ui(self, qajson: QajsonRoot) -> NoReturn:
        self.profile_selection.update_ui(qajson)
        self.file_group_selection.update_ui(qajson)

    def persist_exit_settings(self):
        self.profile_selection.persist_exit_settings()
