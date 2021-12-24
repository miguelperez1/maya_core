import os
import logging

import pymel.core as pm
import maya.cmds as cmds

logging.basicConfig()

logger = logging.getLogger(__name__)


def create_displacement_node(name=None, disp_source=None, obj=None):
    disp_node = pm.shadingNode("VRayDisplacement", asUtility=True)

    cmds.vray("addAttributesFromGroup", str(disp_node), "vray_subdivision", 1)
    cmds.vray("addAttributesFromGroup", str(disp_node), "vray_subquality", 1)
    cmds.vray("addAttributesFromGroup", str(disp_node), "vray_displacement", 1)
    disp_node.overrideGlobalDisplacement.set(1)
    disp_node.vrayEdgeLength.set(4)
    disp_node.vrayMaxSubdivs.set(128)
    disp_node.vrayDisplacementShift.set(-0.5)

    if name:
        disp_node.rename(name + "_vrdisp")

    if disp_source:
        pm.connectAttr(disp_source.outColor, disp_node.displacement)

    if obj:
        cmds.sets(str(obj), edit=True, add=str(disp_node))

    return disp_node


def create_vray_distance_tex(name=None, set_members=None):
    dist = pm.shadingNode("VRayDistanceTex", asUtility=True)
    obj_set = dist.listConnections(et=1, t="objectSet")[0]

    if name:
        dist.rename(name + "_VRayDistanceTex")
        obj_set(name + "_distTexSet")

    if set_members:
        if isinstance(set_members, list):
            obj_set.addMembers(set_members)
        else:
            obj_set.addMembers([set_members])