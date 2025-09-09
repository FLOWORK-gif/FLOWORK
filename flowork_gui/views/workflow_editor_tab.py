#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_gui\views\workflow_editor_tab.py
# JUMLAH BARIS : 193
#######################################################################

import ttkbootstrap as ttk
from tkinter import filedialog, messagebox, simpledialog, TclError
import threading
import os
import shutil
import json
import uuid
import time
import random
from flowork_gui.views.dashboard_manager import DashboardManager # PENAMBAHAN: Correct absolute import.
from .ui_components.controllers.TabActionHandler import TabActionHandler
class WorkflowEditorTab(ttk.Frame):
    def __init__(self, parent_notebook, api_client, loc_service, tab_id=None, is_new_tab=False):
        super().__init__(parent_notebook)
        self.api_client = api_client
        self.loc = loc_service
        self.kernel = None # ADDED: Explicitly set kernel to None to catch any remaining direct calls.
        self.tab_id = tab_id or str(uuid.uuid4())
        self.is_new_tab = is_new_tab
        self._execution_state = "IDLE"
        self._drag_data_toplevel = {}
        self.active_suggestions = {}
        self.action_handler = TabActionHandler(self, self.api_client, self.loc)
        self.canvas_area_instance = None
        self.log_viewer_instance = None
        self.logic_toolbox_instance = None
        self.plugin_toolbox_instance = None
        self.widget_toolbox_instance = None
        self.cmd_widget_instance = None
        self.dashboard_manager = None
        self._content_initialized = False
        ttk.Label(self, text="Loading Dashboard...").pack(expand=True) # English Hardcode
    def _initialize_content(self):
        """Creates the actual widgets for the tab the first time it's viewed."""
        if self._content_initialized:
            return
        for widget in self.winfo_children():
            widget.destroy()
        class MockKernel:
            def __init__(self, api_client, loc):
                self.api_client = api_client
                self.loc = loc
                self.write_to_log = lambda msg, lvl="INFO": print(f"[{lvl}] {msg}") # Simple logger
                self.services = {} # Mock services dictionary
            def get_service(self, service_name):
                if service_name not in self.services:
                    class MockService:
                        def __init__(self, api_client):
                            self.api_client = api_client
                    self.services[service_name] = MockService(self.api_client)
                return self.services[service_name]
        mock_kernel = MockKernel(self.api_client, self.loc)
        self.dashboard_manager = DashboardManager(self, self, mock_kernel, self.tab_id, self.is_new_tab)
        self.create_widgets()
        self.apply_styles()
        self.after(50, self.refresh_content_and_states)
        self._subscribe_to_events()
        self._content_initialized = True
    def _subscribe_to_events(self):
        """
        Subscribes this tab to relevant events from the EventBus.
        """
        pass
    def _handle_suggestion_event(self, event_data):
        """
        Callback triggered when an AI Co-pilot suggestion is received.
        It now finds the node by its unique ID (UUID) instead of its name.
        """
        preset_name = event_data.get("preset_name")
        if not self.canvas_area_instance or not hasattr(self.canvas_area_instance, 'preset_combobox'):
            return
        current_preset_on_canvas = self.canvas_area_instance.preset_combobox.get()
        if preset_name != current_preset_on_canvas:
            return
        target_node_id = event_data.get("node_id")
        if not target_node_id or target_node_id not in self.canvas_area_instance.canvas_manager.canvas_nodes:
            return
        suggestion = event_data.get("suggestion_text")
        self.active_suggestions[target_node_id] = suggestion
        self.run_on_ui_thread(self._refresh_suggestion_indicators)
    def _refresh_suggestion_indicators(self):
        """Clears and redraws all suggestion indicators based on the current state."""
        if not self.canvas_area_instance or not self.canvas_area_instance.canvas_manager:
            return
        visual_manager = self.canvas_area_instance.canvas_manager.visual_manager
        visual_manager.clear_all_suggestion_indicators()
        for node_id, suggestion_text in self.active_suggestions.items():
            visual_manager.show_suggestion_indicator(node_id, suggestion_text)
    def _clear_all_suggestions(self):
        """
        Clears all active suggestions and their visual indicators from the canvas.
        """
        self.active_suggestions.clear()
        if self.canvas_area_instance and self.canvas_area_instance.canvas_manager:
            self.run_on_ui_thread(self._refresh_suggestion_indicators)
    def destroy(self):
        super().destroy()
    def run_workflow_from_preset(self, nodes, connections, initial_payload):
        self._clear_all_suggestions()
        self.action_handler.run_workflow_from_preset(nodes, connections, initial_payload)
    def refresh_content_and_states(self):
        self.populate_module_toolbox()
        self.populate_plugin_panel()
        self.populate_preset_dropdown()
        if hasattr(self, 'widget_toolbox_instance') and self.widget_toolbox_instance and hasattr(self.widget_toolbox_instance, 'populate_widget_toolbox'):
            self.widget_toolbox_instance.populate_widget_toolbox()
        self._update_button_states()
    def create_widgets(self):
        dashboard_area = ttk.Frame(self) # Removed style='TFrame' to use default
        dashboard_area.pack(expand=True, fill='both')
        add_widget_button = ttk.Button(dashboard_area, text="+", style="success.Outline.TButton", width=3, command=self.show_add_widget_menu)
        add_widget_button.place(relx=1.0, rely=0.0, x=-5, y=5, anchor="ne")
    def save_dashboard_layout(self):
        if self.dashboard_manager:
            self.dashboard_manager.save_layout()
    def clear_dashboard_widgets(self):
        if self.dashboard_manager:
            self.dashboard_manager.clear_all_widgets()
    def apply_styles(self, colors=None):
        pass
    def show_add_widget_menu(self):
        if not self.dashboard_manager: return
        menu = self.dashboard_manager._create_add_widget_menu(event_x=self.winfo_width() - 150, event_y=40)
        try:
            menu.tk_popup(self.winfo_rootx() + self.winfo_width() - 10, self.winfo_rooty() + 40)
        finally:
            menu.grab_release()
    def populate_module_toolbox(self):
        logic_toolbox = getattr(self, 'logic_toolbox_instance', None)
        if logic_toolbox and hasattr(logic_toolbox, 'populate_module_toolbox'):
            logic_toolbox.populate_module_toolbox()
    def populate_plugin_panel(self):
        plugin_toolbox = getattr(self, 'plugin_toolbox_instance', None)
        if plugin_toolbox and hasattr(plugin_toolbox, 'populate_plugin_panel'):
            plugin_toolbox.populate_plugin_panel()
    def populate_preset_dropdown(self):
        if self.canvas_area_instance and hasattr(self.canvas_area_instance, 'populate_preset_dropdown'):
            self.canvas_area_instance.populate_preset_dropdown()
    def on_drag_start(self, event):
        tree_widget = event.widget
        item_id = tree_widget.identify_row(event.y)
        if not item_id or tree_widget.tag_has('category', item_id): return
        self._drag_data_toplevel = {"item_id": item_id, "widget": None, "tree_widget": tree_widget}
    def on_drag_motion(self, event):
        if not hasattr(self, '_drag_data_toplevel') or not self._drag_data_toplevel.get("item_id"): return
        if not self._drag_data_toplevel.get("widget"):
            item_text = self._drag_data_toplevel["tree_widget"].item(self._drag_data_toplevel["item_id"], "text").strip()
            self._drag_data_toplevel["widget"] = ttk.Label(self.winfo_toplevel(), text=item_text, style="Module.TLabel", relief="solid", borderwidth=1)
        self._drag_data_toplevel["widget"].place(x=event.x_root - self.winfo_toplevel().winfo_rootx(), y=event.y_root - self.winfo_toplevel().winfo_rooty())
    def on_drag_release(self, event):
        if hasattr(self, '_drag_data_toplevel') and self._drag_data_toplevel.get("widget"):
            self._drag_data_toplevel["widget"].destroy()
        if self.canvas_area_instance and hasattr(self.canvas_area_instance, 'canvas_manager') and self.canvas_area_instance.canvas_manager and hasattr(self, '_drag_data_toplevel') and self._drag_data_toplevel.get("item_id"):
            self.canvas_area_instance.canvas_manager.interaction_manager.on_drag_release(event, self._drag_data_toplevel["item_id"], self._drag_data_toplevel["tree_widget"])
        self._drag_data_toplevel = {}
    def run_on_ui_thread(self, func, *args):
        if self.winfo_exists():
            self.after(0, func, *args)
    def _set_execution_state_from_thread(self, new_state):
        self._execution_state = new_state
        self._update_button_states()
    def _update_button_states(self):
        if not self._content_initialized or not self.canvas_area_instance or not hasattr(self.canvas_area_instance, 'run_button'): return
        is_idle = self._execution_state == "IDLE"
        preset_state = "readonly" if is_idle else "disabled"
        if hasattr(self.canvas_area_instance, 'preset_combobox'):
            self.canvas_area_instance.preset_combobox.config(state=preset_state)
        if hasattr(self.canvas_area_instance, 'delete_preset_button'):
            self.canvas_area_instance.delete_preset_button.config(state="normal" if is_idle else "disabled")
        if hasattr(self.canvas_area_instance, 'save_preset_button'):
            self.canvas_area_instance.save_preset_button.config(state="normal" if is_idle else "disabled")
        if hasattr(self.canvas_area_instance, 'manage_versions_button'):
            self.canvas_area_instance.manage_versions_button.config(state="normal" if is_idle else "disabled")
        if hasattr(self.canvas_area_instance, 'simulate_button'):
            self.canvas_area_instance.simulate_button.config(state="normal" if is_idle else "disabled")
        btn_map = {
            "IDLE": ("Run Workflow", "warning.TButton", self.action_handler.run_workflow, "normal", "Pause", "info.TButton", self.action_handler.pause_workflow, "disabled"),
            "RUNNING": ("Stop Workflow", "danger.TButton", self.action_handler.stop_workflow, "normal", "Pause", "info.TButton", self.action_handler.pause_workflow, "normal"),
            "PAUSED": ("Stop Workflow", "danger.TButton", self.action_handler.stop_workflow, "normal", "Resume", "success.TButton", self.action_handler.resume_workflow, "normal"),
            "STOPPING": ("Stopping...", "secondary.TButton", lambda: None, "disabled", "Pause", "info.TButton", lambda: None, "disabled"),
        }
        run_txt, run_sty, run_cmd, run_st, pause_txt, pause_sty, pause_cmd, pause_st = btn_map.get(self._execution_state, btn_map["IDLE"])
        if hasattr(self.canvas_area_instance, 'run_button'):
            self.canvas_area_instance.run_button.config(text=run_txt, style=run_sty, command=run_cmd, state=run_st)
        if hasattr(self.canvas_area_instance, 'pause_resume_button'):
            self.canvas_area_instance.pause_resume_button.config(text=pause_txt, style=pause_sty, command=pause_cmd, state=pause_st)
