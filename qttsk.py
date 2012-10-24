# -*- coding: utf-8 -*-

import os
import sys
import platform
import logging
logging.basicConfig(
        format='%(asctime)s %(levelname)s %(message)s',
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
