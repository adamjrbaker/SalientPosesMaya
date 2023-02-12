#
# Helpful links:
# --------------
#    
#    https://help.autodesk.com/view/MAYAUL/2020/ENU/index.html?guid=__CommandsPython_draggerContext_html
# 

import maya
import maya.cmds as cmds
import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui

import AltMaya as altmaya


class Pointer:    
    
    Default="default"
    Hand="hand"
    Crosshair="crossHair"
    Dolly="dolly"
    Track="track"
    Tumble="tumble"
    
    
class MouseTracker:
    
    def __init__(self, name, press_callback=None, drag_callback=None, release_callback=None, finish_callback=None):
        self.name = name.replace(":", "__")
        self.press_callback = press_callback
        self.drag_callback = drag_callback
        self.release_callback = release_callback
        self.finish_callback = finish_callback
        
    def turn_on(self, pointer_type=Pointer.Crosshair):
                    
        def on_press():
            if self.press_callback is None:
                return
            x, y, _ = cmds.draggerContext(self.name, query=True, anchorPoint=True)
            modifier = cmds.draggerContext(self.name, query=True, modifier=True)
            self.press_callback(x, y, modifier)
            
        def on_drag():
            if self.drag_callback is None:
                return
            x, y, _ = cmds.draggerContext(self.name, query=True, dragPoint=True)
            modifier = cmds.draggerContext(self.name, query=True, modifier=True)
            self.drag_callback(x, y, modifier)
            
        def on_release():
            if self.release_callback is None:
                return
            self.release_callback()
            
        def on_finish():
            if self.finish_callback is None:
                return
            self.finish_callback()
            
        if cmds.draggerContext(self.name, exists=True):
            cmds.deleteUI(self.name)
        
        cmds.draggerContext(
            self.name,
            pressCommand=on_press,
            dragCommand=on_drag,
            releaseCommand=on_release,
            finalize=on_finish,
            name=self.name,
            cursor='crossHair'
        )
        cmds.setToolTo(self.name)
