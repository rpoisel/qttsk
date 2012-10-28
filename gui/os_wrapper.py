import os
import platform
from subprocess import Popen, PIPE, STDOUT

gMountVhd = ""
gUmountVhd = ""

if platform.system().lower() == "windows":
    gMountVhd = 'mountvhd.cmd'
    gUmountVhd = 'umountvhd.cmd'
else:
    pass


def runCommand(pCommand, pRedirectStderr=True):
    print "Invoking command: " + str(pCommand)
    if pRedirectStderr:
        lOutput = Popen(pCommand,
            stdout=PIPE, stderr=STDOUT).communicate()
    else:
        lOutput = Popen(pCommand, stdout=PIPE).communicate()
    return lOutput


def icat(pFilename, pOffset, pInode):
    lCommand = [
            "icat",
            "-o " + pOffset,
            pFilename,
            pInode
            ]
    return runCommand(lCommand)[0]
