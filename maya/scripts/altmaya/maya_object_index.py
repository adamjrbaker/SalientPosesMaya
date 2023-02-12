import maya


class ObjectIndex:
    
    @classmethod
    def get_path_from_name(cls, name):
        sel = maya.OpenMaya.MSelectionList()
        path = maya.OpenMaya.MDagPath()
        try:
            sel.add(name)
        except:
            raise ValueError("Name %s not exist" % name)
        sel.getDagPath(0, path)
        return path
