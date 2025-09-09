#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\services\tab_manager_service\tab_manager_service.py
# JUMLAH BARIS : 59
#######################################################################

import uuid
from ..base_service import BaseService
from flowork_kernel.api_contract import BaseUIProvider
from flowork_kernel.api_client import ApiClient
import threading
from flowork_kernel.utils.performance_logger import log_performance
class TabManagerService(BaseService):
    """
    (REFACTORED V2) Now subscribes to an event to populate tabs, fixing a race condition.
    (REFACTORED V3) Moves tab discovery to the start() method to fix race condition.
    (FIXED V4) Now correctly gets UI providers from PluginManagerService instead of ModuleManagerService.
    (REFACTORED V5 - API DRIVEN) This service no longer creates UI widgets directly. It only manages
    the STATE of the tabs, which the GUI will fetch via API to render.
    """
    def __init__(self, kernel, service_id: str):
        super().__init__(kernel, service_id)
        self.api_client = ApiClient(kernel=self.kernel)
        self.state_manager = self.kernel.get_service("state_manager")
        self.opened_tabs = {}
        self.custom_tab_count = 0
        self.MANAGED_TAB_CLASSES = {}
        self.SESSION_TAB_CLASSES = {} # ADDED: Simplified for backend state management.
        self.initialized_tabs = set()
        self.kernel.write_to_log("Service 'TabManagerService' initialized.", "SUCCESS") # English Log
    def start(self):
        self.kernel.write_to_log("TabManagerService is starting, populating managed tabs immediately.", "INFO") # English Log
        self._populate_managed_tabs()
    def find_workflow_for_node(self, target_node_id: str):
        """
        Searches all WorkflowEditorTabs for a specific node ID.
        If a tab's content is not yet initialized, it will be loaded.
        Returns the workflow graph and the tab instance if found.
        """
        return None, None # ADDED: Return default value. This function is now conceptual for the backend.
    @log_performance("Populating managed tabs from plugins")
    def _populate_managed_tabs(self):
        self.kernel.write_to_log("TabManager: Discovering UI tabs from all plugins...", "DEBUG") # English Log
        plugin_manager = self.kernel.get_service("plugin_manager_service")
        if not plugin_manager:
            self.kernel.write_to_log("TabManager: PluginManagerService not found, cannot discover tabs.", "ERROR") # English Log
            return
        self.MANAGED_TAB_CLASSES.clear()
        for plugin_id, plugin_data in plugin_manager.loaded_plugins.items():
            instance = plugin_manager.get_instance(plugin_id)
            if instance and isinstance(instance, BaseUIProvider):
                provided_tabs = instance.get_ui_tabs()
                for tab_info in provided_tabs:
                    key = tab_info.get("key")
                    if key: #and frame_class:
                        self.MANAGED_TAB_CLASSES[key] = tab_info # Storing the whole info dict
                        self.kernel.write_to_log(f"  -> Discovered tab '{key}' from plugin '{plugin_id}'", "SUCCESS") # English Log
        self.kernel.write_to_log("TabManager's known class list has been updated.", "DEBUG") # English Log
