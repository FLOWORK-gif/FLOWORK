import uuid
from flowork_gui.views.workflow_editor_tab import WorkflowEditorTab
from flowork_gui.plugins.flowork_core_ui.settings_tab import SettingsTab
from flowork_gui.plugins.flowork_core_ui.template_manager_page import TemplateManagerPage
from flowork_gui.plugins.flowork_core_ui.generator_page import GeneratorPage
from flowork_gui.plugins.flowork_core_ui.trigger_manager_page import TriggerManagerPage
from flowork_gui.plugins.flowork_core_ui.marketplace_page import MarketplacePage
from flowork_gui.plugins.flowork_core_ui.ai_architect_page import AiArchitectPage
from flowork_gui.plugins.flowork_core_ui.core_editor_page import CoreEditorPage
from flowork_gui.plugins.flowork_core_ui.pricing_page import PricingPage
from flowork_gui.plugins.flowork_core_ui.ai_trainer_page import AITrainerPage
from flowork_gui.plugins.flowork_core_ui.model_converter_page import ModelConverterPage
from flowork_gui.plugins.flowork_core_ui.prompt_manager_page import PromptManagerPage
# ADDED: Import the missing DiagnosticsPage class. The path is relative to the flowork_gui root.
from scanners.diagnostics_page import DiagnosticsPage
import threading
from flowork_gui.utils.performance_logger import log_performance
class UITabManager:
    """
    Manages all tab-related operations on the GUI side.
    It fetches tab state from the API and renders the corresponding UI widgets.
    This is the client-side counterpart to the TabManagerService in the kernel.
    """
    def __init__(self, main_window, notebook_widget, api_client, loc_service):
        self.main_window = main_window
        self.notebook = notebook_widget
        self.api_client = api_client
        self.loc = loc_service
        self.opened_tabs = {} # Maps tab_key to widget instance
        self.custom_tab_count = 0
        self.initialized_tabs = set()
        self.SESSION_TAB_CLASSES = {
            "WorkflowEditorTab": WorkflowEditorTab,
            "SettingsTab": SettingsTab,
            "TemplateManagerPage": TemplateManagerPage,
            "GeneratorPage": GeneratorPage,
            "TriggerManagerPage": TriggerManagerPage,
            "MarketplacePage": MarketplacePage,
            "AiArchitectPage": AiArchitectPage,
            "CoreEditorPage": CoreEditorPage,
            "PricingPage": PricingPage,
            "AITrainerPage": AITrainerPage,
            "ModelConverterPage": ModelConverterPage,
            "PromptManagerPage": PromptManagerPage,
            # ADDED: Register the DiagnosticsPage so the manager knows how to build it from saved sessions.
            "DiagnosticsPage": DiagnosticsPage,
        }
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_selected)
        print("[INFO] UI Tab Manager initialized.") # English Log
    def _on_tab_selected(self, event):
        """Callback to lazily load the content of a selected tab."""
        try:
            if not self.notebook or not self.notebook.winfo_exists() or not self.notebook.tabs():
                return
            selected_tab_widget = self.notebook.nametowidget(self.notebook.select())
            tab_key = str(selected_tab_widget)
            if tab_key not in self.initialized_tabs:
                if hasattr(selected_tab_widget, '_initialize_content'):
                    print(f"Lazy loading content for tab: {selected_tab_widget.__class__.__name__}") # English Log
                    selected_tab_widget._initialize_content()
                self.initialized_tabs.add(tab_key)
        except Exception as e:
            print(f"Could not lazy-load tab content: {e}") # English Log
    @log_performance("Loading entire tab session via API")
    def load_session_state(self):
        success, saved_tabs = self.api_client.get_tab_session()
        if not success:
            print(f"API Error loading tab session: {saved_tabs}. Starting with a default tab.") # English Log
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
            print(f"Loading tab '{title}' (Type: {class_name}, Key: {tab_key})") # English Log
            TargetTabClass = self.SESSION_TAB_CLASSES.get(class_name)
            if not TargetTabClass:
                # COMMENT: Using print instead of logger here because logger might not be fully initialized.
                print(f"Skipping tab '{title}' because its class ('{class_name}') is not registered in the UI Tab Manager.", "WARN") # English Log
                continue
            self._create_and_add_tab(TargetTabClass, title, tab_id=tab_id, is_new_tab=False, tab_key=tab_key)
        if len(self.notebook.tabs()) == 0:
            self.add_new_workflow_tab(is_default=True)
        else:
            self.notebook.select(0)
            self._on_tab_selected(None)
    @log_performance("Adding a new workflow tab")
    def add_new_workflow_tab(self, is_default=False):
        if is_default:
            title = f" {self.loc.get('workflow_editor_tab_title', fallback='Dashboard')} "
            return self._create_and_add_tab(WorkflowEditorTab, title, set_as_main=True, is_new_tab=True)
        else:
            self.custom_tab_count += 1
            title = f" {self.loc.get('untitled_tab_title', fallback='Untitled {count}', count=self.custom_tab_count)} "
            return self._create_and_add_tab(WorkflowEditorTab, title, is_new_tab=True)
    @log_performance("Creating and adding a generic tab")
    def _create_and_add_tab(self, frame_class, title, tab_id=None, set_as_main=False, is_new_tab=False, tab_key=None):
        new_tab_frame = frame_class(self.notebook, self.api_client, self.loc, tab_id=tab_id, is_new_tab=is_new_tab)
        self.notebook.add(new_tab_frame, text=title)
        self.notebook.select(new_tab_frame)
        if tab_key:
            self.opened_tabs[tab_key] = new_tab_frame
        return new_tab_frame
    def close_tab(self, tab_id_str):
        widget = self.notebook.nametowidget(tab_id_str)
        tab_key = str(widget)
        if tab_key in self.initialized_tabs:
            self.initialized_tabs.remove(tab_key)
        key_to_del = None
        for key, instance in self.opened_tabs.items():
            if instance == widget:
                key_to_del = key
                break
        if key_to_del:
            del self.opened_tabs[key_to_del]
        self.notebook.forget(tab_id_str)
        if len(self.notebook.tabs()) == 0:
            self.add_new_workflow_tab(is_default=True)