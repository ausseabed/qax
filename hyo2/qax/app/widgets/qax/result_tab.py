from PySide2 import QtCore, QtGui, QtWidgets
from typing import Optional, NoReturn
import json
import logging

from hyo2.qax.lib.qa_json import QaJsonRoot
from hyo2.qax.lib.project import QAXProject

logger = logging.getLogger(__name__)


class ResultTab(QtWidgets.QMainWindow):
    """ Displays the results of the check execution based on the contents of
    the qajson object.
    """

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
        self.cur_view = 'Score Board'
        self.force_reload = None
        self.save_as = None
        self.execute_all = None
        self.json_text_group = None
        self.json_viewer = None
        self.score_board_group = None
        self.score_board = None

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


    def display_json(self):
        # logger.debug("displaying js: %s" % self.prj.inputs.qa_json.js)
        qa_json_dict = self.qa_json.to_dict()

        # UI code taken from `checks_tab.py`
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

        self.save_as = QtWidgets.QPushButton()
        self.save_as.setFixedWidth(button_width)
        self.save_as.setText("Save as")
        # noinspection PyUnresolvedReferences
        self.save_as.clicked.connect(self.on_save_as)
        hbox.addWidget(self.save_as)
        hbox.addStretch()

        # Json Text
        self.json_text_group = QtWidgets.QGroupBox("Json Text")
        self.json_text_group.setStyleSheet(
            "QGroupBox::title { color: rgb(155, 155, 155); }")
        self.json_text_group.setHidden(True)
        self.vbox.addWidget(self.json_text_group)
        vbox = QtWidgets.QVBoxLayout()
        self.json_text_group.setLayout(vbox)
        self.json_viewer = QtWidgets.QTextEdit()
        self.json_viewer.setText(json.dumps(qa_json_dict['qa'][self.qa_group], indent=4))
        self.json_viewer.setReadOnly(True)
        vbox.addWidget(self.json_viewer)

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

        self.score_board.setColumnCount(7)
        self.score_board.setHorizontalHeaderLabels(
            ["ID", "Check", "Group", "Input", "Output", "Status", "Action"])
        checks = qa_json_dict['qa'][self.qa_group]['checks']
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

    def on_set_view(self):
        self.cur_view = self.set_view.currentText()
        logger.debug("selected view: %s" % self.cur_view)

        if self.cur_view == "Json Text":
            self.json_text_group.setVisible(True)
            self.score_board_group.setHidden(True)

        elif self.cur_view == "Score Board":
            self.json_text_group.setHidden(True)
            self.score_board_group.setVisible(True)

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
