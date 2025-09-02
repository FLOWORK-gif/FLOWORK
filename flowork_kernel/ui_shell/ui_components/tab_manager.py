#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\ui_components\tab_manager.py
# JUMLAH BARIS : 166
#######################################################################

import uuid
from flowork_kernel.ui_shell.workflow_editor_tab import WorkflowEditorTab
from flowork_kernel.api_contract import BaseUIProvider
from flowork_kernel.api_client import ApiClient
import threading
from flowork_kernel.utils.performance_logger import log_performance # ADDED: Import our new tool
class TabManager:
    """
    Manages all tab-related operations in the main DraggableNotebook.
    [REFACTORED] Removed direct UI access from services. Cleans up state on tab close.
    [UPGRADE] Now supports lazy loading of tab content to improve startup performance.
    """
    def __init__(self, main_window, kernel, notebook_widget):
        self.main_window = main_window
        self.kernel = kernel
        self.notebook = notebook_widget
        self.loc = self.kernel.get_service("localization_manager")
        self.api_client = ApiClient(kernel=self.kernel)
        self.state_manager = self.kernel.get_service("state_manager")
        self.opened_tabs = {}
        self.custom_tab_count = 0
        self.MANAGED_TAB_CLASSES = {}
        self.SESSION_TAB_CLASSES = {"WorkflowEditorTab": WorkflowEditorTab}
        self.initialized_tabs = set()
        self._populate_managed_tabs()
        self.SESSION_TAB_CLASSES.update(self.MANAGED_TAB_CLASSES)
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_selected)
    def _on_tab_selected(self, event):
        """Callback to lazily load the content of a selected tab."""
        try:
            selected_tab_widget = self.notebook.nametowidget(self.notebook.select())
            tab_key = str(selected_tab_widget)
            if tab_key not in self.initialized_tabs:
                if hasattr(selected_tab_widget, '_initialize_content'):
                    self.kernel.write_to_log(f"Lazy loading content for tab: {selected_tab_widget.__class__.__name__}", "DEBUG")
                    selected_tab_widget._initialize_content()
                self.initialized_tabs.add(tab_key)
        except Exception as e:
            self.kernel.write_to_log(f"Could not lazy-load tab content: {e}", "DEBUG")
    @log_performance("Populating managed tabs from plugins") # ADDED
    def _populate_managed_tabs(self):
        self.kernel.write_to_log("TabManager: Discovering UI tabs from all plugins...", "DEBUG")
        module_manager = self.kernel.get_service("module_manager_service")
        if not module_manager:
            return
        for module_id, module_data in module_manager.loaded_modules.items():
            instance = module_data.get("instance")
            if instance and isinstance(instance, BaseUIProvider):
                provided_tabs = instance.get_ui_tabs()
                for tab_info in provided_tabs:
                    key = tab_info.get("key")
                    frame_class = tab_info.get("frame_class")
                    if key and frame_class:
                        self.MANAGED_TAB_CLASSES[key] = frame_class
                        self.kernel.write_to_log(f"  -> Discovered tab '{key}' from plugin '{module_id}'", "SUCCESS")
    @log_performance("Loading entire tab session") # ADDED
    def load_session_state(self):
        success, saved_tabs = self.api_client.get_tab_session()
        if not success:
            self.kernel.write_to_log(f"API Error loading tab session: {saved_tabs}. Starting with a default tab.", "ERROR")
            self.add_new_workflow_tab(is_default=True)
            return
        if not saved_tabs:
            self.add_new_workflow_tab(is_default=True)
            return
        for tab_id_str in list(self.notebook.tabs()):
            self.notebook.forget(tab_id_str)
        for tab_data in saved_tabs:
            class_name = tab_data.get("class_name")
            title = tab_data.get("title")
            tab_id = tab_data.get("tab_id")
            tab_key = tab_data.get("key")
            self.kernel.write_to_log(f"Loading tab '{title}' (Type: {class_name}, Key: {tab_key})", "DEBUG")
            TargetTabClass = self.SESSION_TAB_CLASSES.get(class_name)
            if tab_key and tab_key in self.MANAGED_TAB_CLASSES:
                self.open_managed_tab(tab_key, select_it=False)
            elif class_name == "WorkflowEditorTab":
                self._create_and_add_tab(WorkflowEditorTab, title, tab_id=tab_id, is_new_tab=False)
            elif not TargetTabClass:
                self.kernel.write_to_log(f"Skipping tab '{title}' because its class ('{class_name}') no longer exists or the providing plugin is disabled.", "WARN")
            else:
                 self._create_and_add_tab(TargetTabClass, title, tab_id=tab_id, tab_key=tab_key)
        if len(self.notebook.tabs()) == 0:
            self.add_new_workflow_tab(is_default=True)
        else:
            self.notebook.select(0)
            self._on_tab_selected(None)
    @log_performance("Adding a new workflow tab") # ADDED
    def add_new_workflow_tab(self, is_default=False):
        if is_default:
            title = f" {self.loc.get('workflow_editor_tab_title')} "
            return self._create_and_add_tab(WorkflowEditorTab, title, set_as_main=True, is_new_tab=False)
        else:
            self.custom_tab_count += 1
            title = f" {self.loc.get('untitled_tab_title', count=self.custom_tab_count)} "
            return self._create_and_add_tab(WorkflowEditorTab, title, is_new_tab=True)
    @log_performance("Opening a managed tab") # ADDED
    def open_managed_tab(self, tab_key, select_it=True):
        if tab_key in self.opened_tabs and self.opened_tabs[tab_key].winfo_exists():
            if select_it:
                self.notebook.select(self.opened_tabs[tab_key])
            return
        TabClass = self.MANAGED_TAB_CLASSES.get(tab_key)
        if TabClass:
            title = tab_key.replace('_', ' ').title()
            self._create_and_add_tab(TabClass, f" {title.strip()} ", tab_key=tab_key)
        else:
            self.kernel.write_to_log(f"No managed tab class found for key '{tab_key}'.", "ERROR")
    @log_performance("Creating and adding a generic tab") # ADDED
    def _create_and_add_tab(self, frame_class, title, tab_id=None, set_as_main=False, is_new_tab=False, tab_key=None):
        if issubclass(frame_class, WorkflowEditorTab):
            new_tab_frame = frame_class(self.notebook, self.kernel, tab_id=tab_id, is_new_tab=is_new_tab)
        else:
            new_tab_frame = frame_class(self.notebook, self.kernel)
        self.notebook.add(new_tab_frame, text=title)
        self.notebook.select(new_tab_frame)
        if tab_key:
            self.opened_tabs[tab_key] = new_tab_frame
        if set_as_main and isinstance(new_tab_frame, WorkflowEditorTab):
            self.main_window.workflow_editor_tab = new_tab_frame
        return new_tab_frame
    def close_tab(self, tab_id_str):
        widget = self.notebook.nametowidget(tab_id_str)
        tab_key = str(widget)
        if tab_key in self.initialized_tabs:
            self.initialized_tabs.remove(tab_key)
        if hasattr(widget, 'tab_id') and self.state_manager:
            self.state_manager.delete(f"tab_preset_map::{widget.tab_id}")
        key_to_del = None
        for key, instance in self.opened_tabs.items():
            if instance == widget:
                key_to_del = key
                break
        if key_to_del:
            del self.opened_tabs[key_to_del]
        if widget == self.main_window.workflow_editor_tab:
            self.main_window.workflow_editor_tab = None
        self.notebook.forget(tab_id_str)
        if len(self.notebook.tabs()) == 0:
            self.add_new_workflow_tab(is_default=True)
    def save_session_state(self):
        open_tabs_data = []
        for tab_id_str in self.notebook.tabs():
            widget = self.notebook.nametowidget(tab_id_str)
            tab_key = None
            for key, val in self.opened_tabs.items():
                if val == widget:
                    tab_key = key
                    break
            if not hasattr(widget, 'tab_id') or not widget.tab_id:
                widget.tab_id = str(uuid.uuid4())
            tab_data = {
                "title": self.notebook.tab(tab_id_str, "text").strip(),
                "class_name": widget.__class__.__name__,
                "tab_id": widget.tab_id,
                "key": tab_key
            }
            open_tabs_data.append(tab_data)
        return self.api_client.save_tab_session(open_tabs_data)
