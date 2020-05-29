from PySide2 import QtCore, QtGui, QtWidgets, QtQuickWidgets
from PySide2.QtCore import QObject, Signal, Property
from PySide2.QtQuick import QQuickView
from PySide2.QtCore import QUrl
from PySide2.QtGui import QColor
from PySide2.QtPositioning import QGeoPath, QGeoCoordinate
import os

from ausseabed.qajson.model import QajsonCheck
from hyo2.qax.app.widgets.qax.map_utils import MarkerItem, LineItem, \
    MarkersModel, LinesModel


class Manager(QtCore.QObject):
    name_changed = Signal(str)
    messages_changed = Signal()
    input_files_changed = Signal()
    map_lines_changed = Signal()
    selected_properties_changed = Signal()
    selected_properties_table_changed = Signal()

    def __init__(self, parent=None):
        super(Manager, self).__init__(parent)
        self._check = None
        self._selected_properties = {}
        self._selected_properties_table = []

    @Property(str, notify=name_changed)
    def name(self):
        if self._check is None:
            return "n/a"
        return self._check.info.name

    @Property('QVariantList', notify=messages_changed)
    def messages(self):
        if self._check is None:
            return []
        return self._check.outputs.messages

    @Property('QVariantList', notify=input_files_changed)
    def input_files(self):
        if self._check is None:
            return []
        return [f.path for f in self._check.inputs.files]

    @Property('QVariantList', notify=selected_properties_table_changed)
    def selected_properties_table(self):
        return self._selected_properties_table

    def get_selected_properties(self):
        return self._selected_properties

    def set_selected_properties(self, value):
        # check that a dictionary was previously selected, and that the
        # keys are the same in old and new selections. This ensures we only
        # track changes when the same kind of thing is selected.
        d_1 = self._selected_properties
        d_2 = value
        changed_props = {}
        if (self._selected_properties is not None
                and set(d_1.keys()) == set(d_2.keys())):
            changed_props = {
                k: d_2[k]
                for k, _ in set(d_2.items()) - set(d_1.items())
            }

        self._selected_properties = value

        props_table = []
        import random
        for key, value in self._selected_properties.items():
            props_table.append({
                'key': key,
                'value': value,
                'changed': key in changed_props
            })
        self._selected_properties_table = props_table

        self.selected_properties_changed.emit()
        self.selected_properties_table_changed.emit()

    selected_properties = Property(
        'QVariantMap',
        fget=get_selected_properties,
        fset=set_selected_properties,
        notify=selected_properties_changed
    )

    def set_check(self, check):
        self._selected_properties = {}
        self._selected_properties_table = []
        self._check = check
        self.name_changed.emit(self._check.info.name)
        self.messages_changed.emit()
        self.input_files_changed.emit()
        self.selected_properties_changed.emit()
        self.selected_properties_table_changed.emit()


class ScoreboardDetailsWidget(QtWidgets.QGroupBox):

    def __init__(self, parent=None):
        QtWidgets.QGroupBox.__init__(self, "Details", parent=parent)

        view = QtQuickWidgets.QQuickWidget()
        rc = view.rootContext()

        self.manager = Manager()
        rc.setContextProperty('manager', self.manager)

        self.markersModel = MarkersModel()
        rc.setContextProperty('markersModel', self.markersModel)

        self.linesModel = LinesModel()
        rc.setContextProperty('linesModel', self.linesModel)

        url = QUrl.fromLocalFile(os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "scoreboard_details.qml")
        )
        view.setSource(url)
        view.setResizeMode(QtQuickWidgets.QQuickWidget.SizeRootObjectToView)
        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)
        vbox.addWidget(view)

    def get_check_geojson(self, check):
        if (check is None or
                check.outputs is None or
                check.outputs.data is None or
                'map' not in check.outputs.data):
            # if there's no map data just return None
            return None
        return check.outputs.data['map']

    def set_selected_check(self, check: QajsonCheck):
        self.markersModel.removeAllMarkers()
        self.linesModel.removeAllLines()
        geojson = self.get_check_geojson(check)
        if geojson is not None:
            self.markersModel.addMarkersFromGeojson(geojson)
            self.linesModel.addLinesFromGeojson(geojson, color='blue')

        self.manager.set_check(check)
