import os
import logging
from pathlib import Path
from PySide2 import QtCore, QtGui, QtWidgets

from hyo2.qax.app.widgets.layout import FlowLayout
from hyo2.qax.lib.config import QaxConfigProfile


class ProfileGroupBox(QtWidgets.QGroupBox):
    """ Profile selection and display of check tools included in the selected
    profile.
    """

    profile_selected = QtCore.Signal(QaxConfigProfile)

    def __init__(self, parent_win, prj, config):
        QtWidgets.QGroupBox.__init__(self, "Profile Settings")

        self.label_size = 160

        self.prj = prj
        self.parent_win = parent_win
        self.config = config

        self.setStyleSheet("QGroupBox::title { color: rgb(155, 155, 155); }")

        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        self.profile_name_label = QtWidgets.QLabel("Profile:")
        hbox = QtWidgets.QHBoxLayout(self)
        hbox.setAlignment(QtCore.Qt.AlignLeft)
        vbox.addLayout(hbox)
        hbox.addWidget(self.profile_name_label)

        self.profile_combobox = QtWidgets.QComboBox()
        for profile in config.profiles:
            self.profile_combobox.addItem(profile.name, profile)

        self.profile_combobox.currentIndexChanged.connect(self.on_set_profile)
        hbox.addWidget(self.profile_combobox)
        self.profile_combobox.setMinimumWidth(300)
        self.profile_combobox.setFixedWidth(300)

        self.profile_description_label = QtWidgets.QLabel("")
        hbox.addWidget(self.profile_description_label)

        self.check_tools_layout = FlowLayout()
        vbox.addLayout(self.check_tools_layout)

        self.profile_combobox.setCurrentIndex(0)
        self.on_set_profile(0)

    def update_check_tools(self, profile):
        """ Updates the list of check tool checkboxes based on the given
        profile.
        """
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

            self.check_tools_layout.addWidget(check_tool_widget)

    def on_set_profile(self, currentIndex):
        """ Event handler for user selection of profile
        """
        profile = self.profile_combobox.itemData(currentIndex)
        if profile.description is not None:
            self.profile_description_label.setText(profile.description)
        self.update_check_tools(profile)
        self.profile_selected.emit(profile)
