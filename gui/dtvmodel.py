import types
from PySide import QtCore, QtGui


class DynamicTreeViewNode(object):

    def __init__(self, name=None, data=None, parent=None, icon=None):
        super(DynamicTreeViewNode, self).__init__()
        self.Name = name
        self.Data = data
        self.Parent = parent
        self.Children = []
        self.Icon = icon

    def getName(self):
        return self._name

    def setName(self, value):
        self._name = value

    Name = property(getName, setName)

    def getIcon(self):
        return self._icon

    def setIcon(self, value):
        if isinstance(value, QtGui.QIcon):
            self._icon = value
        elif isinstance(value, basestring):
            self._icon = QtGui.QIcon(value)
        else:
            self._icon = None

    Icon = property(getIcon, setIcon)

    def getData(self):
        return self._data

    def setData(self, value):
        self._data = value

    Data = property(getData, setData)

    def getParent(self):
        return self._parent

    def setParent(self, parent):
        if parent is not None:
            self._parent = parent
            self._parent.appendCild(self)
        else:
            self._parent = None

    Parent = property(getParent, setParent)

    def getChildren(self):
        return self._children

    def setChildren(self, value):
        self._children = value

    Children = property(getChildren, setChildren)

    def appendCild(self, child):
        self.Children.append(child)

    def childAtRow(self, row):
        return self.Children[row]

    def rowOfChild(self, child):
        for i, item in enumerate(self.Children):
            if item == child:
                return i
        return -1

    def removeChild(self, row):
        value = self.Children[row]
        self.Children.remove(value)
        return True

    def __len__(self):
        return len(self.Children)


class DynamicTreeViewModel(QtCore.QAbstractItemModel):

    def __init__(self, headerColumns, parent=None):
        super(DynamicTreeViewModel, self).__init__(parent)
        self.Header = headerColumns

        self.Root = DynamicTreeViewNode('rootNode', None)

    def getHeader(self):
        return self.__headers

    def setHeader(self, cols):
        self.__headers = cols
        self.__updateColumnCount()

    Header = property(getHeader, setHeader)

    def getRoot(self):
        return self._root

    def setRoot(self, node):
        self._root = node

    Root = property(getRoot, setRoot)

    def __updateColumnCount(self):
        self.columns = len(self.__headers)

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and \
                role == QtCore.Qt.DisplayRole:
            return self.__headers[section]
        return None

    def insertRow(self, row, parent):
        return self.insertRows(row, 1, parent)

    def insertRows(self, row, count, parent):
        self.beginInsertRows(parent, row, (row + (count - 1)))
        self.endInsertRows()
        return True

    def index(self, row, column, parent):
        node = self.nodeFromIndex(parent)
        return self.createIndex(row, column, node.childAtRow(row))

    def data(self, index, role):
        node = self.nodeFromIndex(index)

        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                if node.Icon is not None:
                    return node.Icon
                else:
                    return None
            else:
                return QtGui.QIcon(self.parseData(node,
                    index.column() - 1, role))
            return None

        if role == QtCore.Qt.TextAlignmentRole:
            return int(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        if role != QtCore.Qt.DisplayRole:
            return None

        if index.column() == 0:
            return node.Name
        else:
            return self.parseData(node, index.column() - 1)

    def columnCount(self, parent):
        return self.columns

    def rowCount(self, parent):
        node = self.nodeFromIndex(parent)
        if node is None:
            return 0
        return len(node)

    def parent(self, child):
        if not child.isValid():
            return QtCore.QModelIndex()
        node = self.nodeFromIndex(child)
        if node is None:
            return QtCore.QModelIndex()

        parent = node.Parent

        if parent is None:
            return QtCore.QModelIndex()

        grandparent = parent.Parent
        if grandparent is None:
            return QtCore.QModelIndex()

        row = grandparent.rowOfChild(parent)

        assert row != -1

        self.createIndex(row, 0, parent)

        return self.createIndex(row, 0, parent)

    def nodeFromIndex(self, index):
        return index.internalPointer() if index.isValid() else self._root

    def hasChildren(self, parent):
        node = self.nodeFromIndex(parent)
        # invoke method from dtvaccess_tsk
        return self.hasChildrenImpl(node)

    def canFetchMore(self, parent):
        if not parent.isValid():
            return False
        else:
            parentNode = parent.internalPointer()
            if self.hasChildrenImpl(parentNode):
                if len(parentNode.Children) > 0:
                    return False
            return True

    def fetchMore(self, parent):
        self.addItems(self, parent.internalPointer())
        #self.__fetchMoreFunc(self, parent.internalPointer())

    def addRoot(self, name, data, icon=None):
        self.addItem(self._root, name, data, icon)

    def addItem(self, parentNode, name, data, icon=None):
        DynamicTreeViewNode(name, data, parentNode, icon)
