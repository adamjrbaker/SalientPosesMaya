import maya


class Report:
    
    @classmethod
    def message(cls, message):
        maya.OpenMaya.MGlobal.displayInfo(message)
        
    @classmethod
    def warning(cls, message):
        maya.OpenMaya.MGlobal.displayWarning(message)
    
    @classmethod
    def error(cls, message):
        maya.OpenMaya.MGlobal.displayError(message)
