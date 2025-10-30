import unreal

class Menu():
    def __init__(self):
        self.toolMenus = unreal.ToolMenus.get()
        self.menuOwnerName = "JSONImportTool"
        self.subMenu = None

        self.toolMenuName = "LevelEditor.MainMenu.JSONImportTool"
        
    def create(self):
        mainMenu = self.toolMenus.find_menu("LevelEditor.MainMenu")
        self.subMenu = mainMenu.add_sub_menu(owner = self.menuOwnerName,
                                             section_name = "JSON",
                                             name = self.menuOwnerName,
                                             label = "JSON Importer",
                                             tool_tip = "Open the JSON Importer menu")
        self.subMenu = self.toolMenus.register_menu(self.toolMenuName, "", unreal.MultiBoxType.MENU, True)
        self.toolMenus.refresh_all_widgets()

        self.addMenuEntry()
    
    def addMenuEntry(self):
        command = ('import ImportWindow\n'
                   'ImportWindow.Launch()\n')
        
        menuEntry = unreal.ToolMenuEntryExtensions.init_menu_entry(
            owner = self.menuOwnerName,
            name = self.menuOwnerName,
            label = "Open Window",
            tool_tip = "Open the JSON Importer window",
            command_type = unreal.ToolMenuStringCommandType.PYTHON,
            custom_command_type = "",
            command_string = command
        )

        self.subMenu.add_menu_entry("JSON", menuEntry)
        self.toolMenus.refresh_all_widgets()