from PySide.QtCore import Qt
from PySide.QtCore import QAbstractTableModel
from PySide.QtCore import QModelIndex
from PySide.QtGui import QBrush
from PySide.QtGui import QColor


class CModelVsc(QAbstractTableModel):

    def __init__(self, pVolumes, parent=None):
        super(CModelVsc, self).__init__(parent)

        # pVolumes is a list of dictionaries
        self.__mVolumes = pVolumes

    def rowCount(self, index=QModelIndex()):
        if self.__mVolumes is None:
            return 0
        return len(self.__mVolumes)

    def columnCount(self, pIndex=QModelIndex()):
        return 4

    def data(self, pIndex, pRole=Qt.DisplayRole):
        if not pIndex.isValid():
            return None

        if not 0 <= pIndex.row() < len(self.__mVolumes):
            return None

        if pRole == Qt.DisplayRole:
            lVolume = self.__mVolumes[pIndex.row()]

            if pIndex.column() == 0:
                # id
                return lVolume['id']
            elif pIndex.column() == 1:
                # device
                return lVolume['Shadow copy device name']
            elif pIndex.column() == 2:
                # creation timestamp
                return lVolume['Creation Time']
            elif pIndex.column() == 3:
                # source drive
                return lVolume['srcDrive']
            return None

        elif pRole == Qt.TextAlignmentRole:
            return int(Qt.AlignLeft) | int(Qt.AlignVCenter)

    def headerData(self, pSection, pOrientation, pRole=Qt.DisplayRole):
        """ Set the headers to be displayed. """

        if pRole != Qt.DisplayRole:
            return None

        if pOrientation == Qt.Horizontal:
            if pSection == 0:
                return "Id"
            elif pSection == 1:
                return "Device"
            elif pSection == 2:
                return "Creation Timestamp"
            elif pSection == 3:
                return "Source Drive"

        return None

    def flags(self, pIndex):
        """ Set the item flags at the given index. Seems like we're
            implementing this function just to see how it's done, as we
            manually adjust each tableView to have NoEditTriggers.
        """
        if not pIndex.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractTableModel.flags(self, pIndex) |
                            Qt.ItemIsSelectable)
