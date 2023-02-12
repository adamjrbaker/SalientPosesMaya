import maya


class AttributeIndex:
    
    def __init__(self, node_name, attribute_name):
        self.obj = node_name
        self.attr = attribute_name
        self.key = "%s.%s" % (self.obj, self.attr)
        
    @classmethod
    def enumerate_selected(cls):
        attrs = []
        for o in maya.cmds.ls(selection=True):
            for a in maya.cmds.listAttr(o, keyable=True):
                attr = AttributeIndex(o, a)
                attrs.append(attr)
        return attrs
    
    @staticmethod
    def from_key(key):
        node_name, attr_name = key.split(".")
        return AttributeIndex(node_name, attr_name)
        
    def __str__(self):
        return self.key
        
    def read(self):
        return maya.cmds.getAttr(self.key)
        
    def read_at_time(self, time):
        return maya.cmds.getAttr(self.key, time=time)
        
    def set(self, value):
        return maya.cmds.setAttr(self.key, value)
        
    def set_at_time(self, time, value):
        maya.cmds.setKeyframe(self.key, time=time, value=value)
                
    def exists(self):
        if not maya.cmds.objExists(self.obj):
            return False
            
        short_names = maya.cmds.listAttr(self.obj, shortNames=True, keyable=True)
        long_names = maya.cmds.listAttr(self.obj, keyable=True)
        if self.attr not in short_names and self.attr not in long_names:
            return False
            
        return True
    
    def has_keyframes(self):
        ret = maya.cmds.keyframe(self.key, query=True)
        if ret is None:
            return False
        else:
            return len(ret) != 0
