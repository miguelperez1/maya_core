import logging
import importlib

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm

from maya_core.maya_pyqt import MWidgets
from tools_core.pyqt_commons import common_widgets as cw
from tools_core.lightboard import LightBoardWidget

logger = logging.getLogger(__name__)
logger.setLevel(10)

importlib.reload(LightBoardWidget)


class LightBoardUI(QtWidgets.QMainWindow):
    def __init__(self, parent=MWidgets.maya_main_window()):
        super(LightBoardUI, self).__init__(parent)

        self.setWindowTitle("Light Board")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.setObjectName("LightBoardUI")

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.light_board_widget = LightBoardWidget.LightBoardWidget()

    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.addWidget(self.light_board_widget)

    def create_connections(self):
        pass


def main():
    try:
        cmds.deleteUI("LightBoardUI")
    except Exception:
        pass

    dialog = LightBoardUI()
    dialog.show()


if __name__ == "__main__":
    main()
