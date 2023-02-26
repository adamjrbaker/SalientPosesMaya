import maya.cmds as cmds


class Types:
    
    @classmethod
    def is_mesh(cls, name):
        m_type = cmds.nodeType(name)
        shapes = cmds.listRelatives(name, shapes=True)
        if shapes is None:
            return False
        else:
            n = len(shapes)
            print(n)
            print(
                "WARNING - not sure if %s is a mesh, but it has at least %d mesh nodes" % (name, n)
            )
            return len(shapes) >= 1
