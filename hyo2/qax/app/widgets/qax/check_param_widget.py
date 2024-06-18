from ausseabed.qajson.model import QajsonParam
from PySide2 import QtCore, QtGui, QtWidgets
from typing import Optional, NoReturn, List

from hyo2.qax.app.gui_settings import GuiSettings
from hyo2.qax.lib.plugin import QaxCheckReference


def get_param_widget(param: QajsonParam, parent=None) -> 'CheckParamWidget':
    """ Returns a `CheckParamWidget` of the correct type for the given
    param. Factory method.
    """
    # todo: implementation here will need to change to support more advanced
    # parameter types
    if param.options is not None:
        return CheckParamOptionsWidget(param, parent)
    elif isinstance(param.value, str):
        return CheckParamStringWidget(param, parent)
    elif isinstance(param.value, bool):
        return CheckParamBoolWidget(param, parent)
    elif isinstance(param.value, int):
        return CheckParamIntWidget(param, parent)
    elif isinstance(param.value, float):
        return CheckParamFloatWidget(param, parent)
    else:
        # special case. Return a widget that doesn't allow modification.
        # it simply shows that this is an unsupported type.
        return CheckParamUnknownWidget(param, parent)


class CheckParamWidget(QtWidgets.QWidget):
    """ base class for all CheckParamWidgets. These show the parameter details
    to the user, allow modification, and perform validation of user entered
    data.
    """

    # emitted when a new file is selected
    value_changed = QtCore.Signal(QajsonParam)

    def __init__(self, param: QajsonParam, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        self._param = param
        self.label_min_width = 200

    def param(self) -> QajsonParam:
        ''' Will return valid QajsonParam if user has entered valid data, otherwise
        None for invalid data.
        '''
        raise NotImplementedError(
            "Must implement in param function of child class to return "
            "correct value type within an QajsonParam")

    def _on_edited(self, *args, **kwargs) -> NoReturn:
        sender = self.sender()
        validation_color = self.check_state_color(sender)
        self._set_validation_color(validation_color)
        self._raise_value_changed(self.param())

    def _raise_value_changed(self, param: QajsonParam) -> NoReturn:
        self.value_changed.emit(param)

    @property
    def value(self):
        return self.param().value

    @value.setter
    def value(self, value):
        raise NotImplementedError("Must implement in child class")

    def check_state_color(self, sender):
        try:
            validator = sender.validator()
        except AttributeError as ae:
            # then this component has no validator, so skip validation
            return None
        if validator is None:
            # then this component doesn't need validation (eg; could be a
            # checkbox that has only valid states)
            return None
        state = validator.validate(sender.text(), 0)[0]
        if state == QtGui.QValidator.Acceptable:
            color = '#c4df9b'  # green
        else:
            color = '#f6989d'  # red
        return color

    def _set_validation_color(self, color):
        # each child class must implement this method to show a validation color.
        # How this is shown is up to the component.
        pass


class CheckParamStringWidget(CheckParamWidget):
    """ Supports parameters with string value types
    """

    def __init__(self, param: QajsonParam, parent=None):
        super().__init__(param, parent=parent)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(hbox)

        label_name = QtWidgets.QLabel("{}".format(self._param.name))
        label_name.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        label_name.setMinimumWidth(self.label_min_width)
        label_name.setStyleSheet(GuiSettings.stylesheet_check_param_name())
        hbox.addWidget(label_name)

        self.lineedit_value = QtWidgets.QLineEdit()
        self.lineedit_value.setText(self._param.value)
        self.lineedit_value.textEdited.connect(self._on_edited)
        hbox.addWidget(self.lineedit_value)

    def param(self) -> QajsonParam:
        if len(self.lineedit_value.text()) == 0:
            return None
        return QajsonParam(
            name=self._param.name,
            value=self.lineedit_value.text()
        )

    @CheckParamWidget.value.setter
    def value(self, value):
        self.lineedit_value.setText(str(value))

    def _set_validation_color(self, color):
        self.lineedit_value.setStyleSheet(
            f"QLineEdit {{ background-color: {color} }}"
        )


class CheckParamIntWidget(CheckParamWidget):
    """ Supports parameters with int value types
    """

    def __init__(self, param: QajsonParam, parent=None):
        super().__init__(param, parent=parent)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(hbox)

        label_name = QtWidgets.QLabel("{}".format(self._param.name))
        label_name.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        label_name.setMinimumWidth(self.label_min_width)
        label_name.setStyleSheet(GuiSettings.stylesheet_check_param_name())
        hbox.addWidget(label_name)

        self.lineedit_value = QtWidgets.QLineEdit()
        validator = QtGui.QIntValidator()
        self.lineedit_value.setValidator(validator)
        self.lineedit_value.setText(str(self._param.value))
        self.lineedit_value.textEdited.connect(self._on_edited)
        hbox.addWidget(self.lineedit_value)

    def param(self) -> QajsonParam:
        if len(self.lineedit_value.text()) == 0:
            return None
        return QajsonParam(
            name=self._param.name,
            value=int(self.lineedit_value.text())
        )

    @CheckParamWidget.value.setter
    def value(self, value):
        self.lineedit_value.setText(str(value))

    def _set_validation_color(self, color):
        self.lineedit_value.setStyleSheet(
            f"QLineEdit {{ background-color: {color} }}"
        )


class CheckParamBoolWidget(CheckParamWidget):
    """ Supports parameters with bool value types
    """

    def __init__(self, param: QajsonParam, parent=None):
        super().__init__(param, parent=parent)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setAlignment(QtCore.Qt.AlignLeft)
        self.setLayout(hbox)

        label_name = QtWidgets.QLabel(f"{self._param.name}")
        label_name.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        label_name.setMinimumWidth(self.label_min_width)
        label_name.setStyleSheet(GuiSettings.stylesheet_check_param_name())
        hbox.addWidget(label_name)

        self.checkbox = QtWidgets.QCheckBox()
        self.checkbox.setChecked(self._param.value)
        self.checkbox.stateChanged.connect(self._on_edited)
        hbox.addWidget(self.checkbox)

    def param(self) -> QajsonParam:
        return QajsonParam(
            name=self._param.name,
            value=self.checkbox.isChecked()
        )

    @CheckParamWidget.value.setter
    def value(self, value):
        self.checkbox.setChecked(value)


class CheckParamFloatWidget(CheckParamWidget):
    """ Supports parameters with int value types
    """

    def __init__(self, param: QajsonParam, parent=None):
        super().__init__(param, parent=parent)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(hbox)

        label_name = QtWidgets.QLabel("{}".format(self._param.name))
        label_name.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        label_name.setMinimumWidth(self.label_min_width)
        label_name.setStyleSheet(GuiSettings.stylesheet_check_param_name())
        hbox.addWidget(label_name)

        self.lineedit_value = QtWidgets.QLineEdit()
        validator = QtGui.QDoubleValidator()
        self.lineedit_value.setValidator(validator)
        self.lineedit_value.setText(str(self._param.value))
        self.lineedit_value.textEdited.connect(self._on_edited)
        hbox.addWidget(self.lineedit_value)

    def param(self) -> QajsonParam:
        if len(self.lineedit_value.text()) == 0:
            return None
        return QajsonParam(
            name=self._param.name,
            value=float(self.lineedit_value.text())
        )

    @CheckParamWidget.value.setter
    def value(self, value):
        self.lineedit_value.setText(str(value))

    def _set_validation_color(self, color):
        self.lineedit_value.setStyleSheet(
            f"QLineEdit {{ background-color: {color} }}"
        )


class CheckParamUnknownWidget(CheckParamWidget):
    """ Supports parameters with string value types
    """

    def __init__(self, param: QajsonParam, parent=None):
        super().__init__(param, parent=parent)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(hbox)

        label_name = QtWidgets.QLabel(
            "Unknown param type: {}".format(self._param.name))
        label_name.setMinimumWidth(self.label_min_width)
        label_name.setStyleSheet(GuiSettings.stylesheet_check_param_name())
        hbox.addWidget(label_name)

    def param(self) -> QajsonParam:
        return QajsonParam(
            name=self._param.name,
            value=None
        )

    @CheckParamWidget.value.setter
    def value(self, value):
        pass


class CheckParamOptionsWidget(CheckParamWidget):
    """ Supports parameters with string value types
    """

    def __init__(self, param: QajsonParam, parent=None):
        super().__init__(param, parent=parent)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(hbox)

        label_name = QtWidgets.QLabel("{}".format(self._param.name))
        label_name.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        label_name.setMinimumWidth(self.label_min_width)
        label_name.setStyleSheet(GuiSettings.stylesheet_check_param_name())
        hbox.addWidget(label_name)

        self.cb_value = QtWidgets.QComboBox()
        self.cb_value.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.Preferred
        )
        for option in param.options:
            self.cb_value.addItem(str(option), option)

        self.cb_value.setCurrentIndex(param.options.index(param.value))
        self.cb_value.currentIndexChanged.connect(self._on_edited)
        hbox.addWidget(self.cb_value)

    def param(self) -> QajsonParam:
        currentIndex = self.cb_value.currentIndex()
        return QajsonParam(
            name=self._param.name,
            value=self.cb_value.itemData(currentIndex)
        )

    @CheckParamWidget.value.setter
    def value(self, value):
        new_index = self._param.options.index(value)
        self.cb_value.setCurrentIndex(new_index)

    def _set_validation_color(self, color):
        self.cb_value.setStyleSheet(
            f"QComboBox {{ background-color: {color}; }}"
            f"QComboBox::drop-down {{ background-color: {color}; }}"
            f"QComboBox QAbstractItemView {{ background-color: {color}; }}"
        )
