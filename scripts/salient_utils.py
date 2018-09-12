from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import QPen, QBrush, QPainter

import maya.cmds as cmds

WINDOW_WIDTH = 400
WINDOW_QUARTER = WINDOW_WIDTH * 0.25
LABEL_WIDTH = WINDOW_QUARTER * 1


class Prompt:

    @staticmethod
    def get_file(message):
        paths = cmds.fileDialog2(fileMode=0, caption=message)
        if paths == None:
            cmds.error("Please select a valid filepath")
            return None
        elif len(paths) == 1:
            return paths[0]
        else:
            cmds.error("Please select a valid filepath")
            return None

    @staticmethod
    def get_folder(message):
        paths = cmds.fileDialog2(fileMode=2, caption=message)
        if paths == None:
            cmds.error("Please select a valid filepath")
        elif len(paths) == 1:
            return paths[0]
        else:
            cmds.error("Please select a valid filepath")
            return None
    
    @staticmethod
    def get_string(title, message):
        result = cmds.promptDialog(
                    title=title,
                    message=message,
                    button=['OK', 'Cancel'],
                    defaultButton='OK',
                    cancelButton='Cancel',
                    dismissString='Cancel')

        if result == 'OK':
            return cmds.promptDialog(query=True, text=True)
        else:
            return None

class UIFonts:
    header = QtGui.QFont("Arial", 10, QtGui.QFont.Bold)

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
