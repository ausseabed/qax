from ausseabed.qajson.model import QajsonRoot
from pathlib import Path
from PySide2 import QtGui, QtCore, QtWidgets
from typing import Optional, NoReturn, List
import logging
import os

from hyo2.qax.app import qta
from hyo2.abc.app.qt_progress import QtProgress
from hyo2.qax.app.widgets.qax.main_tab import MainTab
from hyo2.qax.app.widgets.qax.plugin_tab import PluginTab
from hyo2.qax.app.widgets.qax.plugins_tab import PluginsTab
from hyo2.qax.app.widgets.qax.result_tab import ResultTab
from hyo2.qax.app.widgets.qax.run_tab import RunTab, QtCheckExecutorThread
from hyo2.qax.app.widgets.widget import AbstractWidget
from hyo2.qax.lib.config import QaxConfig, QaxConfigProfile, QaxConfigSpecification
from hyo2.qax.lib.plugin import QaxPlugins, QaxCheckToolPlugin
from hyo2.qax.lib.project import QAXProject

from ausseabed.qajson.parser import QajsonParser
from ausseabed.qajson.model import QajsonRoot, QajsonQa, QajsonDataLevel, \
    QajsonParam, QajsonCheck, QajsonInfo, QajsonGroup, QajsonFile

logger = logging.getLogger(__name__)


class QAXWidget(QtWidgets.QTabWidget):
    # overloading
    here = os.path.abspath(os.path.join(os.path.dirname(__file__)))

    # (message, timeout)
    status_message = QtCore.Signal((str, int))

    def __init__(self, main_win):
        QtWidgets.QTabWidget.__init__(self)
        self.prj = QAXProject()
        self.prj.params.progress = QtProgress(self)

        self.profile = None  # QaxConfigProfile

        # make tabs
        self.tabs = self

        # self.vbox = QtWidgets.QVBoxLayout()
        # self.setLayout(self.vbox)
        # self.vbox.addWidget(self.tabs)
        # self.tabs.setContentsMargins(0, 0, 0, 0)
        self.tabs.setIconSize(QtCore.QSize(72, 72))
        # self.tabs.setTabPosition(QtWidgets.QTabWidget.South)
        # main tab
        self.tab_inputs = MainTab(parent_win=self, prj=self.prj)
        self.tab_inputs.profile_selected.connect(self._on_profile_selected)
        self.tab_inputs.specification_selected.connect(self._on_specification_selected)
        self.tab_inputs.check_inputs_changed.connect(
            self._on_update_check_inputs)
        # noinspection PyArgumentList
        self.idx_inputs = self.tabs.insertTab(
            0, self.tab_inputs,
            qta.icon('fa.files-o'), "")

        self.tabs.setTabToolTip(self.idx_inputs, "QAX")

        self.tab_plugins = PluginsTab(parent_win=self, prj=self.prj)
        self.tab_plugins.plugin_changed.connect(self._on_plugin_changed)
        self.idx_plugins = self.tabs.insertTab(
            1, self.tab_plugins,
            qta.icon('ri.list-check-2'), "")
        self.tabs.setTabToolTip(self.idx_plugins, "Plugins")

        self.tab_run = RunTab(self.prj)
        self.tab_run.objectName = "tab_run"
        self.tab_run.run_checks.connect(self._on_execute_checks)
        self.idx_run = self.tabs.insertTab(
            2, self.tab_run,
            qta.icon('fa.play'), "")
        self.tabs.setTabToolTip(self.idx_run, "Run Checks")

        self.tab_result = ResultTab(self.prj)
        self.tab_result.objectName = "tab_result"
        self.idx_result = self.tabs.insertTab(
            3, self.tab_result,
            qta.icon('fa.check'), "")
        self.tabs.setTabToolTip(self.idx_result, "View check results")

        self.tabs.currentChanged.connect(self.change_tabs)

    def initialize(self):
        # set initial profile, this may be replaced when the tab_inputs is initialised
        # as that is where the config file is loaded and we read the selected profile
        # info from the ast QAX session
        self.profile = QaxConfig.instance().profiles[0]
        self.tab_plugins.set_profile(self.profile)

        self.tab_inputs.initialize()
        self.status_message.emit("Initialised", 1000)

    def _on_plugin_changed(self, plugin: QaxCheckToolPlugin):
        qa_json = self._build_qa_json()
        self.prj.qa_json = qa_json

    def _on_profile_selected(self, profile: QaxConfigProfile):
        self.profile = profile
        self.tab_plugins.set_profile(self.profile)

    def _on_specification_selected(self, specification: QaxConfigSpecification):
        self.tab_plugins.set_specification(specification)
        qa_json = self._build_qa_json()
        self.prj.qa_json = qa_json

        self.status_message.emit(f"Parameter values updated to {specification.name} Standard", 2000)

    def _on_update_check_inputs(self):
        """ Read the feature files provided by the user"""
        qa_json = self._build_qa_json()
        self.prj.qa_json = qa_json

    # QA JSON methods
    def _build_qa_json(self) -> QajsonRoot:
        """
        Builds a QA JSON root object based on the information currently
        entered into the user interface.
        """
        root = QajsonRoot(None)

        # assume schema naming convention is
        #  `some_path/v0.1.2/qa.schema.json` or similar
        last_path = QajsonParser.schema_paths()[-1]
        version = last_path.parent.name[1:]
        root.qa = QajsonQa(
            version=version,
            raw_data=None,
            survey_products=None,
        )
        root.qa.get_or_add_data_level('raw_data')
        root.qa.get_or_add_data_level('survey_products')

        grouped_files = self.tab_inputs.file_group2_selection.get_grouped_files()
        for file_group_list in grouped_files:
            # the plugin function we use to check if the group of files is suitable
            # for a specific check uses a simple tuple list (not a list of QajsonFiles)
            # so we need to convert this
            paths_and_types = [(Path(f.path), f.file_type) for f in file_group_list]

            for config_check_tool in self.tab_inputs.selected_check_tools:
                plugin_check_tool = QaxPlugins.instance().get_plugin(
                    self.profile.name,
                    config_check_tool.plugin_class
                )

                for check in plugin_check_tool.checks():
                    if check.supports_files(paths_and_types):
                        data_level = root.qa.get_or_add_data_level(check.data_level)
                        qajson_check = plugin_check_tool.add_check(data_level, check)
                        qajson_inputs = qajson_check.get_or_add_inputs()
                        qajson_inputs.files.extend(file_group_list)

        # update the qajson object with the check tool details
        for config_check_tool in self.tab_inputs.selected_check_tools:
            plugin_check_tool = QaxPlugins.instance().get_plugin(
                self.profile.name, config_check_tool.plugin_class)
            if plugin_check_tool is None:
                # then the qajson includes a check tool that isn't available within
                # the current profile
                continue
            # # update the `root` qa json object with the selected checks
            # plugin_check_tool.update_qa_json(root)

            # # get a list of user selected files from the relevant controls
            # # for this plugin (based on the file groups)
            # file_groups = plugin_check_tool.get_file_groups()
            # all_files = self.tab_inputs.file_group_selection.get_files(
            #     file_groups)
            # # update the `root` qa json object with files selected by the
            # # user
            # plugin_check_tool.update_qa_json_input_files(root, all_files)

            # get the plugin tab for the current check tool
            plugin_tab = next(
                (
                    ptab
                    for ptab in self.tab_plugins.plugin_tabs
                    if ptab.plugin == plugin_check_tool
                ),
                None
            )
            if plugin_tab is None:
                raise RuntimeError(
                    "No plugin tab found for {}".format(
                        config_check_tool.name))
            check_param_details = plugin_tab.get_check_ids_and_params()
            for (check_id, params) in check_param_details:
                plugin_check_tool.update_qa_json_input_params(
                    root, check_id, params)

        return root

    def _on_execute_checks(self):
        """ the run checks """
        logger.debug('executing checks ...')
        qa_json = self._build_qa_json()

        # only the selected ones
        check_tool_plugin_class_names = [
            config_check_tool.plugin_class
            for config_check_tool in self.tab_inputs.selected_check_tools
        ]

        executor = QtCheckExecutorThread(
            qa_json,
            self.profile.name,
            check_tool_plugin_class_names)
        self.tab_run.run_executor(executor)

    def change_tabs(self, index):
        self.tabs.setCurrentIndex(index)
        self.tabs.currentWidget().setFocus()

    def change_info_url(self, url):
        self.main_win.change_info_url(url)

    def update_ui(self, qajson: QajsonRoot) -> NoReturn:
        self.tab_inputs.update_ui(qajson)
        self.tab_plugins.update_ui(qajson)

    def persist_exit_settings(self):
        self.tab_inputs.persist_exit_settings()
