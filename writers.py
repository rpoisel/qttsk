import csv

from gui import os_wrapper


class CWriter(object):

    def __init__(self, pFile):
        super(CWriter, self).__init__()
        self.mFH = open(pFile, "wb")

    def write(self, pFile, pType, pInode, pHash):
        pass

    def close(self):
        pass


class CWriterCsv(CWriter):

    def __init__(self, pFile):
        super(CWriterCsv, self).__init__(pFile)
        self.mWriter = csv.writer(
                self.mFH,
                delimiter=',',
                quotechar='\'',
                quoting=csv.QUOTE_MINIMAL)
        self.mWriter.writerow(['Path', 'Type', 'Inode', 'Hash'])

    def write(self, pPathBase, pPath, pType, pInode, pHash):
        self.mWriter.writerow([pPath, pType, pInode, pHash])


class CWriterHtml(CWriter):

    def __init__(self, pFile):
        super(CWriterHtml, self).__init__(pFile)
        self.mFH.write("""
<html>
<head>
    <title>Report</title>
</head>
<body>
    <table border="1">
    <thead>
    <tr>
        <td>Path</td><td>Type</td><td>Inode</td><td>Hash</td>
    </tr>
    </thead>
""")

    def write(self, pPathBase, pPath, pType, pInode, pHash):
        self.mFH.write("        <tr>")
        self.mFH.write("<td>" + pPath + "</td>")
        self.mFH.write("<td>" + pType + "</td>")
        self.mFH.write("<td>" + pInode + "</td>")
        self.mFH.write("<td>" + pHash + "</td>")
        self.mFH.write("</tr>\n")

    def close(self):
        self.mFH.write("""</table>
</body>
</html>
""")
