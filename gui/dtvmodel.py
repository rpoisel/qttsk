import types
from PySide import QtCore, QtGui
from dtvaccess import DTVAccess


class DynamicTreeViewNode(object):

    def __init__(self, name=None, data=None, parent=None, icon=None):
        self.Name = name
        self.Data = data
        self.Parent = parent
        self.Children = []
        self.Icon = icon

    def getName(self):
        return self.__name

    def setName(self, value):
        self.__name = value

    Name = property(getName, setName)

    def getIcon(self):
        return self.__icon

    def setIcon(self, value):
        if isinstance(value, QtGui.QIcon):
            self.__icon = value
        elif isinstance(value, basestring):
            self.__icon = QtGui.QIcon(value)
        else:
            self.__icon = None

    Icon = property(getIcon, setIcon)

    def getData(self):
        return self.__data

    def setData(self, value):
        self.__data = value

    Data = property(getData, setData)

    def getParent(self):
        return self.__parent

    def setParent(self, parent):
        if parent is not None:
            self.__parent = parent
            self.__parent.appendCild(self)
        else:
            self.__parent = None

    Parent = property(getParent, setParent)

    def getChildren(self):
        return self.__children

    def setChildren(self, value):
        self.__children = value

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
        self.__fetchMoreFunc = None
        self.__dataParserFunc = None
        self.__hasChildrenFunc = None
        self.__accessCls = None

    def getAccessClass(self):
        return self.__accessCls

    def setAccessClass(self, cls):
        if isinstance(cls, DTVAccess):
            self.__accessCls = cls
            self.__fetchMoreFunc = self.__accessCls.addItems
            self.__dataParserFunc = self.__accessCls.parseData
            self.__hasChildrenFunc = self.__accessCls.hasChildren
        else:
            raise TypeError("Class must be a Subclass of \"DTVAccess\"")

    AccessClass = property(getAccessClass, setAccessClass)

    def getHeader(self):
        return self.__headers

    def setHeader(self, cols):
        self.__headers = cols
        self.__updateColumnCount()

    Header = property(getHeader, setHeader)

    def getRoot(self):
        return self.__root

    def setRoot(self, node):
        self.__root = node

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
                if self.__dataParserFunc is not None:
                    return QtGui.QIcon(self.__dataParserFunc(node,
                        index.column() - 1, role))
                else:
                    return None
            return None

        if role == QtCore.Qt.TextAlignmentRole:
            return int(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        if role != QtCore.Qt.DisplayRole:
            return None

        if index.column() == 0:
            return node.Name
        else:
            if self.__dataParserFunc is not None:
                return self.__dataParserFunc(node, index.column() - 1)
            return None

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
        return index.internalPointer() if index.isValid() else self.__root

    def hasChildren(self, parent):
        node = self.nodeFromIndex(parent)
        return self.__hasChildrenFunc(node)

    def canFetchMore(self, parent):
        if not parent.isValid():
            return False
        else:
            parentNode = parent.internalPointer()
            if self.__hasChildrenFunc(parentNode):
                if len(parentNode.Children) > 0:
                    return False
            return True

    def fetchMore(self, parent):
        if self.__fetchMoreFunc is not None:
            self.__fetchMoreFunc(self, parent.internalPointer())

    def addRoot(self, name, data, icon=None):
        self.addItem(self.__root, name, data, icon)

    def addItem(self, parentNode, name, data, icon=None):
        DynamicTreeViewNode(name, data, parentNode, icon)
