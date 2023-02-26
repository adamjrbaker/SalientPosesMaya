import numpy as np

import maya.cmds as cmds
import maya.api.OpenMaya as om

import AltMaya as altmaya


class VisualizeDeformation:
    
    def __init__(self, mesh):

        map_x = {}
        map_y = {}
        map_z = {}
        for v in mesh.vertices:
            d = v.read_delta()
            map_x[v.index] = d[0]
            map_y[v.index] = d[1]
            map_z[v.index] = d[2]
        vec_x = np.array(map_x.values())
        vec_y = np.array(map_y.values())
        vec_z = np.array(map_z.values())

        scaling = 1.0
        inds = []
        colors = []
        for i in range(len(mesh.vertices)):
            r = ((map_x[i] / scaling) + scaling) * 0.5
            g = ((map_y[i] / scaling) + scaling) * 0.5
            b = ((map_z[i] / scaling) + scaling) * 0.5
            c = om.MColor([r,g,b])
            colors.append(c)
            inds.append(i)
            
        try:
            cmds.polyColorPerVertex(mesh.name, colorDisplayOption=True)
        except RuntimeError as e:
            altmaya.Report.error("Failed to turn on vertex coloring for %s, maya error is %s" % (mesh.name, str(e)))
        
        try:
            cmds.polyColorPerVertex(mesh.name, remove=True)
        except RuntimeError as e:
            altmaya.Report.error("Failed to remove existing vertex color on %s, maya error is %s" % (mesh.name, str(e)))

        try:
            mesh.m_mesh.setVertexColors(colors, inds)
        except RuntimeError as e:
            altmaya.Report.error("Failed to set vertex color on %s (you may need to collapse history), maya error is %s" % (mesh.name, str(e)))
