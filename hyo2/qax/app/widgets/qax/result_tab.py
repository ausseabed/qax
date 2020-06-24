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
        self.display_json()

    def add_summary_view(self):
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

    def _on_clicked_summary(self, item):
        selected_row = item.row()

        summaries = self.prj.get_summary()
        summary = summaries[selected_row]
        self.summary_details.set_selected_summary(summary)
        self.summary_details.setVisible(True)

    def add_json_view(self, qa_json_dict):
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
        if (('qa' in qa_json_dict) and
                (qa_json_dict['qa'] is not None) and
                (self.qa_group in qa_json_dict['qa'])):
            self.json_viewer.setText(
                json.dumps(qa_json_dict['qa'][self.qa_group], indent=4))
        self.json_viewer.setReadOnly(True)
        vbox.addWidget(self.json_viewer)

    def add_score_board_view(self, qa_json_dict):
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

        checks = []
        if (('qa' in qa_json_dict) and
                (qa_json_dict['qa'] is not None) and
                (self.qa_group in qa_json_dict['qa'])):
            checks = qa_json_dict['qa'][self.qa_group]['checks']

        nr_of_checks = len(checks)
        self.score_board.setRowCount(nr_of_checks)
        for idx in range(nr_of_checks):
            item0 = QtWidgets.QTableWidgetItem(checks[idx]['info']['id'])
            self.score_board.setItem(idx, 0, item0)

            check_name = checks[idx]['info']['name']
            try:
                check_name = "{} [v.{}]".format(
                    check_name, checks[idx]['info']['version'])
            except Exception as e:
                check_name = "{} [no version]".format(check_name)
            item1 = QtWidgets.QTableWidgetItem(check_name)
            self.score_board.setItem(idx, 1, item1)

            if len(checks[idx]['inputs']['files']) == 0:
                file_item = QtWidgets.QTableWidgetItem("")
            else:
                full_path = checks[idx]['inputs']['files'][0]['path']
                _, file_name = os.path.split(full_path)
                file_item = QtWidgets.QTableWidgetItem(file_name)
            self.score_board.setItem(idx, 2, file_item)

            try:
                status = checks[idx]['outputs']['execution']['status']
                status_item = QtWidgets.QTableWidgetItem(status)
                if status in ["aborted", "failed"]:
                    status_item.setBackground(ResultTab.color_fail)
                elif status in ["draft", "queued", "running"]:
                    status_item.setBackground(ResultTab.color_in_progress)
                else:
                    status_item.setBackground(ResultTab.color_ok)
                self.score_board.setItem(idx, 3, status_item)
            except KeyError as e:
                logger.debug("skipping grade for #%d: %s" % (idx, e))

            check_state = ""
            try:
                check_state = checks[idx]['outputs']['check_state']
            except KeyError as e:
                logger.debug("skipping check_state for #%d: %s" % (idx, e))
            if check_state == "fail":
                check_state_item = QtWidgets.QTableWidgetItem(self.cross_icon, "")
            elif check_state == "pass":
                check_state_item = QtWidgets.QTableWidgetItem(self.tick_icon, "")
            elif check_state == "warning":
                check_state_item = QtWidgets.QTableWidgetItem(self.warning_icon, "")
            else:
                check_state_item = QtWidgets.QTableWidgetItem("")
            check_state_item.setTextAlignment(QtCore.Qt.AlignHCenter)
            self.score_board.setItem(idx, 4, check_state_item)

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

    def _on_clicked_scoreboard(self, item):
        selected_row = item.row()

        # to get the right check we must be sure to get the data level that
        # the user has selected
        qajson_datalevel = getattr(self.qa_json.qa, self.qa_group)
        check = self.qa_json.qa.raw_data.checks[selected_row]
        self.scoreboard_selected_check = check
        self.scoreboard_details.set_selected_check(
            self.scoreboard_selected_check)
        self.scoreboard_details.setVisible(True)

    def display_json(self):
        # logger.debug("displaying js: %s" % self.prj.inputs.qa_json.js)
        qa_json_dict = self.qa_json.to_dict()

        while self.vbox.count():
            child = self.vbox.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        gb = QtWidgets.QGroupBox()
        # gb.setFixedHeight(40)
        hbox = QtWidgets.QHBoxLayout()
        gb.setLayout(hbox)

        self.vbox.addWidget(gb)

        data_level_label = QtWidgets.QLabel("Data level:")
        # data_level_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        hbox.addWidget(data_level_label)
        possible_dl_names = ['raw_data', 'survey_products', 'chart_adequacy']
        data_level_names = [
            name
            for name in possible_dl_names
            if (self.qa_json.qa is not None) and getattr(self.qa_json.qa, name) is not None
        ]
        self.set_data_level = QtWidgets.QComboBox()
        self.set_data_level.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.set_data_level.addItems(data_level_names)
        if self.qa_group in data_level_names:
            self.set_data_level.setCurrentText(self.qa_group)
        elif len(data_level_names) > 0:
            self.qa_group = data_level_names[0]
            self.set_data_level.setCurrentText(self.qa_group)

        # noinspection PyUnresolvedReferences
        self.set_data_level.currentTextChanged.connect(self.on_set_data_level)
        hbox.addWidget(self.set_data_level)

        hbox.addStretch()
        self.set_view = QtWidgets.QComboBox()
        self.set_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.set_view.addItems(['Summary', 'Score Board', 'Json Text'])
        self.set_view.setCurrentText(self.cur_view)
        # noinspection PyUnresolvedReferences
        self.set_view.currentTextChanged.connect(self.on_set_view)
        hbox.addWidget(self.set_view)
        hbox.setSpacing(16)

        self.add_summary_view()
        self.add_json_view(qa_json_dict)
        self.add_score_board_view(qa_json_dict)

        self.on_set_view()

    def on_set_view(self):
        self.cur_view = self.set_view.currentText()
        logger.debug("selected view: %s" % self.cur_view)

        if self.cur_view == "Json Text":
            self.json_text_group.setVisible(True)
            self.score_board_widget.setHidden(True)
            self.summary_widget.setHidden(True)
        elif self.cur_view == "Score Board":
            self.json_text_group.setHidden(True)
            self.score_board_widget.setVisible(True)
            self.summary_widget.setHidden(True)
        elif self.cur_view == "Summary":
            self.json_text_group.setHidden(True)
            self.score_board_widget.setHidden(True)
            self.summary_widget.setVisible(True)

    def on_set_data_level(self):
        self.qa_group = self.set_data_level.currentText()
        self._update()

    def on_button_clicked(self):
        button = QtGui.qApp.focusWidget()
        index = self.score_board.indexAt(button.pos())
        if index.isValid():
            logger.debug("(%s, %s)" % index.row(), index.column())
