#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\services\workflow_executor_service\workflow_executor_service.py
# JUMLAH BARIS : 470
#######################################################################

import json
import time
import threading
import logging
import re
import os
import uuid
import random
import sys
import psutil
import traceback
from queue import Queue
from ..base_service import BaseService
from flowork_kernel.api_contract import LoopConfig
from flowork_kernel.execution.VariableResolver import VariableResolver
from flowork_kernel.exceptions import PermissionDeniedError
import queue
class WorkflowExecutorService(BaseService):
    """
    (REMASTERED V2) The main engine for running workflows. This version includes a critical
    fix for branching logic to correctly handle single-path execution from nodes with multiple
    output ports like 'IF Condition'.
    """
    def __init__(self, kernel, service_id: str):
        super().__init__(kernel, service_id)
        self._paused = False
        self._pause_event = threading.Event()
        self._pause_event.set()
        self._stop_event = threading.Event()
        self.behavior_manager = None
        self.current_workflow_context_id = None
        self._connection_history = {}
        self._history_lock = threading.Lock()
        self.variable_resolver = VariableResolver(self.kernel)
        self.logger("Service 'WorkflowExecutor' initialized.", "DEBUG")
        self.process = psutil.Process(os.getpid())
        self.ai_analyzer = self.kernel.get_service("ai_analyzer_service")
    def trigger_workflow_from_node(self, target_node_id: str, payload: dict):
        self.logger(f"Executor searching for node '{target_node_id}' in all active workflow tabs...", "DEBUG")
        tab_manager = self.kernel.get_service("tab_manager_service")
        if not tab_manager:
            self.logger("Cannot trigger from node: TabManagerService is not available.", "ERROR")
            return
        workflow_data, target_tab_widget = tab_manager.find_workflow_for_node(target_node_id)
        if workflow_data and target_tab_widget:
            self.logger(f"Target node '{target_node_id}' found. Starting workflow in tab '{target_tab_widget.tab_id}'.", "SUCCESS")
            self._start_remote_workflow_on_ui_thread(target_tab_widget, target_node_id, payload, workflow_data)
            return
        self.logger(f"Could not find any workflow containing node ID '{target_node_id}'.", "WARN")
    def _wait_for_canvas_manager(self, tab_id, target_node_id, payload, workflow_data, attempt=0):
        MAX_ATTEMPTS = 50
        if attempt > MAX_ATTEMPTS:
            self.logger(f"Timeout waiting for CanvasManager on tab '{tab_id}'. Aborting trigger.", "ERROR")
            return
        tab_manager = self.kernel.get_service("tab_manager_service")
        if not tab_manager or not tab_manager.notebook: return
        target_tab_widget = None
        for tab_id_str in tab_manager.notebook.tabs():
            widget = tab_manager.notebook.nametowidget(tab_id_str)
            if hasattr(widget, 'tab_id') and widget.tab_id == tab_id:
                target_tab_widget = widget
                break
        if not target_tab_widget: return
        if hasattr(target_tab_widget, '_content_initialized') and not target_tab_widget._content_initialized:
            target_tab_widget._initialize_content()
        if hasattr(target_tab_widget, 'canvas_area_instance') and target_tab_widget.canvas_area_instance and hasattr(target_tab_widget.canvas_area_instance, 'canvas_manager') and target_tab_widget.canvas_area_instance.canvas_manager:
            self.logger(f"CanvasManager for tab '{tab_id}' is ready. Starting workflow.", "SUCCESS")
            self._start_remote_workflow_on_ui_thread(target_tab_widget, target_node_id, payload, workflow_data)
        else:
            self.kernel.root.after(100, self._wait_for_canvas_manager, tab_id, target_node_id, payload, workflow_data, attempt + 1)
    def _start_remote_workflow_on_ui_thread(self, target_tab_widget, target_node_id, payload, workflow_data):
        visual_manager = target_tab_widget.canvas_area_instance.canvas_manager.visual_manager
        nodes_dict = {node['id']: node for node in workflow_data['nodes']}
        connections_dict = {conn['id']: conn for conn in workflow_data.get('connections', [])}
        self.execute_workflow(
            nodes_dict, connections_dict, payload,
            logger=self.logger,
            status_updater=visual_manager.update_node_status,
            highlighter=visual_manager.highlight_element,
            ui_callback=target_tab_widget.run_on_ui_thread,
            workflow_context_id=f"remote_trigger_{target_node_id}",
            mode='EXECUTE',
            job_status_updater=None,
            on_complete=target_tab_widget.action_handler._on_execution_finished,
            start_node_id=target_node_id
        )
    def _record_connection_event(self, context_id, connection_id, payload):
        with self._history_lock:
            if context_id not in self._connection_history:
                self._connection_history[context_id] = {}
            if 'steps' not in self._connection_history[context_id]:
                self._connection_history[context_id]['steps'] = []
            history_entry = {
                'connection_id': connection_id,
                'payload': payload,
                'timestamp': time.time()
            }
            self._connection_history[context_id]['steps'].append(history_entry)
    def get_connection_history(self, context_id, connection_id=None):
        with self._history_lock:
            history = self._connection_history.get(context_id, {})
            try:
                serializable_history = json.loads(json.dumps(history, default=str))
                return serializable_history
            except (TypeError, OverflowError):
                history['steps'] = [{'payload': str(step['payload']), 'connection_id': step['connection_id']} for step in history.get('steps', [])]
                return history
    def get_current_context_id(self):
        return self.current_workflow_context_id
    def _get_fresh_settings(self):
        settings_path = os.path.join(self.kernel.data_path, "settings.json")
        if not os.path.exists(settings_path):
            return {}
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.kernel.write_to_log(f"Failed to read settings.json directly: {e}", "ERROR")
            return {}
    def _execute_global_error_handler(self, original_error, failed_workflow_id):
        fresh_settings = self._get_fresh_settings()
        handler_preset_name = fresh_settings.get('global_error_workflow_preset')
        self.kernel.write_to_log(f"GLOBAL ERROR HANDLER: Triggering preset '{handler_preset_name}'...", "WARN")
        preset_manager = self.kernel.get_service("preset_manager")
        if not preset_manager:
            self.kernel.write_to_log(f"GLOBAL ERROR HANDLER: Failed, PresetManager service not available.", "ERROR")
            return
        handler_workflow_data = preset_manager.get_preset_data(handler_preset_name)
        if not handler_workflow_data:
            self.kernel.write_to_log(f"GLOBAL ERROR HANDLER: Failed, preset '{handler_preset_name}' not found.", "ERROR")
            return
        error_payload = { "data": { "failed_workflow_id": failed_workflow_id, "error_message": str(original_error), "error_time": time.time() }, "history": [] }
        try:
            nodes = {node['id']: node for node in handler_workflow_data.get('nodes', [])}
            connections = {conn['id']: conn for conn in handler_workflow_data.get('connections', [])}
            self.execute_workflow_synchronous(
                nodes=nodes, connections=connections, initial_payload=error_payload,
                logger=self.kernel.write_to_log, status_updater=lambda a, b, c: None,
                highlighter=lambda a, b: None, ui_callback=lambda func, *args: func(*args),
                workflow_context_id=f"error_handler_for_{failed_workflow_id}", mode='EXECUTE', job_status_updater=None
            )
            self.kernel.write_to_log(f"GLOBAL ERROR HANDLER: Execution of preset '{handler_preset_name}' completed.", "SUCCESS")
        except Exception as handler_e:
            self.kernel.write_to_log(f"GLOBAL ERROR HANDLER: An error occurred while EXECUTING the error handler itself: {handler_e}", "ERROR")
    def execute_workflow(self, nodes, connections, initial_payload, logger=None, status_updater=None, highlighter=None, ui_callback=None, workflow_context_id="default_workflow", mode='EXECUTE', job_status_updater=None, on_complete=None, start_node_id=None):
        log = logger if callable(logger) else self.kernel.write_to_log
        exec_thread = threading.Thread(
            target=self.execute_workflow_synchronous,
            args=(nodes, connections, initial_payload, log, status_updater, highlighter, ui_callback, workflow_context_id, mode, job_status_updater, on_complete, start_node_id)
        )
        exec_thread.daemon = True
        exec_thread.start()
        return exec_thread
    def execute_workflow_synchronous(self, nodes, connections, initial_payload, logger, status_updater, highlighter, ui_callback, workflow_context_id, mode, job_status_updater, on_complete=None, start_node_id=None):
        log = logger or self.kernel.write_to_log
        run_on_ui = ui_callback if callable(ui_callback) else lambda func, *args: func(*args) if callable(func) else None
        with self._history_lock:
            if workflow_context_id in self._connection_history:
                del self._connection_history[workflow_context_id]
                log(f"Cleared previous run history for context: {workflow_context_id}", "DEBUG")
        if self.behavior_manager is None:
            self.behavior_manager = self.kernel.get_service("behavior_manager_service")
        self.current_workflow_context_id = workflow_context_id
        if callable(job_status_updater):
            job_status_updater(workflow_context_id, {"status": "RUNNING"})
        self._paused = False
        self._pause_event.set()
        self._stop_event.clear()
        if mode == 'SIMULATE':
            log("===== STARTING SIMULATION MODE =====", "WARN")
        if not nodes:
            log("Execution failed: No nodes to execute.", "ERROR")
            return ValueError("No nodes to execute.")
        state_manager = self.kernel.get_service("state_manager")
        checkpoint_key = f"checkpoint::{workflow_context_id}"
        saved_checkpoint = state_manager.get(checkpoint_key) if state_manager else None
        final_payload = None
        try:
            if saved_checkpoint and isinstance(saved_checkpoint, dict) and mode == 'EXECUTE':
                resume_node_id = saved_checkpoint.get("node_id")
                resume_payload = saved_checkpoint.get("payload")
                if resume_node_id and resume_payload is not None:
                    node_name = nodes.get(resume_node_id, {}).get('name', resume_node_id)
                    log(f"CHECKPOINT FOUND: Resuming workflow from state after '{node_name}'.", "WARN")
                    if state_manager:
                        state_manager.delete(checkpoint_key)
                    final_payload = self._find_and_execute_next_nodes(
                        current_node_id=resume_node_id,
                        execution_result=resume_payload,
                        nodes=nodes, connections=connections, log=log,
                        update_status=status_updater, highlight=highlighter,
                        run_on_ui=run_on_ui,
                        workflow_context_id=workflow_context_id, mode=mode
                    )
            elif start_node_id:
                log(f"Service call: Starting workflow execution from specific node '{nodes.get(start_node_id, {}).get('name', start_node_id)}'.", "DEBUG")
                final_payload = self._traverse_and_execute(start_node_id, nodes, connections, initial_payload, log, status_updater, highlighter, run_on_ui, workflow_context_id, mode)
            else:
                all_node_ids = set(nodes.keys())
                nodes_with_incoming = set(conn_data['to'] for conn_data in connections.values() if conn_data.get('to') and conn_data.get('type', 'data') == 'data')
                start_nodes = all_node_ids - nodes_with_incoming
                if not start_nodes:
                    log("Execution failed: No start node found.", "ERROR")
                    return ValueError("No start node found.")
                final_payload = self._run_all_flows_sequentially(start_nodes, nodes, connections, log, status_updater, highlighter, run_on_ui, initial_payload, workflow_context_id, mode)
            if isinstance(final_payload, Exception):
                raise final_payload
        except PermissionDeniedError as e:
            final_payload = e
            log(f"!!! PERMISSION DENIED IN WORKFLOW: {e}", "CRITICAL")
            if hasattr(self.kernel, 'root') and self.kernel.root and hasattr(self.kernel.root, 'display_permission_denied_popup'):
                run_on_ui(self.kernel.display_permission_denied_popup, str(e))
        except Exception as e:
            final_payload = e
            log(f"!!! FATAL ERROR IN WORKFLOW EXECUTOR: {e}", "ERROR")
            log(traceback.format_exc(), "DEBUG")
        finally:
            if isinstance(final_payload, Exception):
                if callable(job_status_updater):
                    job_status_updater(workflow_context_id, {"status": "FAILED", "end_time": time.time(), "error": str(final_payload)})
                fresh_settings = self._get_fresh_settings()
                if fresh_settings.get('global_error_handler_enabled') and fresh_settings.get('global_error_workflow_preset') and not workflow_context_id.startswith("error_handler_for_"):
                    self._execute_global_error_handler(final_payload, workflow_context_id)
            else:
                if callable(job_status_updater):
                     job_status_updater(workflow_context_id, {"status": "SUCCEEDED", "end_time": time.time(), "result": "Execution completed successfully."})
            if mode == 'SIMULATE':
                log("===== SIMULATION FINISHED =====", "WARN")
            self.current_workflow_context_id = None
            history = self.get_connection_history(workflow_context_id)
            if callable(on_complete):
                run_on_ui(on_complete, history)
            if self.ai_analyzer and mode == 'EXECUTE':
                log(f"Executor: Attempting to dispatch analysis request for context '{workflow_context_id}'", "INFO")
                try:
                    permission_manager = self.kernel.get_service("permission_manager_service", is_system_call=True)
                    if permission_manager and permission_manager.check_permission("ai_copilot", is_system_call=False):
                         self.ai_analyzer.request_analysis(workflow_context_id)
                except PermissionDeniedError:
                    self.logger("AI Co-pilot analysis skipped due to license tier.", "WARN")
        return final_payload
    def stop_execution(self):
        self.kernel.write_to_log("STOP request received.", "INFO")
        self._stop_event.set()
    def pause_execution(self):
        self._paused = True
        self._pause_event.clear()
    def resume_execution(self):
        self._paused = False
        self._pause_event.set()
    def _run_all_flows(self, start_nodes, nodes, connections, log, update_status, highlight, run_on_ui, initial_payload, workflow_context_id, mode):
        final_payload = initial_payload
        threads = []
        results_queue = queue.Queue()
        def target_wrapper(start_node_id, payload_copy):
            try:
                result = self._traverse_and_execute(start_node_id, nodes, connections, payload_copy, log, update_status, highlight, run_on_ui, workflow_context_id, mode)
                results_queue.put(result)
            except Exception as e:
                results_queue.put(e)
        for start_node_id in start_nodes:
            payload_copy = json.loads(json.dumps(initial_payload))
            thread = threading.Thread(target=target_wrapper, args=(start_node_id, payload_copy))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        while not results_queue.empty():
            result = results_queue.get()
            if isinstance(result, Exception):
                return result
            final_payload = result
        return final_payload
    def _run_all_flows_sequentially(self, start_nodes, nodes, connections, log, update_status, highlight, run_on_ui, initial_payload, workflow_context_id, mode):
        final_payload = initial_payload
        for start_node_id in start_nodes:
             final_payload = self._traverse_and_execute(start_node_id, nodes, connections, final_payload, log, update_status, highlight, run_on_ui, workflow_context_id, mode)
             if isinstance(final_payload, Exception):
                 return final_payload
        return final_payload
    def _find_and_execute_next_nodes(self, current_node_id, execution_result, nodes, connections, log, update_status, highlight, run_on_ui, workflow_context_id="default_workflow", mode: str = 'EXECUTE'):
        if self._stop_event.is_set():
            return execution_result
        if isinstance(execution_result, Exception):
            return execution_result
        payload_for_next = execution_result.get('payload', execution_result) if isinstance(execution_result, dict) else execution_result
        expected_output_name = None
        if isinstance(execution_result, dict) and "output_name" in execution_result:
            expected_output_name = execution_result["output_name"]
        next_nodes_to_execute = []
        for conn_id, conn_data in connections.items():
            if conn_data.get('from') == current_node_id and conn_data.get('type', 'data') != 'tool':
                source_port_name = conn_data.get('source_port_name')
                if expected_output_name is not None:
                    if source_port_name == expected_output_name:
                        self._record_connection_event(workflow_context_id, conn_id, payload_for_next)
                        next_nodes_to_execute.append((conn_id, conn_data.get('to'), payload_for_next))
                else:
                    self._record_connection_event(workflow_context_id, conn_id, payload_for_next)
                    next_nodes_to_execute.append((conn_id, conn_data.get('to'), payload_for_next))
        if not next_nodes_to_execute:
            node_name_for_log = nodes.get(current_node_id, {}).get('name', '[Unnamed Node]')
            log(f"Execution path finished. Node '{node_name_for_log}' has no outgoing connections from port '{expected_output_name or 'default'}'.", "INFO")
            return execution_result
        if len(next_nodes_to_execute) > 1:
            threads = []
            results_queue = queue.Queue()
            def target_wrapper(next_node_id, payload_copy):
                try:
                    result = self._traverse_and_execute(next_node_id, nodes, connections, payload_copy, log, update_status, highlight, run_on_ui, workflow_context_id, mode)
                    results_queue.put(result)
                except Exception as e:
                    results_queue.put(e)
            for conn_id, next_node_id, payload in next_nodes_to_execute:
                if not next_node_id: continue
                if callable(highlight): run_on_ui(highlight, 'connection', conn_id); time.sleep(0.1)
                payload_copy = json.loads(json.dumps(payload, default=str))
                thread = threading.Thread(target=target_wrapper, args=(next_node_id, payload_copy))
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join()
            successful_results = []
            exceptions = []
            while not results_queue.empty():
                result = results_queue.get()
                if isinstance(result, Exception):
                    exceptions.append(result)
                else:
                    successful_results.append(result)
            if exceptions:
                for exc in exceptions:
                    log(f"A parallel branch failed with an error: {exc}", "WARN")
            if successful_results:
                return successful_results[-1]
            elif exceptions:
                log(f"All {len(exceptions)} parallel branches failed. Propagating the first error.", "ERROR")
                return exceptions[0]
            else:
                return execution_result
        else:
            conn_id, next_node_id, payload = next_nodes_to_execute[0]
            if not next_node_id: return payload
            if callable(highlight): run_on_ui(highlight, 'connection', conn_id); time.sleep(0.1)
            return self._traverse_and_execute(next_node_id, nodes, connections, payload, log, update_status, highlight, run_on_ui, workflow_context_id, mode)
    def _traverse_and_execute(self, current_node_id, nodes, connections, payload, log, update_status, highlight, run_on_ui, workflow_context_id, mode):
        if self._stop_event.is_set(): return payload
        self._pause_event.wait()
        if current_node_id not in nodes: return payload
        node_info = nodes[current_node_id]
        start_time = time.perf_counter()
        mem_before = self.process.memory_info().rss
        payload_size_in = sys.getsizeof(payload)
        execution_result = None
        try:
            node_name_for_log = node_info.get('name', '[Unnamed]')
            module_id_to_run = node_info.get("module_id")
            module_manager = self.kernel.get_service("module_manager_service")
            if not module_manager: raise ValueError("ModuleManagerService not available.")
            if module_id_to_run in self.kernel.MODULE_CAPABILITY_MAP:
                capability_needed = self.kernel.MODULE_CAPABILITY_MAP[module_id_to_run]
                self.logger(f"Capability check required for module '{module_id_to_run}': '{capability_needed}'", "DEBUG")
                permission_manager = self.kernel.get_service("permission_manager_service")
                if permission_manager:
                    permission_manager.check_permission(capability_needed)
            module_instance = module_manager.get_instance(module_id_to_run)
            if not module_instance: raise ValueError(f"Module '{module_id_to_run}' not found or is paused.")
            if callable(highlight) and not getattr(module_instance, 'MANAGES_OWN_HIGHLIGHTING', False):
                run_on_ui(highlight, 'node', current_node_id); time.sleep(0.1)
            log(f"INFO: Executing node '{node_name_for_log}' (Module: {module_id_to_run})", "INFO")
            node_config = node_info.get("config_values", {})
            node_config['__internal_node_id'] = current_node_id
            resolved_config = self.variable_resolver.resolve(node_config)
            kwargs_for_execute = {}
            if module_id_to_run == 'agent_host_module':
                log("Executor: Agent Host Node detected. Gathering connected components.", "DEBUG")
                kwargs_for_execute['highlighter'] = highlight
                kwargs_for_execute['connections'] = connections
                connected_tools = []
                connected_brain = None
                connected_prompt = None
                log(f"--- START AGENT HOST CONNECTION INSPECTION (Node ID: {current_node_id}) ---", "DEBUG")
                for conn_id, conn_data in connections.items():
                    log(f"  Inspecting connection '{conn_id}': FROM {conn_data.get('from')} TO {conn_data.get('to')} | TYPE: {conn_data.get('type')} | TARGET PORT: {conn_data.get('target_port_name')}", "DEBUG")
                    if conn_data.get('to') == current_node_id:
                        log(f"    -> Connection is incoming to Agent Host.", "DEBUG")
                        if conn_data.get('type') == 'tool':
                            log(f"    -> Connection type is 'tool'. MATCH!", "SUCCESS")
                            source_node_id = conn_data.get('from')
                            target_port = conn_data.get('target_port_name')
                            if source_node_id in nodes:
                                source_node_data = nodes[source_node_id]
                                if target_port == 'brain_port':
                                    connected_brain = source_node_data
                                    log(f"    -> Target port is 'brain_port'. BRAIN FOUND: '{source_node_data.get('name')}'", "SUCCESS")
                                elif target_port == 'prompt_port':
                                    connected_prompt = source_node_data
                                    log(f"    -> Target port is 'prompt_port'. PROMPT FOUND: '{source_node_data.get('name')}'", "SUCCESS")
                                elif target_port == 'tools_port':
                                    connected_tools.append(source_node_data)
                                    log(f"    -> Target port is 'tools_port'. TOOL ADDED: '{source_node_data.get('name')}'", "SUCCESS")
                                else:
                                    log(f"    -> WARNING: Connection is 'tool' type but target port '{target_port}' is unknown.", "WARN")
                            else:
                                log(f"    -> ERROR: Source node '{source_node_id}' not found in nodes dictionary.", "ERROR")
                        else:
                            log(f"    -> Connection type is '{conn_data.get('type')}', not 'tool'. SKIPPING.", "INFO")
                log(f"--- END AGENT HOST CONNECTION INSPECTION ---", "DEBUG")
                kwargs_for_execute['connected_tools'] = connected_tools
                kwargs_for_execute['connected_brain'] = connected_brain
                kwargs_for_execute['connected_prompt'] = connected_prompt
            def safe_status_updater(msg, lvl):
                if callable(update_status):
                    run_on_ui(update_status, current_node_id, msg, lvl)
            def core_execution_function(current_payload, current_config, status_updater_func, ui_callback_func, current_mode, node_info_func, highlight_func, **kwargs):
                return module_instance.execute(
                    current_payload, current_config, status_updater_func, ui_callback_func,
                    current_mode, **kwargs
                )
            wrapped_executor = self.behavior_manager.wrap_execution(module_id_to_run, core_execution_function)
            execution_result = wrapped_executor(
                payload, resolved_config, safe_status_updater, run_on_ui, mode,
                node_info, highlight, **kwargs_for_execute
            )
            if not self._stop_event.is_set():
                connections_from_this_node = [c for c in connections.values() if c.get('from') == current_node_id]
                if not connections_from_this_node:
                    log(f"Service workflow reached an end node '{node_name_for_log}'. Returning its result.", "DEBUG")
                    return execution_result
                return self._find_and_execute_next_nodes(current_node_id, execution_result, nodes, connections, log, update_status, highlight, run_on_ui, workflow_context_id, mode)
            else:
                return payload
        except PermissionDeniedError as e:
            execution_result = e
            log(f"ERROR: An error occurred while executing node '{node_info.get('name', 'N/A')}': {e}", "ERROR")
            if callable(update_status):
                run_on_ui(update_status, current_node_id, "Error", "ERROR")
            raise e
        except Exception as e:
            execution_result = e
            log(f"ERROR: An error occurred while executing node '{node_info.get('name', 'N/A')}': {e}", "ERROR")
            if callable(update_status):
                run_on_ui(update_status, current_node_id, "Error", "ERROR")
            return e
        finally:
            if mode == 'EXECUTE':
                end_time = time.perf_counter()
                mem_after = self.process.memory_info().rss
                payload_size_out = sys.getsizeof(execution_result)
                metric_data = {
                    "workflow_context_id": workflow_context_id,
                    "node_id": current_node_id,
                    "node_name": node_info.get('name', '[Unnamed]'),
                    "module_id": node_info.get("module_id"),
                    "status": "ERROR" if isinstance(execution_result, Exception) else "SUCCESS",
                    "execution_time_ms": (end_time - start_time) * 1000,
                    "memory_usage_bytes": mem_after - mem_before,
                    "payload_size_in_bytes": payload_size_in,
                    "payload_size_out_bytes": payload_size_out,
                }
                event_bus = self.kernel.get_service("event_bus")
                if event_bus:
                    event_bus.publish("NODE_EXECUTION_METRIC", metric_data)
