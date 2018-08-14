import math

from PySide2 import QtGui, QtCore, QtWidgets
from shiboken2 import wrapInstance
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin, MayaQWidgetDockableMixin
from maya import OpenMayaUI as omui 
import maya.cmds as cmds
import maya.mel as mel
from shiboken2 import wrapInstance

import salient_poses_utils as utils

def _reload():
    reload(utils)

UIBuilder = utils.UIBuilder
UIFonts = utils.UIFonts
UIHelper = utils.UIHelper
DrawingBuilder = utils.DrawingBuilder
MayaScene = utils.MayaScene


def getMayaMainWindow():
    mayaPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(mayaPtr), QtWidgets.QWidget)
    
_win = None
def show():
    global _win
    if _win == None:
        _win = SalientPosesDialog(parent=getMayaMainWindow())
    _win.show(dockable=True)

class SalientPosesDialog(MayaQWidgetDockableMixin, QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(SalientPosesDialog, self).__init__(parent)
        self.my_parent = parent
        self.algorithm = 1
        self.selection_cache = []
        self.selection_errors = []

        self.animation_before_reduction = {}
        self.start_frame_before_reduction = -1

        self.last_ghosted = []

        def init_ui(): 
            vbox = UIBuilder.vertical_box(parent=self)

            # Start frame box
            hbox = UIBuilder.horizontal_box(add_to=vbox)
            UIBuilder.label(hbox, "Start End")
            self.start_edit = UIBuilder.line_edit(hbox, str(MayaScene.get_animation_range()[0]), self.set_start_frame_via_text)
            UIBuilder.make_spacer_2(hbox)

            # End frame box
            hbox = UIBuilder.horizontal_box(add_to=vbox)
            UIBuilder.label(hbox, "End Frame")
            self.end_edit = UIBuilder.line_edit(hbox, str(MayaScene.get_animation_range()[1]), self.set_end_frame_via_text)
            UIBuilder.make_spacer_2(hbox)

            # Algorithm combox box
            hbox = UIBuilder.horizontal_box(add_to=vbox)
            UIBuilder.label(hbox, "Type")
            self.algorithm_combo = UIBuilder.make_combo(hbox, ["Salient Poses", "Lim Thalmann"], fn=self.set_algorithm_via_combo)

            # N keyframes text field
            hbox = UIBuilder.horizontal_box(add_to=vbox)
            UIBuilder.label(hbox, "N Keyframes")
            self.n_keyframes_edit = UIBuilder.line_edit(hbox, str(3), self.set_n_keyframes_via_text)

            # Error text field
            UIBuilder.label(hbox, "Error")
            self.error_edit = UIBuilder.line_edit(hbox, "%2.4f" % -1)
            self.error_edit.setEnabled(False)

            # N keyframes slider
            hbox = UIBuilder.horizontal_box(add_to=vbox)
            self.n_keyframes_slider = UIBuilder.slider(hbox, 3, self.get_number_of_frames_halved(), 1, 3, self.set_n_keyframes_via_slider)

            # Error drawing
            hbox = UIBuilder.horizontal_box(add_to=vbox)
            self.painter = DrawingBuilder.make(hbox, self, (400, 200))

            # Buttons
            hbox = UIBuilder.horizontal_box(add_to=vbox)
            UIBuilder.label(hbox, "Actions")
            UIBuilder.button(hbox, "Compute", fn=self.compute_selections_and_errors)
            UIBuilder.button(hbox, "Apply", fn=self.apply_reduction_and_fitting)
            UIBuilder.button(hbox, "Undo", fn=self.undo_reduction)

        init_ui()
        self.setWindowTitle('Salient Poses')
        self.resize(utils.WINDOW_WIDTH, utils.WINDOW_WIDTH)

    def compute_selections_and_errors(self):

        selected_at_start_of_this_function = MayaScene.get_selected()

        # Build error table
        curves = MayaScene.make_motion_curves(MayaScene.get_selected(), "error_table_curves", int(self.start_edit.text()), int(self.end_edit.text()))
        curves = MayaScene.get_items_in_list_matching_type(curves, "motionTrail")
        error_table_name = cmds.createNode("vuwAnalysisNode", name="error_table")
        cmds.setAttr("%s.start" % error_table_name, int(self.start_edit.text()))
        cmds.setAttr("%s.end" % error_table_name, int(self.end_edit.text()))
        cmds.setAttr("%s.mode" % error_table_name, 1) # 1 for Euclidean-bounding, 2 for forced-bounding
        MayaScene.connect_attribute_list(error_table_name, "curves", curves, "points")
        MayaScene.provoke_attribute(error_table_name, "errorTable")
        MayaScene.provoke_attribute(error_table_name, "indexTable")

        # Build selector
        selector_node_name = cmds.createNode("vuwSelectorNode", name="node_name")
        cmds.setAttr("%s.startOffset" % selector_node_name, 0) # no offset
        cmds.setAttr("%s.framesTotal" % selector_node_name, self.get_total_number_of_frames())
        cmds.setAttr("%s.start" % selector_node_name, int(self.start_edit.text()))
        cmds.setAttr("%s.end" % selector_node_name, int(self.end_edit.text()))
        cmds.setAttr("%s.nKeyframes" % selector_node_name, self.n_keyframes_slider.value())
        cmds.setAttr("%s.mode" % selector_node_name, self.algorithm)
        cmds.connectAttr("%s.errorTable" % error_table_name, "%s.errorTable" % selector_node_name)
        cmds.connectAttr("%s.indexTable" % error_table_name, "%s.indexTable" % selector_node_name)

        # Run Salient Poses, then cache selections and errors and update the interface
        self.selection_cache = cmds.getAttr("%s.selection" % selector_node_name)
        self.selection_errors = cmds.getAttr("%s.errors" % selector_node_name)

        # Delete
        for curve in curves:
            MayaScene.delete_connected_based_on_type(curve, "motionTrailShape")

        MayaScene.remove_connection_to_attribute(selector_node_name, "errorTable", "errorTable")
        MayaScene.remove_connection_to_attribute(selector_node_name, "indexTable", "indexTable")
        MayaScene.delete(curves + [error_table_name, selector_node_name]) 

        # Revert selection
        MayaScene.select(selected_at_start_of_this_function)
        self.update_visualization()

    def apply_reduction_and_fitting(self):
        self.animation_before_reduction = {}
        self.start_frame_before_reduction_frame_before_reduction = int(self.start_edit.text())
        for obj in MayaScene.get_selected():
            self.animation_before_reduction[obj] = MayaScene.cache_animation_for_object(obj, int(self.start_edit.text()), int(self.end_edit.text()), ["tx", "ty", "tz", "rx", "ry", "rz"])

        selection = self.get_selection_of_n_keyframes(self.n_keyframes_slider.value())
        cmds.vuwReduceCommand(start=selection[0], finish=selection[-1], selection=selection)

    def undo_reduction(self):
        for obj in self.animation_before_reduction.keys():
            MayaScene.restore_animation_for_object(obj, self.animation_before_reduction[obj], self.start_frame_before_reduction_frame_before_reduction)

    def get_selection_of_n_keyframes(self, n_keyframes):
        if self.selection_cache == []:
            raise ValueError("The selection cache is empty, please create a selection")
            
        n = int(self.end_edit.text()) - int(self.start_edit.text()) + 1
        return [self.selection_cache[n_keyframes * n + i] for i in range(n_keyframes)]

    def get_error(self, n_keyframes=-1, normalized=True):
        if self.selection_errors == []:
            raise ValueError("The selection cache is empty, please create a selection")

        n_k = n_keyframes if n_keyframes != -1 else self.n_keyframes_slider.value()
        value = self.selection_errors[n_k] / (self.selection_errors[3] if normalized else 1.0)
        return value

    # Required for update_visualization's callback 
    def get_n_keyframes(self):
        return self.n_keyframes_slider.value()

    # Required for update_visualization's callback 
    def get_keyframe_range(self):
        return 3, self.get_number_of_frames_halved()

    def get_total_number_of_frames(self):
        return int(self.end_edit.text()) - int(self.start_edit.text()) + 1

    # Returns half the number of the frames in range
    def get_number_of_frames_halved(self):
        return int(self.get_total_number_of_frames() * 0.5)

    def update_visualization(self):

        # Interface
        self.error_edit.setText("%2.4f" % self.get_error(self.n_keyframes_slider.value(), normalized=False))
        min_keyframes, max_keyframes = 3, self.get_number_of_frames_halved()
        xs = [float(n - min_keyframes) / float(max_keyframes - min_keyframes) for n in range(min_keyframes, max_keyframes + 1)]
        ys = [self.get_error(n) for n in range(min_keyframes, max_keyframes + 1)]
        points = list(zip(xs, ys))
        self.painter.reset_drawing_fns()
        self.painter.add_drawing_fn(DrawingBuilder.create_points_fn(points, DrawingBuilder.red(), size=3))
        self.painter.add_drawing_fn(DrawingBuilder.create_vertical_line_based_on_attribute_fn(self.get_n_keyframes, self.get_keyframe_range, DrawingBuilder.white()))
        self.painter.add_drawing_fn(DrawingBuilder.create_horizontal_line_based_on_attribute_fn(self.get_error, lambda: (0, 1), DrawingBuilder.white()))
        self.painter.activate()
        self.repaint()

        # Ghosting
        MayaScene.remove_ghosting_for_objects(self.last_ghosted)
        frames = [int(v) for v in self.get_selection_of_n_keyframes(self.n_keyframes_slider.value())]
        MayaScene.set_ghosting_for_objects(MayaScene.get_selected(), frames)
        self.last_ghosted = MayaScene.get_selected()

    def set_algorithm_via_combo(self, arg):
        if arg == 0:
            self.algorithm = 1
        elif arg == 1:
            self.algorithm = 2

    def set_algorithm_by_index(self, mode):
        self.algorithm = mode
        if self.algorithm == 1:
            self.algorithm_combo.setCurrentIndex(0)
        elif self.algorithm == 2:
            self.algorithm_combo.setCurrentIndex(1)
 
    def set_start_frame_via_text(self):
        value = (self.start_edit.text())
        self.start_slider.setValue(value)
        MayaScene.set_animation_section(value, self.end_slider.value())
        self.n_keyframes_slider.setRange(*self.get_keyframe_range())

    def set_start_via_slider(self, value):
        self.start_edit.setText(str(value))
        MayaScene.set_animation_section(value, self.end_slider.value())
        self.n_keyframes_slider.setRange(*self.get_keyframe_range())

    def set_end_frame_via_text(self):
        value = int(self.end_edit.text())
        self.end_slider.setValue(value)
        MayaScene.set_animation_section(self.start_slider.value(), value)
        self.n_keyframes_slider.setRange(*self.get_keyframe_range())

    def set_end_via_slider(self, value):
        self.end_edit.setText(str(value))
        MayaScene.set_animation_section(self.start_slider.value(), value)
        self.n_keyframes_slider.setRange(*self.get_keyframe_range())
        
    def set_n_keyframes_via_text(self):
        value = int(self.n_keyframes_edit.text())
        self.n_keyframes_slider.setValue(value)
        self.error_edit.setText("%2.4f" % self.get_error(self.n_keyframes_slider.value(), normalized=False))
        self.update_visualization()
        self.repaint()

    def set_n_keyframes_via_slider(self, value):
        self.n_keyframes_edit.setText(str(value))
        self.error_edit.setText("%2.4f" % self.get_error(self.n_keyframes_slider.value(), normalized=False))
        self.update_visualization()
        self.repaint()
