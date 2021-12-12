import logging
from functools import partial

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm

from tools_core.asset_library.asset_browser import AssetBrowserWidget
from maya_core.maya_pyqt import MWidgets
from tools_core.asset_library import library_manager as lm

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
        self.custom_browser_setup()

    def create_actions(self):
        pass

    def create_custom_actions(self):
        self.custom_actions = {}

        for library in lm.LIBRARIES.keys():
            if not lm.get_library_data(library):
                continue

            self.custom_actions[library] = {}

        # Model library custom actions
        model_action = QtWidgets.QAction("This is model")
        material_action = QtWidgets.QAction("This is mtl")
        after_action = QtWidgets.QAction("after")

        self.custom_actions["model"] = [
            {
                "action_object": model_action,
                "action_callback": ""
            },
            {
                "action_object": "separator",
                "action_callback": ""
            },
            {
                "action_object": after_action,
                "action_callback": ""
            }
        ]

        self.custom_actions["material"] = [
            {
                "action_object": material_action,
                "action_callback": ""
            }
        ]

        self.asset_browser.add_actions_to_menus(self.custom_actions)

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

    def create_custom_connections(self):
        pass

    def custom_browser_setup(self):
        self.create_custom_connections()
        self.create_custom_actions()

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
