from ausseabed.qajson.model import QajsonRoot
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QSizePolicy
from typing import Optional, NoReturn, List, Any
import logging

from hyo2.qax.app.gui_settings import GuiSettings
from hyo2.qax.app.widgets.qax.check_widget import CheckWidget
from hyo2.qax.lib.config import QaxConfigSpecification
from hyo2.qax.lib.plugin import QaxCheckToolPlugin, QaxCheckReference
from hyo2.qax.lib.project import QAXProject


logger = logging.getLogger(__name__)


class PluginTab(QtWidgets.QWidget):

    plugin_changed = QtCore.Signal(QaxCheckToolPlugin)

    def __init__(self, parent_win, prj: QAXProject, plugin: QaxCheckToolPlugin):
        QtWidgets.QWidget.__init__(self)

        # store a project reference
        self.prj = prj
        self.parent_win = parent_win
        # self.media = self.parent_win.media
        self.plugin = plugin

        self.check_widgets: list[CheckWidget] = []

        self.vbox = QtWidgets.QVBoxLayout()
        self.setLayout(self.vbox)

        # title
        label_name = QtWidgets.QLabel(plugin.name)
        label_name.setStyleSheet(GuiSettings.stylesheet_plugin_tab_titles())
        self.vbox.addWidget(label_name)

        # description (if one is include in config)
        if plugin.description is not None:
            label_desc = QtWidgets.QLabel(plugin.description)
            self.vbox.addWidget(label_desc)

        self.groupbox_checks = QtWidgets.QGroupBox("Checks")
        self.groupbox_checks.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.vbox.addWidget(self.groupbox_checks)

        layout_gb_checks = QtWidgets.QVBoxLayout()
        layout_gb_checks.setContentsMargins(0, 8, 0, 0)
        self.groupbox_checks.setLayout(layout_gb_checks)

        self.scrollarea_checks = QtWidgets.QScrollArea()
        self.scrollarea_checks.setWidgetResizable(True)
        self.scrollarea_checks.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollarea_checks.setStyleSheet("QScrollArea { border: none;}")
        layout_gb_checks.addWidget(self.scrollarea_checks)

        self.widget_checks = QtWidgets.QWidget()
        self.layout_checks = QtWidgets.QVBoxLayout(self.widget_checks)

        self.scrollarea_checks.setWidget(self.widget_checks)

    def _on_check_changed(self, check_reference: QaxCheckReference):
        self.plugin_changed.emit(self.plugin)


    def get_check_ids_and_params(self):
        """ Returns a list of tuples. First element of each tuple is the check
        id, second element is the list of params for the check. Information is
        returned in this manner to support updating qa json.
        """
        check_ids_and_params = [
            check_widget.get_check_id_and_params()
            for check_widget in self.check_widgets]
        return check_ids_and_params

    def set_selected_checks(self, checks: list[QaxCheckReference], standard: QaxConfigSpecification|None = None):

        # cache info users may have entered into the plugin params
        # just because they've removed a check doesn't mean we should
        # throw away info that was given to other checks that haven't been
        # removed.
        user_input_cache: dict[str, dict[str, Any]] = {}
        for cw in self.check_widgets:
            user_input_cache[cw.check_reference.id] = cw.get_params_and_values()

        # clear out any existing check parameter widgets
        self.check_widgets.clear()

        while self.layout_checks.count():
            item = self.layout_checks.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # track whether we've added any checks on this plugin tab
        no_checks_added = True
        for check in self.plugin.checks():
            # we only add check widgets for the checks that have been selected
            selected_check = next((x for x in checks if x.id == check.id), None)
            if selected_check is not None:
                check_widget = CheckWidget(check)
                check_widget.check_changed.connect(self._on_check_changed)
                self.layout_checks.addWidget(check_widget)
                self.check_widgets.append(check_widget)
                no_checks_added = False

        if no_checks_added:
            nothing_label = QtWidgets.QLabel("No checks have been selected for this plugin")
            self.layout_checks.addWidget(nothing_label)

        # set state of check widgets to what they were before the UI was rebuilt
        # assuming the check wasn't removed.
        for cw in self.check_widgets:
            if cw.check_reference.id in user_input_cache:
                cw.set_params_and_values(user_input_cache[cw.check_reference.id])
            elif standard is not None:
                # then get values from the currently selected standard
                check = standard.get_config_check(cw.check_reference.id)
                if check is not None:
                    standard_p_and_v: dict[str, Any] = {}
                    for p in check.parameters:
                        standard_p_and_v[p.name] = p.value
                    cw.set_params_and_values(standard_p_and_v)

        self.layout_checks.addStretch(1)

    def update_ui(self, qajson: QajsonRoot) -> NoReturn:
        for check_widget in self.check_widgets:
            check_widget.update_ui(qajson)

    def set_specification(self, specification: QaxConfigSpecification):
        for check_widget in self.check_widgets:
            check_widget.set_specification(specification)
