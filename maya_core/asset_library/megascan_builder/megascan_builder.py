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

    # Build maya asset world node
    create_world_node_file(asset)

    # Reinitialize file to get mesh name
    cmds.file(f=1, new=1)
    cmds.file(rename=os.path.join(asset_data["asset_path"], "02_model", "wip",
                                  "{}_model_v001.ma".format(asset_data["asset_name"])))

    # Import mesh
    cmds.file(asset_data["mesh"], i=1)

    mesh = pm.ls(type="mesh")[0].getTransform()

    mesh.rename(asset_data["asset_name"] + "_PART")

    # Import world node
    cmds.file(asset.world_path, i=True)

    # Parent mesh
    pm.parent(mesh, "GEO")

    # TODO Publish model stage
    cmds.file(save=True, type="mayaAscii")

    # TODO Create vray proxy

    # Build material
    if asset_data["materials"]:
        # Reinitialize to lookdev
        cmds.file(rename=os.path.join(asset_data["asset_path"], "03_lookdev", "wip",
                                      asset_data["asset_name"] + "_lookdev_v001.ma"))

        mtl = mb.build_material(asset_data["materials"][0])[1]

        # Assign material
        cmds.sets(str(mesh), edit=True, forceElement=str(mtl))

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
    json_file = open(sys.argv[1], "r")
    asset_data = json.load(json_file)
    json_file.close()

    logger.debug("json_file")

    build_megascan_model(asset_data)

    logger.info("Built %s successfully", asset_data['asset_name'])


if __name__ == '__main__':
    main()
