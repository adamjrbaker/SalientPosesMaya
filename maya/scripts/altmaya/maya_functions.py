import maya

class Functions:

    @classmethod
    def delete(cls, obj):
        maya.cmds.delete(obj)
    
    @classmethod
    def duplicate(cls, obj, name=""):
        if name:
            ret = maya.cmds.duplicate(obj, name=name)
        else:
            ret = maya.cmds.duplicate(obj)
        return ret[0]
