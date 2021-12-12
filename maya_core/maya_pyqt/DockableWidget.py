from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

import maya.OpenMayaUI as omui
import maya.cmds as cmds
from shiboken2 import getCppPointer


class DockableWidget(QtWidgets.QWidget):
    widget_instance = None

    @classmethod
    def display(cls):
        if cls.widget_instance:
            cls.widget_instance.show_workspace_control()
        else:
            cls.widget_instance = cls()

    @classmethod
    def get_workspace_control_name(cls):
        return "{}WorkspaceControl".format(cls.__name__)

    @classmethod
    def get_ui_script(cls):
        module_name = cls.__module__
        if module_name == "__main__":
            module_name = cls.module_name_override

        ui_script = "from {0} import {1}\n{1}.display()".format(module_name, cls.__name__)
        return ui_script

    def __init__(self):
        super(DockableWidget, self).__init__()

        self.setObjectName(self.__class__.__name__)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.create_workspace_control()

    def create_actions(self):
        pass

    def create_widgets(self):
        pass

    def create_layout(self):
        pass

    def create_connections(self):
        pass

    def create_workspace_control(self):
        self.workspace_control = WorkspaceControl(self.get_workspace_control_name())

        if self.workspace_control.exists():
            # pass instance of widget to restore
            self.workspace_control.restore(self)
        else:
            # ui_script makes it persistent
            self.workspace_control.create(self.WINDOW_TITLE, self, ui_script=self.get_ui_script())

    def show_workspace_control(self):
        self.workspace_control.set_visible(True)


class WorkspaceControl(object):

    def __init__(self, name):
        self.name = name
        self.widget = None

    def create(self, label, widget, ui_script=None):
        cmds.workspaceControl(self.name, label=label)

        if ui_script:
            cmds.workspaceControl(self.name, e=True, uiScript=ui_script)

        self.add_widget_to_layout(widget)
        self.set_visible(True)

    def restore(self, widget):
        self.add_widget_to_layout(widget)

    def add_widget_to_layout(self, widget):
        if widget:
            self.widget = widget
            self.widget.setAttribute(QtCore.Qt.WA_DontCreateNativeAncestors)

            workspace_control_ptr = int(omui.MQtUtil.findControl(self.name))
            widget_ptr = int(getCppPointer(self.widget)[0])

            omui.MQtUtil.addWidgetToMayaLayout(widget_ptr, workspace_control_ptr)

    def exists(self):
        return cmds.workspaceControl(self.name, q=True, exists=True)

    def is_visible(self):
        return cmds.workspaceControl(self.name, q=True, visible=True)

    def set_visible(self, visible):
        if visible:
            cmds.workspaceControl(self.name, e=True, restore=True)
        else:
            cmds.workspaceControl(self.name, e=True, visible=False)

    def set_label(self, label):
        cmds.workspaceControl(self.name, e=True, label=label)

    def is_floating(self):
        return cmds.workspaceControl(self.name, q=True, floating=True)

    def is_collapsed(self):
        return cmds.workspaceControl(self.name, q=True, collapsed=True)
