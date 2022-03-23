import os
import string
import logging

import pymel.core as pm
import maya.cmds as cmds

logging.basicConfig()

logger = logging.getLogger(__name__)

MATERIAL_TYPES = [
    "VRayMtl"
]


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
        cc_node = create_cc_node(source_node=texture_node)
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


def create_cc_node(name=None, source_node=None):
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

    if source_node and not name:
        pm.rename(cc_node, str(source_node) + "_CC")
    elif name:
        name = (name + "_CC") if not name.endswith("_CC") else name
        cc_node.rename(name)

    logger.info("Created %s", str(cc_node))

    return cc_node


def create_color_composite_node(name=None, source_a=None, source_b=None):
    # Create CC Node
    cc_node = pm.shadingNode('colorComposite', asUtility=True)

    sources = [source_a, source_b]

    # Connect gamma attributes
    for i, source in enumerate(sources):
        if not source:
            continue

        if not isinstance(source, pm.PyNode):
            source = pm.PyNode(source)

        # Connect to cc
        if hasattr(source, "outColor"):
            pm.connectAttr(source.outColor, getattr(cc_node, "color" + string.ascii_uppercase[i]))

        if hasattr(source, "outAlpha"):
            pm.connectAttr(source.outAlpha, getattr(cc_node, "alpha" + string.ascii_uppercase[i]))

    if source_a and not name:
        pm.rename(cc_node, str(source_a) + "_CComp")
    elif name:
        name = (name + "_CComp") if not name.endswith("_CComp") else name
        cc_node.rename(name)

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
    materials_tmp = {}

    for c in pm.ls(sl=1):
        sgs = pm.listConnections(c.getShape(), type="shadingEngine")

        for sg in sgs:
            mats = pm.listConnections(sg.surfaceShader, type=MATERIAL_TYPES)

            if mats:
                for mat in mats:
                    if str(mat) not in materials_tmp.keys():
                        materials_tmp[str(mat)] = mat

    materials = []

    for material, node in materials_tmp.items():
        materials.append(node)

    return materials


def get_materials_from_node(node=None):
    materials_tmp = {}

    sgs = pm.listConnections(node.getShape(), type="shadingEngine")

    for sg in sgs:
        mats = pm.listConnections(sg.surfaceShader, type=MATERIAL_TYPES)

        if mats:
            for mat in mats:
                if str(mat) not in materials_tmp.keys():
                    materials_tmp[str(mat)] = mat

    materials = []

    for material, node in materials_tmp.items():
        materials.append(node)

    return materials


def assign_material(mtl, nodes):
    if not isinstance(nodes, list):
        nodes = [nodes]

    for node in nodes:
        cmds.sets(str(node), edit=True, forceElement=str(mtl))


def create_noise(name=None, cc=False, uv=True):
    nodes = {}

    noise_node = pm.shadingNode('noise', asTexture=True, isColorManaged=True)
    noise_node.noiseType.set(0)

    nodes['texture_node'] = noise_node

    if uv:
        uv_node = pm.shadingNode("place2dTexture", asUtility=True)

        nodes['uv_node'] = uv_node

        pm.connectAttr(uv_node.outUV, noise_node.uvCoord)

    if cc:
        cc_node = create_cc_node(source_node=noise_node)
        nodes['cc_node'] = cc_node

    if name:
        noise_node.rename(name + "_Noise")

        if uv:
            uv_node.rename(name + "_Noise_UV")

        if cc:
            cc_node.rename(name + "_Noise_CC")

    logger.info("Created %s", str(noise_node))


    return nodes
