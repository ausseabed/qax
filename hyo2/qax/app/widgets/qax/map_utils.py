from PySide2.QtCore import QAbstractListModel, QModelIndex, Qt, QByteArray, \
    QPointF
from PySide2.QtGui import QColor


class MarkerItem(object):
    def __init__(self, position, color=QColor("red"), size=20, properties={}):
        self._position = position
        self._color = color
        self._size = size
        self._properties = properties

    def position(self):
        return self._position

    def setPosition(self, value):
        self._position = value

    def color(self):
        return self._color

    def setColor(self, value):
        self._color = value

    def size(self):
        return self._size

    def setSize(self, value):
        self._size = size

    def properties(self):
        return self._properties

    def set_properties(self, value):
        self._properties = value


class LineItem(object):
    def __init__(self, coordinates, color=QColor("blue"), width=5):
        self._coordinates = coordinates
        self._color = color
        self._width = width

    def coordinates(self):
        return self._coordinates

    def setCoordinates(self, value):
        self._coordinates = value

    def color(self):
        return self._color

    def setColor(self, value):
        self._color = value

    def width(self):
        return self._width

    def setWidth(self, value):
        self._width = size


class MarkersModel(QAbstractListModel):
    PositionRole = Qt.UserRole + 1
    ColorRole = Qt.UserRole + 2
    SizeRole = Qt.UserRole + 3
    PropertiesRole = Qt.UserRole + 4

    _roles = {
        PositionRole: QByteArray(b"markerPosition"),
        ColorRole: QByteArray(b"markerColor"),
        SizeRole: QByteArray(b"markerSize"),
        PropertiesRole: QByteArray(b"markerProperties")
    }

    def __init__(self, parent=None):
        QAbstractListModel.__init__(self, parent)
        self._items = []

    def rowCount(self, index=QModelIndex()):
        return len(self._items)

    def roleNames(self):
        return self._roles

    def data(self, index, role=Qt.DisplayRole):
        if index.row() >= self.rowCount():
            return QVariant()
        marker = self._items[index.row()]

        if role == MarkersModel.PositionRole:
            return marker.position()
        elif role == MarkersModel.ColorRole:
            return marker.color()
        elif role == MarkersModel.SizeRole:
            return marker.size()
        elif role == MarkersModel.PropertiesRole:
            return marker.properties()

        return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid():
            marker = self._items[index.row()]
            if role == MarkersModel.PositionRole:
                marker.setPosition(value)
            if role == MarkersModel.ColorRole:
                marker.setColor(value)
            if role == MarkersModel.SizeRole:
                marker.setSize(value)
            if role == MarkersModel.PropertiesRole:
                marker.set_properties(value)
            self.dataChanged.emit(index, index)
            return True
        return QAbstractListModel.setData(self, index, value, role)

    def addMarker(self, marker):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._items.append(marker)
        self.endInsertRows()

    def removeAllMarkers(self):
        self.beginRemoveRows(QModelIndex(), 0, self.rowCount())
        self._items.clear()
        self.endRemoveRows()

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return QAbstractListModel.flags(index) | Qt.ItemIsEditable

    def moveRandom(self, ix):
        ind = self.index(ix, 0)
        current_pos = self.data(ind, MarkersModel.PositionRole)
        next_pos = current_pos + 0.002*QPointF(random() - 0.5, random() - 0.5)
        self.setData(ind, next_pos, MarkersModel.PositionRole)
        self.setData(
            ind,
            QColor(randint(0, 255), randint(0, 255), randint(0, 255)),
            MarkersModel.ColorRole)

    def addMarkersFromGeojson(self, geojson, color='red'):
        new_items = []
        assert(geojson['type'] == 'FeatureCollection')
        features = geojson['features']
        for feature in features:
            if feature['type'] != 'Feature':
                continue
            geometry = feature['geometry']
            if geometry['type'] != 'Point':
                continue
            coordinate = geometry['coordinates']

            new_marker = MarkerItem(
                QPointF(coordinate[1], coordinate[0]),
                color=QColor(color),
                properties=feature['properties']
            )
            new_items.append(new_marker)

        self.beginInsertRows(
            QModelIndex(),
            self.rowCount(),
            self.rowCount() + len(new_items) - 1
        )
        self._items.extend(new_items)
        self.endInsertRows()


class LinesModel(QAbstractListModel):
    CoordinatesRole = Qt.UserRole + 1
    ColorRole = Qt.UserRole + 2
    WidthRole = Qt.UserRole + 3

    _roles = {
        CoordinatesRole: QByteArray(b"lineCoordinates"),
        ColorRole: QByteArray(b"lineColor"),
        WidthRole: QByteArray(b"lineWidth")
    }

    def __init__(self, parent=None):
        QAbstractListModel.__init__(self, parent)
        self._items = []

    def rowCount(self, index=QModelIndex()):
        return len(self._items)

    def roleNames(self):
        return self._roles

    def data(self, index, role=Qt.DisplayRole):
        if index.row() >= self.rowCount():
            return QVariant()
        marker = self._items[index.row()]

        if role == LinesModel.CoordinatesRole:
            return marker.coordinates()
        elif role == LinesModel.ColorRole:
            return marker.color()
        elif role == LinesModel.WidthRole:
            return marker.width()

        return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid():
            marker = self._items[index.row()]
            if role == MarkersModel.CoordinatesRole:
                marker.setCoordinates(value)
            if role == MarkersModel.ColorRole:
                marker.setColor(value)
            if role == MarkersModel.WidthRole:
                marker.setWidth(value)
            self.dataChanged.emit(index, index)
            return True
        return QAbstractListModel.setData(self, index, value, role)

    def addLine(self, line):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._items.append(line)
        self.endInsertRows()

    def removeAllLines(self):
        self.beginRemoveRows(QModelIndex(), 0, self.rowCount())
        self._items.clear()
        self.endRemoveRows()

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return QAbstractListModel.flags(index) | Qt.ItemIsEditable

    def addLinesFromGeojson(self, geojson, color='red'):
        new_lines = []
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

            new_line = LineItem(
                line_points,
                QColor(color)
            )
            new_lines.append(new_line)

        self.beginInsertRows(
            QModelIndex(),
            self.rowCount(),
            self.rowCount() + len(new_lines) - 1
        )
        self._items.extend(new_lines)
        self.endInsertRows()
