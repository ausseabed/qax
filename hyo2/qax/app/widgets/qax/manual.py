import sys
from PySide2.QtCore import QUrl, QFileInfo
from PySide2.QtGui import QIcon, QColor
from PySide2.QtWidgets import QLineEdit, \
    QMainWindow, QPushButton, QToolBar, QVBoxLayout, QWidget
from PySide2.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
import os

from hyo2.qax.app import qta
from hyo2.qax.app import app_info


class ManualWindow(QMainWindow):

    def __init__(self):
        super(ManualWindow, self).__init__()

        self.setWindowTitle('QAX Manual')

        icon_info = QFileInfo(app_info.app_icon_path)
        self.setWindowIcon(QIcon(icon_info.absoluteFilePath()))

        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)
        self.back_button = QPushButton()
        self.back_button.setIcon(qta.icon('fa.arrow-left'))
        self.back_button.clicked.connect(self.back)
        self.toolbar.addWidget(self.back_button)
        self.forward_button = QPushButton()
        self.forward_button.setIcon(qta.icon('fa.arrow-right'))
        self.forward_button.clicked.connect(self.forward)
        self.toolbar.addWidget(self.forward_button)

        self.address_line_edit = QLineEdit()
        self.address_line_edit.returnPressed.connect(self.load)
        self.address_line_edit.setVisible(False)
        self.toolbar.addWidget(self.address_line_edit)

        self.main_widget = QWidget()
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)

        self.web_engine_view = QWebEngineView()
        self.layout.addWidget(self.web_engine_view)
        initialUrl = self.docs_url()

        self.address_line_edit.setText(str(initialUrl))
        self.web_engine_view.load(QUrl(initialUrl))
        self.web_engine_view.page().urlChanged.connect(self.urlChanged)

    def docs_url(self):
        rel_docs_path = 'docs/_build/html/index.html'
        abs_docs_oath = os.path.abspath(rel_docs_path)
        if (os.path.isfile(abs_docs_oath)):
            return QUrl.fromLocalFile(abs_docs_oath)
        raise RuntimeError("Docs not found at {}".format(abs_docs_oath))

    def load(self):
        url = QUrl.fromUserInput(self.address_line_edit.text())
        if url.isValid():
            self.web_engine_view.load(url)

    def back(self):
        self.web_engine_view.page().triggerAction(QWebEnginePage.Back)

    def forward(self):
        self.web_engine_view.page().triggerAction(QWebEnginePage.Forward)

    def urlChanged(self, url):
        self.address_line_edit.setText(url.toString())
