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
from maya_core.pipeline.lighting.vray_lighting import vray_lighting
from maya_core.pipeline.lookdev.material_builder import MaterialBuilder
from maya_core.pipeline.lookdev import lookdev_utils

logger = logging.getLogger(__name__)
logger.setLevel(10)


class AssetBrowserWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=MWidgets.maya_main_window()):
        super(AssetBrowserWindow, self).__init__(parent)

        self.setWindowTitle("Asset Browser")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.setObjectName("AssetBrowser")

        app_icon = QtGui.QIcon(r"F:\share\tools\tools_core\tools_core\asset_library\asset_browser\icons\browser.png")
        self.setWindowIcon(app_icon)

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

        # Actions

        # STD Library Actions
        import_action = QtWidgets.QAction("Import")
        reference_action = QtWidgets.QAction("Reference")
        import_vrayproxy_action = QtWidgets.QAction("Import VRay Proxy")
        import_mesh_action = QtWidgets.QAction("Import as Mesh")

        # STD Library Actions

        for std_library in lm.STD_LIBRARIES:
            if std_library not in self.custom_actions.keys():
                continue

            action_datas = [
                {
                    "action_object": import_action,
                    "action_callback": partial(self.import_action_callback),
                    "action_asset_data_conditions": ["maya_file"]
                },
                {
                    "action_object": reference_action,
                    "action_callback": partial(self.reference_action_callback),
                    "action_asset_data_conditions": ["maya_file"]
                },
                {
                    "action_object": import_vrayproxy_action,
                    "action_callback": partial(self.import_vrayproxy_action_callback),
                    "action_asset_data_conditions": ["vrproxy_maya"]
                },
                {
                    "action_object": import_mesh_action,
                    "action_callback": partial(self.import_mesh_action_callback),
                    "action_asset_data_conditions": ["mesh"]
                }
            ]

            for action_data in action_datas:
                if action_data not in self.custom_actions[std_library]:
                    self.custom_actions[std_library].append(action_data)

        # StudioLights
        create_vray_light_action = QtWidgets.QAction("Create Light")

        self.custom_actions["StudioLights"] = [
            {
                "action_object": create_vray_light_action,
                "action_callback": partial(self.create_vray_light_action_callback)
            },
        ]

        # Cucoloris
        create_vray_gobo_action = QtWidgets.QAction("Create VRay Gobo")

        self.custom_actions["Cucoloris"] = [
            {
                "action_object": create_vray_gobo_action,
                "action_callback": partial(self.create_vray_gobo_action_callback)
            }
        ]

        # Material

        build_vray_material_action = QtWidgets.QAction("Build VRay Material")

        self.custom_actions["Material"] = [
            {
                "action_object": build_vray_material_action,
                "action_callback": partial(self.build_vray_material_action_callback)
            }
        ]

        # HDR

        self.custom_actions["HDR"] = [
            {
                "action_object": create_vray_light_action,
                "action_callback": partial(self.create_vray_light_action_callback)
            }
        ]

        # Texture

        create_texture_action = QtWidgets.QAction("Create Texture")

        self.custom_actions["Texture"] = [
            {
                "action_object": create_texture_action,
                "action_callback": partial(self.create_texture_action_callback)
            }
        ]

        self.asset_browser.add_actions_to_menus(self.custom_actions)

    def create_widgets(self):
        self.asset_browser = AssetBrowserWidget.AssetBrowserWidget(dims=self.dims)

        self.asset_browser.assets_tw.setColumnWidth(0, self.dims[0] * 0.125)

    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)

        main_layout.addWidget(self.asset_browser)

    def create_connections(self):
        pass

    def create_custom_connections(self):
        connections = []

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
                    if not os.path.isfile(item.asset_data["maya_file"]):
                        continue

                    cmds.file(item.asset_data["maya_file"], i=True)

    def reference_action_callback(self):
        items = self.asset_browser.assets_tw.selectedItems()

        if not items:
            return

        current_library = items[0].library

        if current_library in lm.STD_LIBRARIES:
            for item in items:
                if item.asset_data["maya_file"]:
                    if not os.path.isfile(item.asset_data["maya_file"]):
                        continue

                    cmds.file(item.asset_data["maya_file"], r=True)

    def import_vrayproxy_action_callback(self):
        items = self.asset_browser.assets_tw.selectedItems()

        if not items:
            return

        current_library = items[0].library

        if current_library in lm.STD_LIBRARIES:
            for item in items:
                if item.asset_data["vrproxy_maya"]:
                    if not os.path.isfile(item.asset_data["vrproxy_maya"]):
                        continue

                    cmds.file(item.asset_data["vrproxy_maya"], i=True)

    def create_vray_light_action_callback(self):
        items = self.asset_browser.assets_tw.selectedItems()

        if not items:
            return

        for item in items:
            if item.asset_data["asset_path"]:
                if not os.path.isfile(item.asset_data["asset_path"]):
                    continue

                if item.asset_data["asset_type"] == "StudioLights":
                    vray_lighting.create_vray_light("VRayLightRectShape", name=item.asset_data["asset_name"],
                                                    texture=item.asset_data["asset_path"])
                elif item.asset_data["asset_type"] == "HDR":
                    vray_lighting.create_vray_light("VRayLightDomeShape", name=item.asset_data["asset_name"],
                                                    texture=item.asset_data["asset_path"])

    def create_vray_gobo_action_callback(self):
        items = self.asset_browser.assets_tw.selectedItems()

        if not items:
            return

        for item in items:
            if item.asset_data["asset_path"]:
                if not os.path.isfile(item.asset_data["asset_path"]):
                    continue

                vray_lighting.create_gobo(name=item.asset_data["asset_name"], texture=item.asset_data["asset_path"])

    def build_vray_material_action_callback(self):
        items = self.asset_browser.assets_tw.selectedItems()

        if not items:
            return

        for item in items:
            if not item.asset_data["materials"]:
                continue

            MaterialBuilder.build_material(item.asset_data["materials"][0])

    def create_texture_action_callback(self):
        items = self.asset_browser.assets_tw.selectedItems()

        if not items:
            return

        for item in items:
            if not item.asset_data["asset_path"]:
                continue

            lookdev_utils.create_texture(name=item.asset_data["asset_name"], path=item.asset_data["asset_path"])

    def import_mesh_action_callback(self):
        items = self.asset_browser.assets_tw.selectedItems()

        if not items:
            return

        for item in items:
            # Import mesh
            pass

            # Build material

            # Assign materia


def main():
    try:
        cmds.deleteUI("AssetBrowser")
    except Exception:
        pass

    dialog = AssetBrowserWindow()
    dialog.show()


if __name__ == "__main__":
    main()
