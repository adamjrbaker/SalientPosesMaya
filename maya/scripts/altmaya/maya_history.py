import maya


class History:
    
    @classmethod
    def start_undo_block(cls):
        maya.cmds.undoInfo(openChunk=True)
    
    @classmethod
    def finish_undo_block(cls):
        maya.cmds.undoInfo(closeChunk=True)
    
    @classmethod
    def undo(cls):
        maya.cmds.undo()
        