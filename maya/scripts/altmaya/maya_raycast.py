#
# Helpful links:
# --------------
#    
#    https://gist.github.com/fredrikaverpil/731e5d43c35d6372e19864243c6e0231
#

import numpy as np

import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui

import AltMaya as altmaya
    

class Ray:
    
    def __init__(self, point, param, face, tri, bary_1, bary_2):
        self.point = np.array([
            point[0], point[1], point[2]
        ])
        self.face_index = face
    
    def hit_something(self):
        return self.face_index != -1
        
        
class RaycastTraceOnObject:
    
    def __init__(self, obj, release_callback):
        self.obj = obj
        self.release_callback = release_callback
        
        self.fn_set = altmaya.API.get_mesh_function_set_from_name(self.obj)
        self.tracker = altmaya.MouseTracker(
            "RaycastTraceOnObject_%s" % obj,
            press_callback=self.on_start,
            drag_callback=self.on_drag,
            release_callback=self.on_release
        )
        
        self.rays = []
    
    def turn_on(self):
        self.tracker.turn_on()
        
    def on_start(self, x, y, modifier):
        if modifier != "shift":
            self.rays = []
        
    def on_drag(self, x, y, modifier):
        p = om.MPoint()
        d = om.MVector()
        omui.M3dView().active3dView().viewToWorld(int(x), int(y), p, d)

        intersection = self.fn_set.closestIntersection(
            om.MFloatPoint(p),
            om.MFloatVector(d),
            om.MSpace.kWorld,
            99999,
            False # test both directions
        )

        point, param, face, tri, bary_1, bary_2 = intersection
        ray = Ray(point, param, face, tri, bary_1, bary_2)
        self.rays.append(ray)
        
    def on_release(self):
        inds = [ray.face_index for ray in self.rays if ray.hit_something()]
        inds = list(set(inds))
        altmaya.Selection.set(["%s.f[%d]" % (self.obj, ix) for ix in inds])
        self.release_callback(inds)
