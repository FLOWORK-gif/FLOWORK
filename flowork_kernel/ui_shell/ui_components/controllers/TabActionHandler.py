#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\ui_components\controllers\TabActionHandler.py
# (File baru untuk refactoring main_window.py)
#######################################################################

import ttkbootstrap as ttk
from tkinter import filedialog, messagebox, simpledialog
import threading
import os
import shutil
import json
import uuid
from flowork_kernel.api_client import ApiClient
from flowork_kernel.exceptions import PermissionDeniedError
import time
import random

class TabActionHandler:
    """
    Acts as the 'Controller' for the WorkflowEditorTab.
    It handles all user actions like running, saving, loading workflows,
    and managing the execution state for a specific tab.
    This class was created by refactoring the massive main_window.py.
    """
    def __init__(self, tab_instance, kernel):
        self.tab = tab_instance
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        self.api_client = ApiClient(kernel=self.kernel)
        self.state_manager = self.kernel.get_service("state_manager")

    def run_workflow_from_preset(self, nodes, connections, initial_payload):
        """Used by widgets to trigger a run on this tab's canvas."""
        if self.tab._execution_state != "IDLE":
            self.kernel.write_to_log("Execution command from widget ignored, another workflow is running.", "WARN")
            return

        if hasattr(self.tab, '_clear_all_suggestions'):
            self.tab._clear_all_suggestions()

        try:
            workflow_executor = self.kernel.get_service("workflow_executor_service")
            if not workflow_executor:
                self.kernel.write_to_log("WorkflowExecutorService not found.", "ERROR")
                return

            workflow_context_id = f"preset_run_{uuid.uuid4()}"
            self.tab._execution_state = "RUNNING"
            self.tab._update_button_states()
            self.kernel.write_to_log(f"Running Workflow from External Trigger...", "INFO")

            exec_thread = workflow_executor.execute_workflow(
                nodes, connections, initial_payload,
                logger=self.kernel.write_to_log,
                status_updater=lambda *args: None, # No visual updates for external triggers
                highlighter=lambda *args: None,
                ui_callback=self.tab.run_on_ui_thread,
                workflow_context_id=workflow_context_id,
                job_status_updater=None,
                on_complete=self._on_execution_finished
            )
            self.tab.after(100, lambda: self._check_workflow_completion(exec_thread))

        except PermissionDeniedError as e:
            self.kernel.write_to_log(f"Permission denied to run workflow from preset: {e}", "WARN")
            if hasattr(self.kernel.root, 'show_permission_denied_popup'):
                self.kernel.root.show_permission_denied_popup(str(e))

    def _on_execution_finished(self, history_data):
        """Callback after a workflow run is complete."""
        self.kernel.write_to_log("Execution finished. Passing history data to UI.", "DEBUG")
        if self.tab.canvas_area_instance and hasattr(self.tab.canvas_area_instance, 'show_debugger'):
            self.tab.canvas_area_instance.execution_history = history_data
            if self.tab.canvas_area_instance.debugger_mode_var.get():
                self.tab.canvas_area_instance.show_debugger(history_data)

    def _start_workflow_thread(self, mode: str):
        """Prepares and starts the main workflow loop in a background thread."""
        if not self.tab.canvas_area_instance: return
        if self.tab._execution_state != "IDLE":
            self.kernel.write_to_log("Execution command ignored, another workflow is running.", "WARN")
            return

        try:
            loop_count = int(self.tab.canvas_area_instance.loop_count_var.get())
            if loop_count < 1: loop_count = 1
            enable_delay = self.tab.canvas_area_instance.enable_delay_var.get()
            delay_type = self.tab.canvas_area_instance.delay_type_var.get()
            static_delay = float(self.tab.canvas_area_instance.static_delay_var.get())
            random_min = float(self.tab.canvas_area_instance.random_min_var.get())
            random_max = float(self.tab.canvas_area_instance.random_max_var.get())
        except (ValueError, TypeError):
            messagebox.showerror("Invalid Input", "Loop count and delay values must be valid numbers.")
            return

        delay_settings = {
            "enabled": enable_delay, "type": delay_type, "static": static_delay,
            "min": random_min, "max": random_max
        }

        workflow_executor = self.kernel.get_service("workflow_executor_service", is_system_call=True)
        if workflow_executor:
            workflow_executor._stop_event.clear()

        loop_thread = threading.Thread(target=self._workflow_loop_worker, args=(mode, loop_count, delay_settings), daemon=True)
        loop_thread.start()

    def _workflow_loop_worker(self, mode: str, loop_count: int, delay_settings: dict):
        if hasattr(self.tab, '_clear_all_suggestions'):
            self.tab.after(0, self.tab._clear_all_suggestions)

        try:
            workflow_executor = self.kernel.get_service("workflow_executor_service")
            if not workflow_executor:
                self.kernel.write_to_log("Cannot run workflow, WorkflowExecutorService is not available.", "ERROR")
                self.tab.after(0, messagebox.showerror, self.loc.get("error_title"), "Workflow Executor service is not available.")
                return

            self.tab.after(0, self.tab._set_execution_state_from_thread, "RUNNING")
            self.kernel.write_to_log(f"Starting Workflow Loop (Mode: {mode}, Iterations: {loop_count})...", "INFO")

            for i in range(loop_count):
                if workflow_executor._stop_event.is_set():
                    self.tab.after(0, self.tab.canvas_area_instance.loop_status_var.set, self.loc.get('loop_stopped', fallback="Looping stopped by user."))
                    self.kernel.write_to_log("Workflow loop stopped by user.", "WARN")
                    break

                loop_status_msg = self.loc.get('loop_status_update', fallback="Running iteration {current} of {total}...", current=i + 1, total=loop_count)
                self.tab.after(0, self.tab.canvas_area_instance.loop_status_var.set, loop_status_msg)

                workflow_context_id = f"{self.tab.tab_id}_loop_{i+1}"
                workflow_data = self.tab.canvas_area_instance.canvas_manager.get_workflow_data()
                nodes_dict = {node['id']: node for node in workflow_data['nodes']}
                connections_dict = {conn['id']: conn for conn in workflow_data.get('connections', [])} if workflow_data.get('connections') else {}

                visual_manager = self.tab.canvas_area_instance.canvas_manager.visual_manager
                result = workflow_executor.execute_workflow_synchronous(
                    nodes_dict, connections_dict, {"data": {"start_time": time.time()}, "history": []},
                    logger=self.kernel.write_to_log,
                    status_updater=visual_manager.update_node_status,
                    highlighter=visual_manager.highlight_element,
                    ui_callback=self.tab.run_on_ui_thread,
                    workflow_context_id=workflow_context_id,
                    mode=mode,
                    job_status_updater=None,
                    on_complete=self._on_execution_finished
                )

                if isinstance(result, Exception):
                    self.kernel.write_to_log(f"Loop stopped due to an error on iteration {i+1}: {result}", "ERROR")
                    self.tab.after(0, self.tab.canvas_area_instance.loop_status_var.set, f"Error on iteration {i+1}")
                    break

                if delay_settings['enabled'] and loop_count > 1 and i < loop_count - 1:
                    if delay_settings['type'] == 'static':
                        delay = delay_settings['static']
                        time.sleep(delay)
                    elif delay_settings['type'] == 'random':
                        min_d, max_d = delay_settings['min'], delay_settings['max']
                        delay = random.uniform(min_d, max_d)
                        time.sleep(delay)

            if not workflow_executor._stop_event.is_set():
                 self.tab.after(0, self.tab.canvas_area_instance.loop_status_var.set, self.loc.get('loop_finished', fallback="Looping finished."))

        except PermissionDeniedError as e:
            self.kernel.write_to_log(f"Permission denied to run workflow: {e}", "WARN")
            if hasattr(self.kernel.root, 'show_permission_denied_popup'):
                self.tab.after(0, self.kernel.root.show_permission_denied_popup, str(e))
        finally:
            self.tab.after(0, self.tab._set_execution_state_from_thread, "IDLE")

    def run_workflow(self):
        self._start_workflow_thread(mode='EXECUTE')

    def simulate_workflow(self):
        if self.tab.canvas_area_instance:
            self.tab.canvas_area_instance.debugger_mode_var.set(True)
        self._start_workflow_thread(mode='SIMULATE')

    def _check_workflow_completion(self, exec_thread):
        if exec_thread.is_alive():
            self.tab.after(100, lambda: self._check_workflow_completion(exec_thread))
        else:
            self.kernel.write_to_log("Workflow thread finished.", "SUCCESS")
            self.tab._execution_state = "IDLE"
            self.tab._update_button_states()

    def stop_workflow(self):
        workflow_executor = self.kernel.get_service("workflow_executor_service", is_system_call=True)
        if self.tab._execution_state not in ["RUNNING", "PAUSED"] or not workflow_executor: return
        self.tab._execution_state = "STOPPING"
        self.tab._update_button_states()
        workflow_executor.stop_execution()

    def pause_workflow(self):
        workflow_executor = self.kernel.get_service("workflow_executor_service", is_system_call=True)
        if self.tab._execution_state != "RUNNING" or not workflow_executor: return
        workflow_executor.pause_execution()
        self.tab._execution_state = "PAUSED"
        self.tab._update_button_states()
        self.kernel.write_to_log("Workflow paused.", "INFO")

    def resume_workflow(self):
        workflow_executor = self.kernel.get_service("workflow_executor_service", is_system_call=True)
        if self.tab._execution_state != "PAUSED" or not workflow_executor: return
        workflow_executor.resume_execution()
        self.tab._execution_state = "RUNNING"
        self.tab._update_button_states()
        self.kernel.write_to_log("Workflow resumed.", "INFO")

    def save_workflow(self):
        if not self.tab.canvas_area_instance or not self.tab.canvas_area_instance.canvas_manager:
            return
        workflow_data = self.tab.canvas_area_instance.canvas_manager.get_workflow_data()
        if not workflow_data.get("nodes"):
            messagebox.showwarning(self.loc.get('save_workflow_empty_title'), self.loc.get('save_workflow_empty_message'))
            return
        filepath = filedialog.asksaveasfilename(
            title=self.loc.get('save_workflow_title'),
            filetypes=[(self.loc.get('flowork_workflow_filetype'), "*.json"), ("All files", "*.*")],
            defaultextension=".json"
        )
        if not filepath: return
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(workflow_data, f, indent=4)
            self.kernel.write_to_log(f"Workflow saved to: {filepath}", "SUCCESS")
        except Exception as e:
            self.kernel.write_to_log(f"Failed to save workflow to {filepath}: {e}", "ERROR")

    def load_workflow(self):
        if not self.tab.canvas_area_instance or not self.tab.canvas_area_instance.canvas_manager:
            return
        if messagebox.askyesno(self.loc.get('confirm_load_workflow_title'), self.loc.get('confirm_load_workflow_message')):
            filepath = filedialog.askopenfilename(
                title=self.loc.get('load_workflow_title'),
                filetypes=[(self.loc.get('flowork_workflow_filetype'), "*.json"), ("All files", "*.*")]
            )
            if not filepath: return
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    workflow_data = json.load(f)
                self.tab.canvas_area_instance.canvas_manager.load_workflow_data(workflow_data)
                self.tab.canvas_area_instance.preset_combobox.set('')
                if self.state_manager:
                    self.state_manager.delete(f"tab_preset_map::{self.tab.tab_id}")
                self.kernel.write_to_log(f"Workflow loaded from: {filepath}", "SUCCESS")
            except Exception as e:
                self.kernel.write_to_log(f"Failed to load workflow from {filepath}: {e}", "ERROR")

    def clear_canvas(self, feedback=True):
        if hasattr(self.tab, '_clear_all_suggestions'):
            self.tab._clear_all_suggestions()
        if self.tab.canvas_area_instance:
            self.tab.canvas_area_instance.canvas_manager.clear_canvas(feedback)
            if hasattr(self.tab.canvas_area_instance, '_update_webhook_info'):
                self.tab.canvas_area_instance._update_webhook_info()
            if self.state_manager:
                self.state_manager.delete(f"tab_preset_map::{self.tab.tab_id}")

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
            if self.state_manager:
                self.state_manager.set(f"tab_preset_map::{self.tab.tab_id}", preset_name)
        else:
            messagebox.showerror(self.loc.get('error_title'), f"API Error: {data}")

    def save_as_preset(self):
        if not self.tab.canvas_area_instance: return
        preset_name = simpledialog.askstring(self.loc.get('save_preset_popup_title'), self.loc.get('save_preset_popup_prompt'), parent=self.tab)
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
            if self.state_manager:
                self.state_manager.set(f"tab_preset_map::{self.tab.tab_id}", preset_name)
        else:
            messagebox.showerror(self.loc.get('error_title'), f"API Error: {response}")

    def _delete_selected_preset(self):
        if not self.tab.canvas_area_instance: return
        selected_preset = self.tab.canvas_area_instance.preset_combobox.get()
        if not selected_preset: return
        if messagebox.askyesno(self.loc.get('confirm_delete_title'), self.loc.get('confirm_delete_preset_message', name=selected_preset)):
            threading.Thread(target=self._delete_preset_worker, args=(selected_preset,), daemon=True).start()

    def _delete_preset_worker(self, preset_name):
        success, response = self.api_client.delete_preset(preset_name)
        self.tab.after(0, self._on_delete_preset_complete, success, response, preset_name)

    def _on_delete_preset_complete(self, success, response, preset_name):
        if success:
            self.tab.populate_preset_dropdown()
            if self.state_manager and self.state_manager.get(f"tab_preset_map::{self.tab.tab_id}") == preset_name:
                self.state_manager.delete(f"tab_preset_map::{self.tab.tab_id}")
        else:
            messagebox.showerror(self.loc.get('error_title'), f"API Error: {response}")

    def clear_cache(self):
        if not self.state_manager:
            messagebox.showerror("Error", "StateManager is not available.")
            return

        if messagebox.askyesno(
            title=self.loc.get('confirm_cache_clear_title'),
            message=self.loc.get('confirm_cache_clear_message')
        ):
            try:
                deleted_folders, deleted_files = 0, 0
                current_log_file = None
                if self.kernel.file_logger and self.kernel.file_logger.handlers:
                    current_log_file = self.kernel.file_logger.handlers[0].baseFilename

                for root, dirs, files in os.walk(self.kernel.project_root_path, topdown=False):
                    if '__pycache__' in dirs:
                        pycache_path = os.path.join(root, '__pycache__')
                        try:
                            shutil.rmtree(pycache_path)
                            deleted_folders += 1
                        except (OSError, PermissionError):
                            pass # Ignore if locked
                    for name in files:
                        if name.endswith((".pyc", ".log")):
                            file_path = os.path.join(root, name)
                            if file_path == current_log_file: continue
                            try:
                                os.remove(file_path)
                                deleted_files += 1
                            except (OSError, PermissionError):
                                pass

                deleted_ai_caches = 0
                all_state_keys = list(self.state_manager.get_all().keys())
                for key in all_state_keys:
                    if key.startswith("ai_suggestion::"):
                        self.state_manager.delete(key)
                        deleted_ai_caches += 1

                summary_message = self.loc.get('cache_clear_summary_log_full',
                                               folders=deleted_folders,
                                               files=deleted_files,
                                               ai_caches=deleted_ai_caches)
                messagebox.showinfo(self.loc.get('info_done'), summary_message)

            except Exception as e:
                self.kernel.write_to_log(f"An unexpected error occurred during cache clearing: {e}", "CRITICAL")
                messagebox.showerror(self.loc.get('error_title'), f"An unexpected error occurred: {e}")