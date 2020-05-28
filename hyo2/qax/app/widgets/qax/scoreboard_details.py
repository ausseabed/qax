from PySide2 import QtCore, QtGui, QtWidgets, QtQuickWidgets
from PySide2.QtCore import QObject, Signal, Property
from PySide2.QtQuick import QQuickView
from PySide2.QtCore import QUrl
from PySide2.QtPositioning import QGeoPath, QGeoCoordinate
from ausseabed.qajson.model import QajsonCheck

from PySide.QtCore import QAbstractListModel, QModelIndex, Qt


import os

#
# class SimpleListModel(QAbstractListModel):
#     def __init__(self, mlist):
#         QAbstractListModel.__init__(self)
#
#         # Cache the passed data list as a class member.
#         self._items = mlist
#
#         # We need to tell the view how many rows we have present in our data.
#         # For us, at least, it's fairly straightforward, as we have a python list of data,
#         # so we can just return the length of that list.
#         def rowCount(self, parent = QModelIndex()):
#             return len(self._items)
#
#         def data(self, index, role = Qt.DisplayRole):
#             if role == Qt.DisplayRole:
#                 # The view is asking for the actual data, so, just return the item it's asking for.
#                 return QVariant(self._items[index.row()])
#








class Manager(QtCore.QObject):
    nameChanged = Signal(str)
    messagesChanged = Signal()
    input_files_changed = Signal()
    map_lines_changed = Signal()
    map_points_changed = Signal()

    def __init__(self, parent=None):
        super(Manager, self).__init__(parent)
        self._check = None

        self.points = []
        self.list = [
            {
                "color": "red",
                "size": 20,
                "coordinate": {
                    "latitude": -41.552876,
                    "longitude": 81.695257
                }
            },
            {
                "color": "red",
                "size": 20,
                "coordinate": {
                    "latitude": -42.552876,
                    "longitude": 81.695257
                }
            },
            {
                "color": "red",
                "size": 20,
                "coordinate": {
                    "latitude": -43.552876,
                    "longitude": 81.695257
                }
            },
            {
                "color": "red",
                "size": 20,
                "coordinate": {
                    "latitude": -36.392197,
                    "longitude": 151.274747
                }
            },
            {
                "color": "red",
                "size": 20,
                "coordinate": {
                    "latitude": -36.392244,
                    "longitude": 152.274708
                }
            },
            {
                "color": "red",
                "size": 20,
                "coordinate": {
                    "latitude": -36.392244,
                    "longitude": 149.274708
                }
            },
            {
                "color": "red",
                "size": 20,
                "coordinate": {
                    "latitude": -36.392293,
                    "longitude": 148.274671
                }
            },
            {
                "color": "red",
                "size": 20,
                "coordinate": {
                    "latitude": -36.392342,
                    "longitude": 147.274634
                }
            },
            {
                "color": "red",
                "size": 20,
                "coordinate": {
                    "latitude": -35.392342,
                    "longitude": 146.274634
                }
            },
            {
                "color": "red",
                "size": 20,
                "coordinate": {
                    "latitude": -38.393312,
                    "longitude": 150.273858
                }
            },
            {
                "color": "red",
                "size": 20,
                "coordinate": {
                    "latitude": -36.393312,
                    "longitude": 150.273858
                }
            },
            {
                "color": "red",
                "size": 20,
                "coordinate": {
                    "latitude": -36.39336,
                    "longitude": 150.273819
                }
            }

        ]

    @Property(str, notify=nameChanged)
    def name(self):
        if self._check is None:
            return "n/a"
        return self._check.info.name

    @Property('QVariantList', notify=messagesChanged)
    def messages(self):
        if self._check is None:
            return []
        return self._check.outputs.messages

    @Property('QVariantList', notify=input_files_changed)
    def input_files(self):
        if self._check is None:
            return []
        return [f.path for f in self._check.inputs.files]

    @Property('QVariantList', notify=map_lines_changed)
    def map_lines(self):
        if (self._check is None or
                self._check.outputs is None or
                self._check.outputs.data is None or
                'map' not in self._check.outputs.data):
            # if there's no map data just return an empty list
            return []

        lines = []

        geojson = self._check.outputs.data['map']
        assert(geojson['type'] == 'FeatureCollection')
        features = geojson['features']
        for feature in features:
            if feature['type'] != 'Feature':
                continue
            geometry = feature['geometry']
            if geometry['type'] != 'LineString':
                continue
            coordinates = geometry['coordinates']
            line_points = []
            for coordinate in coordinates:
                line_points.append({
                    'latitude': coordinate[1],
                    'longitude': coordinate[0],
                })
            line = {
                'color': 'blue',
                'points': line_points
            }
            lines.append(line)

        # import json
        # print(json.dumps(lines, indent=4))
        return lines


    @Property('QVariantList', notify=map_points_changed)
    def nmap_points(self):
        if (self._check is None or
                self._check.outputs is None or
                self._check.outputs.data is None or
                'map' not in self._check.outputs.data):
            # if there's no map data just return an empty list
            print("return early")
            return []

        points = []

        geojson = self._check.outputs.data['map']
        assert(geojson['type'] == 'FeatureCollection')
        features = geojson['features']
        for feature in features:
            print("feature")
            if feature['type'] != 'Feature':
                continue
            print("geom")
            geometry = feature['geometry']
            if geometry['type'] != 'Point':
                print("geom type = {}".format(geometry['type']))
                continue
            print("coord")
            coordinate = geometry['coordinates']

            point = {
                "color": "red",
                "size": 20,
                'coordinate': {
                    'latitude': coordinate[1],
                    'longitude': coordinate[0],
                }
            }
            points.append(point)

        import json
        print(json.dumps(points, indent=4))
        return points

        # list = [
        #     {
        #         "color": "red",
        #         "size": 20,
        #         "coordinate": {"latitude": -27, "longitude": 154.1}
        #     },
        #     {
        #         "color": "blue",
        #         "size": 20,
        #         "coordinate": {"latitude": -26, "longitude": 152.0}
        #     }
        # ]
        # return list

    @Property('QVariantList', constant=True)
    def old_map_lines(self):
        list = [
            {
                "color": "red",
                "points": [
                    {"latitude": -26, "longitude": 153.0},
                    {"latitude": -27, "longitude": 154.1},
                    {"latitude": -28, "longitude": 153.9},
                    {"latitude": -30, "longitude": 153.5}
                ]
            },
            {
                "color": "blue",
                "points": [
                    {"latitude": -26, "longitude": 152.0},
                    {"latitude": -27, "longitude": 153.1},
                    {"latitude": -28, "longitude": 152.9},
                    {"latitude": -30, "longitude": 152.5}
                ]
            }
        ]
        return list

    @Property('QVariantList', notify=map_points_changed)
    def map_points(self):
        import json
        print(json.dumps(self.points, indent=4))
        return self.points

    def set_check(self, check):
        self.points.append(self.list[len(self.points)])
        self._check = check
        self.nameChanged.emit(self._check.info.name)
        self.messagesChanged.emit()
        self.input_files_changed.emit()
        self.map_lines_changed.emit()
        self.map_points_changed.emit()


class ScoreboardDetailsWidget(QtWidgets.QGroupBox):

    def __init__(self, parent=None):
        QtWidgets.QGroupBox.__init__(self, "Details", parent=parent)

        self.manager = Manager()

        view = QtQuickWidgets.QQuickWidget()
        rc = view.rootContext()
        rc.setContextProperty('manager', self.manager)

        url = QUrl.fromLocalFile(os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "scoreboard_details.qml")
        )

        view.setSource(url)
        view.setResizeMode(QtQuickWidgets.QQuickWidget.SizeRootObjectToView)

        vbox = QtWidgets.QVBoxLayout()
        # vbox.setContentsMargins(0, 4, 0, 4)
        self.setLayout(vbox)

        vbox.addWidget(view)

    def set_selected_check(self, check: QajsonCheck):
        self.manager.set_check(check)
