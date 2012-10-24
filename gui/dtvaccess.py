

# Grundklasse NodeData
class NodeData(object):

    def __init__(self):
        raise NotImplementedError("Should have implemented this")


# Grundklasse DTVAccess
class DTVAccess(object):
    def __init__(self):
        pass

    def addItems(self, DTreeView, parentNode):
        raise NotImplementedError("Should have implemented this")

    def parseData(self, nodedata, index, role=None):
        raise NotImplementedError("Should have implemented this")

    def hasChildren(self, nodedata):
        raise NotImplementedError("Should have implemented this")
