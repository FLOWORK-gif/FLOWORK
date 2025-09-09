#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_gui\views\ui_components\controllers\TabActionHandler.py
# JUMLAH BARIS : 142
#######################################################################

import ttkbootstrap as ttk
from tkinter import filedialog, messagebox, simpledialog
import threading
import os
import shutil
import json
import uuid
import time
import random
class TabActionHandler:
    """
    Acts as the 'Controller' for the WorkflowEditorTab.
    It handles all user actions like running, saving, loading workflows,
    and managing the execution state for a specific tab.
    This class was created by refactoring the massive main_window.py.
    (REFACTORED V2) Now fully API-driven and receives its dependencies via constructor.
    """
    def __init__(self, tab_instance, api_client, loc_service): # MODIFIED: Signature updated to accept api_client and loc_service
        self.tab = tab_instance
        self.api_client = api_client
        self.loc = loc_service
    def run_workflow_from_preset(self, nodes, connections, initial_payload):
        """Used by widgets to trigger a run on this tab's canvas."""
        pass
    def _on_execution_finished(self, history_data):
        """Callback after a workflow run is complete."""
        pass
    def _start_workflow_thread(self, mode: str):
        """Prepares and starts the main workflow loop in a background thread."""
        pass
    def _workflow_loop_worker(self, mode: str, loop_count: int, delay_settings: dict):
        pass
    def run_workflow(self):
        self._start_workflow_thread(mode='EXECUTE')
    def simulate_workflow(self):
        self._start_workflow_thread(mode='SIMULATE')
    def _check_workflow_completion(self, exec_thread):
        pass
    def stop_workflow(self):
        pass
    def pause_workflow(self):
        pass
    def resume_workflow(self):
        pass
    def save_workflow(self):
        if not self.tab.canvas_area_instance or not self.tab.canvas_area_instance.canvas_manager:
            return
        workflow_data = self.tab.canvas_area_instance.canvas_manager.get_workflow_data()
        if not workflow_data.get("nodes"):
            messagebox.showwarning(self.loc.get('save_workflow_empty_title', fallback="Cannot Save Empty Workflow"), self.loc.get('save_workflow_empty_message', fallback="There are no nodes on the canvas to save."))
            return
        filepath = filedialog.asksaveasfilename(
            title=self.loc.get('save_workflow_title', fallback="Save Workflow File"),
            filetypes=[(self.loc.get('flowork_workflow_filetype', fallback="Flowork Workflow (*.json)"), "*.json"), ("All files", "*.*")],
            defaultextension=".json"
        )
        if not filepath: return
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(workflow_data, f, indent=4)
            print(f"Workflow saved to: {filepath}") # English Log
        except Exception as e:
            print(f"Failed to save workflow to {filepath}: {e}") # English Log
    def load_workflow(self):
        if not self.tab.canvas_area_instance or not self.tab.canvas_area_instance.canvas_manager:
            return
        if messagebox.askyesno(self.loc.get('confirm_load_workflow_title', fallback="Load Workflow?"), self.loc.get('confirm_load_workflow_message', fallback="Loading a workflow will discard any unsaved changes on the current canvas. Continue?")):
            filepath = filedialog.askopenfilename(
                title=self.loc.get('load_workflow_title', fallback="Load Workflow File"),
                filetypes=[(self.loc.get('flowork_workflow_filetype', fallback="Flowork Workflow (*.json)"), "*.json"), ("All files", "*.*")]
            )
            if not filepath: return
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    workflow_data = json.load(f)
                self.tab.canvas_area_instance.canvas_manager.load_workflow_data(workflow_data)
                self.tab.canvas_area_instance.preset_combobox.set('')
                print(f"Workflow loaded from: {filepath}") # English Log
            except Exception as e:
                print(f"Failed to load workflow from {filepath}: {e}") # English Log
    def clear_canvas(self, feedback=True):
        if hasattr(self.tab, '_clear_all_suggestions'):
            self.tab._clear_all_suggestions()
        if self.tab.canvas_area_instance:
            self.tab.canvas_area_instance.canvas_manager.clear_canvas(feedback)
            if hasattr(self.tab.canvas_area_instance, '_update_webhook_info'):
                self.tab.canvas_area_instance._update_webhook_info()
    def on_preset_selected(self, event=None):
        if not self.tab.canvas_area_instance: return
        selected_preset = self.tab.canvas_area_instance.preset_combobox.get()
        if not selected_preset: return
        threading.Thread(target=self._load_preset_worker, args=(selected_preset,), daemon=True).start()
    def _load_preset_worker(self, preset_name):
        self.tab.after(0, self.tab._clear_all_suggestions)
        success, data = self.api_client.get_preset_data(preset_name)
        self.tab.after(0, self._on_load_preset_complete, success, data, preset_name)
    def _on_load_preset_complete(self, success, data, preset_name):
        if not self.tab.canvas_area_instance: return
        if success:
            self.tab.canvas_area_instance.canvas_manager.load_workflow_data(data)
        else:
            messagebox.showerror(self.loc.get('error_title', fallback="Error"), f"API Error: {data}")
    def save_as_preset(self):
        if not self.tab.canvas_area_instance: return
        preset_name = simpledialog.askstring(self.loc.get('save_preset_popup_title', fallback="Save As Preset"), self.loc.get('save_preset_popup_prompt', fallback="Enter a name for this preset:"), parent=self.tab)
        if not preset_name or not preset_name.strip(): return
        preset_name = preset_name.strip()
        workflow_data = self.tab.canvas_area_instance.canvas_manager.get_workflow_data()
        threading.Thread(target=self._save_preset_worker, args=(preset_name, workflow_data), daemon=True).start()
    def _save_preset_worker(self, preset_name, workflow_data):
        success, response = self.api_client.save_preset(preset_name, workflow_data)
        self.tab.after(0, self._on_save_preset_complete, success, response, preset_name)
    def _on_save_preset_complete(self, success, response, preset_name):
        if not self.tab.canvas_area_instance: return
        if success:
            self.tab.populate_preset_dropdown()
            self.tab.canvas_area_instance.preset_combobox.set(preset_name)
        else:
            messagebox.showerror(self.loc.get('error_title', fallback="Error"), f"API Error: {response}")
    def _delete_selected_preset(self):
        if not self.tab.canvas_area_instance: return
        selected_preset = self.tab.canvas_area_instance.preset_combobox.get()
        if not selected_preset: return
        if messagebox.askyesno(self.loc.get('confirm_delete_title', fallback="Confirm Deletion"), self.loc.get('confirm_delete_preset_message', fallback="Are you sure you want to delete the preset '{name}'?", name=selected_preset)):
            threading.Thread(target=self._delete_preset_worker, args=(selected_preset,), daemon=True).start()
    def _delete_preset_worker(self, preset_name):
        success, response = self.api_client.delete_preset(preset_name)
        self.tab.after(0, self._on_delete_preset_complete, success, response, preset_name)
    def _on_delete_preset_complete(self, success, response, preset_name):
        if success:
            self.tab.populate_preset_dropdown()
        else:
            messagebox.showerror(self.loc.get('error_title', fallback="Error"), f"API Error: {response}")
    def clear_cache(self):
        pass
