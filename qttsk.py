# -*- coding: utf-8 -*-

"""The user interface for our app"""

# VSS investigation (no particular order)
# http://encase-forensic-blog.guidancesoftware.com/2012/06/examining-volume-shadow-copies-easy-way.html
# http://www.forensicswiki.org/wiki/Windows_Shadow_Volumes
# http://dfstream.blogspot.co.at/2012/05/vsc-toolset-update-browsing-shadow.html
# http://computer-forensics.sans.org/blog/2011/09/16/shadow-timelines-and-other-shadowvolumecopy-digital-forensics-techniques-with-the-sleuthkit-on-windows

# AlphaVSS
# http://alphavss.codeplex.com/

# windows disk driver in order to mount images
# http://www.ltr-data.se/opencode.html/#ImDisk

# Short HowTo
# imdisk -a -t file -m e: -f z:\hdimages\image.ntfs -o ro,hd
# imdisk -D -m e:

import os
import sys
import platform
import logging
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
        level=logging.DEBUG)

from gui import controller

sys.path.append('.')
if platform.system().lower() == "windows":
    lBits = 32
    if sys.maxsize > 2 ** 32:
        lBits = 64
#    lPath = r"collating\fragment\lib\magic\dll" + str(lBits)
#    lPath += r";collating\fragment"
    os.environ['PATH'] += ";" + 'win' + str(lBits) + ";" + "winxx"


def main():
    lMain = controller.CMain()
    lMain.run()

if __name__ == "__main__":
    main()
