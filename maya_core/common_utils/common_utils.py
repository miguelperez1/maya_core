import pymel.core as pm
import maya.cmds as cmds


def filter_connected_nodes(node, node_type=None):
    connected_nodes = []

    if node_type:
        connections = cmds.ls(*cmds.listHistory(str(node)), type=node_type)
        if connections:
            connected_nodes.extend([pm.PyNode(n) for n in connections])
    else:
        connections = cmds.ls(*cmds.listHistory(str(node)))
        if connections:
            connected_nodes.extend([pm.PyNode(n) for n in connections])

    return connected_nodes
