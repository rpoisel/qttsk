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
from dtvmodel import DynamicTreeViewModel
from dtvaccess_tsk import TskDTVAccess, TskNodeData


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

        self.mHash = hashlib.sha1()

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
        self.mainwidget.hashButton.clicked.connect(
                self.on_hash_clicked)
        self.mainwidget.tskTree.clicked.connect(
                self.on_file_clicked)

    def on_input_dir_clicked(self):
        self.mFilename = QtGui.QFileDialog.getOpenFileName(self.ui,
                "Choose Image",
                os.getcwd(),
                "All Files (*)")[0]
        if self.mFilename != "":
            self.mModel = DynamicTreeViewModel(["Name", "Filetype", "iNode"])
            self.mModel.addRoot("/",
                    TskNodeData(["/", None, None], True),
                    os.path.join("gui", "icons", "b.png"))
            self.mTreeAccess = TskDTVAccess()
            self.mModel.AccessClass = self.mTreeAccess
            self.mTreeAccess.setImage(self.mFilename,
                    self.mainwidget.offset.text())
            self.mainwidget.tskTree.setModel(self.mModel)
            self.mainwidget.tskTree.header().setStretchLastSection(False)
            self.mainwidget.tskTree.header().setResizeMode(0,
                    QtGui.QHeaderView.Stretch)
            self.mainwidget.tskTree.expandToDepth(0)

            self.mainwidget.exportButton.setEnabled(True)
            self.mainwidget.hashButton.setEnabled(True)
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

    def __getInodeData(self):
        if self.mainwidget.outputDir.text() == "":
            self.on_output_dir_clicked()
        if self.mainwidget.outputDir.text() == "":
            return
        if self.mainwidget.inode.text() == "":
            # what shall be exported?
            return
        lCommand = ["icat",
                "-o " + self.mainwidget.offset.text(),
                self.mFilename,
            self.mainwidget.inode.text()
            ]
        return os_wrapper.runCommand(lCommand)

    def on_export_clicked(self):
        lOutput = self.__getInodeData()
        # stdout: lOutput[0]
        # stderr: lOutput[1]
        with open(os.path.join(self.mainwidget.outputDir.text(),
            self.mainwidget.filename.text()),
                "wb") as lFH:
            lFH.write(lOutput[0])
        if len(lOutput) > 1 and lOutput[1] is not None:
            print "Status: " + lOutput[1]

    def on_hash_clicked(self):
        # TODO put this into a try-except block
        lOutput = self.__getInodeData()
        # stdout: lOutput[0]
        # stderr: lOutput[1]
        self.mHash.update(lOutput[0])
        with open(os.path.join(self.mainwidget.outputDir.text(),
            self.mainwidget.filename.text() + ".hash"),
                "wb") as lFH:
            lFH.write(self.mHash.hexdigest())

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