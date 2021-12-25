import logging

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

logger = logging.getLogger(__name__)


def set_render_settings():
    cmds.setAttr("defaultRenderGlobals.currentRenderer", "vray", type="string")

    mel.eval("vrayCreateVRaySettingsNode();")

    vray_settings = pm.PyNode("vraySettings")

    vray_settings.aspectLock.set(0)
    vray_settings.width.set(1920)
    vray_settings.height.set(960)
    vray_settings.aspectRatio.set(1920 / 960)
    vray_settings.pixelAspect.set(1)
    vray_settings.rgbColorSpace.set(2)
    vray_settings.imageFormatStr.set("exr (multichannel)")
    vray_settings.fileNamePrefix.set("<Scene>.<Layer>")

    mel.eval("updateRendererUI")


def startup_maya():
    mel.eval("loadPlugin vrayformaya")
    mel.eval("loadPlugin lookdevKit")
    set_render_settings()

    cmds.currentUnit(linear='m')
    cmds.grid(default=True, spacing='1m', size='12m', divisions=12)

    logger.info("Maya startup completed")


def main():
    cmds.evalDeferred(startup_maya, lp=1)
