from ausseabed.qajson.model import QajsonRoot
from pathlib import Path
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QSizePolicy
from typing import List, NoReturn
import logging
import os

from hyo2.qax.app.gui_settings import GuiSettings
from hyo2.qax.app.widgets.layout import FlowLayout
from hyo2.qax.app.widgets.lines import QHLine
from hyo2.qax.lib.config import QaxConfigCheckTool
from hyo2.qax.lib.config import QaxConfigProfile, QaxConfig, QaxConfigSpecification


class ProfileGroupBox(QtWidgets.QGroupBox):
    """ Profile selection and display of check tools included in the selected
    profile.
    """

    profile_selected = QtCore.Signal(QaxConfigProfile)
    specification_selected = QtCore.Signal(QaxConfigSpecification)
    # Signal is of type List[QaxConfigCheckTool]
    check_tool_selection_change = QtCore.Signal(object)

    def __init__(self, parent_win, prj, config: QaxConfig):
        QtWidgets.QGroupBox.__init__(self, "Profile and Specification Settings")

        self.prj = prj
        self.parent_win = parent_win
        self.config = config
        self.check_tool_checkboxes = []

        self.selected_profile: QaxConfigProfile = None
        self.selected_specification: QaxConfigSpecification = None

        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        # Profile selection
        self.profile_name_label = QtWidgets.QLabel("Profile:")
        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        vbox_profile_label_selection = QtWidgets.QVBoxLayout()
        vbox_profile_label_selection.setAlignment(QtCore.Qt.AlignTop)
        hbox.addLayout(vbox_profile_label_selection)
        vbox_profile_label_selection.addWidget(self.profile_name_label)

        self.profile_combobox = QtWidgets.QComboBox()
        self.profile_combobox.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        for profile in config.profiles:
            self.profile_combobox.addItem(profile.name, profile)

        self.profile_combobox.currentIndexChanged.connect(self.on_set_profile)
        vbox_profile_label_selection.addWidget(self.profile_combobox)

        self.profile_description_label = QtWidgets.QLabel("")
        self.profile_description_label.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.profile_description_label.setWordWrap(True)
        self.profile_description_label.setStyleSheet("padding-left :5px")
        vbox_profile_label_selection.addWidget(self.profile_description_label)
        vbox_profile_label_selection.setAlignment(self.profile_description_label, QtCore.Qt.AlignTop)

        # Specification selection
        vbox_profile_specification_selection = QtWidgets.QVBoxLayout()
        vbox_profile_specification_selection.setAlignment(QtCore.Qt.AlignTop)
        hbox.addLayout(vbox_profile_specification_selection)
        vbox_profile_specification_selection.addWidget(QtWidgets.QLabel("Standard:"))

        self.specification_combobox = QtWidgets.QComboBox()
        self.specification_combobox.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        self.specification_combobox.currentIndexChanged.connect(self.on_set_specification)
        vbox_profile_specification_selection.addWidget(self.specification_combobox)
        self.specification_description_label = QtWidgets.QLabel("")
        self.specification_description_label.setWordWrap(True)
        self.specification_description_label.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.specification_description_label.setStyleSheet("padding-left :5px")
        vbox_profile_specification_selection.addWidget(self.specification_description_label)
        vbox_profile_specification_selection.setAlignment(self.specification_description_label, QtCore.Qt.AlignTop)

        vbox.addWidget(QHLine())

        check_tools_label = QtWidgets.QLabel("Check Tools:")
        vbox.addWidget(check_tools_label)

        self.check_tools_layout = FlowLayout()
        vbox.addLayout(self.check_tools_layout)

    def initialize(self):
        settings = GuiSettings.settings()
        settings_selected_profile_name = settings.value("selected_profile", defaultValue="None")
        settings_selected_specification_name = settings.value("selected_specification", defaultValue="None")

        self.profile_combobox.setCurrentIndex(0)
        self.on_set_profile(0)
        for index, p in enumerate(self.config.profiles):
            if settings_selected_profile_name != "None" and settings_selected_profile_name == p.name:
                self.profile_combobox.setCurrentIndex(index)
                self.on_set_profile(index)

        for index, s in enumerate(self.selected_profile.specifications):
            if settings_selected_specification_name != "None" and settings_selected_specification_name == s.name:
                self.specification_combobox.setCurrentIndex(index)
                self.on_set_specification(index)

    def update_check_tools(self, profile):
        """ Updates the list of check tool checkboxes based on the given
        profile.
        """
        self.check_tool_checkboxes.clear()

        # clear all items from check tools layout
        for i in reversed(range(self.check_tools_layout.count())):
            self.check_tools_layout.itemAt(i).widget().setParent(None)

        # add new label for each check tool
        for check_tool in profile.check_tools:
            checked_state = QtCore.Qt.CheckState.Checked \
                if check_tool.checked else QtCore.Qt.CheckState.Unchecked
            check_tool_widget = QtWidgets.QCheckBox(check_tool.name, self)
            check_tool_widget.setStyleSheet("padding-right: 30px;")

            # set enabled and checked state based on config file setting
            check_tool_widget.setEnabled(check_tool.enabled)
            check_tool_widget.setCheckState(checked_state)

            # store the check tool to make it easier to obtain list of
            # selected check tools.
            check_tool_widget.setProperty('check_tool', check_tool)
            check_tool_widget.stateChanged.connect(
                self.on_check_tool_check_change)

            self.check_tools_layout.addWidget(check_tool_widget)
            self.check_tool_checkboxes.append(check_tool_widget)

    def update_specifications(self, profile: QaxConfigProfile):
        """ updates the combobox list of specifications with the specifications
        from the selected profile """
        self.specification_combobox.clear()
        for specification in profile.specifications:
            self.specification_combobox.addItem(specification.name, specification)

        if len(profile.specifications) > 0:
            self.specification_combobox.setCurrentIndex(0)
            self.specification_combobox.setEnabled(True)
        else:
            self.specification_combobox.setEnabled(False)
            self.specification_description_label.setText(
                "Profile does not include any specifications"
            )

    def selected_check_tools(self) -> List[QaxConfigCheckTool]:
        """ Gets a list of check tools based on what is selected
        """
        selected_check_tools = [
            cb.property('check_tool')
            for cb in self.check_tool_checkboxes
            if cb.checkState() == QtCore.Qt.CheckState.Checked
        ]
        return selected_check_tools

    def on_set_profile(self, currentIndex):
        """ Event handler for user selection of profile
        """
        profile = self.profile_combobox.itemData(currentIndex)
        self.selected_profile = profile
        if profile.description is not None:
            self.profile_description_label.setText(profile.description)
        else:
            self.profile_description_label.setText("")
        self.update_specifications(profile)
        self.update_check_tools(profile)
        self.profile_selected.emit(profile)
        self.on_check_tool_check_change()

    def on_set_specification(self, currentIndex):
        if currentIndex == -1:
            self.specification_description_label.setText("")
            self.selected_specification = None
            return

        specification = self.specification_combobox.itemData(currentIndex)
        self.selected_specification = specification
        if specification.description is not None:
            self.specification_description_label.setText(specification.description)

        self.specification_selected.emit(specification)

    def on_check_tool_check_change(self):
        """ Event handler for user selection change of individual check tool
        """
        self.check_tool_selection_change.emit(self.selected_check_tools())

    def update_ui(self, qajson: QajsonRoot) -> NoReturn:
        # we don't save the profile in the qajson file, so there's nothing we
        # can do here till qajson is updated
        pass

    def persist_exit_settings(self):
        settings = GuiSettings.settings()

        if self.selected_profile is None:
            settings.setValue("selected_profile", "None")
        else:
            settings.setValue("selected_profile", self.selected_profile.name)

        if self.selected_specification is None:
            settings.setValue("selected_specification", "None")
        else:
            settings.setValue("selected_specification", self.selected_specification.name)
