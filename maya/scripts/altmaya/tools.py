from PySide2 import QtCore
from PySide2 import QtWidgets

from maya_gui import StandardMayaWindow
from maya_animation import Animation
from maya_selection import Selection       
from maya_attr_index import AttributeIndex


class AttributeSelector(StandardMayaWindow):
    
    VALUE_ROLE = QtCore.Qt.UserRole
    TICK_COLUMN_SIZE = 50
    ROW_SIZE = 50
    
    def __init__(self, title="Attribute Selector", preselected_attr_indices=[], parent=None):
        super(AttributeSelector, self).__init__(title, parent=parent)
        
        self.object_list = []
        self.attribute_list = []
        
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.update_table()
        self.check_cells_corresponding_to_attrs(preselected_attr_indices)
        
    def get_item_text(self, item): return item.text()
    def set_item_text(self, item, text): item.setText(text)    
    def get_item_value(self, item): return item.data(self.VALUE_ROLE)
    def set_item_value(self, item, value): item.setData(self.VALUE_ROLE, value)
        
    def insert_standard_item(self, row, column, text, value):
        item = QtWidgets.QTableWidgetItem()
        self.set_item_text(item, text)
        self.set_item_value(item, value)
        self.table_wdg.setItem(row, column, item)
        
    def insert_checking_item(self, row, column, checked, value):
        item = QtWidgets.QTableWidgetItem()
        if checked: item.setCheckState(QtCore.Qt.Checked)
        else: item.setCheckState(QtCore.Qt.Unchecked)
        self.table_wdg.setItem(row, column, item)
        self.set_item_value(item, value)
        
    def check_cells_corresponding_to_attrs(self, attr_indices):
        for ai in attr_indices:
            for r in range(self.table_wdg.rowCount()):
                obj_item = self.table_wdg.item(r, 0)
                if self.get_item_text(obj_item) == ai.obj:
                    c = self.attribute_list.index(ai.attr) + 1
                    if c >= 1:
                        attr_item = self.table_wdg.item(r, c)
                        attr_item.setCheckState(QtCore.Qt.Checked)
                    continue
        
    def update_table(self):
        currently_checked = self.read_values_as_indices()
        
        while self.table_wdg.rowCount() > 0: self.table_wdg.removeRow(0)
        
        self.object_list = Selection.get()
        self.attribute_list = []
        for o in self.object_list:
            for a in Animation.list_keyable_attributes(o):
                if a not in self.attribute_list:
                    self.attribute_list.append(a)
                    
        self.table_wdg.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.table_wdg.setColumnCount(len(self.attribute_list) + 1)
        self.table_wdg.setHorizontalHeaderLabels(["Object"] + self.attribute_list)
        self.table_wdg.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        for i in range(1, self.table_wdg.columnCount() + 1):
            self.table_wdg.setColumnWidth(i, self.TICK_COLUMN_SIZE)
            
        for o in self.object_list:
            r = self.table_wdg.rowCount()
            self.table_wdg.insertRow(r)
            self.insert_standard_item(r, 0, o, None)
            for c, a in enumerate(self.attribute_list):
                index = AttributeIndex(o, a)
                if index.exists():
                    self.insert_checking_item(r, c + 1, False, index)
        
        self.check_cells_corresponding_to_attrs(currently_checked)
        
        w = 100 + self.TICK_COLUMN_SIZE * len(self.attribute_list)
        h = 25 + self.ROW_SIZE * self.table_wdg.rowCount()
        self.resize(w, h)
        
    def create_widgets(self):
        self.table_wdg = QtWidgets.QTableWidget()
        self.table_wdg.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.update_button = QtWidgets.QPushButton("Update")
        self.close_button = QtWidgets.QPushButton("Close")
        
    def create_layout(self):
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(2)
        button_layout.addStretch()
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.close_button)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.table_wdg)
        main_layout.addLayout(button_layout)
        
    def create_connections(self):
        self.update_button.clicked.connect(self.update_table)
        self.close_button.clicked.connect(self.close)
        self.table_wdg.horizontalHeader().sectionClicked.connect(self.toggle_checkboxes_in_column)
        self.table_wdg.itemClicked.connect(self.toggle_item)
        
    def toggle_item(_, item):
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)        
        
    def toggle_checkboxes_in_column(self, column):
        c = column
        if c == 0:
            return # no action for column zero (name column)
            
        states = []
        for r in range(self.table_wdg.rowCount()):
            states.append(self.table_wdg.item(r, c).checkState())
            
        nTrue = states.count(QtCore.Qt.Checked)
        nFalse = states.count(QtCore.Qt.Unchecked)
        new_state = QtCore.Qt.Checked if nTrue <= nFalse else QtCore.Qt.Unchecked
            
        for r in range(self.table_wdg.rowCount()):
            self.table_wdg.item(r, c).setCheckState(new_state)
            
    def read_values_as_indices(self):
        indices = []
        for r in range(self.table_wdg.rowCount()):
            for c in range(1, self.table_wdg.columnCount()):
                checked = self.table_wdg.item(r, c).checkState() == QtCore.Qt.Checked
                if checked:
                    item = self.table_wdg.item(r, c)
                    index = self.get_item_value(item)
                    indices.append(index)
        return indices