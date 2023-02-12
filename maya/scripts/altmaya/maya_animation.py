import maya

from maya_selection import Selection
from maya_reporting import Report


class Animation:

    @classmethod
    def clear_range(cls, attribute_index, start, end):
        maya.cmds.cutKey(attribute_index.key, time=(start, end))

    @classmethod
    def add_keyframe(cls, attribute_index, time, value, is_breakdown):
        maya.cmds.setKeyframe(attribute_index.key, time=time, value=value, breakdown=is_breakdown)
        
    @classmethod
    def add_keyframes(cls, attribute_index, times, values, are_breakdowns):
        for (time, value) in zip(times, values):
            cls.add_keyframe(attribute_index, time, value, are_breakdowns)
    
    @classmethod
    def list_frames_that_have_keyframes(cls, attribute_index):
        res = maya.cmds.keyframe(attribute_index, query=True)
        if res is None:
            return []
        else:
            return res
        
    @classmethod
    def is_attribute_animated(cls, attribute_index):
        return len(cls.list_frames_that_have_keyframes(attribute_index)) != 0
        
    @classmethod
    def list_keyable_attributes(cls, obj, get_long_names=True):
        result = maya.cmds.listAttr(obj, shortNames=(not get_long_names), keyable=True)
        if result is None:
            return []
        else:
            return result
            
    @classmethod
    def list_animated_attributes(cls, obj):
        return [attr for attr in cls.list_keyable_attributes(obj) if cls.is_attribute_animated(attr)]
    
    @classmethod
    def evaluate_at_frame(cls, attribute_index, frame):
        return maya.cmds.getAttr(str(attribute_index), t=frame)
        
    @classmethod
    def evaluate_for_timeline(cls, attribute_index):
        return [
            cls.evaluate_at_frame(attribute_index, frame)
            for frame in range(
                int(Timeline.get_start()),
                int(Timeline.get_end()) + 1
            )
        ]
    
    @classmethod
    def convert_to_free_splines(cls, attribute_index):
        maya.cmds.keyTangent(attribute_index.key, outTangentType="linear", inTangentType="linear")
        maya.cmds.keyTangent(attribute_index.key, lock=False)
        maya.cmds.keyTangent(attribute_index.key, weightedTangents=True)
        maya.cmds.keyTangent(attribute_index.key, weightLock=False)

    @classmethod
    def set_keyframe_ingoing_tangent(cls, attribute_index, frame, weight, angle):
        maya.cmds.keyTangent(
            attribute_index.key, time=(frame, frame),
            edit=True, absolute=True,
            outWeight=weight, outAngle=angle
        )

    @classmethod
    def set_keyframe_outgoing_tangent(cls, attribute_index, frame, weight, angle):
        maya.cmds.keyTangent(
            attribute_index.key, time=(frame, frame),
            edit=True, absolute=True,
            inWeight=weight, inAngle=angle
        )
    
    @classmethod
    def clear_ghosts(cls):
        maya.mel.eval("unGhostAll")
        
    @classmethod
    def ghost_keyframes(cls, keyframes):
        cls.clear_ghosts()
        for o in Selection.get():
            obj_for_ghosting = o
            obj_is_transform = maya.cmds.objectType(o) == 'transform'
            if obj_is_transform: # Change the object to the shape if this is a transform
                obj_for_ghosting = maya.cmds.listRelatives(o, shapes=True)[0]
            maya.cmds.setAttr("%s.ghosting" % obj_for_ghosting, 1)
            maya.cmds.setAttr("%s.ghostingControl" % obj_for_ghosting, 1)
            maya.cmds.setAttr("%s.ghostFrames" % obj_for_ghosting, keyframes, type="Int32Array")


class AnimationCurve:
    
    def __init__(self, attribute_index):
        self.attribute_index = attribute_index
        self.cached_start = None
        self.cached_end = None
        self.cached_times = None
        self.cached_values = None
        self.cached_out_weights = None
        self.cached_in_weights = None
        self.cached_out_angles = None
        self.cached_in_angles = None
        self.cached_out_types = None
        self.cached_in_types = None

    def cache(self, start, end):
        if not Animation.is_attribute_animated(self.attribute_index):
            Report.error(str(self.attribute_index) + " is not animated")
            return
        key = str(self.attribute_index)
        s = start
        e = end
        self.cached_start = s
        self.cached_end = e
        self.cached_times = maya.cmds.keyframe(key, query=True, time=(s, e)) or []
        self.cached_values = [maya.cmds.keyframe(key, eval=True, time=(t, t), query=True)[0] for t in self.cached_times]
        self.cached_out_weights = maya.cmds.keyTangent(key, query=True, time=(s, e), outWeight=True) or []
        self.cached_in_weights = maya.cmds.keyTangent(key, query=True, time=(s, e), inWeight=True) or []
        self.cached_out_angles = maya.cmds.keyTangent(key, query=True, time=(s, e), outAngle=True) or []
        self.cached_in_angles = maya.cmds.keyTangent(key, query=True, time=(s, e), inAngle=True) or []
        self.cached_out_types = maya.cmds.keyTangent(key, query=True, time=(s, e), outTangentType=True) or []
        self.cached_in_types = maya.cmds.keyTangent(key, query=True, time=(s, e), inTangentType=True) or []
    
    def revert(self):
        if self.cached_times is None:
            Report.error("The cache has not yet been set")
            return
            
        key = str(self.attribute_index)
        s = self.cached_start
        e = self.cached_end
        
        # Delete what is there now
        maya.cmds.cutKey(key, time=(s, e))
        
        # Rebuild key by key
        for (time, value, out_weight, in_weight, out_angle, in_angle, out_type, in_type) in zip(
            self.cached_times,
            self.cached_values,
            self.cached_out_weights,
            self.cached_in_weights,
            self.cached_out_angles,
            self.cached_in_angles,
            self.cached_out_types,
            self.cached_in_types
        ):
            t = time
            maya.cmds.setKeyframe(key, time=(t, t), value=value)
            maya.cmds.keyTangent(
                key, time=(t, t),
                edit=True, absolute=True,
                outWeight=out_weight, inWeight=in_weight,
                outAngle=out_angle, inAngle=in_angle,
                outTangentType=out_type, inTangentType=in_type
            )
