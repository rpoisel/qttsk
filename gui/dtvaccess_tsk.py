import os

from PySide import QtCore

import os_wrapper


class TskNodeData(object):

    def __init__(self, data, isDir, parent=None):
        super(TskNodeData, self).__init__()
        self.metadata = data
        self.isDir = isDir
        self.parent = parent


class TskDTVAccess(object):

    def __init__(self):
        super(TskDtvAccess, self).__init__()
        self.imageset = False

    def setImage(self, image, offset=0):
        self.imagefile = image
        self.offset = offset
        self.imageset = True

    def __getData(self, inode=None):

        if self.imageset is False:
            return []

        offsettext = "-o " + str(self.offset)

        if inode is None:
            ausgabe = os_wrapper.runCommand(
                ["fls", offsettext, self.imagefile])[0]
        else:
            ausgabe = os_wrapper.runCommand(
                ["fls", offsettext, self.imagefile, inode])[0]

        dateien = ausgabe.splitlines()
        retValue = []

        for line in dateien:
            # Metadaten auslesen
            metadaten = line[:line.find(":")]

            filetype = line[:3].strip()

            # Geloeschte Dateien filtern
            deleted = True if metadaten.find("*") != -1 else False

            # Inode filtern
            inodeStart = metadaten.find("*")
            if inodeStart == -1:
                inodeStart = metadaten.find(" ")
            inodeEnd = metadaten.find("(")
            if inodeEnd == -1:
                inode = metadaten[inodeStart + 1:].strip()
            else:
                inode = metadaten[inodeStart:inodeEnd].strip()

            # Realloc setzen
            # Wenn inodeEnd != -1 dann ist (realloc) vorhanden
            realloc = False
            if inodeEnd != -1:
                realloc = True

            #Dateiname filtern
            filename = line[line.find(":") + 1:].strip()

            #Eintrag zusammenstellen
            data = [filename, filetype, inode, deleted, realloc]

            # Eintrag ins Ausgabenarray einfuegen
            retValue.append(data)

        return retValue

    def addItems(self, DTreeView, parentNode):

        items = self.__getData(parentNode.Data.metadata[2])

        for item in items:
            isDir = True if item[1][:1] == "d" else False
            DTreeView.addItem(parentNode,
                    item[0],
                    TskNodeData(item, isDir, parentNode),
                    os.path.join("gui", "icons", item[1][:1] + ".png"))

    def parseData(self, node, index, role=None):
        # Icons anzeigen
        if role == QtCore.Qt.DecorationRole:
            if index == 0:
                if len(node.Data.metadata) >= 4:
                    if node.Data.metadata[3] is True:
                        return os.path.join("gui", "icons", "deleted.png")
            else:
                return None

        # Text anzeigen
        if node.Data is not None:
            if index + 1 <= len(node.Data.metadata) - 1:
                return node.Data.metadata[index + 1]
        return None

    def hasChildrenImpl(self, node):
        if node.Data is not None:
            return node.Data.isDir
        return True
