import os
import logging
from importlib import reload

from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.cmds as cmds
import pymel.core as pm

from maya_core.maya_pyqt import MWidgets
from tools_core.pyqt_commons import common_widgets as cw
from tools_core.asset_library import library_manager as lm
from maya_core.asset_library.asset_publish import asset_publish

reload(asset_publish)

logger = logging.getLogger(__name__)
logger.setLevel(10)


class AssetPublisherUI(QtWidgets.QMainWindow):
    def __init__(self, parent=MWidgets.maya_main_window()):
        super(AssetPublisherUI, self).__init__(parent)

        self.setWindowTitle("Publish Asset")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.setObjectName("AssetPublisherUI")

        self.prefs_directory = cmds.internalVar(userPrefDir=True)

        self.setMinimumWidth(800)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_actions(self):
        pass

    def create_widgets(self):
        self.asset_name_lble = cw.LabeledLineEdit("Name: ")

        self.library_cmbx = QtWidgets.QComboBox()
        self.library_cmbx.addItems(lm.LIBRARIES.keys())

        self.tags_lble = cw.LabeledLineEdit("Tags: ")

        self.preview_fb = cw.FileBrowseWidget("Preview")

        self.build_btn = QtWidgets.QPushButton("Build")

    def create_layout(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QtWidgets.QVBoxLayout(central_widget)

        row1_layout = QtWidgets.QHBoxLayout()
        row1_layout.addWidget(self.asset_name_lble)
        row1_layout.addWidget(self.library_cmbx)

        main_layout.addLayout(row1_layout)

        row2_layout = QtWidgets.QHBoxLayout()

        row2_layout.addWidget(self.preview_fb)

        main_layout.addLayout(row2_layout)

        row3_layout = QtWidgets.QHBoxLayout()

        row3_layout.addWidget(self.tags_lble)

        main_layout.addLayout(row3_layout)

        btn_layout = QtWidgets.QHBoxLayout()

        btn_layout.addStretch()
        btn_layout.addWidget(self.build_btn)

        main_layout.addLayout(btn_layout)

    def create_connections(self):
        self.asset_name_lble.le_widget.textChanged.connect(self.asset_name_check)
        self.build_btn.clicked.connect(self.build_btn_callback)

    def build_btn_callback(self):
        selection = pm.ls(sl=1)

        if not selection or not self.asset_name_lble.text():
            return

        source_node = pm.ls(sl=1)[0]

        tags = []

        if "," in self.tags_lble.text():
            tags = self.tags_lble.text().split(",")
        else:
            tags = [self.tags_lble.text()]

        preview_source = self.preview_fb.text()

        if preview_source and not os.path.isfile(preview_source):
            preview_source = ""

        asset_publish.publish_from_selection(asset_name=self.asset_name_lble.text(), source_node=source_node,
                                             library=self.library_cmbx.currentText(), tags=tags,
                                             preview_source=preview_source)

        self.asset_name_check()

    def asset_name_check(self):

        if self.asset_name_lble.le_widget.text().lower() in [a.lower() for a in
                                                      lm.get_library_data(self.library_cmbx.currentText())[
                                                          "assets"].keys()]:
            self.asset_name_lble.le_widget.setStyleSheet("color: red")
            self.build_btn.setEnabled(False)

        else:
            self.asset_name_lble.le_widget.setStyleSheet("")
            self.build_btn.setEnabled(True)


def main():
    try:
        cmds.deleteUI("AssetPublisherUI")
    except Exception:
        pass

    dialog = AssetPublisherUI()
    dialog.show()


if __name__ == "__main__":
    main()
