import os
import json
import logging

import pymel.core as pm
import maya.cmds as cmds

from tools_core.pipeline.Asset import Asset

logger = logging.getLogger(__name__)
logger.setLevel(10)


def create_node_struct(d, parent=None):
    logger.debug("%s, %s", d['node_name'], parent)
    if "children" in d.keys():
        if d['node_name'] == "top_level":
            _ = [create_node_struct(a, parent) for a in d['children']]
        else:
            p = pm.createNode("transform", n=d['node_name'], p=parent)
            logger.info("Created %s", str(p))
            _ = [create_node_struct(a, p) for a in d['children']]
    else:
        p = pm.createNode("transform", n=d['node_name'], p=parent)
        logger.info("Created %s", str(p))


class MayaAsset(Asset.Asset):
    def __init__(self, asset_data=None, node=None):
        super(MayaAsset, self).__init__(asset_data=asset_data)
        self.world_node = node
        self.maya_file = os.path.join(self.asset_root_path, self.asset_name + ".ma")

    def create_maya_asset_node(self):
        # Create Nodes
        self.world_node = pm.createNode("transform", n=self.asset_data['asset_name'])

        asset_structure_json_path = r"F:\share\tools\maya_core\maya_core\maya_asset\MayaAsset_node_structure.json"

        json_file = open(asset_structure_json_path, "r")
        asset_structure_data = json.load(json_file)
        json_file.close()

        create_node_struct(asset_structure_data, parent=self.world_node)

        # Create Attrs
        cmds.addAttr(str(self.world_node), ln="mayaAsset", at="long")
        cmds.addAttr(str(self.world_node), ln="assetType", dt="string")
        cmds.addAttr(str(self.world_node), ln="assetName", dt="string")
        cmds.addAttr(str(self.world_node), ln="geoVis", at="enum", en="HiRes:Proxy")

        self.world_node.mayaAsset.set(1)
        self.world_node.mayaAsset.lock()
        self.world_node.assetType.set(self.asset_data['asset_type'])
        self.world_node.assetType.lock()
        self.world_node.assetName.set(self.asset_data['asset_name'])
        self.world_node.assetName.lock()

        # Geo Vis Setup

        # Reverse Node
        reverse = pm.createNode("reverse", n=self.asset_data["asset_name"] + "_GeoVis_Reverse")

        self.world_node.geoVis >> reverse.input.inputX
        reverse.output.outputX >> pm.PyNode("HiRes").visibility
        self.world_node.geoVis >> pm.PyNode("Proxy").visibility

    def import_world_node(self):
        cmds.file(self.world_node_path, i=1)
        self.world_node = pm.PyNode(self.asset_name)
        return self.world_node

    def apply_hair_cache(self, cache_path):
        pass

    def cache_hair(self, cache_path, frame_range):
        pass

    def cache_geo(self):
        pass
