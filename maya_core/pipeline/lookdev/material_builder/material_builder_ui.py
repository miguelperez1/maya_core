import logging

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm

from maya_core.maya_pyqt import MWidgets
from maya_core.pipeline.lookdev.material_builder import MaterialBuilder
from tools_core.pyqt_commons import common_widgets as cw

logger = logging.getLogger(__name__)
logger.setLevel(10)


class MaterialBuilderUI(QtWidgets.QMainWindow):
    def __init__(self, parent=MWidgets.maya_main_window()):
        super(MaterialBuilderUI, self).__init__(parent)

        self.setWindowTitle("Material Builder")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.setObjectName("MaterialBuilderUI")

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.setMinimumSize(900, 400)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.material_name_lble = cw.LabeledLineEdit("Name")

        self.material_type_cmbx = QtWidgets.QComboBox()

        self.material_type_cmbx.addItems(MaterialBuilder.DEFAULT_CONNECTIONS.keys())

        self.fb_widgets = []

        for tex_type in MaterialBuilder.TEX_TYPES:
            fb_widget = cw.FileBrowseWidget(tex_type.title())

            fb_widget.tex_type = tex_type
            fb_widget.lble_widget.lbl_widget.setMinimumWidth(150)

            self.fb_widgets.append(fb_widget)

        self.assign_cb = QtWidgets.QCheckBox("Assign")
        self.build_btn = QtWidgets.QPushButton("Build")

    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)

        margin = 30
        spacing = 10
        main_layout.setContentsMargins(margin, margin, margin, margin)
        main_layout.setSpacing(spacing)

        header_layout = QtWidgets.QHBoxLayout()

        header_layout.addWidget(self.material_name_lble)
        header_layout.addWidget(self.material_type_cmbx)

        main_layout.addLayout(header_layout)

        main_layout.addWidget(cw.QHLine())

        for fb_widget in self.fb_widgets:
            main_layout.addWidget(fb_widget)

        btn_layout = QtWidgets.QHBoxLayout()

        btn_layout.addStretch()

        btn_layout.addWidget(self.assign_cb)
        btn_layout.addWidget(self.build_btn)

        main_layout.addLayout(btn_layout)

    def create_connections(self):
        pass


def main():
    try:
        cmds.deleteUI("MaterialBuilderUI")
    except Exception:
        pass

    dialog = MaterialBuilderUI()
    dialog.show()


if __name__ == "__main__":
    main()
