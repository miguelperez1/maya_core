from functools import partial
import os
import logging

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm

from maya_core.maya_pyqt import MWidgets
from maya_core.pipeline.lookdev.material_builder import MaterialBuilder
from tools_core.pyqt_commons import common_widgets as cw
from maya_core.pipeline.lookdev import lookdev_utils


logger = logging.getLogger(__name__)
logger.setLevel(10)


class MaterialBuilderUI(QtWidgets.QMainWindow):
    def __init__(self, parent=MWidgets.maya_main_window()):
        super(MaterialBuilderUI, self).__init__(parent)

        self.setWindowTitle("Material Builder")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.setObjectName("MaterialBuilderUI")

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.setMinimumSize(800, 400)

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
            cb_widget = QtWidgets.QCheckBox()

            fb_widget = cw.FileBrowseWidget(tex_type.title())

            fb_widget.tex_type = tex_type
            fb_widget.lble_widget.lbl_widget.setMinimumWidth(120)

            fb_widget.main_layout.insertWidget(0, cb_widget)

            fb_widget.cb_widget = cb_widget

            fb_widget.lble_widget.le_widget.textChanged.connect(partial(self.fb_changed_callback, fb_widget))

            self.fb_widgets.append(fb_widget)

        self.assign_cb = QtWidgets.QCheckBox("Assign")
        self.assign_cb.setChecked(True)

        self.build_btn = QtWidgets.QPushButton("Build")
        self.check_all_btn = QtWidgets.QPushButton("Check All")

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

        btn_layout.addWidget(self.check_all_btn)

        btn_layout.addStretch()

        btn_layout.addWidget(self.assign_cb)
        btn_layout.addWidget(self.build_btn)

        main_layout.addLayout(btn_layout)

    def create_connections(self):
        self.build_btn.clicked.connect(self.build_material)
        self.check_all_btn.clicked.connect(self.check_all_btn_callback)

    def fb_changed_callback(self, widget, text):
        if widget.text():
            if os.path.isfile(widget.text()):
                widget.cb_widget.setChecked(True)

    def check_all_btn_callback(self):
        for fb_widget in self.fb_widgets:
            fb_widget.cb_widget.setChecked(True)

    def build_material(self):
        selection = pm.ls(sl=1)

        material_data = {
            "material_name": self.material_name_lble.text(),
            "material_shader": self.material_type_cmbx.currentText(),
            "textures": {}
        }

        for fb_widget in self.fb_widgets:
            if fb_widget.cb_widget.isChecked():
                if os.path.isfile(fb_widget.text()):
                    material_data["textures"][fb_widget.tex_type] = fb_widget.text()

        mtls = MaterialBuilder.build_material(material_data)

        if self.assign_cb.isChecked():
            if not selection:
                return

            lookdev_utils.assign_material(mtls[1], selection)

            if len(mtls) == 3 and mtls[2] is not None:
                lookdev_utils.assign_material(mtls[2], selection)


def main():
    try:
        cmds.deleteUI("MaterialBuilderUI")
    except Exception:
        pass

    dialog = MaterialBuilderUI()
    dialog.show()


if __name__ == "__main__":
    main()
