import os
from functools import partial
import logging

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


class AssetBrowserWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=MWidgets.maya_main_window()):
        super(AssetBrowserWindow, self).__init__(parent)

        self.setWindowTitle("Asset Browser")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.setObjectName("AssetBrowserWindow")

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.dims = (1920, 1080)
        self.setMinimumSize(self.dims[0], self.dims[1])

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

            self.custom_actions[library] = []

        self.import_action = QtWidgets.QAction("Import")
        self.import_vrayproxy_action = QtWidgets.QAction("Import VRay Proxy")

        for std_library in lm.STD_LIBRARIES:
            if std_library not in self.custom_actions.keys():
                continue

            action_data = [
                {
                    "action_object": self.import_action,
                    "action_callback": partial(self.import_action_callback)
                },
                {
                    "action_object": self.import_vrayproxy_action,
                    "action_callback": partial(self.import_vrayproxy_action_callback),
                    "action_asset_data_condition": "vrproxy_maya"
                }
            ]

            self.custom_actions[std_library].extend(action_data)

        self.asset_browser.add_actions_to_menus(self.custom_actions)

    def create_widgets(self):
        self.asset_browser = AssetBrowserWidget.AssetBrowserWidget(dims=self.dims)

    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)

        main_layout.addWidget(self.asset_browser)

    def create_connections(self):
        pass

    def create_custom_connections(self):
        connections = [
            {
                "widget": "assets_tw",
                "signal": "itemClicked",
                "function": ""
            }
        ]

        self.asset_browser.create_custom_connections(connections)

    def custom_browser_setup(self):
        self.create_custom_actions()
        # self.create_custom_connections()

    def import_action_callback(self):
        items = self.asset_browser.assets_tw.selectedItems()

        if not items:
            return

        current_library = items[0].library

        if current_library in lm.STD_LIBRARIES:
            for item in items:
                if item.asset_data["maya_file"]:
                    cmds.file(item.asset_data["maya_file"], i=True)

    def import_vrayproxy_action_callback(self):
        items = self.asset_browser.assets_tw.selectedItems()

        if not items:
            return

        current_library = items[0].library

        if current_library in lm.STD_LIBRARIES:
            for item in items:
                if item.asset_data["maya_file"]:
                    if not os.path.isfile(item.asset_data["maya_file"]):
                        continue

                    cmds.file(item.asset_data["maya_file"], i=True)


def main():
    try:
        cmds.deleteUI("AssetBrowserWindow")
    except Exception:
        pass

    dialog = AssetBrowserWindow()
    dialog.show()


if __name__ == "__main__":
    main()
