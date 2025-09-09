#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_gui\views\ui_components\menubar_manager.py
# JUMLAH BARIS : 66
#######################################################################

from tkinter import Menu
import webbrowser
from utils.performance_logger import log_performance
class MenubarManager:
    """
    (MODIFIED) The menubar is now DYNAMIC and 100% API-DRIVEN.
    It fetches its entire structure from the server and builds the UI accordingly.
    It includes a simple command dispatcher to handle actions sent from the server.
    """
    def __init__(self, main_window, api_client, loc_service):
        self.main_window = main_window
        self.api_client = api_client
        self.loc = loc_service # The localization helper is passed in.
        self.menubar = Menu(self.main_window)
        self.main_window.config(menu=self.menubar)
        self.main_window.main_menus = {}
    def _command_dispatcher(self, command_obj):
        """
        ADDED: This is the core of the new API-driven command system.
        It interprets the command object from the server and calls the appropriate LOCAL UI function.
        """
        command_type = command_obj.get("type")
        command_value = command_obj.get("value")
        if command_type == "open_tab":
            print(f"ACTION: Open managed tab '{command_value}'") # English Log
        elif command_type == "open_url":
            webbrowser.open(command_value)
        elif command_type == "show_about_dialog":
            pass
        elif command_type == "exit_app":
            pass
        else:
            print(f"Warning: Unknown menu command type received from server: {command_type}") # English Log
    @log_performance("Building main menubar from API")
    def build_menu(self):
        self.menubar.delete(0, 'end' )
        self.main_window.main_menus.clear()
        success, menu_data = self.api_client.get_menubar()
        if not success:
            error_menu = Menu(self.menubar, tearoff=0)
            self.menubar.add_cascade(label="Error", menu=error_menu) # English Hardcode
            error_menu.add_command(label="Could not load menu from server") # English Hardcode
            return
        for menu_dict in menu_data:
            parent_label = menu_dict.get("label")
            menu_items = menu_dict.get("items", [])
            new_menu = Menu(self.menubar, tearoff=0)
            self.menubar.add_cascade(label=parent_label, menu=new_menu)
            self.main_window.main_menus[parent_label] = new_menu
            for item in menu_items:
                if item.get("type") == "separator":
                    new_menu.add_separator()
                else:
                    item_label = item.get("label")
                    command_obj = item.get("command")
                    new_menu.add_command(
                        label=item_label,
                        command=lambda cmd=command_obj: self._command_dispatcher(cmd)
                    )
