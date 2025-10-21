import unreal
import sys

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, 
                               QLineEdit, QSpinBox, QComboBox,
                               QFormLayout, QGroupBox, QFileDialog)

windowName = "jsonWindow"

# Subclass QMainWindow to customize your application's main window
class UnrealWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.openAction = QAction(self, text = "Load scene JSON...",
                                  triggered = self.open)

        self.fileMenu = self.menuBar().addMenu("File")
        self.fileMenu.addAction(self.openAction)

        self.formGroupBox = QGroupBox("File Names")

        self.formLayout = QFormLayout()
        # formLayout.addRow(QLabel("Line 1:"), QLineEdit())
        # formLayout.addRow(QLabel("Line 2, long text:"), QComboBox())
        # formLayout.addRow(QLabel("Line 3:"), QSpinBox())

        self.formGroupBox.setLayout(self.formLayout)

        self.setCentralWidget(self.formGroupBox)

    @Slot()
    def open(self):
        directory = unreal.Paths.project_content_dir()
        fileName = QFileDialog.getOpenFileName(self,("Open JSON"), directory, ("JSON Files (*.json)"))
        if (not fileName):
            return
        
        unreal.log(fileName[0])

        import json
        with open(fileName[0], "r") as f:
            self.data = json.load(f)
        
        # for package in self.data['packages']:
        #     self.formLayout.addRow(QLabel(package['fileName'], QLineEdit()))

def launchWindow():
    if QApplication.instance():
        # Id any current instances of tool and destroy
        for win in (QApplication.allWindows()):
            if (windowName in win.objectName()): # update this name to match name below
                win.destroy()
    else:
        QApplication(sys.argv)

    UnrealWindow.window = UnrealWindow()
    UnrealWindow.window.show()
    UnrealWindow.window.setWindowTitle("JSON Scene Importer")
    UnrealWindow.window.setObjectName(windowName)
    unreal.parent_external_window_to_slate(UnrealWindow.window.winId())

launchWindow()