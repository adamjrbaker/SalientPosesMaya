import maya.cmds as cmds
from PySide2 import QtGui, QtCore, QtWidgets
from shiboken2 import wrapInstance
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin, MayaQWidgetDockableMixin

import salient_poses_utils as utils
import math

from maya import OpenMayaUI as omui 
import maya.cmds as cmds

def _reload():
    reload(utils)

UIBuilder = utils.UIBuilder
UIFonts = utils.UIFonts
UIHelper = utils.UIHelper
DrawingBuilder = utils.DrawingBuilder
MayaScene = utils.MayaScene

_win = None
def show():
    global _win
    if _win == None:
        _win = SalientPosesDialog()
    _win.show(dockable=True, area='right', floating=False)

class AnalysesDialog(QtWidgets.QWidget):

    def __init__(self, parent):
        super(AnalysesDialog, self).__init__(parent)
        self.my_parent = parent

        def init_parameters():
            self.min_frame, self.max_frame = MayaScene.get_animation_range()

        def init_ui(): 
            vbox = UIBuilder.vertical_box(parent=self)

            hbox = UIBuilder.horizontal_box(add_to=vbox)
            UIBuilder.label(hbox, "Analysis") 
            self.new_analysis_button = UIBuilder.button(hbox, "New", fn=self.new_analysis_node)
            self.delete_analysis_button = UIBuilder.button(hbox, "Delete", fn=self.delete_analysis_node)
            UIBuilder.make_spacer_1(hbox)

            hbox = UIBuilder.horizontal_box(add_to=vbox)
            UIBuilder.label(hbox, "Minimum Frame")
            self.min_frame_edit = UIBuilder.line_edit(hbox, str(self.min_frame))
            UIBuilder.make_spacer_2(hbox)

            hbox = UIBuilder.horizontal_box(add_to=vbox)
            UIBuilder.label(hbox, "Maximum Frame")
            self.max_frame_edit = UIBuilder.line_edit(hbox, str(self.max_frame))
            UIBuilder.make_spacer_2(hbox)

            hbox = UIBuilder.horizontal_box(add_to=vbox)
            UIBuilder.label(hbox, "Analyses")
            self.analysis_list = UIBuilder.list(hbox, [], fn=self.set_active_analysis)

        init_parameters()
        init_ui()
        self.setEnabled(False)
        self.delete_analysis_button.setEnabled(False)

    def atleast_one_analysis_exists(self):
        return self.analysis_list.count() > 0

    def new_analysis_node(self):
        result = cmds.promptDialog(
                title='Set Name for Analysis',
                message='Enter Name:',
                button=['OK', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel')

        if result == 'OK':
            node_name = cmds.promptDialog(query=True, text=True)

            curves = MayaScene.make_motion_curves(MayaScene.get_selected(), node_name + "_curves", self.min_frame, self.max_frame)
            curves = MayaScene.get_items_in_list_matching_type(curves, "motionTrail")

            analysis_node_name = cmds.createNode("vuwAnalysisNode", name=node_name)
            cmds.setAttr("%s.start" % analysis_node_name, self.min_frame)
            cmds.setAttr("%s.end" % analysis_node_name, self.max_frame)
            UIHelper.add_item_to_list(analysis_node_name, analysis_node_name, self.analysis_list)
            self.delete_analysis_button.setEnabled(True)
            MayaScene.connect_attribute_list(analysis_node_name, "curves", curves, "points")
            MayaScene.provoke_attribute(analysis_node_name, "errorTable")

            self.set_active_analysis()
            self.update()

    def delete_analysis_node(self):
        analysis = UIHelper.pop_active_item_from_list(self.analysis_list)
        curves = MayaScene.get_connected_based_on_type(analysis, "motionTrail")
        for curve in curves:
            MayaScene.delete_connected_based_on_type(curve, "motionTrailShape")
        MayaScene.delete(curves + [analysis])

        if not self.atleast_one_analysis_exists():
            self.delete_analysis_button.setEnabled(False)
        self.update()

    def get_analysis(self):
        return UIHelper.read_active_item_from_list(self.analysis_list)

    def set_active_analysis(self):
        if not self.my_parent.selectors_dialog.atleast_one_selector_exists():
            return
        selector_node_name = self.my_parent.selectors_dialog.get_selector()
        MayaScene.replace_solo_connection(selector_node_name, "errorTable", self.get_analysis(), "errorTable")

    def update_based_on_current_selector(self):
        selector_node_name = self.my_parent.selectors_dialog.get_selector()
        connected_analysis = MayaScene.get_connected_based_on_type(selector_node_name, "vuwAnalysisNode")[0]
        analyses = UIHelper.read_items_from_list(self.analysis_list)

        for index, analysis_node in enumerate(analyses):
            if analysis_node == connected_analysis:
                UIHelper.set_active_index(self.analysis_list, index)
                return

        MayaScene.error("%s not found in analysis list (%s)" % (selector_node_name, analyses))
    
    def is_complete(self):
        return self.atleast_one_analysis_exists()

    def paintEvent(self, e):
        self.my_parent.update_state()

    def add_existing(self, analyses):
        for item in analyses:
            UIHelper.add_item_to_list(item, item, self.analysis_list)
            self.delete_analysis_button.setEnabled(True)
            self.setEnabled(True)

class SelectorsDialog(QtWidgets.QWidget):

    def __init__(self, parent):
        super(SelectorsDialog, self).__init__(parent)
        self.my_parent = parent
        
        def init_ui():
            start_frame, end_frame = MayaScene.get_animation_section()
            n_frames = end_frame - start_frame + 1

            vbox = UIBuilder.vertical_box(parent=self)

            UIBuilder.make_separator(vbox)

            hbox = UIBuilder.horizontal_box(add_to=vbox)
            UIBuilder.label(hbox, "Selection") 
            self.new_selector_button = UIBuilder.button(hbox, "New", fn=self.new_selector_node)
            self.delete_selector_button = UIBuilder.button(hbox, "Delete", fn=self.delete_selector_node)
            UIBuilder.make_spacer_1(hbox)

            hbox = UIBuilder.horizontal_box(add_to=vbox)
            UIBuilder.label(hbox, "Selectors")
            self.selectors_list = UIBuilder.list(hbox, [], fn=self.set_active_selector)

            hbox = UIBuilder.horizontal_box(add_to=vbox)
            UIBuilder.label(hbox, "Start Frame")
            self.start_frame_edit = UIBuilder.line_edit(hbox, str(start_frame), self.set_start_frame_via_text)
            self.start_frame_slider = UIBuilder.slider(hbox, parent.analyses_dialog.min_frame, parent.analyses_dialog.max_frame, 1, start_frame, self.set_start_frame_via_slider)
            self.start_frame_slider.sliderReleased.connect(self.provoke_selector)

            hbox = UIBuilder.horizontal_box(add_to=vbox)
            UIBuilder.label(hbox, "End Frame")
            self.end_frame_edit = UIBuilder.line_edit(hbox, str(end_frame),  self.set_end_frame_via_text)
            self.end_frame_slider = UIBuilder.slider(hbox, parent.analyses_dialog.min_frame, parent.analyses_dialog.max_frame, 1, end_frame, self.set_end_frame_via_slider)
            self.end_frame_slider.sliderReleased.connect(self.provoke_selector)

            # N Keyframes edit and slider
            hbox = UIBuilder.horizontal_box(add_to=vbox)
            UIBuilder.label(hbox, "N Keyframes")
            self.n_keyframes_edit = UIBuilder.line_edit(hbox, str(3), self.set_n_keyframes_via_text)
            UIBuilder.label(hbox, "Error")
            self.error_edit = UIBuilder.line_edit(hbox, "%2.4f" % -1)
            self.error_edit.setEnabled(False)

            hbox = UIBuilder.horizontal_box(add_to=vbox)
            self.n_keyframes_slider = UIBuilder.slider(hbox, 3, n_frames, 1, 3, self.set_n_keyframes_via_slider)

            # Error drawing
            hbox = UIBuilder.horizontal_box(add_to=vbox)
            self.painter = DrawingBuilder.make(hbox, self, (400, 200))

        init_ui()
        self.setEnabled(False)
        self.start_frame_slider.setEnabled(False)
        self.start_frame_edit.setEnabled(False)
        self.end_frame_slider.setEnabled(False)
        self.end_frame_edit.setEnabled(False)
        self.n_keyframes_slider.setEnabled(False)
        self.n_keyframes_edit.setEnabled(False)
        self.delete_selector_button.setEnabled(False)

    def atleast_one_selector_exists(self):
        return self.selectors_list.count() > 0 and UIHelper.current_item_not_none(self.selectors_list)

    def new_selector_node(self):
        result = cmds.promptDialog(
                title='Set Name for Selector',
                message='Enter Name:',
                button=['OK', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel')

        if result == 'OK':
            node_name = cmds.promptDialog(query=True, text=True)

            start_frame, end_frame = self.start_frame_slider.value(), self.end_frame_slider.value()
            n_frames = end_frame - start_frame + 1

            selector_node_name = cmds.createNode("vuwSelectorNode", name=node_name)
            cmds.setAttr("%s.startOffset" % selector_node_name, start_frame - self.my_parent.analyses_dialog.min_frame)
            cmds.setAttr("%s.framesTotal" % selector_node_name, self.my_parent.analyses_dialog.max_frame - self.my_parent.analyses_dialog.min_frame + 1)
            cmds.setAttr("%s.start" % selector_node_name, start_frame)
            cmds.setAttr("%s.end" % selector_node_name, end_frame)
            cmds.setAttr("%s.nKeyframes" % selector_node_name, self.n_keyframes_slider.value())
            cmds.connectAttr("%s.errorTable" % self.my_parent.analyses_dialog.get_analysis(), "%s.errorTable" % selector_node_name)

            UIHelper.add_item_to_list(selector_node_name, selector_node_name, self.selectors_list)
            self.delete_selector_button.setEnabled(True)

            self.start_frame_slider.setEnabled(True)
            self.start_frame_edit.setEnabled(True)
            self.end_frame_slider.setEnabled(True)
            self.end_frame_edit.setEnabled(True)
            self.n_keyframes_slider.setEnabled(True)
            self.n_keyframes_edit.setEnabled(True)
            self.repaint()
            self.update()

    def delete_selector_node(self):
        selector = UIHelper.pop_active_item_from_list(self.selectors_list)
        MayaScene.remove_connection_to_attribute(selector, "errorTable", "errorTable")

        MayaScene.delete([selector]) 
 
        if not self.atleast_one_selector_exists(): 
            self.painter.reset_drawing_fns()
            self.delete_selector_button.setEnabled(False) 

            self.start_frame_slider.setEnabled(False)
            self.start_frame_edit.setEnabled(False)
            self.end_frame_slider.setEnabled(False)
            self.end_frame_edit.setEnabled(False)
            self.n_keyframes_slider.setEnabled(False)
            self.n_keyframes_edit.setEnabled(False)
        else:
            self.set_active_selector()

        self.repaint()
        self.update()

    def get_selector(self):
        return UIHelper.read_active_item_from_list(self.selectors_list)

    def get_n_keyframes(self):
        return cmds.getAttr("%s.nKeyframes" % self.get_selector())

    def get_n_frames(self):
        start = cmds.getAttr("%s.start" % self.get_selector())
        end = cmds.getAttr("%s.end" % self.get_selector())
        return end - start + 1

    def get_keyframe_range(self):
        return 3, self.get_n_frames()

    def get_start_frame(self):
        return cmds.getAttr("%s.start" % self.get_selector())

    def get_end_frame(self):
        return cmds.getAttr("%s.end" % self.get_selector())

    def set_active_selector(self):
        if not self.atleast_one_selector_exists():
            return

        start = self.get_start_frame()
        end = self.get_end_frame()
        n_keyframes = self.get_n_keyframes()

        self.start_frame_slider.setValue(start)
        self.start_frame_edit.setText(str(start))
        self.end_frame_slider.setValue(end)
        self.end_frame_edit.setText(str(end))
        self.n_keyframes_slider.setValue(n_keyframes)
        self.n_keyframes_edit.setText(str(n_keyframes))
        self.my_parent.analyses_dialog.update_based_on_current_selector()
        self.provoke_selector()
        self.my_parent.visualize_dialog.update_visualization()

    def get_selection(self, n_keyframes=-1):
        n_k = n_keyframes if n_keyframes != -1 else self.get_n_keyframes()
        n = self.get_n_frames()
        return [self.selections[n_k * n + i] for i in range(n_k)]

    def get_error(self, i=-1, normalized=True):
        index = self.get_n_keyframes() if i == -1 else i
        value = self.errors[index] / (self.errors[3] if normalized else 1.0)
        return value

    def provoke_selector(self):
        if self.get_n_frames() < 3 or self.get_n_keyframes() > self.get_n_frames():
            MayaScene.error("Invalid section settings")
            self.painter.reset_drawing_fns()
            self.repaint()
            return

        self.selections = cmds.getAttr("%s.selection" % self.get_selector())
        self.errors = cmds.getAttr("%s.errors" % self.get_selector())
        self.error_edit.setText("%2.4f" % self.get_error(normalized=False))

        min_keyframes, max_keyframes = self.get_keyframe_range()
        xs = [float(n - min_keyframes) / float(max_keyframes - min_keyframes) for n in range(min_keyframes, max_keyframes + 1)]
        ys = [self.get_error(i=n) for n in range(min_keyframes, max_keyframes + 1)]
        points = list(zip(xs, ys))

        self.painter.reset_drawing_fns()
        self.painter.add_drawing_fn(DrawingBuilder.create_points_fn(points, DrawingBuilder.red(), size=3))
        self.painter.add_drawing_fn(DrawingBuilder.create_vertical_line_based_on_attribute_fn(self.get_n_keyframes, self.get_keyframe_range, DrawingBuilder.white()))
        self.painter.add_drawing_fn(DrawingBuilder.create_horizontal_line_based_on_attribute_fn(self.get_error, lambda: (0, 1), DrawingBuilder.white()))
        self.painter.activate()
        self.my_parent.visualize_dialog.update_visualization()
        self.repaint()

    def set_start_frame_via_text(self):
        value = self.start_frame_edit.text()
        cmds.setAttr("%s.startOffset" % self.get_selector(), int(value) - self.my_parent.analyses_dialog.min_frame)
        cmds.setAttr("%s.start" % self.get_selector(), int(value))
        self.start_frame_slider.setValue(int(value))
        MayaScene.set_animation_section(value, self.get_end_frame())
        self.n_keyframes_slider.setRange(*self.get_keyframe_range())
        self.provoke_selector()

    def set_start_frame_via_slider(self, value):
        cmds.setAttr("%s.startOffset" % self.get_selector(), value - self.my_parent.analyses_dialog.min_frame)
        cmds.setAttr("%s.start" % self.get_selector(), value)
        self.start_frame_edit.setText(str(value))
        MayaScene.set_animation_section(value, self.get_end_frame())
        self.n_keyframes_slider.setRange(*self.get_keyframe_range())

    def set_end_frame_via_text(self):
        value = self.end_frame_edit.text()
        cmds.setAttr("%s.end" % self.get_selector(), int(value))
        self.end_frame_slider.setValue(int(value))
        MayaScene.set_animation_section(self.get_start_frame(), value)
        self.n_keyframes_slider.setRange(*self.get_keyframe_range())
        self.provoke_selector()

    def set_end_frame_via_slider(self, value):
        cmds.setAttr("%s.end" % self.get_selector(), value)
        self.end_frame_edit.setText(str(value))
        MayaScene.set_animation_section(self.get_start_frame(), value)
        self.n_keyframes_slider.setRange(*self.get_keyframe_range())

    def set_n_keyframes_via_text(self):
        value = self.n_keyframes_edit.text()
        cmds.setAttr("%s.nKeyframes" % self.get_selector(), int(value))
        self.n_keyframes_slider.setValue(int(value))
        self.error_edit.setText("%2.4f" % self.get_error(normalized=False))
        self.my_parent.visualize_dialog.update_visualization()
        self.repaint()

    def set_n_keyframes_via_slider(self, value):
        cmds.setAttr("%s.nKeyframes" % self.get_selector(), value)
        self.n_keyframes_edit.setText(str(value))
        self.error_edit.setText("%2.4f" % self.get_error(normalized=False))
        self.my_parent.visualize_dialog.update_visualization()
        self.repaint()

    def is_complete(self):
        return self.atleast_one_selector_exists()

    def paintEvent(self, e):
        self.my_parent.update_state()

    def add_existing(self, selectors):
        for item in selectors:
            UIHelper.add_item_to_list(item, item, self.selectors_list)
            self.delete_selector_button.setEnabled(True)
            self.start_frame_slider.setEnabled(True)
            self.start_frame_edit.setEnabled(True)
            self.end_frame_slider.setEnabled(True)
            self.end_frame_edit.setEnabled(True)
            self.n_keyframes_slider.setEnabled(True)
            self.n_keyframes_edit.setEnabled(True)
        self.set_active_selector()

class VisualizeDialog(QtWidgets.QWidget):

    def __init__(self, parent):
        super(VisualizeDialog, self).__init__(parent)
        self.my_parent = parent
        
        def init_parameters():
            self.visualization_toggle = True
            self.objects = []

        def init_ui():
            vbox = UIBuilder.vertical_box(parent=self)

            UIBuilder.make_separator(vbox)

            hbox = UIBuilder.horizontal_box(add_to=vbox)
            UIBuilder.button(hbox, "Ghost", fn=self.set_character_list)
            UIBuilder.button(hbox, "Duplicate", fn=self.new_anim)
            UIBuilder.button(hbox, "Reduce", fn=self.reduce_and_fit)
            UIBuilder.make_spacer_1(hbox)

        init_parameters()
        init_ui()
        self.setEnabled(False)

    def set_character_list(self):
        self.remove_visualization()
        self.objects = MayaScene.get_selected()
        self.update_visualization()

    def toggle_visualization(self):
        if self.visualization_toggle:
            self.visualization_toggle = False
            self.remove_visualization()
        else:
            self.visualization_toggle = True
            self.update_visualization()

    def update_visualization(self):
        if not self.visualization_toggle or self.my_parent.selectors_dialog.get_n_frames() < 3:
            return
        for item in self.objects:
            frames = [int(v) for v in self.my_parent.selectors_dialog.get_selection()]
            MayaScene.set_ghosting(item, frames)

    def remove_visualization(self):
        for item in self.objects:
            MayaScene.remove_ghosting(item)

    def new_anim(self):
        dup = cmds.duplicate(returnRootsOnly=True, renameChildren=True, upstreamNodes=True)[0]
        s = self.my_parent.analyses_dialog.min_frame
        e = self.my_parent.analyses_dialog.max_frame
        MayaScene.bake_translation(dup, s, e)

    def reduce_and_fit(self):
        selection = self.my_parent.selectors_dialog.get_selection()
        cmds.vuwReduceCommand(start=selection[0], finish=selection[-1], selection=selection)

class SalientPosesDialog(MayaQWidgetDockableMixin, QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(SalientPosesDialog, self).__init__(parent=parent)
        
        def init_fn():
            vbox = UIBuilder.vertical_box(parent=self)

            self.analyses_dialog = AnalysesDialog(self)
            vbox.addWidget(self.analyses_dialog)
            self.selectors_dialog = SelectorsDialog(self)
            vbox.addWidget(self.selectors_dialog)
            self.visualize_dialog = VisualizeDialog(self)
            vbox.addWidget(self.visualize_dialog)

            self.setWindowTitle('Salient Poses')

        init_fn()

        self.analyses_dialog.add_existing(MayaScene.find_existing_by_type("vuwAnalysisNode"))
        self.selectors_dialog.add_existing(MayaScene.find_existing_by_type("vuwSelectorNode"))
        self.resize(utils.WINDOW_WIDTH, utils.WINDOW_WIDTH)

    def update_state(self):
        self.analyses_dialog.setEnabled(True)

        if self.analyses_dialog.is_complete():
            self.selectors_dialog.setEnabled(True)

            if self.selectors_dialog.is_complete():
                self.visualize_dialog.setEnabled(True)
            else:
                self.visualize_dialog.setEnabled(False)
        else:
            self.selectors_dialog.setEnabled(False)
            self.visualize_dialog.setEnabled(False)
