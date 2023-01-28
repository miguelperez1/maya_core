import os
import sys
import json
import logging


import maya.standalone as standalone

standalone.initialize(name='python')

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

sys.path.append("F:\\share\\tools\\tools_core")
sys.path.append("F:\\share\\tools\\maya_core")

from maya_core.maya_startup import maya_startup

maya_startup.main()

from maya_core.maya_asset import MayaAsset

logging.basicConfig()
logger = logging.getLogger(__name__)


def create_world_node_file(asset):
    cmds.file(f=True, new=True)

    asset_data = asset.asset_data

    asset_name = asset_data['asset_name']

    asset_maya_path = os.path.join(asset_data["asset_path"], '01_build', 'world_node', '{}.ma'.format(asset_name))

    cmds.file(rename=os.path.join(asset_maya_path))

    asset_node = MayaAsset.MayaAsset(asset_data=asset_data)
    asset_node.create_maya_asset_node()

    cmds.file(save=True, type="mayaAscii")

    if os.path.isfile(asset_maya_path) and pm.objExists(asset_node.world_node):
        logger.info("Successfully built %s maya file", asset_name)


def main():
    json_file = open(sys.argv[1], "r")
    asset_data = json.load(json_file)
    json_file.close()

    new_asset = MayaAsset.MayaAsset(asset_data=asset_data)

    create_world_node_file(new_asset)


if __name__ == '__main__':
    main()
