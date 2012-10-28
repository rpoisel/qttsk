# -*- coding: utf-8 -*-

"""The user interface for our app"""

import os
import sys
import platform
import logging
import datetime
import string
import subprocess
import re
import hashlib

from subprocess import Popen, PIPE, STDOUT, call

# PyQt4, PySide stuff
from PySide import QtCore

from PySide import QtGui
from PySide import QtXml
from PySide import QtUiTools

# Import the compiled UI module
import gui_resources
import os_wrapper
from model_vsc import CModelVsc
from dtvmodel_tsk import DynamicTreeViewModelTsk
from writers import CWriterCsv, CWriterHtml


# Create a class for our main window
class CMain(object):

    def __init__(self, parent=None):
        super(CMain, self).__init__()

        # set up gui
        self.__mApp = QtGui.QApplication(sys.argv)

        lLoader = QtUiTools.QUiLoader()

        self.ui = lLoader.load(":/forms/mainwindow.ui")
        self.mainwidget = lLoader.load(":/forms/mainwidget.ui")

        self.ui.setCentralWidget(self.mainwidget)

        # initialize widgets

        # signals and slots
        self.ui.actionExit.triggered.connect(self.on_actionExit_triggered)
        self.ui.actionAbout.triggered.connect(self.on_actionAbout_triggered)
        self.ui.actionOpenImage.triggered.connect(
                self.on_input_dir_clicked)
        self.mainwidget.outputDirButton.clicked.connect(
                self.on_output_dir_clicked)
        self.mainwidget.exportButton.clicked.connect(
                self.on_export_clicked)
        self.mainwidget.reportButton.clicked.connect(
                self.on_report_clicked)
        self.mainwidget.tskTree.clicked.connect(
                self.on_file_clicked)

    def on_input_dir_clicked(self):
#        self.mFilename = QtGui.QFileDialog.getOpenFileName(self.ui,
#                "Choose Image",
#                os.getcwd(),
#                "All Files (*)")[0]
        self.mFilename = "/home/rpoisel/git/mmc/data/usbkey.dd"
        self.mainwidget.offset.setText("51")
        if self.mFilename != "":
            self.mModel = DynamicTreeViewModelTsk(
                    self.mFilename,
                    self.mainwidget.offset.text()
                    )
            self.mainwidget.tskTree.setModel(self.mModel)
            self.mainwidget.tskTree.header().setStretchLastSection(False)
            self.mainwidget.tskTree.header().setResizeMode(0,
                    QtGui.QHeaderView.Stretch)
            self.mainwidget.tskTree.expandToDepth(0)

            self.mainwidget.exportButton.setEnabled(True)
            self.mainwidget.reportButton.setEnabled(True)
            self.mainwidget.outputDirButton.setEnabled(True)

    def on_file_clicked(self, pIndex):
        lNode = self.mModel.nodeFromIndex(pIndex).Data.metadata
        self.mainwidget.inode.setText(
            lNode[2]
            )
        self.mainwidget.filename.setText(
            lNode[0]
            )

    def on_output_dir_clicked(self):
        lDialog = QtGui.QFileDialog()
        lDialog.setFileMode(QtGui.QFileDialog.Directory)
        lFilename = lDialog.getExistingDirectory(self.ui,
            "Choose output directory",
            os.getcwd(),
            QtGui.QFileDialog.ShowDirsOnly)
        if lFilename != "":
            self.mainwidget.outputDir.setText(lFilename)

    def __prepareRecursion(self):
        if self.mainwidget.outputDir.text() == "":
            self.on_output_dir_clicked()
        if self.mainwidget.outputDir.text() == "":
            return QtCore.QModelIndex()
        return self.mainwidget.tskTree.currentIndex()

    def __recurse(self, pIdxParent, pPathBase, pFunc, pData, pPath=""):
        try:
            lNode = self.mModel.nodeFromIndex(pIdxParent).Data.metadata
            if pPath == '/':
                lPath = lNode[0]
            else:
                lPath = os.path.join(
                        pPath,
                        lNode[0]
                        )
            if self.mModel.hasChildren(pIdxParent):
                # lPath refers to a directory
                lPathFQ = os.path.join(
                        pPathBase.decode('utf-8'),
                        lPath.decode('utf-8')
                        )
                if not os.path.exists(lPathFQ):
                    os.mkdir(lPathFQ)
                elif not os.path.isdir(lPathFQ):
                    raise Exception("Could not create directory.")
            else:
                pFunc(pPathBase, lPath, lNode[1], lNode[2], pData)
            lNumChildren = self.mModel.rowCount(pIdxParent)
            if lNumChildren > 0:
                for lRowChild in range(lNumChildren):
                    lIdxChild = self.mModel.index(lRowChild, 0, pIdxParent)
                    self.__recurse(lIdxChild, pPathBase, pFunc, pData, lPath)
        except OSError, lExc:
            # could not create directory
            pass

    def __exportFunc(self, pPathBase, pPath, pType, pInode, pData=None):
        if pInode == '0' or pPath == '/':
            return
        lPath = os.path.join(pPathBase.decode('utf-8'), pPath.decode('utf-8'))
        with open(lPath, "wb") as lFH:
            lFH.write(
                    os_wrapper.icat(
                        self.mFilename,
                        self.mainwidget.offset.text(),
                        pInode
                        )
                    )

    def __reportFunc(self, pPathBase, pPath, pType, pInode, pData):
        if pInode == '0':
            lHashDigest = ''
        else:
            lHash = hashlib.sha1()
            lHash.update(os_wrapper.icat(
                self.mFilename,
                self.mainwidget.offset.text(),
                pInode
                ))
            lHashDigest = lHash.hexdigest()
        pData.write(pPathBase, pPath, pType, pInode, lHashDigest)

    def on_export_clicked(self):
        lIndex = self.__prepareRecursion()
        if lIndex.isValid():
            if self.mainwidget.recursive.checkState() == QtCore.Qt.Checked:
                self.__recurse(
                        lIndex,
                        self.mainwidget.outputDir.text(),
                        self.__exportFunc,
                        None
                        )
            else:
                lNode = self.mModel.nodeFromIndex(lIndex).Data.metadata
                self.__exportFunc(
                        self.mainwidget.outputDir.text(),
                        lNode[0],
                        lNode[1],
                        lNode[2]
                        )

    def on_report_clicked(self):
        # TODO put this into a try-except block
        lIndex = self.mainwidget.tskTree.currentIndex()
        if not lIndex.isValid():
            return
        lFilename = QtGui.QFileDialog.getSaveFileName(self.ui,
                    "Determine filename to export CSV",
                    os.getcwd(),
                    ';;'.join([
                        "CSV files (*.csv)",
                        "HTML files (*.html)",
                    ])
                    )[0]
        if lFilename != "":
            if lFilename.endswith('.csv'):
                lWriter = CWriterCsv(lFilename)
            elif lFilename.endswith('.html'):
                lWriter = CWriterHtml(lFilename)
            else:
                return
            if self.mainwidget.recursive.checkState() == QtCore.Qt.Checked:
                self.__recurse(
                        lIndex,
                        self.mainwidget.outputDir.text(),
                        self.__reportFunc,
                        lWriter
                        )
            else:
                lNode = self.mModel.nodeFromIndex(lIndex).Data.metadata
                self.__reportFunc(
                        self.mainwidget.outputDir.text(),
                        lNode[0],
                        lNode[1],
                        lNode[2],
                        lWriter
                        )
            lWriter.close()

    def on_actionExit_triggered(self):
        self.ui.close()

    def on_actionAbout_triggered(self, pChecked=None):
        QtGui.QMessageBox.about(self.ui,
            "Qt TSK Bindings",
            "<html>Key developers:  \
            <ul> \
                <li>Rainer Poisel</li> \
                <li>Manfred Ruzicka</li> \
            </ul> \
            &copy; 2011, 2012 St. Poelten University of Applied "
            "Sciences</html> \
            <p> \
            This software is released under the terms of the LGPLv3:<br /> \
            <a href=\"http://www.gnu.org/licenses/lgpl.html\">"
            "http://www.gnu.org/licenses/lgpl.html</a> \
            </p> \
            "
            )

    def run(self):
        self.ui.show()
        lReturn = self.__mApp.exec_()
        sys.exit(lReturn)
