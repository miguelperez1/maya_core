import subprocess

import maya.cmds as cmds
import pymel.core as pm


def send_to_painter(smooth=False):
    # Duplicate and smooth selection
    sel = pm.ls(sl=1)
    pm.select(cl=1)

    export_sel = sel

    if smooth:
        pm.select(cl=1)
        export_sel = []

        for n in sel:
            d = n.duplicate()
            pm.polySmooth(d, dv=2)
            export_sel.append(d)

    # Browse to obj
    obj_path = cmds.fileDialog2(fileFilter="*.obj")[0]

    if not obj_path.endswith(".obj"):
        obj_path += ".obj"

    pm.select(export_sel)

    cmds.file(obj_path, typ="OBJexport", op="groups=1; ptgroups=1; materials=1; smoothing=1; normals=1", es=1)

    if smooth:
        pm.delete(export_sel)

    # Browse to spp
    spp_path = cmds.fileDialog2(fileFilter="*.spp")[0]

    if not spp_path.endswith(".spp"):
        spp_path += ".spp"

    export_path = "/".join(spp_path.split("/")[:-1])

    # Create command
    cmd = [
        "Adobe Substance 3D Painter.exe",
        "--mesh", obj_path,
        "--export-path", export_path,
        spp_path
    ]

    subprocess.Popen(cmd)