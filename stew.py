import unreal
import sys

from PySide6.QtCore import Qt, Slot, QMargins
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QHBoxLayout,
                               QGroupBox, QVBoxLayout, QScrollArea, QPushButton,
                               QFormLayout, QWidget, QFileDialog, QStyleFactory)

windowName = "jsonWindow"

class StaticMeshField(QWidget):
    def __init__(self, label = ''):
        super().__init__()

        self.pushButton = QPushButton(label)

        self.hLayout = QHBoxLayout(self)
        self.hLayout.setContentsMargins(QMargins())

        self.hLayout.addWidget(self.pushButton)

        self.setLayout(self.hLayout)

class StaticMeshList(QGroupBox):
    def __init__(self, title = "Static Meshes"):
        super().__init__(title)

        self.scrollLayout = QFormLayout(formAlignment = Qt.AlignmentFlag.AlignLeft)
        self.scrollLayout.setContentsMargins(QMargins(5, 5, 5, 5))

        self.scrollWidget = QWidget()
        self.scrollWidget.setLayout(self.scrollLayout)

        self.scrollArea = QScrollArea(self, widgetResizable = True)
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollArea.setStyleSheet("background-clip:content;")

        self.mainLayout = QHBoxLayout()
        self.mainLayout.setContentsMargins(QMargins())

        self.mainLayout.addWidget(self.scrollArea)

        self.setLayout(self.mainLayout)

    def loadPackages(self, packages):
        for _ in range(self.scrollLayout.rowCount()):
            self.scrollLayout.removeRow(0)
        
        for package in packages:
            # spans both columns (QFormLayout.SpanningRole)
            self.scrollLayout.addRow(StaticMeshField(label = package["fileName"]))

class ImportSettings(QGroupBox):
    def __init__(self, title = "Import Options"):
        super().__init__(title)

        self.importButton = QPushButton("Import Scene")
        
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins(QMargins(5, 5, 5, 5))
        self.mainLayout.addWidget(self.importButton)
        self.mainLayout.addStretch(1)

        self.setLayout(self.mainLayout)

class UnrealWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.openAction = QAction(self, text = "Load scene JSON...",
                                  triggered = self.open)

        self.createMainLayout()

        self.fileMenu = self.menuBar().addMenu("File")
        self.fileMenu.addAction(self.openAction)

    def createMainLayout(self):
        self.staticMeshList = StaticMeshList()
        self.importSettings = ImportSettings()
        
        self.hLayout = QHBoxLayout()
        self.hLayout.addWidget(self.staticMeshList)
        self.hLayout.addWidget(self.importSettings)

        self.cWidget = QWidget()
        self.cWidget.setLayout(self.hLayout)

        self.setCentralWidget(self.cWidget)

    @Slot()
    def open(self):
        directory = unreal.Paths.project_content_dir()
        fileName = QFileDialog.getOpenFileName(self,("Open JSON"), directory, ("JSON Files (*.json)"))
        if (not fileName or fileName[0] == ''):
            return

        import json
        with open(fileName[0], "r") as f:
            self.data = json.load(f)
                
        self.staticMeshList.loadPackages(self.data['packages'])

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