import sys
from PySide2.QtCore import QUrl, QFileInfo, QTimer
from PySide2.QtGui import QIcon, QColor
from PySide2.QtWidgets import QLineEdit, QApplication, \
    QMainWindow, QPushButton, QToolBar, QVBoxLayout, QWidget, \
    QHBoxLayout, QLabel
from PySide2.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
import os

from hyo2.qax.app import qta
from hyo2.qax.app import app_info
import hyo2.qax.app.widgets.qax.manual_links as manual_links


REL_DOCS_PATH = 'docs/_build/html/'
ALT_DOCS_PATH = '_internal/' + REL_DOCS_PATH  # for both the Windows exe and dist versions


def _docs_root():
    """
    Something to disentangle the original logic that hardcodes the path to be
    manual_links.INDEX which may not exist, causing the docs widget to display
    an error.
    Preference is to return a valid path, and avoid checking multiple times.
    """
    docs_path = os.path.abspath(REL_DOCS_PATH)
    alt_docs_path = os.path.abspath(ALT_DOCS_PATH)

    if os.path.exists(docs_path):
        path = docs_path
    elif os.path.exists(alt_docs_path):
        path = alt_docs_path
    else:
        raise RuntimeError(f"Docs not found at {docs_path} or {alt_docs_path}")

    return path


class ManualWindow(QMainWindow):

    # singleton instance for the Manual Dialog window
    _instance = None

    # Use a combination of this class method and singleton instance
    # to enable this function to be called from anywhere in the QAX
    # code base
    @classmethod
    def show_manual(cls, link = None):
        if (ManualWindow._instance is None):
            man_win = ManualWindow()
            app = QApplication.instance()
            available_geometry = app.desktop().availableGeometry(man_win)
            man_win.resize(
                available_geometry.width() * 2 / 3,
                available_geometry.height() * 2 / 3)
            ManualWindow._instance = man_win

        # if a url link is provided, then set the manual window to display
        # this links content. Otherwise just go to the index page
        if (link is None):
            ManualWindow._instance.set_url(manual_links.INDEX)
        else:
            ManualWindow._instance.set_url(link)

        ManualWindow._instance.show()
        ManualWindow._instance.activateWindow()

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
        self.home_button = QPushButton()
        self.home_button.setIcon(qta.icon('fa.home'))
        self.home_button.clicked.connect(self.home)
        self.toolbar.addWidget(self.home_button)

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
        self.initialUrl = QUrl(self.docs_url())

        self.address_line_edit.setText(str(self.initialUrl))

        # There's a two set process used by this dialog to set a new URL
        # First is to load the page, second is to setUrl.
        # The reason for this is that the web view scroll cannot be
        # set to a fragment (eg; #heading) if it's included in a URL by
        # simply calling `.load` because the content isn't loaded. Instead
        # we need to call `.load` wait for the content to be loaded, then
        # setUrl so the web view scroll position is set to the refrenced
        # heading.
        self.last_loaded_url = None
        self.web_engine_view.loadFinished.connect(self.load_finished)

    def docs_url(self):
        root_path = _docs_root()

        docs_index = root_path + manual_links.INDEX
        if not os.path.exists(docs_index):
            raise RuntimeError(f"Docs index not found at {docs_index}")

        return docs_index

    def load(self):
        url = QUrl.fromUserInput(self.address_line_edit.text())
        if url.isValid():
            self.last_loaded_url = url
            self.web_engine_view.load(url)

    def back(self):
        self.web_engine_view.page().triggerAction(QWebEnginePage.Back)

    def forward(self):
        self.web_engine_view.page().triggerAction(QWebEnginePage.Forward)

    def home(self):
        self.web_engine_view.load(self.initialUrl)

    def set_url(self, url: str) -> None:
        """ Sets the contents displayed by the manual dialog. url
        is assumed to be in the short form (taken from the manual_links
        module).
        """
        docs_root = _docs_root()
        abs_docs_path = os.path.join(docs_root, url)
        file_only_path = None
        fragment = None
        if '#' in abs_docs_path:
            # then it has a fragment, so separate the two components
            # as this messes with the `fromLocalFile` fn
            parts = abs_docs_path.split('#')
            file_only_path = os.path.abspath(parts[0])
            fragment = parts[1]
        else:
            file_only_path = os.path.abspath(abs_docs_path)

        file_url =  QUrl.fromLocalFile(file_only_path)
        if fragment is not None:
            file_url.setFragment(fragment)

        self.last_loaded_url = file_url
        self.web_engine_view.load(file_url)

    def load_finished(self, arg):
        if self.last_loaded_url is not None:
            self.web_engine_view.setUrl(self.last_loaded_url)
            self.last_loaded_url = None


class ManualButton(QPushButton):
    """
    Button definition specific for showing the user manual. Cuts down
    on amount of boilerplate code needed to open the manual to a specific
    page.
    """

    def __init__(self, link: str, tooltip: str = None):
        super(ManualButton, self).__init__()

        self.setIcon(qta.icon('fa.info-circle', color='grey'))
        if tooltip is not None:
            self.setToolTip(tooltip)
        self.clicked.connect(self._click_show_manual)
        self.setFlat(True)

        self.setStyleSheet(
            "QPushButton {"
                # "background: rgb(255, 0, 0);"
                # "color: rgb(125, 125, 0);"
                "font-size: 10pt;"
                "border: none;"
            "}"
        )

        self.link = link

    def _click_show_manual(self):
        ManualWindow.show_manual(self.link)


class ManualLabelButton(QWidget):
    """
    Widget implementation that includes a label for something, and a help
    button.
    """

    def __init__(self, link: str, label: str, tooltip: str = None):
        super(ManualLabelButton, self).__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        label = QLabel(label)
        layout.addWidget(label)
        help_button = ManualButton(
            link,
            tooltip
        )
        layout.addWidget(help_button)
        layout.addStretch(1)
