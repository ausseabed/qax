from PySide2.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide2.QtGui import QColor, QFont, QBrush
from typing import List
import os
import qtawesome as qta

from hyo2.qax.lib.project import QaCheckSummary


class SummaryModel(QAbstractTableModel):

    color_fail = QColor(200, 100, 100, 50)
    color_warning = QColor(255, 213, 0, 50)
    color_ok = QColor(100, 200, 100, 50)
    color_in_progress = QColor(200, 200, 100, 50)

    def __init__(self, checks: List[QaCheckSummary] = None, parent=None):
        super(SummaryModel, self).__init__(parent)

        if checks is None:
            self.check_summaries = []
        else:
            self.check_summaries = checks

    def rowCount(self, index=QModelIndex()):
        """ Returns the number of rows the model holds. """
        return len(self.check_summaries)

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

        if not 0 <= index.row() < len(self.check_summaries):
            return None

        check_summary = self.check_summaries[index.row()]

        if role == Qt.DisplayRole:
            if index.column() == 0:
                # name column
                check_name = check_summary.name
                if check_summary.version is None:
                    check_name = "{} [no version]".format(check_name)
                else:
                    check_name = "{} [v.{}]".format(
                        check_name, check_summary.version)

                return check_name
            elif index.column() == 1:
                # total runs column
                return check_summary.total_executions
            elif index.column() == 2:
                # failed runs column
                return check_summary.failed_executions
            elif index.column() == 3:
                # QA Fails
                return check_summary.failed_check_state
            elif index.column() == 4:
                return check_summary.warning_check_state
        elif role == Qt.BackgroundRole:
            if index.column() == 2:
                if check_summary.failed_executions > 0:
                    return SummaryModel.color_fail
            elif index.column() == 3:
                if check_summary.failed_check_state > 0:
                    return SummaryModel.color_fail
            elif index.column() == 4:
                if check_summary.warning_check_state > 0:
                    return SummaryModel.color_warning

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """ Set the headers to be displayed. """
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            if section == 0:
                return "Check"
            elif section == 1:
                return "Total Runs"
            elif section == 2:
                return "Failed Runs"
            elif section == 3:
                return "QA Fails"
            elif section == 4:
                return "QA Warnings"

        return None

    def setCheckSummaries(self, check_summaries):
        self.beginResetModel()

        self.check_summaries = check_summaries

        self.endResetModel()
        return True
