from PySide2.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide2.QtGui import QColor, QFont, QBrush
from typing import List
import os

from hyo2.qax.app import qta
from ausseabed.qajson.model import QajsonCheck, QajsonInfo, QajsonInputs


class ScoreBoardCheckModel(QAbstractTableModel):

    color_fail = QColor(200, 100, 100, 50)
    color_warning = QColor(255, 213, 0, 50)
    color_ok = QColor(100, 200, 100, 50)
    color_in_progress = QColor(200, 200, 100, 50)

    def __init__(self, checks: List[QajsonCheck] = None, parent=None):
        super(ScoreBoardCheckModel, self).__init__(parent)

        # qtawesome needs a GUI running to load icons, this prevents these from
        # being created at a class level (instead of per instance)
        self.cross_icon = qta.icon('fa.close', color='red')
        self.tick_icon = qta.icon('fa.check', color='green')
        self.warning_icon = qta.icon('fa.warning', color='orange')

        if checks is None:
            self.checks = []
        else:
            self.checks = checks

    def rowCount(self, index=QModelIndex()):
        """ Returns the number of rows the model holds. """
        return len(self.checks)

    def columnCount(self, index=QModelIndex()):
        """ Returns the number of columns the model holds. """
        return 5

    def data(self, index, role=Qt.DisplayRole):
        """ Depending on the index and role given, return data. If not
            returning data, return None (PySide equivalent of QT's
            "invalid QVariant").
        """
        if not index.isValid():
            return None

        if not 0 <= index.row() < len(self.checks):
            return None

        check = self.checks[index.row()]

        if role == Qt.DisplayRole:
            if index.column() == 0:
                # check ID column
                return check.info.id
            elif index.column() == 1:
                # check name column
                check_name = check.info.name
                try:
                    check_name = f"{check_name} [v.{check.info.version}]"
                except Exception as e:
                    check_name = f"{check_name} [no version]"
                return check_name
            elif index.column() == 2:
                # file name column
                filename_list = []
                for f in check.inputs.files:
                    full_path = f.path
                    _, file_name = os.path.split(full_path)
                    filename_list.append(file_name)
                file_item = "\n".join(filename_list)
                return file_item
            elif index.column() == 3:
                # status column
                status = "Not run"
                if check.outputs is not None:
                    status = check.outputs.execution.status
                return status
            elif index.column() == 4:
                check_state = ""
                try:
                    check_state = check.outputs.check_state
                except AttributeError as e:
                    # then this check doesn't have outputs as it hasn't been
                    # run
                    pass
                return check_state
                # # Use icons to present state, not text, so return None
                # return None
        elif role == Qt.BackgroundRole:
            if index.column() == 3:
                # status column
                status = "Not run"
                if check.outputs is not None:
                    status = check.outputs.execution.status

                if status in ["aborted", "failed"]:
                    return ScoreBoardCheckModel.color_fail
                elif status in ["draft", "queued", "running", "Not run"]:
                    return ScoreBoardCheckModel.color_in_progress
                else:
                    return ScoreBoardCheckModel.color_ok
        elif role == Qt.DecorationRole:
            if index.column() == 4:
                check_state = ""
                try:
                    check_state = check.outputs.check_state
                except AttributeError as e:
                    # then this check doesn't have outputs as it hasn't been
                    # run
                    pass
                if check_state == "fail":
                    return self.cross_icon
                elif check_state == "pass":
                    return self.tick_icon
                elif check_state == "warning":
                    return self.warning_icon
                elif check.outputs is None:
                    return self.warning_icon
        elif role == Qt.ToolTipRole:
            if index.column() == 4:
                try:
                    check_state = check.outputs.check_state
                    return check_state
                except AttributeError as e:
                    # then this check doesn't have outputs as it hasn't been
                    # run
                    pass
        elif role == Qt.FontRole:
            if index.column() == 4:
                font = QFont()
                font.setPointSize(1)
                return font
        elif role == Qt.ForegroundRole:
            if index.column() == 4:
                return QColor(255, 0, 0, 0)
        elif role == Qt.TextAlignmentRole:
            if index.column() in [0, 1, 2]:
                return (Qt.AlignLeft | Qt.AlignTop)

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """ Set the headers to be displayed. """
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            if section == 0:
                return "ID"
            elif section == 1:
                return "Check"
            elif section == 2:
                return "Input"
            elif section == 3:
                return "Status"
            elif section == 4:
                return "QA Pass"

        return None

    def setChecks(self, checks):
        self.beginResetModel()

        self.checks = checks

        self.endResetModel()
        return True
