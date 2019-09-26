from PySide2 import QtCore, QtGui, QtWidgets
from typing import List, NoReturn
import re
import os

from hyo2.qax.app.gui_settings import GuiSettings
from hyo2.qax.lib.config import QaxConfigSurveyProduct


class SurveyProductWidget(QtWidgets.QWidget):
    """ Widget to support selection of one or more files for a *single* survey
    product. """

    def __init__(self, survey_product: QaxConfigSurveyProduct, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)
        self.survey_product = survey_product
        hbox = QtWidgets.QHBoxLayout()
        self.setLayout(hbox)

        self.selected_files = []

        left_space = 100

        label = QtWidgets.QLabel("{}:".format(survey_product.name))
        label.setMinimumWidth(left_space)
        hbox.addWidget(label)

        self.file_list = QtWidgets.QListWidget()
        hbox.addWidget(self.file_list)
        self.file_list.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)
        self.file_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(
            self.__make_context_menu)
        self.file_list.setAlternatingRowColors(True)
        self.file_list.setMaximumHeight(100)
        # Enable dropping onto the input ss list
        self.file_list.setAcceptDrops(True)
        self.file_list.installEventFilter(self)

        self.add_file_button = QtWidgets.QPushButton()
        hbox.addWidget(self.add_file_button)
        self.add_file_button.setFixedHeight(GuiSettings.single_line_height())
        self.add_file_button.setFixedWidth(GuiSettings.single_line_height())
        self.add_file_button.setText(" + ")
        self.add_file_button.setToolTip(
            "Add (or drag-and-drop) the survey {} files"
            .format(survey_product.name))
        # noinspection PyUnresolvedReferences
        self.add_file_button.clicked.connect(self._click_add)

    def _click_add(self):
        """ Add files selected by user. Opens file selection dialog
        """
        import_folder_name = "{}_import_folder".format(
            self.survey_product.clean_name())

        filters = []
        if len(self.survey_product.file_types) > 0:
            all_ext = [
                "*.{}".format(ft.extension)
                for ft in self.survey_product.file_types]
            all_formats = "Supported formats ({})".format(" ".join(all_ext))
            filters.append(all_formats)
            for ft in self.survey_product.file_types:
                filters.append("{} (*.{})".format(ft.name, ft.extension))
        filters.append("All files (*.*)")

        # ask the file path to the user
        # noinspection PyCallByClass
        selections, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            "Add {} file".format(self.survey_product.name.lower()),
            QtCore.QSettings().value(import_folder_name),
            ";; ".join(filters))
        if len(selections) == 0:
            logger.debug('adding raw: aborted')
            return
        last_open_folder = os.path.dirname(selections[0])
        if os.path.exists(last_open_folder):
            QtCore.QSettings().setValue(import_folder_name, last_open_folder)

        selected_files = [
            os.path.abspath(selection).replace("\\", "/")
            for selection in selections
        ]
        self.selected_files = selected_files
        self._update_file_list()

    def __make_context_menu(self, pos):
        remove_action = QtWidgets.QAction(
            "Remove files",
            self,
            statusTip="Remove {} files".format(self.survey_product.lower()),
            triggered=self.remove_files)

        menu = QtWidgets.QMenu(parent=self)
        # noinspection PyArgumentList
        menu.addAction(remove_action)
        # noinspection PyArgumentList
        menu.exec_(self.input_raw.mapToGlobal(pos))

    def remove_files(self) -> NoReturn:
        """ Clears the list of selected files """
        logger.debug("user want to remove raw files")
        self.file_list.clear()
        self.selected_files.clear()

    def _update_file_list(self) -> NoReturn:
        self.file_list.clear()
        for selected_file in self.selected_files:
            file_item = QtWidgets.QListWidgetItem()
            file_item.setText(selected_file)
            file_item.setFont(GuiSettings.console_font())
            file_item.setForeground(GuiSettings.console_fg_color())
            self.file_list.addItem(file_item)


class SurveyProductGroupBox(QtWidgets.QGroupBox):
    """ Widget to support selection of survey products (the input files) that
    will be passed to the check tools. Widget includes multiple
    `SurveyProductWidget` instances.
    """

    def __init__(self, parent_win, prj):
        QtWidgets.QGroupBox.__init__(self, "Survey Products")
        self.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")

        self.prj = prj
        self.parent_win = parent_win
        self.survey_product_widgets = []

        self.survey_products_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.survey_products_layout)

    def update_survey_products(
            self, survey_products: List[QaxConfigSurveyProduct]
            ) -> NoReturn:
        """ Updates the various lists of files based on the `survey_products`
        list
        """
        # clear all items from survey products layout
        for sp_widget in self.survey_product_widgets:
            sp_widget.setParent(None)
        self.survey_product_widgets.clear()

        for survey_product in survey_products:
            sp_widget = SurveyProductWidget(survey_product, self)
            self.survey_products_layout.addWidget(sp_widget)
            self.survey_product_widgets.append(sp_widget)
