from ausseabed.qajson.model import QajsonRoot, QajsonParam
from PySide2 import QtCore, QtGui, QtWidgets
from typing import Optional, NoReturn, List

from hyo2.qax.app.gui_settings import GuiSettings
from hyo2.qax.app.widgets.lines import QHLine
from hyo2.qax.app.widgets.qax.check_param_widget import CheckParamWidget, \
    get_param_widget
from hyo2.qax.app.widgets.qax.manual import ManualButton
from hyo2.qax.lib.plugin import QaxCheckReference
from hyo2.qax.lib.config import QaxConfigSpecification


class CheckWidget(QtWidgets.QWidget):
    """ Display details for single check
    """

    check_changed = QtCore.Signal(QaxCheckReference)

    def __init__(self, check_reference: QaxCheckReference, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        self.check_reference = check_reference
        self.param_widgets: List[CheckParamWidget] = []

        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 4, 0, 4)
        self.setLayout(vbox)

        label_name = QtWidgets.QLabel("{}".format(self.check_reference.name))
        label_name.setStyleSheet(GuiSettings.stylesheet_check_titles())
        vbox.addWidget(label_name)

        if self.check_reference.description is not None:
            label_description = QtWidgets.QLabel(
                "{}".format(self.check_reference.description))
            vbox.addWidget(label_description)

        if (
            (self.check_reference.default_input_params is None) or
            (len(self.check_reference.default_input_params) == 0)
        ):
            hbox = QtWidgets.QHBoxLayout()
            hbox.addStretch()
            label_no_params = QtWidgets.QLabel(
                "Check accepts no input parameters")
            hbox.addWidget(label_no_params)
            hbox.addStretch()
            vbox.addLayout(hbox)
        else:
            hbox = QtWidgets.QHBoxLayout()
            hbox.addSpacing(30)
            vbox.addLayout(hbox)

            params_layout = QtWidgets.QVBoxLayout()
            params_label_layout = QtWidgets.QHBoxLayout()
            params_label = QtWidgets.QLabel("Parameters")
            params_label.setStyleSheet(
                "QLabel { font-weight: bold; "
                "padding: 0px 0px 0px 0px;}"
            )
            params_label_layout.addWidget(params_label)
            if check_reference.parameter_help_link is not None:
                params_help = ManualButton(
                    check_reference.parameter_help_link,
                    f"Show {check_reference.name} parameters help"
                )
                params_label_layout.addWidget(params_help)
            params_label_layout.addStretch(1)
            params_layout.addLayout(params_label_layout)

            hbox.addLayout(params_layout)
            for check_param in self.check_reference.default_input_params:
                widget_param = get_param_widget(check_param)
                widget_param.value_changed.connect(self._param_value_changed)
                params_layout.addWidget(widget_param)
                self.param_widgets.append(widget_param)
            hbox.addSpacing(10)

        vbox.addWidget(QHLine())

    def _param_value_changed(self, param: QajsonParam):
        self.check_changed.emit(self.check_reference)

    def get_check_id_and_params(self):
        """ Returns a tuple. First element of each tuple is the check
        id, second element is the list of params for the check. Information is
        returned in this manner to support updating qa json.
        """
        params = [param_widget.param() for param_widget in self.param_widgets]
        res = (self.check_reference.id, params)
        return res

    def update_ui(self, qajson: QajsonRoot) -> NoReturn:
        data_levels = ['raw_data', 'survey_products', 'chart_adequacy']
        # build list of all checks from all data levels
        this_check = None
        for dl in data_levels:
            data_level = getattr(qajson.qa, dl, None)
            if data_level is None:
                continue
            for check in data_level.checks:
                if check.info.id == self.check_reference.id:
                    this_check = check
                    break

        if this_check is None:
            # then whatever check was in the qajson is not being shown in the
            # UI, so we can't update it.
            return

        for check_param in this_check.inputs.params:
            for widget_param in self.param_widgets:
                if check_param.name == widget_param.param().name:
                    widget_param.value = check_param.value

    def set_specification(self, specification: QaxConfigSpecification):
        check_spec = specification.get_config_check(self.check_reference.id)
        if check_spec is None:
            # then there's no details for this check in the specification
            return
        for param_widget in self.param_widgets:
            for config_param in check_spec.parameters:
                if (param_widget.param().name == config_param.name):
                    param_widget.value = config_param.value
