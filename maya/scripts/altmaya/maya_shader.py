import maya


class Shaders:
    
    @classmethod
    def apply(cls, name, objects):
        shader_group = maya.cmds.listConnections(
            name, destination=True, exactType=True, t='shadingEngine'
        )[0]
        maya.cmds.sets(objects, edit=True, forceElement=shader_group)
