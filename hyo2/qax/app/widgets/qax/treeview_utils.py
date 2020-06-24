import sys

from PySide2.QtGui import QGuiApplication, QStandardItemModel, QStandardItem
from PySide2.QtQml import QQmlApplicationEngine


class SimpleTreeModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setColumnCount(1)

        root = self.invisibleRootItem()
        group1 = QStandardItem("group1")
        group1.setText("group1")
        value1 = QStandardItem("value1")
        value1.setText("value1")
        value2 = QStandardItem("value2")
        value2.setText("value2")
        group1.appendRow(value1)
        group1.appendRow(value2)

        subgroup1 = QStandardItem("subgroup1")
        subgroup1.setText("subgroup1")
        group1.appendRow(subgroup1)
        sg1value1 = QStandardItem("sg1value1")
        sg1value1.setText("sg1value1")
        subgroup1.appendRow(sg1value1)

        root.appendRow(group1)


class DictTreeModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(1)

        # dictionary contains a set of names that are to be excluded
        # at various levels
        # If we didn't exclude the map data here all the geojson would be
        # browseable
        self.exclusions = {
            # 1: set(['map'])
        }

    def _recurse_dict(self, tree_item, data_item, depth):
        exclusions_for_depth = set()
        if depth in self.exclusions:
            exclusions_for_depth = self.exclusions[depth]

        if isinstance(data_item, dict):
            for param_name, param_value in data_item.items():
                if param_name in exclusions_for_depth:
                    # skip over parameters that have been excluded
                    # for this depth
                    continue
                new_item = QStandardItem(param_name)
                new_item.setText(param_name)
                tree_item.appendRow(new_item)
                self._recurse_dict(new_item, param_value, depth+1)
        elif isinstance(data_item, list):
            for param_value in data_item:
                self._recurse_dict(tree_item, param_value, depth+1)
        else:
            new_item = QStandardItem(str(data_item))
            new_item.setText(str(data_item))
            tree_item.appendRow(new_item)

    def set_data_dict(self, data_dict):
        root = self.invisibleRootItem()
        root.clearData()

        for c in reversed(range(0, root.rowCount())):
            root.removeRow(c)

        self._recurse_dict(root, data_dict, 1)
