from ausseabed.qajson.model import QajsonRoot
from hyo2.abc.lib.helper import Helper
from pathlib import Path
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QSizePolicy
from typing import Optional, NoReturn, List
import json
import logging
import os

from hyo2.qax.app.gui_settings import GuiSettings
from hyo2.qax.app.widgets.qax.check_widget import CheckWidget
from hyo2.qax.app.widgets.qax.plugin_tab import PluginTab
from hyo2.qax.lib.plugin import QaxCheckToolPlugin
from hyo2.qax.lib.config import QaxConfig, QaxConfigProfile, QaxConfigSpecification
from hyo2.qax.lib.plugin import QaxPlugins, QaxCheckToolPlugin


logger = logging.getLogger(__name__)


class PluginsTab(QtWidgets.QWidget):

    plugin_changed = QtCore.Signal(QaxCheckToolPlugin)

    def __init__(self, parent_win, prj):
        QtWidgets.QWidget.__init__(self)

        self.prj = prj

        self.vbox = QtWidgets.QVBoxLayout()
        self.setLayout(self.vbox)

        lab = QtWidgets.QLabel("Plugins")
        lab.setStyleSheet(GuiSettings.stylesheet_plugin_tab_titles())
        self.vbox.addWidget(lab)

        self.tabs = QtWidgets.QTabWidget()
        self.vbox.addWidget(self.tabs)

        self.profile = None  # QaxConfigProfile
        # includes only the PluginTab instances, one per plugin
        self.plugin_tabs = []

    def set_profile(self, profile: QaxConfigProfile):
        self.profile = profile
        self.update_plugin_tabs()

    def set_specification(self, specification: QaxConfigSpecification):
        for plugin_tab in self.plugin_tabs:
            plugin_tab.set_specification(specification)

    def update_plugin_tabs(self):
        """ Updates what plugins are shown in the bottom tabs
        """
        for plugin_tab in self.plugin_tabs:
            plugin_tab.setParent(None)
        self.plugin_tabs.clear()

        if self.profile is None:
            return

        # get plugin instances for current profile from singleton
        plugins = (
            QaxPlugins.instance().get_profile_plugins(self.profile)
            .plugins
        )

        for plugin in plugins:
            plugin_tab = PluginTab(
                parent_win=self, prj=self.prj, plugin=plugin)
            plugin_tab.plugin_changed.connect(self._on_plugin_changed)
            self.plugin_tabs.append(plugin_tab)
            icon_path = GuiSettings.icon_path(plugin.icon)
            if icon_path is not None:
                tab_index = self.tabs.addTab(
                    plugin_tab, QtGui.QIcon(icon_path), "")
            else:
                tab_index = self.tabs.addTab(plugin_tab, plugin.name)
            self.tabs.setTabToolTip(tab_index, plugin.name)

    def _on_plugin_changed(self, plugin: QaxCheckToolPlugin):
        self.plugin_changed.emit(plugin)

    def update_ui(self, qajson: QajsonRoot) -> NoReturn:
        for plugin_tab in self.plugin_tabs:
            plugin_tab.update_ui(qajson)
