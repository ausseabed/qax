from PySide2 import QtCore, QtGui, QtWidgets

from hyo2.qax.app.gui_settings import GuiSettings
from hyo2.qax.lib.plugin import QaxCheckReference
from hyo2.qax.app.widgets.lines import QHLine
from hyo2.qax.app.widgets.qax.check_param_widget import CheckParamWidget, \
    get_param_widget


class CheckWidget(QtWidgets.QWidget):
    """ Display details for single check
    """

    def __init__(self, check_reference: QaxCheckReference, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        self.check_reference = check_reference
        self.param_widgets = []

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
            params_label = QtWidgets.QLabel("Parameters")
            params_layout.addWidget(params_label)
            params_label.setStyleSheet(
                "QLabel { font-weight: bold; "
                "padding: 0px 0px 0px 0px;}")
            hbox.addLayout(params_layout)
            for check_param in self.check_reference.default_input_params:
                widget_param = get_param_widget(check_param)
                params_layout.addWidget(widget_param)
                self.param_widgets.append(widget_param)
            hbox.addSpacing(10)

        vbox.addWidget(QHLine())

    def get_check_id_and_params(self):
        """ Returns a tuple. First element of each tuple is the check
        id, second element is the list of params for the check. Information is
        returned in this manner to support updating qa json.
        """
        params = [param_widget.param() for param_widget in self.param_widgets]
        res = (self.check_reference.id, params)
        return res
