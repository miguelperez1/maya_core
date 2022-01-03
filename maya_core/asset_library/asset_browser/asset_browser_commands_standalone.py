import os
import sys
import json
import logging

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

from maya_core.maya_asset import MayaAsset
from maya_core.pipeline.lookdev.material_builder import MaterialBuilder as mb
from tools_core.asset_library import library_manager as lm
from maya_core.pipeline.modeling.normalize_scale import normalize_scale as ns
from maya_core.pipeline.lighting.vray_lighting import vray_lighting
from maya_core.pipeline.lookdev import lookdev_utils

logging.basicConfig()
logger = logging.getLogger(__name__)


def import_model_asset(asset_path):
    cmds.file(asset_path, i=1)


def import_hdr_asset(asset_path):
    vray_lighting.create_vray_light("VRayLightDomeShape", name=os.path.basename(asset_path), texture=asset_path)


def import_studiolights_asset(asset_path):
    vray_lighting.create_vray_light("VRayLightRectShape", name=os.path.basename(asset_path), texture=asset_path)


def import_cucoloris_asset(asset_path):
    vray_lighting.create_gobo(os.path.basename(asset_path), asset_path)


def import_material_asset(asset):
    asset_data = lm.get_asset_data("Material", asset)

    mb.build_material(asset_data["materials"][0])


def import_assign_material_asset(asset):
    selection = pm.ls(sl=1)

    asset_data = lm.get_asset_data("Material", asset)

    mtls = mb.build_material(asset_data["materials"][0])

    if not selection:
        return

    lookdev_utils.assign_material(mtls[1], selection)
