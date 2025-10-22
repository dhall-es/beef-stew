import unreal
import sys

from PySide6.QtCore import Qt, Slot, QMargins
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QHBoxLayout,
                               QLineEdit, QVBoxLayout, QScrollArea, QPushButton,
                               QFormLayout, QWidget, QFileDialog)

windowName = "jsonWindow"

class StaticMeshField(QWidget):
    def __init__(self, parent = None, label = ''):
        super().__init__(parent)

        self.pushButton = QPushButton(label)

        self.hLayout = QHBoxLayout(self)
        self.hLayout.setContentsMargins(QMargins())

        self.hLayout.addWidget(self.pushButton)

        self.setLayout(self.hLayout)

class UnrealWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.openAction = QAction(self, text = "Load scene JSON...",
                                  triggered = self.open)

        self.createMainLayout()

        self.fileMenu = self.menuBar().addMenu("File")
        self.fileMenu.addAction(self.openAction)

    def createMainLayout(self):
        self.scrollLayout = QFormLayout(formAlignment = Qt.AlignmentFlag.AlignLeft)
        self.scrollLayout.setContentsMargins(QMargins())

        self.scrollWidget = QWidget()
        self.scrollWidget.setLayout(self.scrollLayout)

        self.scrollArea = QScrollArea(self, widgetResizable = True)
        self.scrollArea.setWidget(self.scrollWidget)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins(QMargins(5, 0, 5, 5))

        self.mainLayout.addWidget(self.scrollArea)

        self.cWidget = QWidget(self)
        self.cWidget.setLayout(self.mainLayout)

        self.setCentralWidget(self.cWidget)

    @Slot()
    def open(self):
        directory = unreal.Paths.project_content_dir()
        fileName = QFileDialog.getOpenFileName(self,("Open JSON"), directory, ("JSON Files (*.json)"))
        if (not fileName):
            return
        
        unreal.log(fileName[0])

        for _ in range(self.scrollLayout.rowCount()):
            self.scrollLayout.removeRow(0)

        import json
        with open(fileName[0], "r") as f:
            self.data = json.load(f)
                
        for package in self.data['packages']:
            # spans both columns (QFormLayout.SpanningRole)
            self.scrollLayout.addRow(StaticMeshField(label = package["fileName"]))

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