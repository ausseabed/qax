import os
from pathlib import Path
import logging
from PySide2 import QtGui, QtCore, QtWidgets

from hyo2.abc.app.qt_progress import QtProgress
from hyo2.qax.app.widgets.widget import AbstractWidget
from hyo2.qax.lib.project import QAXProject
from hyo2.qax.app.widgets.qax.main_tab import MainTab
from hyo2.qax.app.widgets.qax.mate_tab import MateTab
from hyo2.qax.app.widgets.qax.qc_tools_tab import QCToolsTab
from hyo2.qax.app.widgets.qax.ca_tools_tab import CAToolsTab

logger = logging.getLogger(__name__)


class QAXWidget(AbstractWidget):
    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))  # overloading

    def __init__(self, main_win):
        AbstractWidget.__init__(self, main_win=main_win)
        self.prj = QAXProject()
        self.prj.params.progress = QtProgress(self)

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
        # noinspection PyArgumentList
        self.idx_inputs = self.tabs.insertTab(0, self.tab_inputs,
                                              QtGui.QIcon(os.path.join(self.media, 'qax.png')), "")
        self.tabs.setTabToolTip(self.idx_inputs, "QAX")
        # Mate tab
        self.tab_mate = MateTab(parent_win=self, prj=self.prj)
        # noinspection PyArgumentList
        self.idx_mate = self.tabs.insertTab(1, self.tab_mate,
                                            QtGui.QIcon(os.path.join(self.media, 'mate.png')), "")
        self.tabs.setTabEnabled(self.idx_mate, False)
        self.tabs.setTabToolTip(self.idx_mate, "Mate")
        # QC Tools tab
        self.tab_qc_tools = QCToolsTab(parent_win=self, prj=self.prj)
        # noinspection PyArgumentList
        self.idx_qc_tools = self.tabs.insertTab(2, self.tab_qc_tools,
                                                QtGui.QIcon(os.path.join(self.media, 'qc_tools.png')), "")
        self.tabs.setTabEnabled(self.idx_qc_tools, False)
        self.tabs.setTabToolTip(self.idx_qc_tools, "QC Tools")
        # CA Tools tab
        self.tab_ca_tools = CAToolsTab(parent_win=self, prj=self.prj)
        # noinspection PyArgumentList
        self.idx_ca_tools = self.tabs.insertTab(3, self.tab_ca_tools,
                                                QtGui.QIcon(os.path.join(self.media, 'ca_tools.png')), "")
        self.tabs.setTabEnabled(self.idx_ca_tools, False)
        self.tabs.setTabToolTip(self.idx_ca_tools, "CA Tools")
        # noinspection PyUnresolvedReferences
        self.tabs.currentChanged.connect(self.change_tabs)

    def enable_mate(self):
        self.tabs.setTabEnabled(self.idx_mate, True)

    def disable_mate(self):
        self.tabs.setTabEnabled(self.idx_mate, False)

    def enable_qc_tools(self):
        self.tabs.setTabEnabled(self.idx_qc_tools, True)
        self.tab_qc_tools.display_json()

    def disable_qc_tools(self):
        self.tabs.setTabEnabled(self.idx_qc_tools, False)

    def enable_ca_tools(self):
        self.tabs.setTabEnabled(self.idx_ca_tools, True)

    def disable_ca_tools(self):
        self.tabs.setTabEnabled(self.idx_ca_tools, False)

    def change_tabs(self, index):
        self.tabs.setCurrentIndex(index)
        self.tabs.currentWidget().setFocus()

    def change_info_url(self, url):
        self.main_win.change_info_url(url)
