import json
import logging
import os
from pathlib import Path
from PySide2 import QtCore, QtGui, QtWidgets
from hyo2.abc.lib.helper import Helper

logger = logging.getLogger(__name__)


class ChecksTab(QtWidgets.QWidget):

    here = os.path.abspath(os.path.dirname(__file__))

    def __init__(self, parent_win, prj, qa_group: str = "survey_products"):
        QtWidgets.QWidget.__init__(self)

        # store a project reference
        self.prj = prj
        self.parent_win = parent_win
        self.media = self.parent_win.media
        self.qa_group = qa_group

        # ui
        self.vbox = QtWidgets.QVBoxLayout()
        self.setLayout(self.vbox)

        self.set_view = None
        self.cur_view = 'Json Text'
        self.force_reload = None
        self.save_as = None
        self.execute_all = None
        self.json_text_group = None
        self.json_viewer = None
        self.score_board_group = None
        self.score_board = None

    def display_json(self):
        logger.debug("displaying js: %s" % self.prj.inputs.qa_json.js)

        self.panel.deleteLater()
        self.vbox.deleteLater()

        button_width = 120

        # ui
        self.panel = QtWidgets.QFrame()
        self.setCentralWidget(self.panel)
        self.vbox = QtWidgets.QVBoxLayout()
        self.panel.setLayout(self.vbox)

        hbox = QtWidgets.QHBoxLayout()
        self.vbox.addLayout(hbox)
        hbox.addStretch()
        self.set_view = QtWidgets.QComboBox()
        self.set_view.addItems(['Json Text', 'Score Board'])
        self.set_view.setCurrentText(self.cur_view)
        # noinspection PyUnresolvedReferences
        self.set_view.currentTextChanged.connect(self.on_set_view)
        hbox.addWidget(self.set_view)
        hbox.setSpacing(16)
        self.force_reload = QtWidgets.QPushButton()
        self.force_reload.setFixedWidth(button_width)
        self.force_reload.setText("Reload")
        # noinspection PyUnresolvedReferences
        self.force_reload.clicked.connect(self.on_force_reload)
        hbox.addWidget(self.force_reload)
        self.save_as = QtWidgets.QPushButton()
        self.save_as.setFixedWidth(button_width)
        self.save_as.setText("Save as")
        # noinspection PyUnresolvedReferences
        self.save_as.clicked.connect(self.on_save_as)
        hbox.addWidget(self.save_as)
        self.execute_all = QtWidgets.QPushButton()
        self.execute_all.setFixedWidth(button_width)
        self.execute_all.setText("Run all")
        # noinspection PyUnresolvedReferences
        self.execute_all.clicked.connect(self.on_execute_all)
        hbox.addWidget(self.execute_all)
        hbox.addStretch()

        # Json Text
        self.json_text_group = QtWidgets.QGroupBox("Json Text")
        self.json_text_group.setHidden(True)
        self.vbox.addWidget(self.json_text_group)
        vbox = QtWidgets.QVBoxLayout()
        self.json_text_group.setLayout(vbox)
        self.json_viewer = QtWidgets.QTextEdit()
        self.json_viewer.setText(json.dumps(self.prj.inputs.qa_json.js['qa'][self.qa_group], indent=4))
        self.json_viewer.setReadOnly(True)
        vbox.addWidget(self.json_viewer)

        # Score Board
        self.score_board_group = QtWidgets.QGroupBox("Score Board")
        self.score_board_group.setHidden(True)
        self.vbox.addWidget(self.score_board_group)
        vbox = QtWidgets.QVBoxLayout()
        self.score_board_group.setLayout(vbox)
        self.score_board = QtWidgets.QTableWidget()
        self.score_board.setSortingEnabled(True)
        self.score_board.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.score_board.setFocus()
        self.score_board.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.score_board.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.score_board.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # noinspection PyUnresolvedReferences
        self.score_board.customContextMenuRequested.connect(self.make_context_menu)
        # noinspection PyUnresolvedReferences
        self.score_board.itemDoubleClicked.connect(self.load_check)
        self.score_board.setColumnCount(7)
        self.score_board.setHorizontalHeaderLabels(["ID", "Check", "Group", "Input", "Output", "Status", "Action"])
        checks = self.prj.inputs.qa_json.js['qa'][self.qa_group]['checks']
        logger.debug("checks: %s" % checks)
        nr_of_checks = len(checks)
        self.score_board.setRowCount(nr_of_checks)
        for idx in range(nr_of_checks):
            item0 = QtWidgets.QTableWidgetItem(checks[idx]['info']['id'])
            self.score_board.setItem(idx, 0, item0)
            item1 = QtWidgets.QTableWidgetItem("%s [v.%s]" % (checks[idx]['info']['name'], checks[idx]['info']['version']))
            self.score_board.setItem(idx, 1, item1)
            item2 = QtWidgets.QTableWidgetItem(checks[idx]['info']['group']['name'])
            self.score_board.setItem(idx, 2, item2)
            item3 = QtWidgets.QTableWidgetItem(checks[idx]['inputs']['files'][0]['path'])
            self.score_board.setItem(idx, 3, item3)
            output_txt = str()
            has_count = False
            # has_percentage = False
            try:
                count_txt = "count: %d" % checks[idx]['outputs']['count']
                has_count = True
                output_txt += count_txt
            except KeyError as e:
                logger.debug("skipping count for #%d: %s" % (idx, e))
            try:
                percentage_txt = "percentage: %.2f" % checks[idx]['outputs']['percentage']
                # has_percentage = True
                if has_count:
                    output_txt += ", "
                output_txt += percentage_txt
            except KeyError as e:
                logger.debug("skipping grade for #%d: %s" % (idx, e))
            item4 = QtWidgets.QTableWidgetItem(output_txt)
            self.score_board.setItem(idx, 4, item4)
            try:
                status = checks[idx]['outputs']['execution']['status']
                item5 = QtWidgets.QTableWidgetItem(status)
                if status in ["aborted", "failed"]:
                    item5.setBackground(QtGui.QColor(200, 100, 100, 50))
                elif status in ["draft", "queued", "running"]:
                    item5.setBackground(QtGui.QColor(200, 200, 100, 50))
                else:
                    item5.setBackground(QtGui.QColor(100, 200, 100, 50))
                self.score_board.setItem(idx, 5, item5)
            except KeyError as e:
                logger.debug("skipping grade for #%d: %s" % (idx, e))
            try:
                item6 = QtWidgets.QPushButton('Run')
                # noinspection PyUnresolvedReferences
                item6.clicked.connect(self.on_button_clicked)
                self.score_board.setCellWidget(idx, 6, item6)
            except KeyError as e:
                logger.debug("skipping grade for #%d: %s" % (idx, e))

        vbox.addWidget(self.score_board)

        self.on_set_view()

    def on_button_clicked(self):
        button = QtGui.qApp.focusWidget()
        index = self.score_board.indexAt(button.pos())
        if index.isValid():
            logger.debug("(%s, %s)" % index.row(), index.column())

    def on_set_view(self):
        self.cur_view = self.set_view.currentText()
        logger.debug("selected view: %s" % self.cur_view)

        if self.cur_view == "Json Text":
            self.json_text_group.setVisible(True)
            self.score_board_group.setHidden(True)

        elif self.cur_view == "Score Board":
            self.json_text_group.setHidden(True)
            self.score_board_group.setVisible(True)

    def on_force_reload(self):
        logger.debug("force reload")
        self.display_json()

    def load_check(self):
        logger.debug("load check")

    def make_context_menu(self, pos):
        """Make a context menu to deal with profile specific actions"""

        # check if any selection
        rows = self.score_board.selectionModel().selectedRows()
        if len(rows) == 0:
            logger.debug('Not check selected')
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.information(self, "Check", "You need to select a check before loading it!")
            return

        menu = QtWidgets.QMenu(parent=self)

        if len(rows) == 1:
            logger.debug('Single check selected')

        else:
            logger.debug('Multiple checks selected')

        delete_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'delete.png')),
                                       "Delete checks", self, toolTip="Delete selected checks",
                                       triggered=self.delete_checks)
        # noinspection PyArgumentList
        menu.addAction(delete_act)

        # # single selection
        # if len(rows) == 1:
        #
        #     map_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'map.png')),
        #                                 "Show map", self, toolTip="Show a map with the profile location",
        #                                 triggered=self.show_map_for_selected)
        #     menu.addAction(map_act)
        #
        #     stats_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'stats.png')),
        #                                   "Profile stats", self, toolTip="Get some statistical info about the profile",
        #                                   triggered=self.stats_profile)
        #     menu.addAction(stats_act)
        #
        #     metadata_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'metadata_profile.png')),
        #                                      "Metadata info", self, toolTip="View/edit the profile metadata",
        #                                      triggered=self.metadata_profile)
        #     menu.addAction(metadata_act)
        #
        #     menu.addMenu(qa_menu)
        #     dqa_compare_ref_act = QtWidgets.QAction("DQA (with reference)", self,
        #                                             toolTip="Assess data quality by comparison with the reference cast",
        #                                             triggered=self.dqa_full_profile)
        #     qa_menu.addAction(dqa_compare_ref_act)
        #     dqa_at_surface_act = QtWidgets.QAction("DQA (at surface)", self, toolTip="DQA with surface sound speed",
        #                                            triggered=self.dqa_at_surface)
        #     qa_menu.addAction(dqa_at_surface_act)
        #
        #     menu.addSeparator()
        #
        #     load_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'load_profile.png')),
        #                                  "Load profile", self, toolTip="Load a profile", triggered=self.load_profile)
        #     menu.addAction(load_act)
        #
        #     export_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'export_profile.png')),
        #                                    "Export profile", self, toolTip="Export a single profile",
        #                                    triggered=self.export_single_profile)
        #     menu.addAction(export_act)
        #
        #     delete_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'delete.png')),
        #                                    "Delete profile", self, toolTip="Delete selected profile",
        #                                    triggered=self.delete_profile)
        #     menu.addAction(delete_act)
        #
        #     def handle_menu_hovered(action):
        #         # noinspection PyArgumentList
        #         QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), action.toolTip(), menu, menu.actionGeometry(action))
        #
        #     # noinspection PyUnresolvedReferences
        #     menu.hovered.connect(handle_menu_hovered)
        #
        # else:  # multiple selection
        #
        #     map_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'map.png')),
        #                                 "Show map", self, toolTip="Show a map with profiles location",
        #                                 triggered=self.show_map_for_selected)
        #     menu.addAction(map_act)
        #
        #     metadata_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'metadata_profile.png')),
        #                                      "Edit metadata",
        #                                      self, toolTip="Edit common metadata fields for multiple profiles",
        #                                      triggered=self.metadata_profile)
        #     menu.addAction(metadata_act)
        #
        #     if len(rows) == 2:
        #         ray_tracing_comparison_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media,
        #                                                                                 'raytracing_comparison.png')),
        #                                                        "Ray-tracing comparison", self,
        #                                                        toolTip="Compare ray-tracing using the selected pair",
        #                                                        triggered=self.ray_tracing_comparison)
        #         menu.addAction(ray_tracing_comparison_act)
        #
        #         bias_plots_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'bias_plots.png')),
        #                                            "Across-swath bias", self,
        #                                            toolTip="Create depth and horizontal bias plots across the swath",
        #                                            triggered=self.bias_plots)
        #         menu.addAction(bias_plots_act)
        #
        #     menu.addMenu(qa_menu)
        #     if len(rows) == 2:
        #         dqa_compare_two_act = QtWidgets.QAction("DQA (among selections)", self,
        #                                                 toolTip="Assess data quality by comparison between two casts",
        #                                                 triggered=self.dqa_full_profile)
        #         qa_menu.addAction(dqa_compare_two_act)
        #
        #     dqa_at_surface_act = QtWidgets.QAction("DQA (at surface)", self, toolTip="DQA with surface sound speed",
        #                                            triggered=self.dqa_at_surface)
        #     qa_menu.addAction(dqa_at_surface_act)
        #
        #     plot_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'plot_comparison.png')),
        #                                  "Comparison plot", self, toolTip="Plot profiles for comparison",
        #                                  triggered=self.plot_comparison)
        #     menu.addAction(plot_act)
        #
        #     menu.addSeparator()
        #
        #     export_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'export_profile.png')),
        #                                    "Export profiles", self, toolTip="Export multiple profiles",
        #                                    triggered=self.export_multi_profile)
        #     menu.addAction(export_act)
        #
        #     delete_act = QtWidgets.QAction(QtGui.QIcon(os.path.join(self.media, 'delete.png')),
        #                                    "Delete profiles", self, toolTip="Delete selected profiles",
        #                                    triggered=self.delete_profile)
        #     menu.addAction(delete_act)
        #
        #     def handle_menu_hovered(action):
        #         # noinspection PyArgumentList
        #         QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), action.toolTip(), menu, menu.actionGeometry(action))
        #
        #     # noinspection PyUnresolvedReferences
        #     menu.hovered.connect(handle_menu_hovered)

        # noinspection PyArgumentList
        menu.exec_(self.score_board.mapToGlobal(pos))

    def delete_checks(self):
        logger.debug("delete checks")
        indices = self.score_board.selectionModel().selectedRows()
        for index in indices:
            row_id = self.score_board.item(index.row(), 0).text()
            logger.debug("row: %s" % row_id)
            for ck in self.prj.inputs.qa_json.js['qa'][self.qa_group]['checks']:
                if row_id == ck['info']['id']:
                    logger.info("removing %s" % row_id)
                    self.prj.inputs.qa_json.js['qa'][self.qa_group]['checks'].remove(ck)
                    self.on_force_reload()
                    break

    def on_save_as(self):
        logger.debug("save as")

        output_folder = GuiSettings.settings().value("json_export_folder")
        if output_folder is None:
            output_folder = self.prj.outputs.output_folder
        else:
            output_folder = Path(output_folder)

        output_path = output_folder.joinpath(self.prj.inputs.qa_json.path.name)
        # noinspection PyCallByClass
        selection, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save file", str(output_path),
                                                             "QA JSON file (*.json);;All files (*.*)", "")
        if selection == "":
            logger.debug('save file: aborted')
            return

        output_path = Path(selection)
        output_folder = output_path.parent
        GuiSettings.settings().setValue("json_export_folder", str(output_folder))

        self.prj.save_cur_json(path=output_path)
        self.on_force_reload()

    def on_execute_all(self):
        logger.debug("execute all")

        self.prj.execute_all(self.qa_group)
        self.on_force_reload()
