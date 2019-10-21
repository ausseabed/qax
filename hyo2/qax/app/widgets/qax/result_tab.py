from PySide2 import QtCore, QtGui, QtWidgets
from typing import Optional, NoReturn
import json
import logging
import os

from hyo2.qax.app.gui_settings import GuiSettings
from hyo2.qax.lib.qa_json import QaJsonRoot
from hyo2.qax.lib.project import QAXProject

logger = logging.getLogger(__name__)


class ResultTab(QtWidgets.QMainWindow):
    """ Displays the results of the check execution based on the contents of
    the qajson object.
    """

    color_fail = QtGui.QColor(200, 100, 100, 50)
    color_ok = QtGui.QColor(100, 200, 100, 50)
    color_in_progress = QtGui.QColor(200, 200, 100, 50)

    def __init__(self, prj: QAXProject):
        super(ResultTab, self).__init__()

        self.prj = prj
        self.prj.qa_json_changed.connect(self._on_qa_json_changed)

        self.qa_group = "raw_data"
        self._qa_json = None

        # ui
        self.panel = QtWidgets.QFrame()
        self.setCentralWidget(self.panel)
        self.vbox = QtWidgets.QVBoxLayout()
        self.panel.setLayout(self.vbox)

        self.set_view = None
        self.cur_view = 'Summary'
        self.set_data_level = None
        self.qa_group = None
        self.force_reload = None
        self.save_as = None
        self.execute_all = None
        self.json_text_group = None
        self.json_viewer = None
        self.score_board_group = None
        self.score_board = None
        self.summary_group = None
        self.summary_table = None

        self.cross_icon = QtGui.QIcon(GuiSettings.icon_path("cross.png"))
        self.tick_icon = QtGui.QIcon(GuiSettings.icon_path("tick.png"))

    @property
    def qa_json(self) -> Optional[QaJsonRoot]:
        return self._qa_json

    @qa_json.setter
    def qa_json(self, value: QaJsonRoot) -> NoReturn:
        self._qa_json = value
        self._update()

    def _on_qa_json_changed(self, qa_json: QaJsonRoot) -> NoReturn:
        self._qa_json = qa_json
        self._update()

    def _update(self) -> NoReturn:
        """ Updates the user interface based on the qa_json
        """
        self.display_json()

    def add_summary_view(self):
        # Score Board
        self.summary_group = QtWidgets.QGroupBox("Summary")
        self.summary_group.setStyleSheet(
            "QGroupBox::title { color: rgb(155, 155, 155); }")
        self.summary_group.setHidden(True)
        self.vbox.addWidget(self.summary_group)
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

        self.summary_table.setColumnCount(4)
        self.summary_table.setHorizontalHeaderLabels(
            ["Check", "Total runs", "Failed runs", "QA Fails"])

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
            self.summary_table.setItem(idx, 2, total_failed_runs_item)
            if summary.failed_executions != 0:
                total_failed_qa_item.setBackground(ResultTab.color_fail)

            total_failed_qa_item = QtWidgets.QTableWidgetItem(
                "{}".format(summary.failed_qa_pass))
            total_failed_qa_item.setTextAlignment(QtCore.Qt.AlignRight)
            self.summary_table.setItem(idx, 3, total_failed_qa_item)
            if summary.failed_qa_pass != 0:
                total_failed_qa_item.setBackground(ResultTab.color_fail)

        vbox.addWidget(self.summary_table)

        self.summary_table.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.Stretch)
        self.summary_table.horizontalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeToContents)
        self.summary_table.horizontalHeader().setSectionResizeMode(
            2, QtWidgets.QHeaderView.ResizeToContents)
        self.summary_table.horizontalHeader().setSectionResizeMode(
            3, QtWidgets.QHeaderView.ResizeToContents)

    def add_json_view(self, qa_json_dict):
        # Json Text
        self.json_text_group = QtWidgets.QGroupBox("Json Text")
        self.json_text_group.setStyleSheet(
            "QGroupBox::title { color: rgb(155, 155, 155); }")
        self.json_text_group.setHidden(True)
        self.vbox.addWidget(self.json_text_group)
        vbox = QtWidgets.QVBoxLayout()
        self.json_text_group.setLayout(vbox)

        self.json_viewer = QtWidgets.QTextEdit()
        font = QtGui.QFont("Courier")
        font.setStyleHint(QtGui.QFont.TypeWriter)
        self.json_viewer.setCurrentFont(font)
        self.json_viewer.setText(
            json.dumps(qa_json_dict['qa'][self.qa_group], indent=4))
        self.json_viewer.setReadOnly(True)
        vbox.addWidget(self.json_viewer)

    def add_score_board_view(self, qa_json_dict):
        # Score Board
        self.score_board_group = QtWidgets.QGroupBox("Score Board")
        self.score_board_group.setStyleSheet(
            "QGroupBox::title { color: rgb(155, 155, 155); }")
        self.score_board_group.setHidden(True)
        self.vbox.addWidget(self.score_board_group)
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

        checks = qa_json_dict['qa'][self.qa_group]['checks']
        logger.debug("checks: %s" % checks)
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

            qa_pass = ""
            try:
                qa_pass = checks[idx]['outputs']['qa_pass']
            except KeyError as e:
                logger.debug("skipping qa_pass for #%d: %s" % (idx, e))
            if qa_pass == "no":
                qa_pass_item = QtWidgets.QTableWidgetItem(self.cross_icon, "")
            elif qa_pass == "yes":
                qa_pass_item = QtWidgets.QTableWidgetItem(self.tick_icon, "")
            else:
                qa_pass_item = QtWidgets.QTableWidgetItem("")
            self.score_board.setItem(idx, 4, qa_pass_item)

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

    def display_json(self):
        # logger.debug("displaying js: %s" % self.prj.inputs.qa_json.js)
        qa_json_dict = self.qa_json.to_dict()

        # UI code taken from `checks_tab.py`
        self.panel.deleteLater()
        self.vbox.deleteLater()

        button_width = 120
        button_height = 35

        # ui
        self.panel = QtWidgets.QFrame()
        self.setCentralWidget(self.panel)
        self.vbox = QtWidgets.QVBoxLayout()
        self.panel.setLayout(self.vbox)

        hbox = QtWidgets.QHBoxLayout()
        self.vbox.addLayout(hbox)

        hbox.addWidget(QtWidgets.QLabel("Data level:"))
        possible_dl_names = ['raw_data', 'survey_products', 'chart_adequacy']
        data_level_names = [
            name
            for name in possible_dl_names
            if getattr(self.qa_json.qa, name) is not None
        ]
        self.set_data_level = QtWidgets.QComboBox()
        self.set_data_level.setFixedHeight(button_height)
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
        self.set_view.setFixedHeight(button_height)
        self.set_view.addItems(['Summary', 'Score Board', 'Json Text'])
        self.set_view.setCurrentText(self.cur_view)
        # noinspection PyUnresolvedReferences
        self.set_view.currentTextChanged.connect(self.on_set_view)
        hbox.addWidget(self.set_view)
        hbox.setSpacing(16)

        self.save_as = QtWidgets.QPushButton()
        self.save_as.setFixedWidth(button_width)
        self.save_as.setFixedHeight(button_height)
        self.save_as.setText("Save as")
        # noinspection PyUnresolvedReferences
        self.save_as.clicked.connect(self.on_save_as)
        hbox.addWidget(self.save_as)

        self.add_summary_view()
        self.add_json_view(qa_json_dict)
        self.add_score_board_view(qa_json_dict)

        self.on_set_view()

    def on_set_view(self):
        self.cur_view = self.set_view.currentText()
        logger.debug("selected view: %s" % self.cur_view)

        if self.cur_view == "Json Text":
            self.json_text_group.setVisible(True)
            self.score_board_group.setHidden(True)
            self.summary_group.setHidden(True)
        elif self.cur_view == "Score Board":
            self.json_text_group.setHidden(True)
            self.score_board_group.setVisible(True)
            self.summary_group.setHidden(True)
        elif self.cur_view == "Summary":
            self.json_text_group.setHidden(True)
            self.score_board_group.setHidden(True)
            self.summary_group.setVisible(True)

    def on_set_data_level(self):
        self.qa_group = self.set_data_level.currentText()
        self._update()

    def on_save_as(self):
        logger.debug("save as")

        output_folder = QtCore.QSettings().value("json_export_folder")
        if output_folder is None:
            output_folder = self.prj.outputs.output_folder
        else:
            output_folder = Path(output_folder)

        output_path = output_folder.joinpath(self.prj.inputs.qa_json.path.name)
        # noinspection PyCallByClass
        selection, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save file", str(output_path),
            "QA JSON file (*.json);;All files (*.*)", "")
        if selection == "":
            logger.debug('save file: aborted')
            return

        output_path = Path(selection)
        output_folder = output_path.parent
        QtCore.QSettings().setValue("json_export_folder", str(output_folder))

        self.prj.save_cur_json(path=output_path)
        # self.on_force_reload()

    def on_button_clicked(self):
        button = QtGui.qApp.focusWidget()
        index = self.score_board.indexAt(button.pos())
        if index.isValid():
            logger.debug("(%s, %s)" % index.row(), index.column())
