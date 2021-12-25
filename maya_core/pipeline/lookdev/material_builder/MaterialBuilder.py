import os
import logging

logging.basicConfig()

import maya.cmds as cmds
import pymel.core as pm

from maya_core.pipeline.lookdev import lookdev_utils
from maya_core.pipeline.lookdev.vray_lookdev import vray_lookdev

TEX_TYPES = [
    'diffuse',
    'si',
    'specular',
    'gloss',
    'metal',
    'normal',
    'opacity',
    'displacement'
]

DEFAULT_CONNECTIONS = {
    'VRayMtl': {
        'diffuse': 'outColor.color',
        'specular': 'outColor.reflectionColor',
        'gloss': 'outColorR.reflectionGlossiness',
        'roughness': 'outColorR.reflectionGlossiness',
        'metal': 'outColorR.metalness',
        'opacity': 'outColor.opacityMap',
        'si': 'outColor.illumColor',
        'normal': 'outColor.bumpMap',
        'displacement': 'outColor.displacementShader',
    },
    'PxrSurface': {
        'diffuse': 'color',
        'specular': 'reflectionColor',
        'gloss': 'reflectionGlossiness',
        'normal': ''
    }
}

logger = logging.getLogger(__name__)
logger.setLevel(10)


class MaterialBuilder(object):
    def __init__(self, material_data):
        self.material_data = material_data
        self.material_type = material_data['material_shader']
        self.name = material_data['material_name']

    def build_material(self):
        build_method = getattr(self, "build_{}".format(self.material_type))

        return build_method()

    def build_VRayMtl(self):
        logger.debug("Creating VRayMtl, %s", self.name)
        shader = pm.PyNode(cmds.shadingNode('VRayMtl', name=self.name + "_mtl", asShader=True))
        shading_group = pm.PyNode(cmds.sets(name=str(shader).replace("_mtl", "") + "_sg", empty=True, renderable=True,
                                            noSurfaceShader=True))

        pm.connectAttr(shader.outColor, shading_group.surfaceShader)

        if 'textures' not in self.material_data.keys() or not self.material_data['textures'].keys():
            return shader, shading_group

        uv_node = pm.shadingNode("place2dTexture", asUtility=True)
        uv_node.rename(self.name + "_UV")

        displacement = None

        for tex_type, tex_path in self.material_data['textures'].items():
            use_ptex = tex_path.endswith(".tex")

            # create nodes
            connection = DEFAULT_CONNECTIONS['VRayMtl'][tex_type].split(".")

            if tex_type != "displacement":
                tex_nodes = lookdev_utils.create_texture(name=self.name + "_" + tex_type, path=tex_path, uv=False,
                                                         ptex=use_ptex)
                cc_node = tex_nodes['cc_node']

                pm.connectAttr(getattr(cc_node, connection[0]), getattr(shader, connection[1]))
            else:
                tex_nodes = lookdev_utils.create_texture(name=self.name + "_" + tex_type, path=tex_path, cc=False,
                                                         uv=False)

                displacement = vray_lookdev.create_displacement_node(name=self.name,
                                                                     disp_source=tex_nodes["texture_node"])

                pm.connectAttr(getattr(tex_nodes["texture_node"], connection[0]),
                               getattr(shading_group, connection[1]))

            if not use_ptex:
                pm.connectAttr(uv_node.outUV, tex_nodes['texture_node'].uvCoord)

            # Set default values
            if tex_type == "roughness":
                shader.useRoughness.set(1)

            if tex_type == "normal":
                shader.bumpMapType.set(1)

        return shader, shading_group, displacement

    def build_VRayMtl2Sided(self):
        shader = pm.PyNode(cmds.shadingNode('VRayMtl2Sided', name=self.name + "_2sided_mat", asShader=True))
        shading_group = pm.PyNode(
            cmds.sets(name=str(shader).replace("_mat", "") + "_2sided_sg", empty=True, renderable=True,
                      noSurfaceShader=True))

        pm.connectAttr(shader.outColor, shading_group.surfaceShader)

        vray_mtl = self.build_VRayMtl()

        pm.connectAttr(vray_mtl[0].outColor, shader.frontMaterial)
        pm.connectAttr(vray_mtl[0].outColor, shader.backMaterial)

        return shader, shading_group, vray_mtl

    def build_VRayBlendMtl(self):
        print("build_VRayBlendMtl")
        return None


def build_material(material_data):
    mb = MaterialBuilder(material_data)

    logger.info("Created %s", mb.name)

    return mb.build_material()
