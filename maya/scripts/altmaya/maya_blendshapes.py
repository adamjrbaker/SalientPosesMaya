import maya.cmds as cmds


class Blendshapes:
    
    @classmethod
    def find_all_blendshapes(cls):
        return [
            b for b 
            in cmds.ls(type="blendShape")
        ]
        
    @classmethod
    def get_object_set_for_blendshape(cls, name):
        ret = [
            c for c in cmds.listConnections(name)
            if cmds.nodeType(c) == "objectSet"
        ]
        if len(ret) == 0:
            raise ValueError("Did not find any object set for %s" % name)
        elif len(ret) == 1:
            return ret[0]
        elif len(ret) > 2:
            raise ValueError("Found more than one object set for %s?" % name)
    
    @classmethod
    def find_all_blendshapes_connected_to(cls, name):
        ret = []
        relatives = cmds.listRelatives(name, allDescendents=True)
        all_bs = cls.find_all_blendshapes()
        for b in all_bs:
            b_objset = cls.get_object_set_for_blendshape(b)
            b_objset_connections = cmds.listConnections(b_objset)
            intersect = [ c for c in b_objset_connections if c in relatives ]
            if len(intersect) > 0: ret.append(b)
        return ret
        
    @classmethod
    def list_targets_connected_to_blendshape(cls, name):
        return cmds.listAttr("%s.w" % name, multi=True)
