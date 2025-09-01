#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\kernel.py
# (Full code for the modified file with the fix)
#######################################################################

import os
import sys
import json
import time
import logging
import threading
import queue
import webbrowser
import importlib
import datetime
from typing import List, Dict, Any, Callable
import requests
from packaging import version
from flowork_kernel.exceptions import PermissionDeniedError

class ServiceWorkflowProxy:
    # ... (code inside this class is unchanged)
    def __init__(self, kernel, service_id, preset_path):
        self.kernel = kernel
        self.service_id = service_id
        self.preset_path = preset_path
        self.workflow_data = None
        self.nodes = {}
        self.connections = {}
        self._load_workflow_definition()
    def _load_workflow_definition(self):
        try:
            if not os.path.exists(self.preset_path):
                raise FileNotFoundError(f"Service preset file not found: {self.preset_path}")
            with open(self.preset_path, 'r', encoding='utf-8') as f:
                self.workflow_data = json.load(f)
            # if "preset_manager.flowork" in self.preset_path:
            #     print("--- DEBUGGING PRESET MANAGER ---")
            #     node_names = [n.get('name') for n in self.workflow_data.get('nodes', [])]
            #     print("Node names found in preset_manager.flowork:", node_names)
            #     print("---------------------------------")
            self.nodes = {node['id']: node for node in self.workflow_data.get('nodes', [])}
            self.connections = {conn['id']: conn for conn in self.workflow_data.get('connections', [])}
            self.kernel.write_to_log(f"Service workflow definition for '{self.service_id}' loaded successfully.", "SUCCESS")
        except Exception as e:
            self.kernel.write_to_log(f"CRITICAL: Failed to load service workflow for '{self.service_id}': {e}", "ERROR")
            self.workflow_data = None
    def reload_definition(self):
        """Public method to manually trigger a reload of the workflow definition."""
        self.kernel.write_to_log(f"Proxy '{self.service_id}': Hot reload triggered.", "WARN") # English Log
        self._load_workflow_definition()
    def __getattr__(self, name):
        def method(*args, **kwargs):
            self.kernel.write_to_log(f"Proxy '{self.service_id}': Method '{name}' called. Executing corresponding workflow...", "INFO")
            if not self.workflow_data:
                self.kernel.write_to_log(f"Cannot execute '{name}' for service '{self.service_id}', workflow definition failed to load.", "ERROR")
                return None
            start_node_id = None
            sanitized_name = name.replace(' ', '_')
            for node_id, node_data in self.nodes.items():
                if node_data.get('name', '').strip().replace(' ', '_') == sanitized_name:
                    start_node_id = node_id
                    break
            if not start_node_id:
                self.kernel.write_to_log(f"No start node named '{name}' found in workflow for service '{self.service_id}'.", "ERROR")
                return None
            context_id = f"service_call_{self.service_id}_{name}_{time.time()}"
            executor = self.kernel.get_service("workflow_executor_service")
            if not executor:
                self.kernel.write_to_log(f"WorkflowExecutorService not available to run service '{self.service_id}'.", "CRITICAL")
                return None
            initial_payload = {"data": { "args": args, "kwargs": kwargs }, "history": []}
            execution_result = executor.execute_workflow_synchronous(
                self.nodes, self.connections, initial_payload, logger=self.kernel.write_to_log,
                status_updater=lambda a,b,c: None, highlighter=lambda a,b: None,
                ui_callback=lambda func, *a: func(*a), workflow_context_id=context_id, mode='EXECUTE',
                job_status_updater=None, start_node_id=start_node_id
            )
            if isinstance(execution_result, dict) and "payload" in execution_result:
                return execution_result["payload"]
            else:
                return execution_result
        return method

class Kernel:
    instance = None
    APP_VERSION = "1.0.0"
    license_tier: str = "free"
    is_premium: bool = False
    DEV_MODE_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAysqZG2+F82W0TgLHmF3Y
0GRPEZvXvmndTY84N/wA1ljt+JxMBVsmcVTkv8f1TrmFRD19IDzl2Yzb2lgqEbEy
GFxHhudC28leDsVEIp8B+oYWVm8Mh242YKYK8r5DAvr9CPQivnIjZ4BWgKKddMTd
harVxLF2CoSoTs00xWKd6VlXfoW9wdBvoDVifL+hCMepgLLdQQE4HbamPDJ3bpra
pCgcAD5urmVoJEUJdjd+Iic27RBK7jD1dWDO2MASMh/0IyXyM8i7RDymQ88gZier
U0OdWzeCWGyl4EquvR8lj5GNz4vg2f+oEY7h9AIC1f4ARtoihc+apSntqz7nAqa/
sQIDAQAB
-----END PUBLIC KEY-----"""

    TIER_HIERARCHY = {
        "free": 0,
        "basic": 1,
        "pro": 2,
        "architect": 3,
        "enterprise": 4
    }
    SERVICE_CAPABILITY_MAP = {
        "ai_provider_manager_service": "ai_provider_access",
        "ai_architect_service": "ai_architect",
        "ai_training_service": "ai_local_models",
        "model_converter_service": "ai_local_models",
        "agent_manager_service": "ai_architect",
        "agent_executor_service": "ai_architect",
        "screen_recorder_service": "screen_recorder"
    }
    MODULE_CAPABILITY_MAP = {
        "advanced_web_scraper_module_1a2b": "web_scraping_advanced",
        "stable_diffusion_xl_module": "ai_local_models",
        "stable_video_diffusion_module_c4d3": "ai_local_models",
        "sentiment_analysis_module": "ai_local_models",
        "text_to_speech_module": "ai_local_models",
        "ai_center_module": "ai_provider_access",
        "prompt_engineer_module_a1b2": "ai_provider_access",
        "nuitka_compiler_module_b4a1": "core_compiler",
        "core_compiler_module": "core_compiler",
        "sub_workflow_module": "preset_versioning"
    }

    class FileSystemProxy:
        # ... (code inside this class is unchanged)
        def __init__(self, kernel):
            self.kernel = kernel
            self.os_module = os
            self.shutil_module = __import__('shutil')
        def _check_permission(self, caller_module_id: str, required_permission: str):
            if not caller_module_id: return
            module_manager = self.kernel.get_service("module_manager_service")
            if not module_manager: raise PermissionDeniedError("Cannot verify permissions: ModuleManagerService is not available.")
            permissions = module_manager.get_module_permissions(caller_module_id)
            if required_permission not in permissions and "file_system:all" not in permissions:
                raise PermissionDeniedError(f"Module '{caller_module_id}' does not have the required permission: '{required_permission}'")
        def read(self, file_path, mode='r', encoding='utf-8', caller_module_id: str = None):
            self._check_permission(caller_module_id, "file_system:read")
            with open(file_path, mode, encoding=encoding) as f:
                return f.read()
        def write(self, file_path, data, mode='w', encoding='utf-8', caller_module_id: str = None):
            self._check_permission(caller_module_id, "file_system:write")
            with open(file_path, mode, encoding=encoding) as f:
                f.write(data)
        def exists(self, path, caller_module_id: str = None):
            self._check_permission(caller_module_id, "file_system:read")
            return self.os_module.path.exists(path)
        def remove(self, path, caller_module_id: str = None):
            self._check_permission(caller_module_id, "file_system:write")
            return self.os_module.remove(path)
        def rmtree(self, path, caller_module_id: str = None):
            self._check_permission(caller_module_id, "file_system:write")
            return self.shutil_module.rmtree(path)

    class NetworkProxy:
        # ... (code inside this class is unchanged)
        def __init__(self, kernel):
            self.kernel = kernel
            self.requests_module = requests
        def _check_permission(self, caller_module_id: str, required_permission: str):
            if not caller_module_id: return
            module_manager = self.kernel.get_service("module_manager_service")
            if not module_manager: raise PermissionDeniedError("Cannot verify permissions: ModuleManagerService is not available.")
            permissions = module_manager.get_module_permissions(caller_module_id)
            if required_permission not in permissions and "network:all" not in permissions:
                 raise PermissionDeniedError(f"Module '{caller_module_id}' does not have the required permission: '{required_permission}'")
        def get(self, url, caller_module_id: str = None, **kwargs):
            self._check_permission(caller_module_id, "network:get")
            return self.requests_module.get(url, **kwargs)
        def post(self, url, caller_module_id: str = None, **kwargs):
            self._check_permission(caller_module_id, "network:post")
            return self.requests_module.post(url, **kwargs)

    def __init__(self, project_root_path: str):
        Kernel.instance = self
        self.project_root_path = project_root_path
        self.is_dev_mode = self._validate_dev_mode()
        if self.is_dev_mode:
            self._log_dev_mode_on_init = True
        else:
            self._log_dev_mode_on_init = False

        self.services: Dict[str, Any] = {}
        self.root = None
        self.startup_complete = False
        # [ADDED BACK] This is the missing line that caused the crash.
        self.current_user = None

        self.data_path = os.path.join(self.project_root_path, "data")
        self.logs_path = os.path.join(self.project_root_path, "logs")
        self.modules_path = os.path.join(self.project_root_path, "modules")
        self.plugins_path = os.path.join(self.project_root_path, "plugins")
        self.system_plugins_path = os.path.join(self.project_root_path, "system_plugins")
        self.widgets_path = os.path.join(self.project_root_path, "widgets")
        self.themes_path = os.path.join(self.project_root_path, "themes")
        self.triggers_path = os.path.join(self.project_root_path, "triggers")
        self.locales_path = os.path.join(self.project_root_path, "locales")
        self.ai_providers_path = os.path.join(self.project_root_path, "ai_providers")
        self.formatters_path = os.path.join(self.project_root_path, "formatters")
        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(self.logs_path, exist_ok=True)
        self.log_queue = queue.Queue()
        self.cmd_log_queue = queue.Queue()
        self.log_viewer_references = {}
        self.file_system = self.FileSystemProxy(self)
        self.network = self.NetworkProxy(self)
        self._setup_file_logger()

        if self._log_dev_mode_on_init:
            self.write_to_log("Kernel booted in secure DEVELOPMENT MODE.", "WARN") # English Log

        self._load_services_from_manifest()

    def _validate_dev_mode(self) -> bool:
        """
        Checks for the existence of devmode.on and verifies its content.
        Returns True only if the file exists and contains the correct public key.
        """
        dev_mode_file = os.path.join(self.project_root_path, "devmode.on")
        if not os.path.exists(dev_mode_file):
            return False

        try:
            with open(dev_mode_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            if content == self.DEV_MODE_PUBLIC_KEY.strip():
                return True
            else:
                self._log_dev_mode_on_init = True
                print("[KERNEL-WARN] devmode.on file found, but its content is invalid. DEV MODE WILL NOT ACTIVATE.") # English Log
                return False
        except Exception:
            print("[KERNEL-ERROR] Could not read devmode.on file. DEV MODE WILL NOT ACTIVATE.") # English Log
            return False

    # ... (rest of the file is unchanged) ...
    @property
    def ai_manager(self):
        return self.get_service("ai_provider_manager_service")
    @property
    def loc(self):
        """ (ADDED) Provides a safe, official public accessor for the LocalizationManager. """
        return self.get_service("localization_manager")
    @property
    def event_bus(self):
        """ (ADDED) Provides a safe, official public accessor for the EventBus. """
        return self.get_service("event_bus")
    def register_ui_service(self, service_id: str, instance: object):
        if service_id in self.services:
            self.write_to_log(f"Service '{service_id}' is being overwritten by a UI-bound instance.", "WARN")
        self.services[service_id] = instance
        self.write_to_log(f"UI-bound service '{service_id}' registered successfully.", "SUCCESS")
    def _log_queue_worker(self):
        while True:
            try:
                log_record = self.log_queue.get()
                if not self.log_viewer_references:
                    print(f"[{log_record['level']}] (No Logger) {log_record['message']}")
                    self.log_queue.task_done()
                    continue
                for tab_id, log_viewer in list(self.log_viewer_references.items()):
                    if self.root and hasattr(self.root, 'after'):
                        self.root.after(0, lambda lv=log_viewer, lr=log_record: lv.write_to_log(lr['message'], lr['level']))
                self.log_queue.task_done()
            except Exception as e:
                print(f"[LOG WORKER ERROR] {e}")
                time.sleep(1)
    def _load_services_from_manifest(self):
        manifest_path = os.path.join(os.path.dirname(__file__), 'services.json')
        self.write_to_log(f"Kernel: Loading services from manifest: {manifest_path}", "INFO")
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                services_manifest = json.load(f)
            service_order = [
                "integrity_checker_service",
                "license_manager_service",
                "event_bus",
                "localization_manager",
                "state_manager",
                "permission_manager_service",
                "variable_manager",
                "preset_manager_service",
                "tab_manager_service"
            ]
            all_services = services_manifest['services']
            loaded_ids = set()
            for service_id in service_order:
                service_config = next((s for s in all_services if s['id'] == service_id), None)
                if service_config:
                    self._load_service(service_config)
                    loaded_ids.add(service_id)
            if "license_manager_service" in self.services:
                self.write_to_log("Kernel: Running early license verification...", "INFO") # English Log
                license_manager = self.get_service("license_manager_service", is_system_call=True)
                if hasattr(license_manager, 'verify_license_on_startup'):
                    license_manager.verify_license_on_startup()
                self.write_to_log(f"Kernel: License tier confirmed as '{self.license_tier.upper()}' before loading premium services.", "SUCCESS") # English Log
            for service_config in all_services:
                if service_config['id'] not in loaded_ids:
                    self._load_service(service_config)
            self.write_to_log("Kernel: All services loaded. Creating aliases...", "DEBUG")
            if "preset_manager_service" in self.services:
                self.services["preset_manager"] = self.services["preset_manager_service"]
                self.write_to_log("Alias 'preset_manager' created for 'preset_manager_service'.", "SUCCESS")
            if "variable_manager" in self.services:
                self.services["variable_manager_service"] = self.services["variable_manager"]
                self.write_to_log("Alias 'variable_manager_service' created for 'variable_manager'.", "SUCCESS")
        except Exception as e:
            raise RuntimeError(f"Could not load services manifest: {e}") from e
    def _load_service(self, service_config: Dict[str, str]):
        service_id = service_config['id']
        service_type = service_config.get("type", "class")
        try:
            if service_id in self.SERVICE_CAPABILITY_MAP:
                capability_needed = self.SERVICE_CAPABILITY_MAP[service_id]
                permission_manager = self.services.get("permission_manager_service")
                if permission_manager and not permission_manager.check_permission(capability_needed, is_system_call=True):
                    raise PermissionDeniedError(f"Permission denied to LOAD service '{service_id}' - requires '{capability_needed}'.")
            if service_type == "service_workflow":
                preset_path = service_config.get("preset_path")
                if not preset_path:
                    self.write_to_log(f"Failed to load service workflow '{service_id}': 'preset_path' is missing.", "ERROR")
                    return
                full_preset_path = os.path.join(self.project_root_path, preset_path)
                self.services[service_id] = ServiceWorkflowProxy(self, service_id, full_preset_path)
            else:
                module_path = service_config['path']
                class_name = service_config['class']
                module = importlib.import_module(module_path)
                ServiceClass = getattr(module, class_name)
                self.services[service_id] = ServiceClass(self, service_id)
                self.write_to_log(f"Service '{service_id}' loaded successfully.", "SUCCESS")
        except PermissionDeniedError as e:
            self.write_to_log(f"Failed to load service '{service_id}' due to insufficient permissions: {e}", "WARN")
            return
        except Exception as e:
            self.write_to_log(f"Failed to load service '{service_id}': {e}", "ERROR")
            if service_id in ["event_bus", "localization_manager", "integrity_checker_service", "license_manager_service", "permission_manager_service", "state_manager", "variable_manager_service", "module_manager_service"]:
                raise RuntimeError(f"Critical service '{service_id}' failed to load.") from e
    def get_service(self, service_id: str, is_system_call: bool = False) -> Any:
        try:
            if service_id in self.SERVICE_CAPABILITY_MAP and not is_system_call:
                capability_needed = self.SERVICE_CAPABILITY_MAP[service_id]
                permission_manager = self.services.get("permission_manager_service")
                if permission_manager:
                    permission_manager.check_permission(capability_needed, is_system_call=False)
            service = self.services.get(service_id)
            if not service:
                self.write_to_log(f"Service '{service_id}' requested but not found!", "ERROR")
            return service
        except PermissionDeniedError as e:
            self.write_to_log(f"Permission Denied accessing service '{service_id}': {e}", "WARN")
            raise e
    def start_all_services(self):
        self.write_to_log("Kernel: Minimalist bootloader starting...", "INFO")
        log_worker_thread = threading.Thread(target=self._log_queue_worker, daemon=True)
        log_worker_thread.start()
        self.write_to_log("Kernel: Handing control directly to StartupService...", "INFO")
        try:
            startup_service = self.get_service('startup_service', is_system_call=True)
            if startup_service:
                result = startup_service.run_startup_sequence()
                self.write_to_log(f"Startup sequence finished with status: {result}", "SUCCESS")
            else:
                 self.write_to_log("CRITICAL: StartupService not found! Cannot start application.", "ERROR")
                 raise RuntimeError("StartupService is essential for application startup and was not found.")
        except Exception as e:
            self.write_to_log(f"CRITICAL: Startup sequence failed with an exception: {e}", "ERROR")
            raise e
    def finalize_startup(self):
        self.write_to_log("Kernel: Finalizing startup sequence (UI is ready).", "INFO")
        self.write_to_log("Kernel: Startup finalized. Application is fully operational.", "SUCCESS")
    def hot_reload_components(self):
        self.write_to_log("HOT RELOAD: A component change was detected. Reloading all components...", "WARN")
        for cache_file in ["module_index.cache", "widget_index.cache", "trigger_index.cache"]:
            cache_path = os.path.join(self.data_path, cache_file)
            if os.path.exists(cache_path):
                try:
                    os.remove(cache_path)
                except OSError: pass
        self.get_service("module_manager_service").discover_and_load_modules()
        self.get_service("widget_manager_service").discover_and_load_widgets()
        self.get_service("trigger_manager_service").discover_and_load_triggers()
        self.get_service("localization_manager").load_all_languages()
        if self.event_bus:
            self.event_bus.publish("COMPONENT_LIST_CHANGED", {"status": "hot_reloaded"})
        if self.root and hasattr(self.root, 'refresh_ui_components'):
            self.root.after(100, self.root.refresh_ui_components)
        self.write_to_log("HOT RELOAD: Component reload process finished.", "SUCCESS")
    def stop_all_services(self):
        self.write_to_log("Kernel: Stopping all services...", "INFO")
        for service_id, service_instance in reversed(list(self.services.items())):
            if hasattr(service_instance, 'stop') and callable(getattr(service_instance, 'stop')):
                try:
                    if not isinstance(service_instance, ServiceWorkflowProxy):
                        service_instance.stop()
                except Exception as e:
                    self.write_to_log(f"Error stopping service '{service_id}': {e}", "ERROR")
        for service_id, service_instance in reversed(list(self.services.items())):
             if isinstance(service_instance, threading.Thread) and service_instance.is_alive():
                service_instance.join(timeout=2)
    def is_premium_user(self) -> bool:
        return self.is_premium
    def is_monetization_active(self) -> bool:
        license_manager = self.get_service("license_manager_service", is_system_call=True)
        if license_manager and license_manager.remote_permission_rules:
            return license_manager.remote_permission_rules.get("monetization_active", True)
        return True
    def is_tier_sufficient(self, required_tier: str) -> bool:
        if not self.is_monetization_active():
            return True
        user_level = self.TIER_HIERARCHY.get(self.license_tier.lower(), 0)
        required_level = self.TIER_HIERARCHY.get(required_tier.lower(), 99)
        return user_level >= required_level
    def activate_license_online(self, full_license_content: dict):
        license_manager = self.get_service("license_manager_service")
        if license_manager:
            return license_manager.activate_license_on_server(full_license_content)
        return False, "License Manager service not found."
    def deactivate_license_online(self):
        license_manager = self.get_service("license_manager_service")
        if license_manager:
            return license_manager.deactivate_license_on_server()
        return False, "License Manager service not found."
    def register_log_viewer(self, tab_id: str, log_viewer_instance):
        if self.log_viewer_references.get(tab_id) is log_viewer_instance:
            return
        self.write_to_log(f"Log Viewer for tab ID '{tab_id}' has been registered.", "DEBUG")
        self.log_viewer_references[tab_id] = log_viewer_instance
    def unregister_log_viewer(self, tab_id: str):
        if tab_id in self.log_viewer_references:
            del self.log_viewer_references[tab_id]
    def set_root(self, root_window):
        self.root = root_window
    def _setup_file_logger(self):
        self.file_logger = logging.getLogger('FloworkFileLogger')
        self.file_logger.setLevel(logging.DEBUG)
        log_file_path = os.path.join(self.logs_path, f"flowork_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        if not self.file_logger.handlers:
            file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
            file_handler.setFormatter(formatter)
            self.file_logger.addHandler(file_handler)
    def write_to_log(self, message, level="INFO"):
        log_record = {"message": str(message), "level": level.upper()}
        self.log_queue.put(log_record)
    def display_approval_popup(self, module_id: str, message: str, callback_func: Callable):
        module_manager = self.get_service("module_manager_service")
        if not module_manager:
            if callable(callback_func):
                threading.Thread(target=callback_func, args=('REJECTED',)).start()
            return
        module_manager.register_approval_callback(module_id, callback_func)
        if self.root and hasattr(self.root, 'popup_manager'):
             self.root.popup_manager.show_approval(module_id, "Current Workflow", message)
        else:
            if callable(callback_func):
                threading.Thread(target=callback_func, args=('REJECTED',)).start()
    def display_permission_denied_popup(self, message: str):
        if self.root and hasattr(self.root, 'show_permission_denied_popup'):
            self.root.show_permission_denied_popup(message)
        else:
            self.write_to_log(f"PERMISSION_DENIED_POPUP_FALLBACK: {message}", "CRITICAL")
    def trigger_workflow_from_node(self, target_node_id: str, payload: dict):
        """
        Finds the correct workflow tab containing the target node and starts
        execution from that specific node.
        """
        self.write_to_log(f"Kernel received request to trigger workflow from node '{target_node_id}'.", "INFO") # English Log
        executor = self.get_service("workflow_executor_service")
        if executor:
            executor.trigger_workflow_from_node(target_node_id, payload)
        else:
            self.write_to_log("WorkflowExecutorService not available, cannot trigger node.", "ERROR") # English Log