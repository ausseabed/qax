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

    def set_color(self, value):
        self._color = value

    def size(self):
        return self._size

    def set_size(self, value):
        self._size = value

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

    def set_coordinates(self, value):
        self._coordinates = value

    def color(self):
        return self._color

    def set_color(self, value):
        self._color = value

    def width(self):
        return self._width

    def set_width(self, value):
        self._width = value


class PolygonItem(object):
    def __init__(
            self,
            coordinates,
            color=QColor("blue"),
            line_color=QColor("blue"),
            line_width=5):
        self._coordinates = coordinates
        self._color = color
        self._line_color = line_color
        self._line_width = line_width

    def coordinates(self):
        return self._coordinates

    def set_coordinates(self, value):
        self._coordinates = value

    def color(self):
        return self._color

    def set_color(self, value):
        self._color = value

    def line_color(self):
        return self._line_color

    def set_line_color(self, value):
        self._line_color = value

    def line_width(self):
        return self._line_width

    def set_line_width(self, value):
        self._line_width = value


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
                marker.set_color(value)
            if role == MarkersModel.SizeRole:
                marker.set_size(value)
            if role == MarkersModel.PropertiesRole:
                marker.set_properties(value)
            self.dataChanged.emit(index, index)
            return True
        return QAbstractListModel.setData(self, index, value, role)

    def add(self, marker):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._items.append(marker)
        self.endInsertRows()

    def remove_all(self):
        self.beginRemoveRows(QModelIndex(), 0, self.rowCount())
        self._items.clear()
        self.endRemoveRows()

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return QAbstractListModel.flags(index) | Qt.ItemIsEditable

    def add_from_geojson(self, geojson, color='red'):
        new_items = []
        if not(geojson['type'] == 'FeatureCollection'):
            return
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
                marker.set_coordinates(value)
            if role == MarkersModel.ColorRole:
                marker.set_color(value)
            if role == MarkersModel.WidthRole:
                marker.set_width(value)
            self.dataChanged.emit(index, index)
            return True
        return QAbstractListModel.setData(self, index, value, role)

    def add(self, line):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._items.append(line)
        self.endInsertRows()

    def remove_all(self):
        self.beginRemoveRows(QModelIndex(), 0, self.rowCount())
        self._items.clear()
        self.endRemoveRows()

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return QAbstractListModel.flags(index) | Qt.ItemIsEditable

    def add_from_geojson(self, geojson, color='red'):
        new_lines = []
        if not (geojson['type'] == 'FeatureCollection'):
            return
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


class PolygonsModel(QAbstractListModel):
    CoordinatesRole = Qt.UserRole + 1
    LineColorRole = Qt.UserRole + 2
    LineWidthRole = Qt.UserRole + 3
    ColorRole = Qt.UserRole + 4

    _roles = {
        CoordinatesRole: QByteArray(b"polygonCoordinates"),
        LineColorRole: QByteArray(b"lineColor"),
        LineWidthRole: QByteArray(b"lineWidth"),
        ColorRole: QByteArray(b"mcolor")
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

        if role == PolygonsModel.CoordinatesRole:
            return marker.coordinates()
        elif role == PolygonsModel.LineColorRole:
            return marker.line_color()
        elif role == PolygonsModel.LineWidthRole:
            return marker.line_width()
        elif role == PolygonsModel.ColorRole:
            return marker.color()

        return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid():
            marker = self._items[index.row()]
            if role == PolygonsModel.CoordinatesRole:
                marker.set_coordinates(value)
            if role == PolygonsModel.ColorRole:
                marker.set_color(value)
            if role == PolygonsModel.LineWidthRole:
                marker.set_line_width(value)
            if role == PolygonsModel.LineColorRole:
                marker.set_line_color(value)
            self.dataChanged.emit(index, index)
            return True
        return QAbstractListModel.setData(self, index, value, role)

    def add(self, line):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._items.append(line)
        self.endInsertRows()

    def remove_all(self):
        self.beginRemoveRows(QModelIndex(), 0, self.rowCount())
        self._items.clear()
        self.endRemoveRows()

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return QAbstractListModel.flags(index) | Qt.ItemIsEditable

    def add_from_geojson(
            self,
            geojson,
            color='green',
            line_color='blue',
            line_width=5
        ):
        ''' Update this model with data from a geojson multipolygon
        '''
        new_polys = []
        if not (geojson['type'] == 'MultiPolygon'):
            return
        poly_list_coords = geojson['coordinates']
        for poly_coords in poly_list_coords:
            poly_points = []
            for coordinate in poly_coords:
                poly_points.append({
                    'latitude': coordinate[1],
                    'longitude': coordinate[0],
                })

            new_poly = PolygonItem(
                poly_points,
                color=color,
                line_color=line_color,
                line_width=line_width
            )
            new_polys.append(new_poly)

        self.beginInsertRows(
            QModelIndex(),
            self.rowCount(),
            self.rowCount() + len(new_polys) - 1
        )
        self._items.extend(new_polys)
        self.endInsertRows()
