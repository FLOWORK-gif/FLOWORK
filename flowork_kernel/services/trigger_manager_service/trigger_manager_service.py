#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\triggers\trigger_manager_service\trigger_manager_service.py
# [MODIFIED V4] Simplification: Removed signature verification block.
#######################################################################

import os
import json
import importlib.util
from importlib.machinery import ExtensionFileLoader
# import py_compile # COMMENT: This import is not used, commenting out.
import uuid
import time
import tempfile
import zipfile
import shutil
from flowork_kernel.api_contract import BaseTriggerListener
from ..base_service import BaseService
import hashlib # [ADDED] For fingerprinting
import subprocess # [ADDED] For running pip
import sys # [ADDED] For getting python executable

class TriggerManagerService(BaseService):
    """
    Manages the discovery, loading, and lifecycle of all Trigger modules.
    [MODIFICATION] Upgraded to support hybrid loading of native (.aola_flowork) and source (.py) triggers.
    [FIXED V2] Now subscribes to an event to start listeners, preventing startup race conditions.
    """
    def __init__(self, kernel, service_id: str):
        super().__init__(kernel, service_id)
        self.triggers_dir = self.kernel.triggers_path
        self.loaded_triggers = {}
        self.active_listeners = []
        self.cache_file = os.path.join(self.kernel.data_path, 'trigger_index.cache')
        self.kernel.write_to_log("Service 'TriggerManager' initialized.", "DEBUG")
    def start(self):
        """
        Subscribes to the main event bus to safely start listeners after all services are ready.
        """
        event_bus = self.kernel.get_service("event_bus")
        if event_bus:
            event_bus.subscribe(
                "event_all_services_started",
                "TriggerManagerStarter",
                self.start_all_listeners
            )
            self.logger("TriggerManager is now waiting for the signal to start all listeners.", "INFO")
    def _is_cache_valid(self):
        if not os.path.exists(self.cache_file):
            return False
        cache_mod_time = os.path.getmtime(self.cache_file)
        if os.path.exists(self.triggers_dir):
            if os.path.getmtime(self.triggers_dir) > cache_mod_time:
                return False
            for root, dirs, _ in os.walk(self.triggers_dir):
                for d in dirs:
                    if os.path.getmtime(os.path.join(root, d)) > cache_mod_time:
                        return False
        return True
    def discover_and_load_triggers(self):
        self.kernel.write_to_log("TriggerManager: Starting discovery and loading of Trigger modules...", "INFO")
        self.loaded_triggers.clear()
        if self._is_cache_valid():
            self.kernel.write_to_log("TriggerManager: Valid cache found. Loading triggers from index...", "INFO")
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            for trigger_id, trigger_data in cached_data.items():
                self._process_single_trigger(
                    trigger_dir=trigger_data['path'],
                    trigger_id=trigger_id,
                    manifest_override=trigger_data['manifest']
                )
            self.kernel.write_to_log(f"Trigger discovery from cache complete. Total processed: {len(self.loaded_triggers)}", "INFO")
            return
        self.kernel.write_to_log("TriggerManager: Cache not found or stale. Discovering from disk...", "WARN")
        discovered_data_for_cache = {}
        if not os.path.exists(self.triggers_dir):
            self.kernel.write_to_log(f"Triggers directory '{self.triggers_dir}' not found. Skipping.", "WARN")
            return
        for trigger_id in os.listdir(self.triggers_dir):
            trigger_dir = os.path.join(self.triggers_dir, trigger_id)
            if not os.path.isdir(trigger_dir) or trigger_id == '__pycache__':
                continue
            manifest = self._process_single_trigger(trigger_dir, trigger_id)
            if manifest:
                discovered_data_for_cache[trigger_id] = {
                    'manifest': manifest,
                    'path': trigger_dir
                }
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(discovered_data_for_cache, f)
            self.kernel.write_to_log(f"TriggerManager: Trigger index cache created at {self.cache_file}", "SUCCESS")
        except Exception as e:
            self.kernel.write_to_log(f"TriggerManager: Failed to write trigger cache file: {e}", "ERROR")
        self.kernel.write_to_log(f"Trigger discovery complete. Total processed: {len(self.loaded_triggers)}", "INFO")
    def _process_single_trigger(self, trigger_dir, trigger_id, manifest_override=None):
        manifest = manifest_override
        if manifest is None:
            manifest_path = os.path.join(trigger_dir, "manifest.json")
            if not os.path.exists(manifest_path):
                return None
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
            except Exception as e:
                self.kernel.write_to_log(f" ! Failed to load trigger manifest for '{trigger_id}': {e}", "ERROR")
                return None
        try:
            self.kernel.write_to_log(f" -> Found trigger: '{manifest.get('name', trigger_id)}'", "DEBUG")

            # [MODIFIED] Run local dependency installation during discovery
            self._install_dependencies_locally(trigger_dir, manifest.get('name', trigger_id))

            trigger_data = {
                "class": None,
                "manifest": manifest,
                "path": trigger_dir,
                "config_ui_class": None
            }
            entry_point = manifest.get("entry_point")
            if entry_point:
                module_filename, class_name = entry_point.split('.')
                source_file_path = os.path.join(trigger_dir, f"{module_filename}.py")
                native_file_path = os.path.join(trigger_dir, f"{module_filename}.aola_flowork")
                path_to_load = None
                is_native_module = False
                if os.path.exists(native_file_path):
                    path_to_load = native_file_path
                    is_native_module = True
                elif os.path.exists(source_file_path):
                    path_to_load = source_file_path
                if not path_to_load:
                    raise FileNotFoundError(f"Entry point file '{module_filename}.py' or '{module_filename}.aola_flowork' not found.")

                # (FIXED V3) Simplified module name for compiled files to fix PyInit error.
                if is_native_module:
                    module_full_name = module_filename
                else:
                    safe_trigger_id = trigger_id.replace('-', '_')
                    module_full_name = f"flowork_native_trigger.{safe_trigger_id}.{module_filename}"

                if is_native_module:
                    loader = ExtensionFileLoader(module_full_name, path_to_load)
                    spec = importlib.util.spec_from_loader(loader.name, loader)
                else:
                    spec = importlib.util.spec_from_file_location(module_full_name, source_file_path)

                module_lib = importlib.util.module_from_spec(spec)
                if module_full_name in sys.modules and not is_native_module:
                    pass
                else:
                    sys.modules[module_full_name] = module_lib
                spec.loader.exec_module(module_lib)
                TriggerClass = getattr(module_lib, class_name)
                if not issubclass(TriggerClass, BaseTriggerListener):
                    if manifest.get("id") != "cron_trigger":
                        raise TypeError(f"Class '{class_name}' must inherit from BaseTriggerListener.")
                trigger_data["class"] = TriggerClass
            config_ui_entry = manifest.get("config_ui_entry_point")
            if config_ui_entry:
                ui_module_filename, ui_class_name = config_ui_entry.split('.')
                ui_source_path = os.path.join(trigger_dir, f"{ui_module_filename}.py")
                if not os.path.exists(ui_source_path):
                     raise FileNotFoundError(f"Config UI file '{ui_module_filename}.py' not found.")
                ui_module_full_name = f"triggers.{trigger_id}.{ui_module_filename}"
                ui_spec = importlib.util.spec_from_file_location(ui_module_full_name, ui_source_path)
                ui_module_lib = importlib.util.module_from_spec(ui_spec)
                ui_spec.loader.exec_module(ui_module_lib)
                trigger_data["config_ui_class"] = getattr(ui_module_lib, ui_class_name)
            self.loaded_triggers[trigger_id] = trigger_data
            self.kernel.write_to_log(f" + Trigger '{manifest.get('name', trigger_id)}' processed successfully.", "SUCCESS")
        except Exception as e:
            self.kernel.write_to_log(f" ! Failed to load trigger from folder '{trigger_id}': {e}", "ERROR")
        return manifest

    # [NEW] Helper function to calculate hash of requirements file
    def _calculate_requirements_hash(self, file_path):
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except IOError:
            return None

    # [NEW] Standardized dependency installer.
    def _install_dependencies_locally(self, component_path, component_name):
        requirements_path = os.path.join(component_path, 'requirements.txt')
        if not os.path.exists(requirements_path):
            return True

        vendor_path = os.path.join(component_path, 'vendor')
        hash_file_path = os.path.join(component_path, '.vendor_hash')

        current_hash = self._calculate_requirements_hash(requirements_path)

        if os.path.isdir(vendor_path) and os.path.exists(hash_file_path):
            try:
                with open(hash_file_path, 'r') as f:
                    saved_hash = f.read().strip()
                if saved_hash == current_hash:
                    return True
            except IOError:
                pass

        self.kernel.write_to_log(f"Trigger '{component_name}' has local dependencies. Installing into 'vendor' folder...", "INFO")

        if os.path.isdir(vendor_path):
            shutil.rmtree(vendor_path, ignore_errors=True)

        try:
            python_exe = sys.executable
            command = [
                python_exe, "-m", "pip", "install", "--target", vendor_path,
                "-r", requirements_path, "--no-user", "--disable-pip-version-check"
            ]
            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = subprocess.CREATE_NO_WINDOW
            subprocess.run(command, check=True, capture_output=True, creationflags=creation_flags)
            with open(hash_file_path, 'w') as f:
                f.write(current_hash)
            self.kernel.write_to_log(f"Successfully installed local dependencies for '{component_name}'.", "SUCCESS")
            return True
        except subprocess.CalledProcessError as e:
            self.kernel.write_to_log(f"FAILED to install local dependencies for '{component_name}'. Pip Error: {e.stderr.decode('utf-8', 'ignore')}", "CRITICAL")
            return False
        except Exception as e:
            self.kernel.write_to_log(f"An unexpected error occurred during local dependency installation for '{component_name}': {e}", "CRITICAL")
            return False

    def get_config_ui_class(self, trigger_id: str):
        trigger_data = self.loaded_triggers.get(trigger_id)
        if trigger_data:
            return trigger_data.get("config_ui_class")
        return None
    def start_all_listeners(self, event_data=None): # (MODIFIED) Now accepts optional event_data
        self.kernel.write_to_log("TriggerManager: Starting all listeners and scheduling rules...", "INFO")
        self.stop_all_listeners()
        scheduler_manager = self.kernel.get_service("scheduler_manager_service")
        if scheduler_manager and scheduler_manager.scheduler.running:
            scheduler_manager.scheduler.remove_all_jobs()
        state_manager = self.kernel.get_service("state_manager")
        rules = state_manager.get("trigger_rules", {}) if state_manager else {}
        for rule_id, rule_data in rules.items():
            if not rule_data.get("is_enabled", False):
                continue
            trigger_id = rule_data.get("trigger_id")
            if trigger_id == 'cron_trigger':
                if scheduler_manager:
                    scheduler_manager.schedule_rule(rule_id, rule_data)
            else:
                trigger_info = self.loaded_triggers.get(trigger_id)
                if not trigger_info: continue
                TriggerClass = trigger_info.get("class")
                if not TriggerClass: continue
                try:
                    config = rule_data.get("config", {})
                    services_to_inject = {
                        "kernel": self.kernel,
                        "loc": self.loc,
                        "state_manager": state_manager,
                        "event_bus": self.kernel.get_service("event_bus"),
                        "logger": self.kernel.write_to_log
                    }
                    listener_instance = TriggerClass(trigger_id=trigger_id, config=config, services=services_to_inject, rule_id=rule_id)
                    listener_instance.set_callback(self._handle_event)
                    listener_instance.start()
                    self.active_listeners.append(listener_instance)
                except Exception as e:
                    self.kernel.write_to_log(f"Failed to start listener for rule '{rule_data.get('name')}': {e}", "ERROR")
    def stop_all_listeners(self):
        if not self.active_listeners:
            return
        for listener in self.active_listeners:
            try:
                listener.stop()
            except Exception as e:
                self.kernel.write_to_log(f"Error while stopping listener for trigger '{listener.trigger_id}': {e}", "ERROR")
        self.active_listeners.clear()
    def _handle_event(self, event_data: dict):
        rule_id = event_data.get("rule_id")
        state_manager = self.kernel.get_service("state_manager")
        if not rule_id or not state_manager: return
        rules = state_manager.get("trigger_rules", {})
        rule_data = rules.get(rule_id)
        if not rule_data: return
        preset_to_run = rule_data.get("preset_to_run")
        if not preset_to_run: return
        self.kernel.write_to_log(f"TRIGGER DETECTED! Rule '{rule_data.get('name')}' met. Scheduling execution for preset '{preset_to_run}'.", "SUCCESS")
        initial_payload = {
            "data": {
                "trigger_type": "event",
                "trigger_rule_id": rule_id,
                "trigger_rule_name": rule_data.get('name'),
                "trigger_event_data": event_data
            },
            "history": []
        }
        api_service = self.kernel.get_service("api_server_service")
        if api_service:
            api_service.trigger_workflow_by_api(preset_name=preset_to_run, initial_payload=initial_payload)
    def install_component(self, zip_filepath: str) -> (bool, str):
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                component_root_path = None
                if os.path.exists(os.path.join(temp_dir, 'manifest.json')):
                    component_root_path = temp_dir
                else:
                    dir_items = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
                    if len(dir_items) == 1:
                        potential_path = os.path.join(temp_dir, dir_items[0])
                        if os.path.exists(os.path.join(potential_path, 'manifest.json')):
                            component_root_path = potential_path
                if not component_root_path:
                    return False, "manifest.json not found in the root of the zip archive or in a single subdirectory."
                with open(os.path.join(component_root_path, 'manifest.json'), 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                required_tier = manifest.get('tier', 'free')
                if not self.kernel.is_tier_sufficient(required_tier):
                    error_msg = f"Installation failed. This trigger requires a '{required_tier.capitalize()}' license."
                    return False, error_msg
                component_id = manifest.get('id')
                if not component_id:
                    return False, "Component 'id' is missing from manifest.json."
                final_path = os.path.join(self.triggers_dir, component_id)
                if os.path.exists(final_path):
                    return False, f"Trigger '{component_id}' is already installed."
                shutil.move(component_root_path, final_path)
                return True, f"Trigger '{manifest.get('name', component_id)}' installed successfully."
            except Exception as e:
                return False, f"An error occurred during trigger installation: {e}"
    def uninstall_component(self, component_id: str) -> (bool, str):
        if component_id not in self.loaded_triggers:
            return False, f"Trigger '{component_id}' is not currently loaded or does not exist."
        component_path = self.loaded_triggers[component_id].get('path')
        if not component_path or not os.path.isdir(component_path):
            return False, f"Path for trigger '{component_id}' not found."
        try:
            shutil.rmtree(component_path)
            del self.loaded_triggers[component_id]
            return True, f"Trigger '{component_id}' uninstalled successfully."
        except Exception as e:
            return False, f"Could not delete trigger folder: {e}"