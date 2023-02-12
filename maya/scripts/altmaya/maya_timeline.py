import maya.cmds as cmds


class Timeline:
    
    @classmethod
    def get_current_frame(cls):
        return cmds.currentTime(query=True)
        
    @classmethod
    def set_current_frame(cls, time):
        return cmds.currentTime(time)
    
    @classmethod
    def get_start(cls):
        return cmds.playbackOptions(query=True, minTime=True)
    
    @classmethod
    def get_end(cls):
        return cmds.playbackOptions(query=True, maxTime=True)
        
    @classmethod
    def list_of_frames(cls):
        return list(range(int(cls.get_start()), int(cls.get_end()) + 1))
    
    @classmethod
    def set_start(cls, frame):
        cmds.playbackOptions(animationStartTime=frame)
        cmds.playbackOptions(minTime=frame)
    
    @classmethod
    def set_end(cls, frame):
        cmds.playbackOptions(animationEndTime=frame)
        cmds.playbackOptions(maxTime=frame)
