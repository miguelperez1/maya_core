import os
import logging
import re

import maya.cmds as cmds
import pymel.core as pm

from tools_core.asset_library import library_manager as lm
from maya_core.maya_asset import MayaAsset
from maya_core.pipeline.lookdev import lookdev_utils
from maya_core.common_utils import common_utils as cu

logger = logging.getLogger(__name__)


def create_kitbash_asset(source_group_node, tags=None, preview_source=None):
    asset_name = str(source_group_node).replace("_grp", "")

    # Gather asset data

    asset_data = {
        "asset_name": asset_name,
        "asset_preview": preview_source,
        "asset_type": "Prop",
        "asset_path": None,
        "usd": None,
        "vrmesh": None,
        "vrproxy_maya": None,
        "vrscene": None,
        "vrscene_maya": None,
        "maya_file": None,
        "mesh": None,
        "scale": None,
        "materials": None,
        "megascan_id": None,
        "tags": ["kitbash"]
    }

    if tags:
        asset_data["tags"].extend(tags)

    # Gather materials/material data
    materials_tmp = {}

    for c in source_group_node.listRelatives(c=1):
        mtls = lookdev_utils.get_materials_from_node(c)

        for mtl in mtls:
            if str(mtl) not in materials_tmp.keys():

                material_data = {
                    "material_name": str(mtl),
                    "material_shader": str(mtl.nodeType()),
                    "textures": {}
                }

                file_nodes = cu.filter_connected_nodes(mtl, "file")

                for file_node in file_nodes:
                    tex_path = file_node.fileTextureName.get()

                    # Check diffuse
                    if re.search("(diffuse|basecolor|albedo)", tex_path.lower()):
                        material_data["textures"]["diffuse"] = tex_path

                    # Check Specular
                    elif re.search("(specular)", tex_path.lower()):
                        material_data["textures"]["specular"] = tex_path

                    # Check Gloss
                    elif re.search("(gloss)", tex_path.lower()):
                        material_data["textures"]["gloss"] = tex_path

                    # Check Roughness
                    elif re.search("(roughness)", tex_path.lower()):
                        material_data["textures"]["roughness"] = tex_path
                        try:
                            pm.disconnectAttr(file_node.outColor.outColorR, mtl.roughnessAmount)
                        except Exception:
                            pass

                    # Check Normal
                    elif re.search("(normal)", tex_path.lower()):
                        material_data["textures"]["normal"] = tex_path

                    # Check metal
                    elif re.search("(metal)", tex_path.lower()):
                        material_data["textures"]["metal"] = tex_path

                materials_tmp[str(mtl)] = {
                    "node": mtl,
                    "material_data": material_data
                }

    materials = []

    for material, mtl_data in materials_tmp.items():
        materials.append(mtl_data["material_data"])

    asset_data["materials"] = materials

    # Create the asset in the pipeline
    new_asset = MayaAsset.MayaAsset(asset_data=asset_data)
    new_asset.build_maya = True

    new_asset.create_asset()

    # Import world node
    asset_world_node = new_asset.import_world_node()

    # Create VRay Proxy
    for c in source_group_node.listRelatives(c=1):
        pm.select(cl=1)

        # Duplicate mesh
        d = c.duplicate()

        pm.select(d)

        model_path = os.path.join(new_asset.asset_root_path, "02_model")

        v = cmds.vrayCreateProxy(createProxyNode=1, dir=os.path.join(model_path, "publish"),
                                 fname=str(c) + ".vrmesh", node=str(c) + "_vrproxy", newProxyNode=1,
                                 exportHierarchy=1, exportType=1, includeTransformation=1, makeBackup=1,
                                 previewFaces=17500, previewType="clustering", lastSelectedAsPreview=1, pointSize=0.500,
                                 vertexColorsOn=1, geomToLoad=3)[0]

        pm.parent(v, "{}|Geometry|Constrain|Proxy".format(asset_name))

        pm.select(cl=1)

    # Parent all geo under world node
    geo_node = pm.PyNode("|".join([str(new_asset.world_node), "Geometry", "Constrain", "HiRes", "GEO"]))

    for c in source_group_node.listRelatives(c=1):
        pm.parent(c, geo_node)

    # Re-path images
    for material, mtl_data in materials_tmp.items():
        mtl = mtl_data["node"]

        file_nodes = cu.filter_connected_nodes(mtl, "file")

        try:
            mtl.reflectionColor.set(.7, .7, .7)
        except Exception:
            pass

        for file_node in file_nodes:
            file_name = os.path.basename(file_node.fileTextureName.get())

            new_file_path = os.path.join(new_asset.asset_root_path, "03_lookdev", "publish", "materials", str(mtl),
                                         file_name)

            if os.path.isfile(new_file_path):
                file_node.fileTextureName.set(new_file_path)
                logger.debug("Re-pathed %s", file_name)

            # Add check if cc node already connected
            if not file_node.listConnections(et=1, t="colorCorrect"):
                try:
                    lookdev_utils.create_cc_node(source_node=file_node)
                except Exception:
                    pass

    # Export world node as master maya file
    pm.select(cl=1)

    pm.select(asset_world_node)

    cmds.file(new_asset.maya_file, typ="mayaAscii", pr=1, es=1)

    pm.select(cl=1)

    asset_data["maya_file"] = new_asset.maya_file

    lm.write_asset_data("Prop", new_asset.asset_name, asset_data)
