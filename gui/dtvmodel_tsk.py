import os

from PySide import QtCore

import os_wrapper
from dtvaccess_tsk import TskNodeData, TskDTVAccess
from dtvmodel import DynamicTreeViewModel


class DynamicTreeViewModelTsk(DynamicTreeViewModel, TskDTVAccess):

    def __init__(self):
        super(DynamicTreeViewModelTsk, self).__init__(
                ["Name", "Filetype", "iNode"]
                )
        self.addRoot(
                "/",
                TskNodeData(
                    ["/", None, None],
                    True
                    ),
                os.path.join("gui", "icons", "b.png")
                )
