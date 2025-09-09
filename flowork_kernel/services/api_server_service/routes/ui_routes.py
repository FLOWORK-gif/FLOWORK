#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\ui_routes.py
# JUMLAH BARIS : 75
#######################################################################

from fastapi import APIRouter, HTTPException, Request
from typing import List, Dict, Any
from flowork_kernel.api_contract import BaseUIProvider
router = APIRouter(
    tags=["UI"]
)
@router.get("/ui/menubar", response_model=List[Dict[str, Any]])
async def get_menubar_structure(request: Request):
    """
    Endpoint to build and return the entire menubar structure dynamically.
    It gathers static menu items and dynamic items from UI provider plugins.
    """
    kernel = request.app.service_instance.kernel
    loc = kernel.get_service("localization_manager")
    main_menus = []
    file_menu = {
        "label": loc.get('menu_file', fallback="File"),
        "items": []
    }
    file_menu["items"].append({"label": "Login / Register", "command": {"type": "open_auth_dialog"}})
    file_menu["items"].append({"label": "Logout", "command": {"type": "user_logout"}})
    file_menu["items"].append({"type": "separator"})
    file_menu["items"].append({"label": loc.get('menu_save_workflow', fallback="Save Workflow"), "command": {"type": "trigger_action", "value": "save_workflow"}})
    file_menu["items"].append({"label": loc.get('menu_load_workflow', fallback="Load Workflow"), "command": {"type": "trigger_action", "value": "load_workflow"}})
    if kernel.is_monetization_active():
        file_menu["items"].append({"type": "separator"})
        file_menu["items"].append({"label": loc.get('menu_activate_license', fallback="Activate New License..."), "command": {"type": "activate_license"}})
        file_menu["items"].append({"label": loc.get('menu_deactivate_license', fallback="Deactivate This Computer"), "command": {"type": "deactivate_license"}})
    file_menu["items"].append({"type": "separator"})
    file_menu["items"].append({"label": loc.get('menu_exit', fallback="Exit"), "command": {"type": "exit_app"}})
    main_menus.append(file_menu)
    plugin_menus = {} # Dictionary to hold menus from plugins
    plugin_manager = kernel.get_service("plugin_manager_service")
    if plugin_manager:
        for plugin_id, plugin_data in plugin_manager.loaded_plugins.items():
            instance = plugin_manager.get_instance(plugin_id)
            if instance and isinstance(instance, BaseUIProvider) and not plugin_data.get("is_paused"):
                menu_items = instance.get_menu_items()
                if menu_items:
                    for item in menu_items:
                        parent_label = item.get('parent')
                        if parent_label not in plugin_menus:
                            plugin_menus[parent_label] = {"label": parent_label, "items": []}
                        if item.get('add_separator'):
                            plugin_menus[parent_label]["items"].append({"type": "separator"})
                        command_obj = {"type": "execute_lambda", "value": item.get('command')}
                        if "open_managed_tab" in str(item.get('command')):
                            tab_key_match = re.search(r"open_managed_tab\('([^']+)'\)", str(item.get('command')))
                            if tab_key_match:
                                command_obj = {"type": "open_tab", "value": tab_key_match.group(1)}
                        plugin_menus[parent_label]["items"].append({
                            "label": item.get('label'),
                            "command": command_obj
                        })
    main_menus.extend(plugin_menus.values())
    help_menu = {
        "label": loc.get('menu_help', fallback="Help"),
        "items": [
            {"label": "View Documentation", "command": {"type": "open_url", "value": "http://127.0.0.1:8000"}},
            {"type": "separator"},
            {"label": loc.get('menu_about', fallback="About Flowork"), "command": {"type": "show_about_dialog"}}
        ]
    }
    if not kernel.is_monetization_active():
        help_menu["items"].append({"type": "separator"})
        help_menu["items"].append({"label": "❤️Support This Project (Donate)❤️", "command": {"type": "open_url", "value": "https://donate.flowork.art/"}})
    main_menus.append(help_menu)
    return main_menus
