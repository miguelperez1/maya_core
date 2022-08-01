import logging

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm

from maya_core.maya_pyqt import MWidgets
from maya_core.pipeline.lookdev import lookdev_utils
from maya_core.pipeline.lookdev.vray_lookdev import vray_lookdev

logger = logging.getLogger(__name__)
logger.setLevel(10)


class LookdevToolKit(QtWidgets.QMainWindow):
    def __init__(self, parent=MWidgets.maya_main_window()):
        super(LookdevToolKit, self).__init__(parent)

        self.setWindowTitle("Lookdev ToolKit")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.setObjectName("LookdevToolKit")

        self.setMinimumWidth(400)

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.prefix_lbl = QtWidgets.QLabel("Prefix:")
        self.prefix_le = QtWidgets.QLineEdit()

        self.material_builder_btn = QtWidgets.QPushButton("Material Builder")
        self.create_cc_btn = QtWidgets.QPushButton("Color Correct")
        self.create_color_composite_btn = QtWidgets.QPushButton("Color Composite")
        self.create_noise_btn = QtWidgets.QPushButton("Noise")
        self.create_distance_tex_btn = QtWidgets.QPushButton("VRay Distance Tex")
        self.create_dirt_btn = QtWidgets.QPushButton("VRay Dirt")
        self.create_file_btn = QtWidgets.QPushButton("Create File")

    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)

        prefix_layout = QtWidgets.QHBoxLayout()
        prefix_layout.addWidget(self.prefix_lbl)
        prefix_layout.addWidget(self.prefix_le)

        main_layout.addLayout(prefix_layout)

        main_layout.addWidget(self.material_builder_btn)
        main_layout.addWidget(self.create_file_btn)
        main_layout.addWidget(self.create_cc_btn)
        main_layout.addWidget(self.create_color_composite_btn)
        main_layout.addWidget(self.create_noise_btn)
        main_layout.addWidget(self.create_distance_tex_btn)
        main_layout.addWidget(self.create_dirt_btn)

    def create_connections(self):
        self.create_file_btn.clicked.connect(self.create_file_btn_callback)
        self.create_cc_btn.clicked.connect(self.create_cc_btn_callback)
        self.create_color_composite_btn.clicked.connect(self.create_color_composite_btn_callback)
        self.create_noise_btn.clicked.connect(self.create_noise_btn_callback)
        self.create_distance_tex_btn.clicked.connect(self.create_distance_tex_btn_callback)

    def create_file_btn_callback(self):
        lookdev_utils.create_texture(name=self.prefix_le.text())

    def create_cc_btn_callback(self):
        selection = pm.ls(sl=1)

        if selection:
            for n in selection:
                lookdev_utils.create_cc_node(name=self.prefix_le.text(), source_node=n)
        else:
            lookdev_utils.create_cc_node(name=self.prefix_le.text())

    def create_color_composite_btn_callback(self):
        selection = pm.ls(sl=1)

        if len(selection) >= 2:
            lookdev_utils.create_color_composite_node(name=self.prefix_le.text(), source_a=selection[0],
                                                      source_b=selection[1])
        elif len(selection) == 1:
            lookdev_utils.create_color_composite_node(name=self.prefix_le.text(), source_a=selection[0])
        else:
            lookdev_utils.create_color_composite_node(name=self.prefix_le.text())

    def create_noise_btn_callback(self):
        selection = pm.ls(sl=1)

        if selection:
            for n in selection:
                lookdev_utils.create_noise(name=self.prefix_le.text())
        else:
            lookdev_utils.create_noise(name=self.prefix_le.text())

    def create_distance_tex_btn_callback(self):
        selection = pm.ls(sl=1)

        if selection:
            vray_lookdev.create_vray_distance_tex(name=self.prefix_le.text(), set_members=selection)
        else:
            vray_lookdev.create_vray_distance_tex(name=self.prefix_le.text())


def main():
    try:
        cmds.deleteUI("LookdevToolKit")
    except Exception:
        pass

    dialog = LookdevToolKit()
    dialog.show()


if __name__ == "__main__":
    main()
