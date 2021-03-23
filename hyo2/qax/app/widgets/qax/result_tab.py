from ausseabed.qajson.model import QajsonRoot
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QSizePolicy
from typing import Optional, NoReturn
import json
import logging
import os
import qtawesome as qta

from hyo2.qax.app.widgets.qax.scoreboard_details import ScoreboardDetailsWidget
from hyo2.qax.app.widgets.qax.summary_details import SummaryDetailsWidget
from hyo2.qax.app.gui_settings import GuiSettings
from hyo2.qax.lib.project import QAXProject

logger = logging.getLogger(__name__)


class ResultTab(QtWidgets.QWidget):
    """ Displays the results of the check execution based on the contents of
    the qajson object.
    """

    color_fail = QtGui.QColor(200, 100, 100, 50)
    color_warning = QtGui.QColor(255, 213, 0, 50)
    color_ok = QtGui.QColor(100, 200, 100, 50)
    color_in_progress = QtGui.QColor(200, 200, 100, 50)

    def __init__(self, prj: QAXProject):
        super(ResultTab, self).__init__()

        self.prj = prj
        self.prj.qa_json_changed.connect(self._on_qa_json_changed)

        self.qa_group = "raw_data"
        self._qa_json = None

        # ui
        self.vbox = QtWidgets.QVBoxLayout()
        self.setLayout(self.vbox)

        self.set_view = None
        self.cur_view = 'Summary'
        self.set_data_level = None
        self.qa_group = None
        self.force_reload = None
        self.execute_all = None
        self.json_text_group = None
        self.json_viewer = None
        self.score_board_widget = None
        self.score_board_group = None
        self.score_board = None
        self.summary_widget = None
        self.summary_group = None
        self.summary_table = None
        self.scoreboard_details = None
        self.scoreboard_selected_check = None

        self.cross_icon = qta.icon('fa.close', color='red')
        self.tick_icon = qta.icon('fa.check', color='green')
        self.warning_icon = qta.icon('fa.warning', color='orange')

        self.view_names = ['Summary', 'Score Board', 'Json Text']

        gb = QtWidgets.QGroupBox('View')
        # gb.setFixedHeight(40)
        hbox = QtWidgets.QHBoxLayout()
        gb.setLayout(hbox)

        hbox_view_and_datalevel = QtWidgets.QHBoxLayout()
        hbox_view_and_datalevel.addWidget(gb)
        self.vbox.addLayout(hbox_view_and_datalevel)

        self.set_view = QtWidgets.QButtonGroup()
        self.set_view.setExclusive(True)
        for idx, view_name in enumerate(self.view_names):
            # viewRadioButton = QtWidgets.QRadioButton(view_name)
            viewRadioButton = QtWidgets.QPushButton(view_name)
            viewRadioButton.setCheckable(True)
            if idx == 0:
                viewRadioButton.setChecked(True)
            viewRadioButton.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Minimum)
            self.set_view.addButton(viewRadioButton, idx)
            hbox.addWidget(viewRadioButton)
        self.set_view.buttonReleased.connect(self._on_set_view)

        gb = QtWidgets.QGroupBox("Data Level")
        hbox = QtWidgets.QHBoxLayout()
        gb.setLayout(hbox)
        hbox_view_and_datalevel.addWidget(gb)

        possible_dl_names = ['raw_data', 'survey_products', 'chart_adequacy']

        self.set_data_level = QtWidgets.QComboBox()
        self.set_data_level.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.set_data_level.addItems(possible_dl_names)
        self.set_data_level.currentTextChanged.connect(self._on_set_data_level)
        # starts off disabled as the default summary view doesn't filter by
        # data level
        self.set_data_level.setDisabled(True)

        hbox.addWidget(self.set_data_level)

        self._add_summary_view()
        self._add_json_view()
        self._add_score_board_view()

        self._on_set_view()

    @property
    def qa_json(self) -> Optional[QajsonRoot]:
        return self._qa_json

    @qa_json.setter
    def qa_json(self, value: QajsonRoot) -> NoReturn:
        self._qa_json = value
        self._update()

    def _on_qa_json_changed(self, qa_json: QajsonRoot) -> NoReturn:
        self._qa_json = qa_json
        self._update()

    def _update(self) -> NoReturn:
        """ Updates the user interface based on the qa_json
        """
        self._display_json()

    def _add_summary_view(self):
        # Summary view
        self.summary_widget = QtWidgets.QWidget()

        self.summary_widget.setHidden(True)
        self.vbox.addWidget(self.summary_widget)
        s_vbox = QtWidgets.QVBoxLayout()
        s_vbox.setContentsMargins(0, 0, 0, 0)
        self.summary_widget.setLayout(s_vbox)

        splitter = QtWidgets.QSplitter()
        splitter.setOrientation(QtCore.Qt.Vertical)
        s_vbox.addWidget(splitter)

        self.summary_group = QtWidgets.QGroupBox("Summary")
        splitter.addWidget(self.summary_group)

        vbox = QtWidgets.QVBoxLayout()
        self.summary_group.setLayout(vbox)

        self.summary_table = QtWidgets.QTableWidget()
        self.summary_table.setSortingEnabled(True)
        self.summary_table.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        self.summary_table.setFocus()
        self.summary_table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows)
        self.summary_table.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)
        self.summary_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.summary_table.setColumnCount(5)
        self.summary_table.setHorizontalHeaderLabels(
            ["Check", "Total runs", "Failed runs", "QA Fails", "QA Warning"])

        vbox.addWidget(self.summary_table)

        self.summary_table.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.Stretch)
        self.summary_table.horizontalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeToContents)
        self.summary_table.horizontalHeader().setSectionResizeMode(
            2, QtWidgets.QHeaderView.ResizeToContents)
        self.summary_table.horizontalHeader().setSectionResizeMode(
            3, QtWidgets.QHeaderView.ResizeToContents)
        self.summary_table.horizontalHeader().setSectionResizeMode(
            4, QtWidgets.QHeaderView.ResizeToContents)

        self.summary_table.clicked.connect(self._on_clicked_summary)

        self.summary_details = SummaryDetailsWidget(parent=self)
        self.summary_details.setVisible(False)
        splitter.addWidget(self.summary_details)

    def _update_summary_view(self):
        summaries = self.prj.get_summary()

        self.summary_table.setRowCount(len(summaries))
        for idx, summary in enumerate(summaries):
            check_name = summary.name
            if summary.version is None:
                check_name = "{} [no version]".format(check_name)
            else:
                check_name = "{} [v.{}]".format(check_name, summary.version)

            name_item = QtWidgets.QTableWidgetItem(check_name)
            self.summary_table.setItem(idx, 0, name_item)

            total_runs_item = QtWidgets.QTableWidgetItem(
                "{}".format(summary.total_executions))
            total_runs_item.setTextAlignment(QtCore.Qt.AlignRight)
            self.summary_table.setItem(idx, 1, total_runs_item)

            total_failed_runs_item = QtWidgets.QTableWidgetItem(
                "{}".format(summary.failed_executions))
            total_failed_runs_item.setTextAlignment(QtCore.Qt.AlignRight)
            if summary.failed_executions != 0:
                total_failed_runs_item.setBackground(ResultTab.color_fail)
            self.summary_table.setItem(idx, 2, total_failed_runs_item)

            total_failed_qa_item = QtWidgets.QTableWidgetItem(
                "{}".format(summary.failed_check_state))
            total_failed_qa_item.setTextAlignment(QtCore.Qt.AlignRight)
            if summary.failed_check_state != 0:
                total_failed_qa_item.setBackground(ResultTab.color_fail)
            self.summary_table.setItem(idx, 3, total_failed_qa_item)

            total_warn_qa_item = QtWidgets.QTableWidgetItem(
                "{}".format(summary.warning_check_state))
            total_warn_qa_item.setTextAlignment(QtCore.Qt.AlignRight)
            if summary.warning_check_state != 0:
                total_warn_qa_item.setBackground(ResultTab.color_warning)
            self.summary_table.setItem(idx, 4, total_warn_qa_item)

    def _on_clicked_summary(self, item):
        selected_row = item.row()

        summaries = self.prj.get_summary()
        summary = summaries[selected_row]
        self.summary_details.set_selected_summary(summary)
        self.summary_details.setVisible(True)

    def _add_json_view(self):
        # Json Text
        self.json_text_group = QtWidgets.QGroupBox("Json Text")
        self.json_text_group.setHidden(True)
        self.vbox.addWidget(self.json_text_group)
        vbox = QtWidgets.QVBoxLayout()
        self.json_text_group.setLayout(vbox)

        self.json_viewer = QtWidgets.QTextEdit()
        font = QtGui.QFont("Courier")
        font.setStyleHint(QtGui.QFont.TypeWriter)
        self.json_viewer.setCurrentFont(font)

        self.json_viewer.setReadOnly(True)
        vbox.addWidget(self.json_viewer)

    def _update_json_view(self):
        qa_json_dict = self.qa_json.to_dict()
        if (('qa' in qa_json_dict) and
                (qa_json_dict['qa'] is not None) and
                (self.qa_group in qa_json_dict['qa'])):
            self.json_viewer.setText(
                json.dumps(qa_json_dict['qa'][self.qa_group], indent=4))

    def _add_score_board_view(self):
        # Score Board
        self.score_board_widget = QtWidgets.QWidget()

        self.score_board_widget.setHidden(True)
        self.vbox.addWidget(self.score_board_widget)
        sb_vbox = QtWidgets.QVBoxLayout()
        sb_vbox.setContentsMargins(0, 0, 0, 0)
        self.score_board_widget.setLayout(sb_vbox)

        splitter = QtWidgets.QSplitter()
        splitter.setOrientation(QtCore.Qt.Vertical)
        sb_vbox.addWidget(splitter)

        self.score_board_group = QtWidgets.QGroupBox("Score Board")
        splitter.addWidget(self.score_board_group)

        vbox = QtWidgets.QVBoxLayout()
        self.score_board_group.setLayout(vbox)

        self.score_board = QtWidgets.QTableWidget()
        self.score_board.setSortingEnabled(True)
        self.score_board.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        self.score_board.setFocus()
        self.score_board.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows)
        self.score_board.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)
        self.score_board.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.score_board.setColumnCount(5)
        self.score_board.setHorizontalHeaderLabels(
            ["ID", "Check", "Input", "Status", "QA Pass"])

        vbox.addWidget(self.score_board)

        self.score_board.setColumnWidth(0, 60)
        self.score_board.horizontalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeToContents)
        self.score_board.horizontalHeader().setSectionResizeMode(
            2, QtWidgets.QHeaderView.Stretch)
        self.score_board.horizontalHeader().setSectionResizeMode(
            3, QtWidgets.QHeaderView.ResizeToContents)
        self.score_board.horizontalHeader().setSectionResizeMode(
            4, QtWidgets.QHeaderView.ResizeToContents)

        self.score_board.clicked.connect(self._on_clicked_scoreboard)

        self.scoreboard_details = ScoreboardDetailsWidget(parent=self)
        self.scoreboard_details.setVisible(False)
        splitter.addWidget(self.scoreboard_details)

    def _update_score_board_view(self):
        data_level = getattr(self.prj.qa_json.qa, self.qa_group)
        if data_level is None:
            return
        checks = data_level.checks

        nr_of_checks = len(checks)
        self.score_board.setRowCount(nr_of_checks)
        for idx in range(nr_of_checks):
            check = checks[idx]
            item0 = QtWidgets.QTableWidgetItem(check.info.id)
            self.score_board.setItem(idx, 0, item0)

            check_name = check.info.name
            try:
                check_name = f"{check_name} [v.{check.info.version}]"
            except Exception as e:
                check_name = f"{check_name} [no version]"
            item1 = QtWidgets.QTableWidgetItem(check_name)
            self.score_board.setItem(idx, 1, item1)

            if len(check.inputs.files) == 0:
                file_item = QtWidgets.QTableWidgetItem("")
            else:
                full_path = check.inputs.files[0].path
                _, file_name = os.path.split(full_path)
                file_item = QtWidgets.QTableWidgetItem(file_name)
            self.score_board.setItem(idx, 2, file_item)

            if check.outputs is None:
                status = "Not run"
                status_item_color = ResultTab.color_in_progress
            else:
                status = check.outputs.execution.status

                if status in ["aborted", "failed"]:
                    status_item.setBackground(ResultTab.color_fail)
                elif status in ["draft", "queued", "running"]:
                    status_item_color = ResultTab.color_in_progress
                    status_item.setBackground()
                else:
                    status_item_color = ResultTab.color_ok
            status_item = QtWidgets.QTableWidgetItem(status)
            status_item.setBackground(status_item_color)
            self.score_board.setItem(idx, 3, status_item)

            check_state = ""
            try:
                check_state = check.outputs.check_state
            except AttributeError as e:
                # then this check doesn't have outputs as it hasn't been run
                pass

            if check_state == "fail":
                check_state_item = QtWidgets.QTableWidgetItem(
                    self.cross_icon, "")
            elif check_state == "pass":
                check_state_item = QtWidgets.QTableWidgetItem(
                    self.tick_icon, "")
            elif check_state == "warning":
                check_state_item = QtWidgets.QTableWidgetItem(
                    self.warning_icon, "")
            elif check.outputs is None:
                check_state_item = QtWidgets.QTableWidgetItem(
                    self.warning_icon, "")
            else:
                check_state_item = QtWidgets.QTableWidgetItem("")
            check_state_item.setTextAlignment(QtCore.Qt.AlignHCenter)
            self.score_board.setItem(idx, 4, check_state_item)

    def _on_clicked_scoreboard(self, item):
        selected_row = item.row()

        # to get the right check we must be sure to get the data level that
        # the user has selected
        qajson_datalevel = getattr(self.qa_json.qa, self.qa_group)
        check = qajson_datalevel.checks[selected_row]
        self.scoreboard_selected_check = check
        self.scoreboard_details.set_selected_check(
            self.scoreboard_selected_check)
        self.scoreboard_details.setVisible(True)

    def _display_json(self):
        if self.qa_json.qa is None:
            # then there is no qajson yet, user probably hasn't added an input
            # file to check
            return

        for row in range(self.set_data_level.count()):
            data_level_name = self.set_data_level.itemText(row)
            data_level_available = getattr(
                self.qa_json.qa, data_level_name) is not None
            self.set_data_level.model().item(row).setEnabled(data_level_available)

        self._update_summary_view()
        self._update_json_view()
        self._update_score_board_view()

        self._on_set_view()

    def _on_set_view(self):
        self.cur_view = self.view_names[self.set_view.checkedId()]

        if self.cur_view == "Json Text":
            self.json_text_group.setVisible(True)
            self.score_board_widget.setHidden(True)
            self.summary_widget.setHidden(True)
            self.set_data_level.setDisabled(False)
        elif self.cur_view == "Score Board":
            self.json_text_group.setHidden(True)
            self.score_board_widget.setVisible(True)
            self.summary_widget.setHidden(True)
            self.set_data_level.setDisabled(False)
        elif self.cur_view == "Summary":
            self.json_text_group.setHidden(True)
            self.score_board_widget.setHidden(True)
            self.summary_widget.setVisible(True)
            self.set_data_level.setDisabled(True)

    def _on_set_data_level(self):
        self.qa_group = self.set_data_level.currentText()
        self._update()

    def _on_button_clicked(self):
        button = QtGui.qApp.focusWidget()
        index = self.score_board.indexAt(button.pos())
        if index.isValid():
            logger.debug("(%s, %s)" % index.row(), index.column())
