import os
from pathlib import Path
import logging
from PySide2 import QtGui, QtCore, QtWidgets

from hyo2.abc.app.qt_progress import QtProgress
from hyo2.qax.app.widgets.qax.checks_tab import ChecksTab
from hyo2.qax.app.widgets.qax.main_tab import MainTab
from hyo2.qax.app.widgets.qax.plugin_tab import PluginTab
from hyo2.qax.app.widgets.widget import AbstractWidget
from hyo2.qax.app.gui_settings import GuiSettings
from hyo2.qax.lib.project import QAXProject
from hyo2.qax.lib.plugin import QaxPlugins
from hyo2.qax.lib.config import QaxConfig, QaxConfigProfile

logger = logging.getLogger(__name__)


class QAXWidget(AbstractWidget):
    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # overloading

    def __init__(self, main_win):
        AbstractWidget.__init__(self, main_win=main_win)
        self.prj = QAXProject()
        self.prj.params.progress = QtProgress(self)

        # includes only the PluginTab instances, one per plugin
        self.plugin_tabs = []
        self.profile = None  # QaxConfigProfile

        # init default settings
        settings = QtCore.QSettings()
        # - output folder
        export_folder = settings.value("qax_export_folder")
        if (export_folder is None) or (not os.path.exists(export_folder)):
            settings.setValue("qax_export_folder", str(self.prj.outputs.output_folder))
        else:  # folder exists
            self.prj.outputs.output_folder = Path(export_folder)
        # - shp
        export_shp = settings.value("qax_export_shp")
        if export_shp is None:
            settings.setValue("qax_export_shp", self.prj.params.write_shp)
        else:  # exists
            self.prj.params.write_shp = (export_shp == "true")
        # - kml
        export_kml = settings.value("qax_export_kml")
        if export_kml is None:
            settings.setValue("qax_export_kml", self.prj.params.write_kml)
        else:  # exists
            self.prj.params.write_kml = (export_kml == "true")
        # - import
        import_folder = settings.value("ff_import_folder")
        if (import_folder is None) or (not os.path.exists(import_folder)):
            settings.setValue("ff_import_folder", str(self.prj.outputs.output_folder))
        import_folder = settings.value("dtm_import_folder")
        if (import_folder is None) or (not os.path.exists(import_folder)):
            settings.setValue("dtm_import_folder", str(self.prj.outputs.output_folder))
        # - project folder
        export_project_folder = settings.value("qax_export_project_folder")
        if export_project_folder is None:
            settings.setValue("qax_export_project_folder", str(self.prj.params.project_folder))
        else:  # exists
            self.prj.params.project_folder = (export_project_folder == "true")
        # - subfolders
        export_subfolders = settings.value("qax_export_subfolders")
        if export_subfolders is None:
            settings.setValue("qax_export_subfolders", self.prj.params.subfolders)
        else:  # exists
            self.prj.params.subfolders = (export_subfolders == "true")

        # make tabs
        self.tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tabs.setContentsMargins(0, 0, 0, 0)
        self.tabs.setIconSize(QtCore.QSize(36, 36))
        self.tabs.setTabPosition(QtWidgets.QTabWidget.South)
        # main tab
        self.tab_inputs = MainTab(parent_win=self, prj=self.prj)
        self.tab_inputs.profile_selected.connect(self._on_profile_selected)
        # noinspection PyArgumentList
        self.idx_inputs = self.tabs.insertTab(0, self.tab_inputs,
                                              QtGui.QIcon(os.path.join(self.media, 'qax.png')), "")
        self.tabs.setTabToolTip(self.idx_inputs, "QAX")

        # todo: save last selected profile and set here as default.
        self.profile = QaxConfig.instance().profiles[0]
        self.update_plugin_tabs()
        # # Mate tab
        # self.tab_mate = ChecksTab(parent_win=self, prj=self.prj, qa_group="raw_data")
        # # noinspection PyArgumentList
        # self.idx_mate = self.tabs.insertTab(1, self.tab_mate,
        #                                     QtGui.QIcon(os.path.join(self.media, 'mate.png')), "")
        # self.tabs.setTabEnabled(self.idx_mate, False)
        # self.tabs.setTabToolTip(self.idx_mate, "Mate")
        # # QC Tools tab
        # self.tab_qc_tools = ChecksTab(parent_win=self, prj=self.prj, qa_group="survey_products")
        # # noinspection PyArgumentList
        # self.idx_qc_tools = self.tabs.insertTab(2, self.tab_qc_tools,
        #                                         QtGui.QIcon(os.path.join(self.media, 'qc_tools.png')), "")
        # self.tabs.setTabEnabled(self.idx_qc_tools, False)
        # self.tabs.setTabToolTip(self.idx_qc_tools, "QC Tools")
        # # CA Tools tab
        # self.tab_ca_tools = ChecksTab(parent_win=self, prj=self.prj, qa_group="chart_adequacy")
        # # noinspection PyArgumentList
        # self.idx_ca_tools = self.tabs.insertTab(3, self.tab_ca_tools,
        #                                         QtGui.QIcon(os.path.join(self.media, 'ca_tools.png')), "")
        # self.tabs.setTabEnabled(self.idx_ca_tools, False)
        # self.tabs.setTabToolTip(self.idx_ca_tools, "CA Tools")
        # noinspection PyUnresolvedReferences
        self.tabs.currentChanged.connect(self.change_tabs)

    def update_plugin_tabs(self):
        """ Updates what plugins are shown in the bottom tabs
        """
        for plugin_tab in self.plugin_tabs:
            plugin_tab.setParent(None)

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
            self.plugin_tabs.append(plugin_tab)
            icon_path = GuiSettings.icon_path(plugin.icon)
            if icon_path is not None:
                tab_index = self.tabs.addTab(
                    plugin_tab, QtGui.QIcon(icon_path), "")
            else:
                tab_index = self.tabs.addTab(plugin_tab, plugin.name)
            self.tabs.setTabToolTip(tab_index, plugin.name)

    def _on_profile_selected(self, profile: QaxConfigProfile):
        self.profile = profile
        self.update_plugin_tabs()


    def enable_mate(self):
        self.tabs.setTabEnabled(self.idx_mate, True)
        self.tab_mate.display_json()

    def disable_mate(self):
        self.tabs.setTabEnabled(self.idx_mate, False)

    def enable_qc_tools(self):
        self.tabs.setTabEnabled(self.idx_qc_tools, True)
        self.tab_qc_tools.display_json()

    def disable_qc_tools(self):
        self.tabs.setTabEnabled(self.idx_qc_tools, False)

    def enable_ca_tools(self):
        self.tabs.setTabEnabled(self.idx_ca_tools, True)
        self.tab_ca_tools.display_json()

    def disable_ca_tools(self):
        self.tabs.setTabEnabled(self.idx_ca_tools, False)

    def change_tabs(self, index):
        self.tabs.setCurrentIndex(index)
        self.tabs.currentWidget().setFocus()

    def change_info_url(self, url):
        self.main_win.change_info_url(url)
