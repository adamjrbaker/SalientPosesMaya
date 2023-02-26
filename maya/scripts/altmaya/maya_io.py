import maya.cmds as cmds

class IO:

    @classmethod
    def import_obj(cls, fp):
        cmds.file(fp, i=True, type="OBJ", renameAll=True)
