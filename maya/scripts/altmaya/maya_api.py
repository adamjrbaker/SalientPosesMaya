
import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui


import maya

class API:
    
    @classmethod
    def get_dag_path_from_name(cls, name):
        selection = om.MSelectionList()
        try:
            selection.add(name)
        except RuntimeError:
            raise RuntimeError("%s was not found in the scene" % name)
        dag_path = selection.getDagPath(0)
        return dag_path
    
    @classmethod
    def get_object_from_dag_path(cls, dag_path):
        return om.MObject(dag_path)
        
    @classmethod
    def get_object_from_name(cls, name):
        return cls.get_object_from_dag_path(
            cls.get_dag_path_from_name(name)
        )
        
    @classmethod
    def get_mesh_function_set_from_dag_path(cls, dag_path):
        return om.MFnMesh(dag_path)
        
    @classmethod
    def get_mesh_function_set_from_name(cls, name):
        return cls.get_mesh_function_set_from_dag_path(
            cls.get_dag_path_from_name(name)
        )
