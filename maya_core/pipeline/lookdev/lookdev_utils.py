import os
import logging

import pymel.core as pm
import maya.cmds as cmds

logging.basicConfig()

logger = logging.getLogger(__name__)


def create_texture(name=None, path=None, cc=True, uv=True, ptex=False):
    nodes = {}

    if ptex:
        texture_node = pm.shadingNode('VRayPtex', asTexture=True, isColorManaged=True)
    else:
        texture_node = pm.shadingNode('file', asTexture=True, isColorManaged=True)

    nodes['texture_node'] = texture_node

    if path:
        if ptex:
            texture_node.ptexFile.set(path)
        else:
            texture_node.fileTextureName.set(path)

    if uv and not ptex:
        uv_node = pm.shadingNode("place2dTexture", asUtility=True)
        nodes['uv_node'] = uv_node

        pm.connectAttr(uv_node.outUV, texture_node.uvCoord)

    if cc:
        cc_node = create_cc_node(texture_node)
        nodes['cc_node'] = cc_node

    if name:
        if not ptex:
            texture_node.rename(name + "_TEX")
        else:
            texture_node.rename(name + "_PTEX")

        if uv and not ptex:
            uv_node.rename(name + "_UV")

        if cc:
            cc_node.rename(name + "_CC")

    logger.info("Created %s", str(texture_node))

    return nodes


def create_cc_node(source_node=None):
    # Create CC Node
    cc_node = pm.shadingNode('colorCorrect', asUtility=True)

    # Connect gamma attributes
    pm.connectAttr(cc_node.colGammaX, cc_node.colGammaY)
    pm.connectAttr(cc_node.colGammaX, cc_node.colGammaZ)

    if source_node:
        if not isinstance(source_node, pm.PyNode):
            source_node = pm.PyNode(source_node)

        # Store original outcolor connections
        out_connections = pm.listConnections(source_node, connections=True, plugs=True)

        # Connect file to cc
        pm.connectAttr(source_node.outColor, cc_node.inColor)
        pm.connectAttr(source_node.outAlpha, cc_node.inAlpha)

        # Connect cc to original connections
        for connection_pair in out_connections:
            out_attr = connection_pair[0].split(".")[-1]
            if out_attr.startswith("outColor") or out_attr == "outAlpha":
                source_connection = connection_pair[0].split(".")[-1]
                target_connection = connection_pair[-1]
                pm.connectAttr(cc_node + "." + source_connection, target_connection, f=True)

        pm.rename(cc_node, str(source_node) + "_CC")

        logger.info("Created %s", str(cc_node))

    return cc_node


def create_projection(name='', path='', comp=True):
    tex_nodes = create_texture(name=name, path=path)
    tex_nodes['uv_node'].wrapU.set(0)
    tex_nodes['uv_node'].wrapV.set(0)
    tex_nodes['texture_node'].defaultColor.set([0, 0, 0])

    # Create 3d projection nodes
    place = pm.shadingNode("place3dTexture", asUtility=True)
    proj = pm.shadingNode("projection", asUtility=True)

    pm.connectAttr(place.worldInverseMatrix, proj.placementMatrix)
    pm.connectAttr(tex_nodes['cc_node'].outColor, proj.image)

    proj.defaultColor.set([0, 0, 0])

    # Composite
    if comp:
        composite = pm.shadingNode("colorComposite", asUtility=True)
        pm.connectAttr(proj.outColorR, composite.factor)
        composite.operation.set(2)

    # Rename
    if name:
        pm.rename(place, "{}_place3dTexture".format(name))
        pm.rename(proj, "{}_projection".format(name))
        if comp:
            pm.rename(composite, "{}_colorComposite".format(name))


def get_materials_from_selection():
    materials = []

    for obj in cmds.ls(sl=1, dag=1, s=1):
        sgs = pm.listConnections(obj, type="shadingEngine")
        for sg in sgs:
            mats = pm.listConnections(sg.surfaceShader)
            if pm.sets(sg, q=1):
                if mats:
                    materials.extend(mats)

    return materials


def get_materials_from_node(nodes=None):
    materials = []

    for obj in nodes:
        sgs = pm.listConnections(obj, type="shadingEngine")
        for sg in sgs:
            mats = pm.listConnections(sg.surfaceShader)
            if pm.sets(sg, q=1):
                if mats:
                    materials.extend(mats)

    return materials


def get_materials(node):
    materials = {}

    sgs = pm.listConnections(node, type="shadingEngine")

    shading_group = None
    if sgs:
        shading_group = sgs[0]
    else:
        return

    mats = pm.listConnections(shading_group.surfaceShader)

    if pm.sets(shading_group, q=1):
        if mats:
            materials[shading_group] = mats

    return materials
