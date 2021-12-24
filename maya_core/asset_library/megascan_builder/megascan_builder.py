import os
import sys
import json
import logging

import maya.standalone as standalone

standalone.initialize(name='python')

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

from maya_core.maya_asset import MayaAsset
from maya_core.pipeline.lookdev.material_builder import MaterialBuilder as mb
from tools_core.asset_library import library_manager as lm
from maya_core.pipeline.modeling.normalize_scale import normalize_scale as ns

logging.basicConfig()
logger = logging.getLogger(__name__)


def create_world_node_file(asset):
    cmds.file(f=True, new=True)

    asset_data = asset.asset_data

    asset_name = asset_data['asset_name']
    asset_type = asset_data['asset_type']

    asset_maya_path = os.path.join(asset_data["asset_path"], '01_build', 'world_node', '{}.ma'.format(asset_name))

    cmds.file(rename=os.path.join(asset_maya_path))

    asset_node = MayaAsset.MayaAsset(asset_data=asset_data)
    asset_node.create_maya_asset_node()

    cmds.file(save=True, type="mayaAscii")

    if os.path.isfile(asset_maya_path) and pm.objExists(asset_node.world_node):
        logger.info("Successfully built %s maya file", asset_name)


def build_megascan_model(asset_data):
    asset = MayaAsset.MayaAsset(asset_data)

    asset_name = asset_data["asset_name"]
    asset_path = asset_data["asset_path"]

    # Build maya asset world node
    create_world_node_file(asset)

    # Reinitialize file to get mesh name
    cmds.file(f=1, new=1)
    model_path = os.path.join(asset_data["asset_path"], "02_model")
    cmds.file(rename=os.path.join(asset_data["asset_path"], "02_model", "wip",
                                  "{}_model_v001.ma".format(asset_data["asset_name"])))

    # Import mesh
    cmds.file(asset_data["mesh"], i=1)

    mesh = pm.ls(type="mesh")[0].getTransform()

    mesh.rename(asset_data["asset_name"] + "_PART")

    pm.select(mesh)

    cmds.CenterPivot()

    for obj in cmds.ls(sl=True, type="transform"):
        bbox = cmds.exactWorldBoundingBox(obj)
        cmds.xform(obj, ws=True, p=True, cp=True)
        center_pos = cmds.xform(obj, q=True, ws=True, sp=True)
        cmds.xform(obj, ws=True, piv=(center_pos[0], bbox[1], center_pos[2]))

    cmds.move(rpr=True)

    mel.eval("FreezeTransformations")

    pm.select(cl=1)

    if asset_data["scale"]:
        ns.normalize_scale(asset_data["scale"], mesh, axis="y")

    # Import world node
    cmds.file(asset.world_path, i=True)

    # Parent mesh
    pm.parent(mesh, "GEO")

    # TODO Publish model stage
    cmds.file(save=True, type="mayaAscii")

    # TODO Create vray proxy
    cmds.vrayCreateProxy(exportType=1, previewFaces=17500, dir=os.path.join(model_path, "publish"),
                         fname=asset_name + ".vrmesh",
                         overwrite=True,
                         previewType="clustering", makeBackup=False, ignoreHiddenObjects=False, vertexColorsOn=True,
                         exportHierarchy=True, includeTransformation=True)

    vrmesh = asset_name + "_vrmesh"
    vrproxy_path = os.path.join(model_path, "publish", asset_name + ".vrmesh")

    cmds.vrayCreateProxy(createProxyNode=True, node=vrmesh, existing=True,
                         dir=vrproxy_path, geomToLoad=3, newProxyNode=True)

    vrmesh = pm.PyNode(vrmesh)

    pm.parent(vrmesh, "Proxy")

    # Build material
    if asset_data["materials"]:
        # Reinitialize to lookdev
        cmds.file(rename=os.path.join(asset_data["asset_path"], "03_lookdev", "wip",
                                      asset_data["asset_name"] + "_lookdev_v001.ma"))

        mtl_nodes = mb.build_material(asset_data["materials"][0])
        mtl = mtl_nodes[1]

        if len(mtl_nodes) == 3:
            disp_node = mtl_nodes[-1]

            cmds.sets(str(mesh), edit=True, forceElement=str(disp_node))
            cmds.sets(str(vrmesh), edit=True, forceElement=str(disp_node))

            disp_node.vrayDisplacementAmount.set(0.01)
            disp_node.vrayDisplacementShift.set(-0.005)

        # Assign material
        cmds.sets(str(mesh), edit=True, forceElement=str(mtl))
        cmds.sets(str(vrmesh), edit=True, forceElement=str(mtl))

        # TODO Publish lookdev stage
        cmds.file(save=True, type="mayaAscii")

    # Constrain to common rig

    # Publish rig stage

    # Save to master
    asset_data["maya_file"] = os.path.join(asset_data["asset_path"], asset_data["asset_name"] + ".ma")

    cmds.file(rename=asset_data["maya_file"])
    cmds.file(save=True, type="mayaAscii")

    lm.write_asset_data("Prop", asset_data["asset_name"], asset_data)


def main():
    mel.eval("loadPlugin vrayformaya")
    mel.eval("loadPlugin lookdevKit")

    json_file = open(sys.argv[1], "r")
    asset_data = json.load(json_file)
    json_file.close()

    logger.debug("json_file")

    build_megascan_model(asset_data)

    logger.info("Built %s successfully", asset_data['asset_name'])


if __name__ == '__main__':
    main()