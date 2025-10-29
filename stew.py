import unreal
import sys

from PySide6.QtCore import Qt, Slot, QMargins
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QHBoxLayout,
                               QGroupBox, QVBoxLayout, QScrollArea, QPushButton,
                               QFormLayout, QWidget, QFileDialog)

windowName = "jsonWindow"

class StaticMeshListItem(QWidget):
    def __init__(self, index, meshList, label = ''):
        super().__init__()

        self.meshList = meshList
        self.index = index

        self.pushButton = QPushButton(label)
        self.pushButton.clicked.connect(self.setMeshToSelected)

        self.hLayout = QHBoxLayout(self)
        self.hLayout.setContentsMargins(QMargins())

        self.hLayout.addWidget(self.pushButton)

        self.setLayout(self.hLayout)

    @Slot()
    def setMesh(self, mesh):
        pathName = mesh.get_path_name()

        self.meshList.staticMeshes.insert(self.index, mesh)
        import re

        match = re.match(r'([^\.]+)\.', pathName)
        self.pushButton.setText(match.group(1))

    @Slot()
    def setMeshToSelected(self):
        assets = unreal.EditorUtilityLibrary.get_selected_assets_of_class(unreal.StaticMesh)
        if (not assets or len(assets) != 1):
            unreal.log("Must have only one StaticMesh asset selected.")
            return
        
        pathName = assets[0].get_path_name()
        print(pathName)

        self.meshList.staticMeshes.insert(self.index, assets[0])
        import re

        match = re.match(r'([^\.]+)\.', pathName)
        self.pushButton.setText(match.group(1))

class StaticMeshList(QGroupBox):
    def __init__(self, unrealWindow, title = "Static Meshes"):
        super().__init__(title)
        self.staticMeshes = []

        self.unrealWindow = unrealWindow

        self.scrollLayout = QFormLayout(formAlignment = Qt.AlignmentFlag.AlignLeft)
        self.scrollLayout.setContentsMargins(QMargins(5, 5, 5, 5))
        
        self.openButton = QPushButton("Load scene JSON")
        self.openButton.clicked.connect(self.unrealWindow.openJSON)
        self.scrollLayout.addRow(self.openButton)

        self.scrollWidget = QWidget()
        self.scrollWidget.setLayout(self.scrollLayout)

        self.scrollArea = QScrollArea(self, widgetResizable = True)
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollArea.setStyleSheet("background-clip:content;")

        self.mainLayout = QHBoxLayout()
        self.mainLayout.setContentsMargins(QMargins())

        self.mainLayout.addWidget(self.scrollArea)

        self.setLayout(self.mainLayout)

    def loadJSON(self, data):
        for _ in range(self.scrollLayout.rowCount()):
            self.scrollLayout.removeRow(0)

        eAS = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)

        for i, package in enumerate(data['packages']):
            listItem = StaticMeshListItem(i, self, label = "No mesh set")

            # spans both columns (QFormLayout.SpanningRole)
            self.scrollLayout.addRow(QLabel(f"\"{package['fileName']}\":"),
                                     listItem)

            import re
            relativePath = unreal.Paths.make_path_relative_to(package['path'], unreal.Paths.project_dir())
            path = f"{re.sub('Content/', '/Game/', relativePath)}.{package['fileName']}"

            print(eAS.does_asset_exist(path))

            if (eAS.does_asset_exist(path)):
                listItem.setMesh(eAS.load_asset(path))

class ImportSettings(QGroupBox):
    def __init__(self, unrealWindow, title = "Instancing Settings"):
        super().__init__(title)

        self.unrealWindow = unrealWindow
        self.importButton = QPushButton("Place Static Meshes")
        self.importButton.clicked.connect(self.unrealWindow.instanceScene)
        
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins(QMargins(5, 5, 5, 5))
        self.mainLayout.addWidget(self.importButton)
        self.mainLayout.addStretch(1)

        self.setLayout(self.mainLayout)

class UnrealWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.openAction = QAction(self, text = "Load scene JSON...",
                                  triggered = self.openJSON)

        self.createMainLayout()

        self.fileMenu = self.menuBar().addMenu("File")
        self.fileMenu.addAction(self.openAction)

        self.fileName = None
        self.data = None

    def createMainLayout(self):
        self.staticMeshList = StaticMeshList(self)
        self.importSettings = ImportSettings(self)
        
        self.hLayout = QHBoxLayout()
        self.hLayout.addWidget(self.staticMeshList)
        self.hLayout.addWidget(self.importSettings)

        self.cWidget = QWidget()
        self.cWidget.setLayout(self.hLayout)

        self.setCentralWidget(self.cWidget)

    @Slot()
    def openJSON(self):
        directory = unreal.Paths.project_content_dir()
        result = QFileDialog.getOpenFileName(self,("Open JSON"), directory, ("JSON Files (*.json)"))
        unreal.log(result)
        if (not result or result[0] == ''):
            return

        self.fileName = result[0]
        
        import json
        with open(self.fileName, "r") as f:
            self.data = json.load(f)
                
        self.staticMeshList.loadJSON(self.data)

    @Slot()
    def instanceScene(self):
        if (not self.data):
            return

        for i, package in enumerate(self.data['packages']):
            staticMesh = self.staticMeshList.staticMeshes[i]
            unreal.log_warning(f"Loading package {package['fileName']}. Static Mesh = {staticMesh.get_name()}")
            for t in package['transforms']:
                placeStaticMesh(staticMesh, t['name'], t['translate'], t['rotate'], t['scale'])


def placeStaticMesh(staticMesh, name, location = [0, 0, 0], rotation = [0, 0, 0], scale = [1, 1, 1]):
    eAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    # transform = unreal.Transform()
    # transform.translation = unreal.Vector(location[0], location[2], location[1])
    # unreal.Quat.set_from_euler(transform.rotation, unreal.Vector(rotation[0], rotation[2], rotation[1]))
    # transform.scale3d = unreal.Vector(scale[0], scale[2], scale[1])

    staticMeshActor = eAS.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector.ZERO)
    staticMeshActor.get_component_by_class(unreal.StaticMeshComponent).set_static_mesh(staticMesh)
    staticMeshActor.set_actor_label(name)

    staticMeshActor.set_actor_location(unreal.Vector(location[0], location[2], location[1]), False, True)
    staticMeshActor.set_actor_rotation(unreal.Rotator(rotation[0], rotation[2], -rotation[1]), True)
    staticMeshActor.set_actor_relative_scale3d(unreal.Vector(scale[0], scale[2], scale[1]))

    # eAS.set_actor_transform(staticMeshActor, transform)

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