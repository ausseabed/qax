import json
import logging
import os
from PySide2 import QtCore, QtGui, QtWidgets
from hyo2.abc.lib.helper import Helper

logger = logging.getLogger(__name__)


class QCToolsTab(QtWidgets.QMainWindow):

    here = os.path.abspath(os.path.dirname(__file__))

    def __init__(self, parent_win, prj, qa_group: str = "survey_products"):
        QtWidgets.QMainWindow.__init__(self)

        # store a project reference
        self.prj = prj
        self.parent_win = parent_win
        self.media = self.parent_win.media
        self.qa_group = qa_group

        # ui
        self.panel = QtWidgets.QFrame()
        self.setCentralWidget(self.panel)
        self.vbox = QtWidgets.QVBoxLayout()
        self.panel.setLayout(self.vbox)

        self.set_view = None
        self.force_reload = None
        self.json_text_group = None
        self.json_viewer = None
        self.score_board_group = None
        self.score_board = None

    def display_json(self):
        logger.debug("displaying js: %s" % self.prj.inputs.qa_json.js)

        self.panel.deleteLater()
        self.vbox.deleteLater()

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
        # noinspection PyUnresolvedReferences
        self.set_view.currentTextChanged.connect(self.on_set_view)
        hbox.addWidget(self.set_view)
        self.force_reload = QtWidgets.QPushButton()
        self.force_reload.setText("Reload")
        # noinspection PyUnresolvedReferences
        self.force_reload.clicked.connect(self.on_force_reload)
        hbox.addWidget(self.force_reload)
        hbox.addStretch()

        # Json Text
        self.json_text_group = QtWidgets.QGroupBox("Json Text")
        self.json_text_group.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        self.json_text_group.setHidden(True)
        self.vbox.addWidget(self.json_text_group)
        vbox = QtWidgets.QVBoxLayout()
        self.json_text_group.setLayout(vbox)
        self.json_viewer = QtWidgets.QTextEdit()
        self.json_viewer.setText(json.dumps(self.prj.inputs.qa_json.js, indent=4))
        self.json_viewer.setReadOnly(True)
        vbox.addWidget(self.json_viewer)

        # Score Board
        self.score_board_group = QtWidgets.QGroupBox("Score Board")
        self.score_board_group.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")
        self.score_board_group.setHidden(True)
        self.vbox.addWidget(self.score_board_group)
        vbox = QtWidgets.QVBoxLayout()
        self.score_board_group.setLayout(vbox)
        self.score_board = QtWidgets.QTableWidget()
        self.score_board.setSortingEnabled(True)
        self.score_board.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.score_board.setColumnCount(6)
        self.score_board.setHorizontalHeaderLabels(["Check", "Group", "Input", "Count", "Percentage", "Status"])
        checks = self.prj.inputs.qa_json.js['qa'][self.qa_group]['checks']
        logger.debug("checks: %s" % checks)
        nr_of_checks = len(checks)
        self.score_board.setRowCount(nr_of_checks)
        for idx in range(nr_of_checks):
            item1 = QtWidgets.QTableWidgetItem("%s [v.%s]" % (checks[idx]['info']['name'], checks[idx]['info']['version']))
            self.score_board.setItem(idx, 0, item1)
            item2 = QtWidgets.QTableWidgetItem(checks[idx]['info']['group']['name'])
            self.score_board.setItem(idx, 1, item2)
            item3 = QtWidgets.QTableWidgetItem(checks[idx]['inputs']['files'][0]['path'])
            self.score_board.setItem(idx, 2, item3)
            try:
                item4 = QtWidgets.QTableWidgetItem("%d" % checks[idx]['outputs']['count'])
                self.score_board.setItem(idx, 3, item4)
            except KeyError as e:
                logger.debug("skipping count for #%d: %s" % (idx, e))
            try:
                item5 = QtWidgets.QTableWidgetItem("%.2f" % checks[idx]['outputs']['percentage'])
                self.score_board.setItem(idx, 4, item5)
            except KeyError as e:
                logger.debug("skipping grade for #%d: %s" % (idx, e))
            item6 = QtWidgets.QTableWidgetItem(checks[idx]['outputs']['execution']['status'])
            self.score_board.setItem(idx, 5, item6)

        vbox.addWidget(self.score_board)

        self.on_set_view()

    def on_set_view(self):
        cur_view = self.set_view.currentText()
        logger.debug("selected view: %s" % cur_view)

        if cur_view == "Json Text":
            self.json_text_group.setVisible(True)
            self.score_board_group.setHidden(True)

        elif cur_view == "Score Board":
            self.json_text_group.setHidden(True)
            self.score_board_group.setVisible(True)

    def on_force_reload(self):
        logger.debug("force reload")
        self.display_json()
