import maya

from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance


def maya_main_window():
    # Return the Maya main window widget as a Python object
    main_window_ptr = maya.OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class StandardMayaWindow(QtWidgets.QDialog):

    def __init__(self, title, parent=None):
        super(StandardMayaWindow, self).__init__(
            maya_main_window() if parent is None else parent
        )
        self.setWindowTitle(title)
        
        # Remove `?` thing on windows
        if maya.cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
          
        # Note sure what this does
        if maya.cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)


class Ask:

    @classmethod
    def string(cls, parent, title, description, default_value):
        text, ok = QtWidgets.QInputDialog.getText(parent, title, description, text=default_value)
        if ok:
            return str(text)
        else:
            return ""
            
    @classmethod
    def decision(cls, parent, title, description):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setText(title)
        msgBox.setInformativeText(description)
        msgBox.setStandardButtons(QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
        # msgBox.setDefaultButton(QMessageBox.Save)
        ret = msgBox.exec_()
        if ret == QtWidgets.QMessageBox.No:
            return False
        elif ret == QtWidgets.QMessageBox.Yes:
            return True
        else:
            raise ValueError("Response `%s` not understood" % (str(ret)))
    
    @classmethod
    def choice(cls, parent, title, label, options):
        ret, okay = QtWidgets.QInputDialog.getItem(parent, title, label, options)
        if not okay:
            return None
        else:
            return ret
        
    @classmethod
    def choose_folder(cls, parent, title):
        dialog = QtWidgets.QFileDialog()
        folder = dialog.getExistingDirectory(parent, title)
        return folder
                
    @classmethod
    def choose_file_to_open(cls, parent, title, files_filter=""):
        dialog = QtWidgets.QFileDialog()
        filepath, selected_filter = dialog.getOpenFileName(parent, title, filter=files_filter)
        return filepath

    @classmethod
    def choose_file_to_open_csv(cls, parent, title):
        return cls.choose_file_to_open(parent, title, "CSV files (*.csv);; All Files (*.*)")
            
    @classmethod
    def choose_file_to_open_json(cls, parent, title):
        return cls.choose_file_to_open(parent, title, "JSON files (*.json);; All Files (*.*)")

    @classmethod
    def choose_file_to_save(cls, parent, title, files_filter=""):
        dialog = QtWidgets.QFileDialog()
        filepath, selected_filter = dialog.getSaveFileName(parent, title, filter=files_filter)
        return filepath

    @classmethod
    def choose_file_to_save_json(cls, parent, title):
        return cls.choose_file_to_save(parent, title, files_filter="JSON files (*.json);; All Files (*.*)")
        
    @classmethod
    def choose_file_to_save_xml(cls, parent, title):
        return cls.choose_file_to_save(parent, title, files_filter="XML files (*.xml);; All Files (*.*)")


class Info:

    @classmethod
    def show(self, title, message):
        box = QtWidgets.QMessageBox()
        box.setWindowTitle(title)
        box.setText(message)
        box.exec_()