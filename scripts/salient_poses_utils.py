# --------------------------------------------------------------------------------------------------------------------#
# Include

# Library
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import QPen, QBrush, QPainter
# import numpy as np

# Maya API
import maya.cmds as cmds

# 
# --------------------------------------------------------------------------------------------------------------------#



# --------------------------------------------------------------------------------------------------------------------#
# Configuration

WINDOW_WIDTH = 400
WINDOW_QUARTER = WINDOW_WIDTH * 0.25
LABEL_WIDTH = WINDOW_QUARTER * 1

# 
# --------------------------------------------------------------------------------------------------------------------#


# --------------------------------------------------------------------------------------------------------------------#
# Execution

class UIFonts:
    header = QtGui.QFont("Arial", 10, QtGui.QFont.Bold);

class UIBuilder:

    @staticmethod
    def vertical_box(parent=None, add_to=None):
        vbox = QtWidgets.QVBoxLayout(parent)
        if add_to != None: add_to.addLayout(vbox)
        return vbox

    @staticmethod
    def horizontal_box(parent=None, add_to=None):
        hbox = QtWidgets.QHBoxLayout(parent)
        if add_to != None: add_to.addLayout(hbox)
        return hbox

    @staticmethod
    def make_separator(add_to):
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        add_to.addWidget(line)

    @staticmethod
    def make_spacer(add_to, size):
        spacer = QtWidgets.QSpacerItem(size[0], size[1])
        add_to.addItem(spacer)

    @staticmethod
    def make_spacer_1(add_to):
        UIBuilder.make_spacer(add_to, (WINDOW_QUARTER * 1, 10))

    @staticmethod
    def make_spacer_2(add_to):
        UIBuilder.make_spacer(add_to, (WINDOW_QUARTER * 2, 10))

    @staticmethod
    def make_spacer_3(add_to):
        UIBuilder.make_spacer(add_to, (WINDOW_QUARTER * 3, 10))

    @staticmethod
    def make_spacer_4(add_to):
        UIBuilder.make_spacer(add_to, (WINDOW_QUARTER * 4, 10))

    @staticmethod
    def label(add_to, text, size=-1, font=None):
        label = QtWidgets.QLabel(text)
        label.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        label.setMinimumWidth(LABEL_WIDTH if size == -1 else size)
        label.setMaximumWidth(LABEL_WIDTH if size == -1 else size)
        if font is not None: label.setFont(font)
        add_to.addWidget(label)
        return label

    @staticmethod
    def button(add_to, text, fn=None):
        button = QtWidgets.QPushButton(text)
        button.setMinimumWidth(WINDOW_QUARTER)
        button.setMaximumWidth(WINDOW_QUARTER)
        button.setText(text)
        if fn != None: button.pressed.connect(fn)
        add_to.addWidget(button)
        return button

    @staticmethod
    def check_box(add_to, fn=None, starts=False):
        check_box = QtWidgets.QCheckBox()
        if starts:
            check_box.setCheckState(QtCore.Qt.CheckState(True))
        else:
            check_box.setCheckState(QtCore.Qt.CheckState(False))

        if fn != None: check_box.stateChanged.connect(fn)
        add_to.addWidget(check_box)
        return check_box

    @staticmethod
    def line_edit(add_to, text, fn=None):
        line_edit = QtWidgets.QLineEdit()
        line_edit.setText(text)
        if fn != None: line_edit.returnPressed.connect(fn)
        add_to.addWidget(line_edit)
        return line_edit

    @staticmethod
    def slider(add_to, min_v, max_v, step_size, value, fn=None):
        slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        slider.setSingleStep(step_size)
        slider.setRange(min_v, max_v)
        slider.setValue(value)
        if fn != None: slider.valueChanged.connect(fn)
        add_to.addWidget(slider)
        return slider

    @staticmethod
    def make_combo(add_to, items, fn=None):
        combo = QtWidgets.QComboBox()
        for item in items: combo.addItem(item)
        if fn != None: combo.currentIndexChanged.connect(fn)
        add_to.addWidget(combo)
        return combo

    @staticmethod
    def list(add_to, items, fn=None):
        qlist = QtWidgets.QListWidget()
        for item in items: qlist.addItem(item)
        if fn != None: qlist.itemSelectionChanged.connect(fn)
        add_to.addWidget(qlist)    
        return qlist


class UIHelper:

    @staticmethod
    def set_active_index(list_object, index):
        return list_object.setCurrentRow(index)

    @staticmethod
    def current_item_not_none(list_object):
        return list_object.currentItem() is not None

    @staticmethod
    def read_active_item_from_list(list_object):
        return list_object.currentItem().data(32)

    @staticmethod
    def read_items_from_list(list_object):
        return [list_object.item(i).data(32) for i in range(list_object.count())]

    @staticmethod
    def pop_active_item_from_list(list_object):
        return list_object.takeItem(list_object.currentRow()).data(32)

    @staticmethod
    def add_item_to_list(name, item, list_object):
        list_item = QtWidgets.QListWidgetItem()
        list_item.setText(name)
        list_item.setData(32, item)
        list_object.addItem(list_item)
        list_object.setCurrentItem(list_item)

    @staticmethod
    def add_items_to_list(names, items, list_object):
        for (name, item) in zip(names, items):
            UIHelper.add_item_to_list(name, item, list_object)

    @staticmethod
    def clear_list(list_object):
        list_object.clear()

# 
# --------------------------------------------------------------------------------------------------------------------#



# --------------------------------------------------------------------------------------------------------------------#
# Execution

class DrawingBuilder:

    @staticmethod
    def makeRGBColor(r, g, b):
        return QtGui.QColor.fromRgb(r, g, b)

    @staticmethod
    def makeHSLColor(h, s, v):
        return QtGui.QColor.fromHsvF(h / 360.0, s / 100.0, v / 100.0)

    @staticmethod
    def red():
        return DrawingBuilder.makeHSLColor(6, 75, 70)
    
    @staticmethod
    def blue():
        return DrawingBuilder.makeHSLColor(182, 29, 81)
    
    @staticmethod
    def white():
        return DrawingBuilder.makeHSLColor(233, 4, 91)

    @staticmethod
    def create_background_color_fn(r, g, b):
        def fn(parent, painter):
            w, h = parent.rect().width(), parent.rect().height()
            brush = QBrush(QtGui.QColor.fromRgb(r, g, b))
            pen = QPen(QtGui.QColor.fromRgb(0, 0, 0, a=0))
            painter.setBrush(brush)
            painter.setPen(pen)
            painter.drawRect(0, 0, w, h)
        return fn

    @staticmethod
    def create_points_fn(points, color, size=1):
        def fn(parent, painter):
            w, h = parent.rect().width(), parent.rect().height()
            pen = QPen(color, size)
            painter.setPen(pen)
            for (a, b) in zip(points[:-1], points[1:]):
                painter.drawLine(a[0] * w, h - a[1] * h, b[0] * w, h - b[1] * h)
        return fn
    
    @staticmethod
    def create_horizontal_line_based_on_attribute_fn(get_attr_fn, get_attr_range_fn, color, size=1):

        def fn(parent, painter):
            w, h = parent.rect().width(), parent.rect().height()
            pen = QPen(color, size)
            pen.setStyle(QtCore.Qt.DashLine)
            painter.setPen(pen)    
            min_v, max_v = get_attr_range_fn()
            y = h * (1 - ((get_attr_fn() - min_v) / (max_v - min_v)))
            painter.drawLine(0, y, w, y)
        return fn

    @staticmethod
    def create_vertical_line_based_on_attribute_fn(get_attr_fn, get_attr_range_fn, color, size=1):
        def fn(parent, painter):
            w, h = parent.rect().width(), parent.rect().height()
            pen = QPen(color, size)
            pen.setStyle(QtCore.Qt.DashLine)
            painter.setPen(pen)
            min_v, max_v = get_attr_range_fn()
            x = w * (get_attr_fn() - min_v) / (max_v - min_v)
            painter.drawLine(x, 0, x, h)
        return fn

    @staticmethod
    def make(add_to, parent, size):

        class DrawingWidget(QtWidgets.QWidget):

            def __init__(self):
                super(DrawingWidget, self).__init__()
                self.setParent(parent)
                self.resize(size[0], size[1])
                self.enabledState = False
                self.enabled = True

                self.disabled_fn = DrawingBuilder.create_background_color_fn(50, 50, 50)
                self.drawing_fns = [DrawingBuilder.create_background_color_fn(30, 30, 30)]

                vbox = UIBuilder.vertical_box(parent=self)
                UIBuilder.make_spacer(vbox, size)

            def reset_drawing_fns(self):
                self.drawing_fns = [DrawingBuilder.create_background_color_fn(30, 30, 30)]
                self.enabledState = False

            def add_drawing_fn(self, fn):
                self.drawing_fns.append(fn)

            def activate(self):
                self.enabledState = True

            def paintEvent(self, e):
                painter = QPainter(self)
                if not self.enabledState:
                    self.disabled_fn(self, painter)
                else:
                    for fn in self.drawing_fns:
                        fn(self, painter)

        painter = DrawingWidget()
        add_to.addWidget(painter)
        return painter

# 
# --------------------------------------------------------------------------------------------------------------------#



# --------------------------------------------------------------------------------------------------------------------#
# Execution

class MayaScene:

    @staticmethod
    def error(message):
        cmds.error(message)

    @staticmethod
    def select(names):
        cmds.select(names, replace=True)

    @staticmethod
    def get_selected():
        return cmds.ls(selection=True)

    @staticmethod
    def make_motion_curves(objects, name, start, end):
        curves = cmds.snapshot(objects, name=name, motionTrail=True, increment=1, startTime=start, endTime=end)
        cmds.hide(curves)
        return curves

    @staticmethod
    def create_copy_of_animation_using_root_joint(root):
        return cmds.duplicate([root], renameChildren=True, upstreamNodes=True)

    @staticmethod
    def delete_nonkeyframes(objects, keyframes):
        pairs_of_keyframes = zip(keyframes[:-1], keyframes[1:])
        for (a, b) in pairs_of_keyframes:
            n_frames = b - a + 1
            if n_frames <= 2:
                continue
            else:
                cmds.cutKey(objects, clear=True, time=(a + 1, b - 1))

    @staticmethod
    def has_attribute(node_name, attr_name):
        return cmds.attributeQuery(attr_name, node=node_name, exists=True)

    @staticmethod
    def check_type(item, type_wanted):
        if not cmds.objectType(item) == type_wanted:
            cmds.error("%s is not of type %s" % (item, type_wanted))

    @staticmethod
    def get_items_in_list_matching_type(items, type_wanted):
        return [item for item in items if cmds.objectType(item) == type_wanted]

    @staticmethod
    def get_items_in_list_where_string_is_not_in_type(items, type_not_wanted):
        return [item for item in items if type_not_wanted not in cmds.objectType(item)]

    @staticmethod
    def delete(items):
        cmds.delete(items)

    @staticmethod
    def duplicateDeep(item):
        return cmds.duplicate(item, returnRootsOnly=True, renameChildren=True, upstreamNodes=True)[0]

    @staticmethod
    def get_connected_based_on_type(object, type_wanted):
        return cmds.listConnections(object, type=type_wanted)

    @staticmethod
    def get_connected_based_on_not_type(object, type_not_wanted):
        connected = cmds.listConnections(object)
        return MayaScene.get_items_in_list_where_string_is_not_in_type(connected, type_not_wanted)
        
    @staticmethod
    def get_children(node):
        cmds.listRelatives(node, children=True)

    @staticmethod
    def get_parent(node):
        cmds.listRelatives(node, parent=True)

    @staticmethod
    def delete_connected_based_on_type(object, type_wanted):
        MayaScene.delete(MayaScene.get_connected_based_on_type(object, type_wanted))

    @staticmethod
    def get_animation_range():
        return ( int(cmds.playbackOptions(query=True, animationStartTime=True))
               , int(cmds.playbackOptions(query=True, animationEndTime=True)) )

    @staticmethod
    def set_animation_range(start, end):
        return ( cmds.playbackOptions(animationStartTime=start)
               , cmds.playbackOptions(animationEndTime=end) )

    @staticmethod
    def get_animation_section():
        return ( int(cmds.playbackOptions(query=True, minTime=True))
               , int(cmds.playbackOptions(query=True, maxTime=True)) )

    @staticmethod
    def set_animation_section(start, end):
        return ( cmds.playbackOptions(minTime=start)
               , cmds.playbackOptions(maxTime=end) )

    @staticmethod
    def list_nodes_attached_to_attribute(node_name, attr_name):
        curves = cmds.listConnections("%s.%s" % (node_name, attr_name))
        return [] if curves is None else curves

    @staticmethod
    def find_existing_by_type(type_wanted):
        return cmds.ls(type=type_wanted)

    @staticmethod
    def set_ghosting(obj, frames):
        obj_for_ghosting = obj
        t = cmds.objectType(obj)
        if t == 'transform':
            obj_for_ghosting = cmds.listRelatives(obj, shapes=True)[0]
        cmds.setAttr("%s.ghosting" % obj_for_ghosting, 1)
        cmds.setAttr("%s.ghostingControl" % obj_for_ghosting, 1)
        cmds.setAttr("%s.ghostFrames" % obj_for_ghosting, frames, type="Int32Array")

    @staticmethod
    def set_ghosting_for_objects(objects, frames):
        for obj in objects: MayaScene.set_ghosting(obj, frames)

    @staticmethod
    def remove_ghosting(obj_for_ghosting):
        cmds.setAttr("%s.ghosting" % obj_for_ghosting, False)
        cmds.setAttr("%s.ghostingControl" % obj_for_ghosting, False)
        cmds.setAttr("%s.ghostFrames" % obj_for_ghosting, [], type="Int32Array")

    @staticmethod
    def remove_ghosting_for_objects(objects):
        for obj in objects: MayaScene.remove_ghosting(obj)

    @staticmethod
    def provoke_attribute(object_name, attribute_name):
        return cmds.getAttr("%s.%s" % (object_name, attribute_name))

    @staticmethod
    def connect_attribute_list(receiver, receiver_attr, items, item_attr):
        for (index, item) in enumerate(items):
            cmds.connectAttr("%s.%s" % (item, item_attr), "%s.%s[%d]" % (receiver, receiver_attr, index))

    @staticmethod
    def replace_solo_connection(object_name, attribute_name, other_object_name, other_attribute_name):
        current = cmds.listConnections("%s.%s" % (object_name, attribute_name))
        if len(current) != 1:
            cmds.error("Can only replace %s when %s has one node connected (to %s)" % (attribute_name, object_name, attribute_name))

        cmds.disconnectAttr("%s.%s" % (current[0], other_attribute_name), "%s.%s" % (object_name, attribute_name))
        cmds.connectAttr("%s.%s" % (other_object_name, other_attribute_name), "%s.%s" % (object_name, attribute_name))

    @staticmethod
    def remove_connection_to_attribute(object_name, attribute_name, other_attribute_name):
        current = cmds.listConnections("%s.%s" % (object_name, attribute_name))
        for c in current:
            cmds.disconnectAttr("%s.%s" % (c, other_attribute_name), "%s.%s" % (object_name, attribute_name))

    @staticmethod
    def get_anim_curves_for_object(object_name):
        return cmds.listConnections(object_name, type="animCurve")

    @staticmethod
    def get_keyframed_points_in_anim_curve(anim_curve, start, end):
        xs = cmds.keyframe(anim_curve, absolute=True, timeChange=True, query=True, time=(start, end))
        ys = cmds.keyframe(anim_curve, absolute=True, valueChange=True, query=True, time=(start, end))
        return list(zip(xs, ys))

    @staticmethod
    def free_tangents(anim_curve):
        cmds.keyTangent(anim_curve, lock=False)
        cmds.keyTangent(anim_curve, weightedTangents=True)
        cmds.keyTangent(anim_curve, weightLock=False)

    @staticmethod
    def keyframe_xy_at(anim_curve, time):
        x = cmds.keyframe(anim_curve, time=(time, time), query=True, timeChange=True)[0]
        y = cmds.keyframe(anim_curve, time=(time, time), query=True, valueChange=True)[0]
        return x, y

    @staticmethod
    def set_in_tangent(anim_curve, time, hx, hy):
        kx, ky = MayaScene.keyframe_xy_at(anim_curve, time)
        dx = kx - hx
        dy = ky - hy
        one_x_unit = 0.125 
        one_y_unit = 3.0 if "translate" in anim_curve else 3.0/180.0
        cmds.keyTangent(anim_curve, time=(time, time), absolute=True, ix=one_x_unit * dx, iy=one_y_unit * dy)

    @staticmethod
    def set_out_tangent(anim_curve, time, hx, hy):
        kx, ky = MayaScene.keyframe_xy_at(anim_curve, time)
        print(hx, hy, kx, ky)
        dx = hx - kx
        dy = hy - ky
        one_x_unit = 0.125 
        one_y_unit = 3.0 if "translate" in anim_curve else 3.0/180.0
        cmds.keyTangent(anim_curve, time=(time, time), absolute=True, ox=one_x_unit * dx, oy=one_y_unit * dy)

    @staticmethod
    def bake(obj, attr, start, end):
        cmds.bakeResults("%s.%s" % (obj, attr), t=(start, end), sampleBy=1)

    @staticmethod
    def bake_translation(obj, start, end):
        MayaScene.bake(obj, "translate", start, end)

    @staticmethod
    def set_key(object):
        cmds.setKeyframe("%s.translate" % object)
        cmds.setKeyframe("%s.rotate" % object)
    
    @staticmethod
    def get_translation(object):
        x, y, z = cmds.xform(object, q=True, worldSpace=True,  translation=True)
        return x, y, z

    @staticmethod
    def set_translation(object, x, y, z):
        cmds.xform(object, worldSpace=True,  translation=[x, y, z])
        
    @staticmethod
    def get_rotation(object):
        x, y, z = cmds.xform(object, q=True, worldSpace=True,  rotation=True)
        return x, y, z

    @staticmethod
    def set_rotation(object, x, y, z):
        cmds.xform(object, worldSpace=True,  rotation=[x, y, z])

    @staticmethod
    def cache_animation_for_object(obj, start_frame, end_frame, attributes):
        animation = {}
        for attr in attributes:
            animation[attr] = [cmds.getAttr("%s.%s" % (obj, attr), time=i) for i in range(start_frame, end_frame)]
        return animation

    @staticmethod
    def restore_animation_for_object(obj, animation, start_frame):
        for attr in animation.keys():
            for i, value in enumerate(animation[attr]):
                cmds.setKeyframe(obj, value=value, attribute=attr, time=i+start_frame)

# 
# --------------------------------------------------------------------------------------------------------------------#


