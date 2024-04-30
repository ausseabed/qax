from ausseabed.qajson.model import QajsonRoot
from pathlib import Path
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QSizePolicy
from typing import NoReturn

from hyo2.qax.app import qta
from hyo2.qax.app.gui_settings import GuiSettings
from hyo2.qax.app.widgets.layout import FlowLayout
from hyo2.qax.app.widgets.lines import QHLine
from hyo2.qax.app.widgets.qax.manual import ManualLabelButton
import hyo2.qax.app.widgets.qax.manual_links as manual_links
from hyo2.qax.lib.plugin import QaxPlugins, QaxCheckReference
from hyo2.qax.lib.config import QaxConfigProfile, QaxConfig, QaxConfigSpecification


class CheckCheckBox(QtWidgets.QCheckBox):
    """ Subclass for checkbox widget to allow it to maintain a reference to
    a QaxCheckReference
    """
    def __init__(self, *args, **kwargs):
        QtWidgets.QCheckBox.__init__(self, *args, **kwargs)
        self._check: QaxCheckReference | None = None

    def check(self):
        return self._check

    def setCheck(self, check: QaxCheckReference):
        self._check = check


class ProfileGroupBox(QtWidgets.QGroupBox):
    """ Profile selection and display of check tools included in the selected
    profile.
    """

    profile_selected = QtCore.Signal(QaxConfigProfile)
    specification_selected = QtCore.Signal(QaxConfigSpecification)
    # Signal is of type List[QaxConfigCheckTool]
    check_selection_change = QtCore.Signal(object)

    def __init__(self, parent_win, prj, config: QaxConfig):
        QtWidgets.QGroupBox.__init__(self, "Profile and Specification Settings")

        self.prj = prj
        self.parent_win = parent_win
        self.config = config
        self.check_checkboxes: list[CheckCheckBox] = []

        self.selected_profile: QaxConfigProfile = None
        self.selected_specification: QaxConfigSpecification = None

        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        vbox_profile_label_selection = QtWidgets.QVBoxLayout()
        vbox_profile_label_selection.setAlignment(QtCore.Qt.AlignTop)
        hbox.addLayout(vbox_profile_label_selection)
        vbox_profile_label_selection.addWidget(ManualLabelButton(
            manual_links.INTERFACE_PROFILE,
            "Profile:",
            "Show profile help"
        ))

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
        vbox_profile_specification_selection.addWidget(ManualLabelButton(
            manual_links.INTERFACE_STANDARD,
            "Standard:",
            "Show Standards help"
        ))

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

        vbox.addWidget(ManualLabelButton(
            manual_links.INTERFACE_CHECK_TOOL_SELECTION,
            "Check Tools:",
            "Show check tool selection help"
        ))

        self.check_tools_layout = QtWidgets.QVBoxLayout()
        self.check_tools_layout.setSpacing(12)
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

    def __clear_layout(self, layout: QtWidgets.QLayout):
        """ Recursively remove all widgets from the given layout and any nested layouts.
        """
        if layout is None:
            return

        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                sublayout = item.layout()
                if sublayout:
                    self.__clear_layout(sublayout)

    def update_check_tools(self, profile: QaxConfigProfile):
        """ Updates the list of check tool checkboxes based on the given
        profile.
        """
        self.check_checkboxes.clear()
        self.__clear_layout(self.check_tools_layout)

        # add new label for each check tool
        for check_tool in profile.check_tools:
            check_tool_layout = QtWidgets.QHBoxLayout()
            self.check_tools_layout.addLayout(check_tool_layout)

            check_tool_label = QtWidgets.QLabel(check_tool.name)
            check_tool_label.setMinimumWidth(120)
            check_tool_label.setAlignment(QtCore.Qt.AlignTop)
            check_tool_label.setStyleSheet("font-weight: bold")

            check_tool_label.setSizePolicy(
                QSizePolicy.Minimum, QSizePolicy.Minimum)
            check_tool_layout.addWidget(check_tool_label)

            checks_frame = QtWidgets.QFrame()
            checks_layout = FlowLayout()
            checks_frame.setLayout(checks_layout)

            checks_frame.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Minimum)
            check_tool_layout.addWidget(checks_frame)

            check_tool_plugin = QaxPlugins.instance().get_plugin(
                profile_name=self.selected_profile.name,
                check_tool_class=check_tool.plugin_class
            )

            for check_ref in check_tool_plugin.checks():
                check_widget = CheckCheckBox(check_ref.name, self)
                check_widget.setCheck(check_ref)
                check_widget.setMinimumWidth(150)
                check_widget.setStyleSheet("padding-right: 10px;")
                check_widget.stateChanged.connect(
                    self.on_check_change
                )
                checks_layout.addWidget(check_widget)

                self.check_checkboxes.append(check_widget)

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

    def selected_checks(self) -> list[QaxCheckReference]:
        """ Gets a list of checks that have been selected
        """
        checks = [
            ccb.check()
            for ccb in self.check_checkboxes
            if ccb.checkState() == QtCore.Qt.CheckState.Checked
        ]
        return checks

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
        self.on_check_change()

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

    def on_check_change(self):
        """ Event handler for user selection change of individual checks
        """
        self.check_selection_change.emit(self.selected_checks())

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
