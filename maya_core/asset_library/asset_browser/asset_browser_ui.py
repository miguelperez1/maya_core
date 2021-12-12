import logging

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm

from tools_core.asset_library.asset_browser import AssetBrowserWidget
from maya_core.maya_pyqt import MWidgets

logger = logging.getLogger(__name__)
logger.setLevel(10)


class ExampleDialog(QtWidgets.QMainWindow):
    def __init__(self, parent=MWidgets.maya_main_window()):
        super(ExampleDialog, self).__init__(parent)

        self.setWindowTitle("Window")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.setObjectName("ExampleDialog")

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.asset_browser = AssetBrowserWidget.AssetBrowserWidget()

    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)

        main_layout.addWidget(self.asset_browser)

    def create_connections(self):
        connections = [
            {
                "widget": "assets_tw",
                "signal": "itemClicked",
                "function": lambda: self.test_connection()
            }
        ]

        self.asset_browser.create_custom_connections(connections)

    def test_connection(self):
        print("hello")


def main():
    try:
        cmds.deleteUI("ExampleDialog")
    except Exception:
        pass

    dialog = ExampleDialog()
    dialog.show()


if __name__ == "__main__":
    main()
