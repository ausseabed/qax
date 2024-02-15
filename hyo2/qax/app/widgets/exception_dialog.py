from PySide2.QtWidgets import QApplication, QDialog, \
    QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, \
    QTextBrowser, QDialogButtonBox
from PySide2.QtGui import QFont
from PySide2 import QtCore
import traceback

from hyo2.qax.app import qta
from hyo2.qax.app import app_info

"""
Dialog for displaying Exception information to users
"""
class ExceptionDialog(QDialog):

    def __init__(
            self,
            exception_type: type,
            exception_value: BaseException,
            exception_traceback: traceback,
            parent=None
        ):
        super(
            ExceptionDialog,
            self).__init__(
            parent,
            QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitle("Error")
        self.setWindowIcon(qta.icon('msc.run-errors'))
        self.setMinimumSize(300, 200)
        self.resize(500, 300)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(16)
        self.layout.setMargin(8)
        self.setLayout(self.layout)

        label = QLabel(f"{exception_type.__name__}: {exception_value}")
        self.layout.addWidget(label)

        self.traceback_str = "".join(traceback.format_tb(exception_traceback))

        groupbox = QGroupBox("Stack Trace")
        self.layout.addWidget(groupbox)
        groupbox_layout = QVBoxLayout()
        groupbox.setLayout(groupbox_layout)

        copy_layout = QHBoxLayout()
        copy_layout.addStretch()
        button_copy = QPushButton("Copy to clipboard")
        button_copy.setIcon(qta.icon('fa.copy'))
        button_copy.clicked.connect(self._copy_stack_trace)
        copy_layout.addWidget(button_copy)
        groupbox_layout.addLayout(copy_layout)

        traceback_textbox = QTextBrowser()
        groupbox_layout.addWidget(traceback_textbox)
        font = QFont("Monospace", 8)
        font.setStyleHint(QFont.TypeWriter)
        traceback_textbox.setCurrentFont(font)
        traceback_textbox.setLineWrapMode(QTextBrowser.NoWrap)
        traceback_textbox.setPlainText(self.traceback_str)
        traceback_textbox.setTextInteractionFlags(
            QtCore.Qt.TextSelectableByKeyboard | QtCore.Qt.TextSelectableByMouse
        )
        traceback_textbox.setReadOnly(True)

        text_label = QLabel(self)
        text = (
            "Please copy the above stack trace text and create a "
            "<a href=\"https://github.com/ausseabed/qax/issues\">bug report</a> "
            f"or write an email to <a href=\"mailto:{app_info.app_support_email}\">{app_info.app_support_email}</a>."
        )

        text_label.setWordWrap(True)
        text_label.setText(text)
        text_label.setTextInteractionFlags(
            QtCore.Qt.LinksAccessibleByMouse | QtCore.Qt.TextSelectableByMouse
        )
        text_label.setOpenExternalLinks(True)
        self.layout.addWidget(text_label)

        buttons_groupbox = QDialogButtonBox(self)
        buttons_groupbox.setOrientation(QtCore.Qt.Horizontal)
        buttons_groupbox.setStandardButtons(QDialogButtonBox.Ignore)
        buttons_groupbox.addButton("Quit QAX", QDialogButtonBox.RejectRole)
        self.layout.addWidget(buttons_groupbox)
        buttons_groupbox.accepted.connect(self.accept)
        buttons_groupbox.rejected.connect(self.reject)

    def _copy_stack_trace(self):
        QApplication.clipboard().setText(self.traceback_str)

