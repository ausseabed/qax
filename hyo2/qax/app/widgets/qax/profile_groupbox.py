from pathlib import Path
from PySide2 import QtCore, QtGui, QtWidgets
from typing import List, NoReturn
import os
import logging

from hyo2.qax.app.widgets.layout import FlowLayout
from hyo2.qax.app.widgets.lines import QHLine
from hyo2.qax.lib.config import QaxConfigCheckTool
from hyo2.qax.lib.config import QaxConfigProfile


class ProfileGroupBox(QtWidgets.QGroupBox):
    """ Profile selection and display of check tools included in the selected
    profile.
    """

    profile_selected = QtCore.Signal(QaxConfigProfile)
    # Signal is of type List[QaxConfigCheckTool]
    check_tool_selection_change = QtCore.Signal(object)

    def __init__(self, parent_win, prj, config):
        QtWidgets.QGroupBox.__init__(self, "Profile Settings")

        self.label_size = 160

        self.prj = prj
        self.parent_win = parent_win
        self.config = config
        self.check_tool_checkboxes = []

        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        self.profile_name_label = QtWidgets.QLabel("Profile:")
        hbox = QtWidgets.QHBoxLayout()
        hbox.setAlignment(QtCore.Qt.AlignLeft)
        vbox.addLayout(hbox)
        hbox.addWidget(self.profile_name_label)

        self.profile_combobox = QtWidgets.QComboBox()
        for profile in config.profiles:
            self.profile_combobox.addItem(profile.name, profile)

        self.profile_combobox.currentIndexChanged.connect(self.on_set_profile)
        hbox.addWidget(self.profile_combobox)
        self.setStyleSheet("QComboBox { min-width:400px; }")

        self.profile_description_label = QtWidgets.QLabel("")
        hbox.addWidget(self.profile_description_label)

        vbox.addWidget(QHLine())

        check_tools_label = QtWidgets.QLabel("Check Tools:")
        vbox.addWidget(check_tools_label)

        self.check_tools_layout = FlowLayout()
        vbox.addLayout(self.check_tools_layout)

    def initialize(self):
        self.profile_combobox.setCurrentIndex(0)
        self.on_set_profile(0)

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
            check_tool_widget.setFixedWidth(self.label_size)

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
        if profile.description is not None:
            self.profile_description_label.setText(profile.description)
        self.update_check_tools(profile)
        self.profile_selected.emit(profile)
        self.on_check_tool_check_change()

    def on_check_tool_check_change(self):
        """ Event handler for user selection change of individual check tool
        """
        self.check_tool_selection_change.emit(self.selected_check_tools())
