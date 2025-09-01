#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\ui_components\menubar_manager.py
# JUMLAH BARIS : 116
#######################################################################

from tkinter import Menu
from flowork_kernel.api_contract import BaseUIProvider
from flowork_kernel.utils.performance_logger import log_performance
import webbrowser
class MenubarManager:
    """
    (MODIFIED) The menubar is now DYNAMIC.
    It shows 'Login / Register' or 'Logout' based on the user's auth state.
    """
    def __init__(self, main_window, kernel):
        self.main_window = main_window
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        self.menubar = Menu(self.main_window)
        self.main_window.config(menu=self.menubar)
    def _logout(self):
        """ Handles the user logout process. """
        self.kernel.write_to_log("User logging out.", "INFO")
        self.kernel.current_user = None
        self.kernel.license_tier = "free"
        self.kernel.is_premium = False
        state_manager = self.kernel.get_service("state_manager")
        if state_manager:
            state_manager.delete("user_session_token")
        event_bus = self.kernel.get_service("event_bus")
        if event_bus:
            event_bus.publish("USER_LOGGED_OUT", {})
        self.build_menu()
    @log_performance("Building main menubar")
    def build_menu(self):
        self.menubar.delete(0, 'end' )
        self.main_window.main_menus.clear()
        file_menu = Menu(self.menubar, tearoff=0)
        file_menu_label = self.loc.get('menu_file', fallback="File")
        self.menubar.add_cascade(label=file_menu_label, menu=file_menu)
        self.main_window.main_menus[file_menu_label] = file_menu
        if self.kernel.current_user:
            file_menu.add_command(label="Logout", command=self._logout)
        else:
            file_menu.add_command(label="Login / Register", command=self.main_window._open_authentication_dialog)
        file_menu.add_separator()
        file_menu.add_command(label=self.loc.get('menu_save_workflow', fallback="Save Workflow"), command=lambda: self.main_window._trigger_workflow_action('save_workflow' ))
        file_menu.add_command(label=self.loc.get('menu_load_workflow', fallback="Load Workflow"), command=lambda: self.main_window._trigger_workflow_action('load_workflow'))
        if self.kernel.is_monetization_active():
            file_menu.add_separator()
            file_menu.add_command(label=self.loc.get('menu_activate_license', fallback="Activate New License..."), command=self.main_window.handle_license_activation_request)
            file_menu.add_command(label=self.loc.get('menu_deactivate_license', fallback="Deactivate This Computer"), command=self.main_window.handle_license_deactivation_request)
        file_menu.add_separator()
        file_menu.add_command(label=self.loc.get('menu_exit', fallback="Exit"), command=self.main_window.lifecycle_handler.on_closing_app)
        ai_tools_menu = Menu(self.menubar, tearoff=0)
        ai_tools_menu_label = self.loc.get('menu_ai_tools', fallback="AI Tools")
        self.menubar.add_cascade(label=ai_tools_menu_label, menu=ai_tools_menu)
        self.main_window.main_menus[ai_tools_menu_label] = ai_tools_menu
        triggers_menu = Menu(self.menubar, tearoff=0)
        triggers_menu_label = self.loc.get('menu_triggers' , fallback="Triggers")
        self.menubar.add_cascade(label=triggers_menu_label, menu=triggers_menu)
        self.main_window.main_menus[triggers_menu_label] = triggers_menu
        triggers_menu.add_command(label=self.loc.get('menu_manage_triggers', fallback="Manage Triggers..."), command=lambda: self.main_window.tab_manager.open_managed_tab("trigger_manager"))
        themes_menu = Menu(self.menubar, tearoff=0)
        themes_menu_label = self.loc.get('menu_themes', fallback="Themes")
        self.menubar.add_cascade(label=themes_menu_label, menu=themes_menu)
        self.main_window.main_menus[themes_menu_label] = themes_menu
        themes_menu.add_command(label=self.loc.get("menu_manage_themes", fallback="Manage Themes..."), command=lambda: self.main_window.tab_manager.open_managed_tab("template_manager"))
        marketplace_menu = Menu(self.menubar, tearoff=0)
        marketplace_menu_label = self.loc.get('menu_marketplace', fallback="Marketplace")
        self.menubar.add_cascade(label=marketplace_menu_label, menu=marketplace_menu)
        self.main_window.main_menus[marketplace_menu_label] = marketplace_menu
        marketplace_menu.add_command(label=self.loc.get("menu_open_marketplace", fallback="Manage Components"), command=lambda: self.main_window._open_managed_tab("marketplace"))
        settings_menu= Menu(self.menubar, tearoff=0)
        settings_menu_label = self.loc.get('menu_settings', fallback="Settings")
        self.menubar.add_cascade(label=settings_menu_label, menu=settings_menu)
        self.main_window.main_menus[settings_menu_label] = settings_menu
        settings_menu.add_command(label=self.loc.get('menu_open_settings_tab', fallback="Open Settings"), command =lambda: self.main_window.tab_manager.open_managed_tab("settings"))
        help_menu= Menu(self.menubar, tearoff=0)
        help_menu_label = self.loc.get('menu_help', fallback="Help")
        self.menubar.add_cascade(label=help_menu_label, menu=help_menu)
        self.main_window.main_menus[help_menu_label] = help_menu
        help_menu.add_command(
            label="View Documentation",
            command=lambda: webbrowser.open("http://127.0.0.1:8000")
        )
        help_menu.add_separator()
        help_menu.add_command(label=self.loc.get('menu_about', fallback="About Flowork"), command=lambda: self.main_window._show_about_dialog())
        if not self.kernel.is_monetization_active():
            help_menu.add_separator()
            help_menu.add_command(
                label="❤️Support This Project (Donate)❤️",
                command=lambda: webbrowser.open("https://donate.flowork.art/")
            )
        module_manager = self.kernel.get_service("module_manager_service")
        if module_manager:
            for module_id, module_data in module_manager.loaded_modules.items():
                instance = module_data.get("instance")
                if instance and isinstance(instance, BaseUIProvider) and not module_data.get("is_paused"):
                    menu_items = instance.get_menu_items()
                    if menu_items:
                        for item in menu_items:
                            parent_label = item.get('parent')
                            label = item.get('label')
                            command = item.get('command')
                            if parent_label not in self.main_window.main_menus:
                                new_menu = Menu(self.menubar, tearoff=0)
                                self.menubar.add_cascade(label=parent_label, menu=new_menu)
                                self.main_window.main_menus[parent_label] = new_menu
                            target_menu = self.main_window.main_menus.get(parent_label)
                            if target_menu and label and command:
                                if item.get('add_separator'):
                                    target_menu.add_separator()
                                target_menu.add_command(label=label, command=command)
