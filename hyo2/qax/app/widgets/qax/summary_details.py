from PySide2 import QtCore, QtGui, QtWidgets, QtQuickWidgets
from PySide2.QtCore import QObject, Signal, Property
from PySide2.QtQuick import QQuickView
from PySide2.QtCore import QUrl
from PySide2.QtGui import QColor
from PySide2.QtPositioning import QGeoPath, QGeoCoordinate
import os

from ausseabed.qajson.model import QajsonCheck
from hyo2.qax.app.widgets.qax.map_utils import MarkerItem, LineItem, \
    MarkersModel, LinesModel, PolygonsModel
from hyo2.qax.lib.project import QaCheckSummary

# from https://colorbrewer2.org/#type=qualitative&scheme=Paired&n=8
# but without the blue colors as they blend in too much with water
colors = [
    '#b2df8a',
    '#33a02c',
    '#fb9a99',
    '#e31a1c',
    '#fdbf6f',
    '#ff7f00',
    '#6a3d9a',
]


def color_with_alpha(color: str, alpha: str):
    ''' Inserts a hex alpha value into an existing hex color. eg: color = #b2df8a
    with alpha = 80 would return #80b2df8a
    '''
    assert len(color) == 7
    assert len(alpha) == 2
    assert color[0] == '#'
    return f'#{alpha}{color[1:]}'


class Manager(QtCore.QObject):
    summary_changed = Signal()
    selected_properties_changed = Signal()
    selected_properties_table_changed = Signal()

    def __init__(self, parent=None):
        super(Manager, self).__init__(parent)
        self._summary = None
        self._selected_properties = {}
        self._selected_properties_table = []

    @Property(str, notify=summary_changed)
    def name(self):
        if self._summary is None:
            return "n/a"
        return self._summary.name

    @Property(str, notify=summary_changed)
    def version(self):
        if self._summary is None:
            return "n/a"
        return self._summary.version

    @Property(str, notify=summary_changed)
    def data_level(self):
        if self._summary is None:
            return "n/a"
        return self._summary.data_level

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

    def set_summary(self, summary: QaCheckSummary):
        self._selected_properties = {}
        self._selected_properties_table = []
        self._summary = summary
        self.summary_changed.emit()
        self.selected_properties_changed.emit()
        self.selected_properties_table_changed.emit()


class SummaryDetailsWidget(QtWidgets.QGroupBox):

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

        self.polygonsModel = PolygonsModel()
        rc.setContextProperty('polygonsModel', self.polygonsModel)

        url = QUrl.fromLocalFile(os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "summary_details.qml")
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

    def set_selected_summary(self, summary: QaCheckSummary):
        self.markersModel.remove_all()
        self.linesModel.remove_all()
        self.polygonsModel.remove_all()

        for idx, check in enumerate(summary.checks):
            geojson = self.get_check_geojson(check)
            if geojson is None:
                continue

            color = colors[idx % len(colors)]
            self.markersModel.add_from_geojson(geojson, color=color)
            self.linesModel.add_from_geojson(geojson, color=color)
            color_transparent = color_with_alpha(color, '80')
            self.polygonsModel.add_from_geojson(
                geojson,
                color=color_transparent,
                line_color=color
            )

        self.manager.set_summary(summary)
