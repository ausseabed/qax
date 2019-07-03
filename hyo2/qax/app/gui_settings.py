from PySide2 import QtGui

import logging

logger = logging.getLogger(__name__)


#
# Settings in common with the QC Tools widgets
#
class GuiSettings:

    @classmethod
    def single_line_height(cls):
        """the height of a single line"""
        return 28

    @classmethod
    def single_line_height_reduced(cls):
        """the height of a single line"""
        return 24

    @classmethod
    def console_font(cls):
        """font used by text console"""
        text_font = QtGui.QFont("Courier Prime", 9)
        text_font.setFixedPitch(True)
        return text_font

    @classmethod
    def console_fg_color(cls):
        """text color (foreground) used by text console"""
        return QtGui.QColor(25, 152, 198)

    @staticmethod
    def stylesheet_console_fg_color():
        """text color (foreground) used by line edit to be equal to text console"""
        return "color: rgb(0, 176, 240);"

    @staticmethod
    def stylesheet_not_editable_bg_color():
        """text color (background) used by line edit to be equal to text console"""
        return "background-color: rgb(243, 243, 243);"

    @staticmethod
    def stylesheet_slider_labels():
        return "QLabel { color: rgb(185, 185, 185); font: 7pt; padding: 5px 0px 0px 0px;}"

    @staticmethod
    def stylesheet_info_button():
        return "QPushButton { background-color: rgba(255, 255, 255, 0); }\n" \
               "QPushButton:hover { background-color: rgba(230, 230, 230, 100); }\n"

    @staticmethod
    def text_button_width():
        """the width of a text button"""
        return 90
