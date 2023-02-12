import maya

class Plugins:
    
    loaded = []
    
    @classmethod
    def load(cls, name):
        maya.cmds.loadPlugin(name)
        cls.loaded.append(name)
        
    @classmethod
    def unload(cls, name):
        if name not in cls.loaded:
            raise ValueError("Cannot unload plugin (no plugin named `%s` is currently loaded)." % name)
        maya.cmds.unloadPlugin(name)
