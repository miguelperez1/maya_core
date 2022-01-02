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
