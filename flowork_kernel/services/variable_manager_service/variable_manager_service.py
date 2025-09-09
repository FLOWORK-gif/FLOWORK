#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\services\variable_manager_service\variable_manager_service.py
# JUMLAH BARIS : 233
#######################################################################

import os
import json
import threading
import base64
import logging
import secrets
import string
import random
from ..base_service import BaseService
from flowork_kernel.exceptions import PermissionDeniedError
class VariableManagerService(BaseService):
    """
    Acts as a secure vault for all global and secret variables.
    [MODIFIED V8] Now auto-creates default Supabase variables.
    """
    VARIABLES_FILENAME = "variables.json"
    def __init__(self, kernel, service_id: str):
        super().__init__(kernel, service_id)
        self.variables_file_path = os.path.join(self.kernel.data_path, self.VARIABLES_FILENAME)
        self._variables_data = {}
        self._lock = threading.Lock()
        self.kernel.write_to_log("Service 'VariableManager' initialized.", "DEBUG") # English Log
        self.load_variables()
    def autodiscover_and_sync_variables(self):
        self.logger("VariableManager: Starting autodiscovery of required variables...", "INFO") # English Log
        all_components = {}
        try:
            module_manager = self.kernel.get_service("module_manager_service")
            if module_manager: all_components.update(module_manager.loaded_modules)
        except PermissionDeniedError:
            self.logger("VariableManager: Could not access ModuleManager due to permissions. Skipping.", "WARN") # English Log
        try:
            widget_manager = self.kernel.get_service("widget_manager_service")
            if widget_manager: all_components.update(widget_manager.loaded_widgets)
        except PermissionDeniedError:
            self.logger("VariableManager: Could not access WidgetManager due to permissions. Skipping.", "WARN") # English Log
        try:
            ai_provider_manager = self.kernel.get_service("ai_provider_manager_service")
            if ai_provider_manager:
                ai_providers_components = {}
                if hasattr(ai_provider_manager, 'loaded_providers'):
                    for pid, provider_instance in ai_provider_manager.loaded_providers.items():
                        if hasattr(provider_instance, 'get_manifest'):
                            ai_providers_components[pid] = {"manifest": provider_instance.get_manifest()}
                all_components.update(ai_providers_components)
        except PermissionDeniedError:
             self.logger("VariableManager: Could not access AIProviderManager due to permissions. Skipping its variables.", "WARN") # English Log
        found_new = False
        with self._lock:
            for component_id, data in all_components.items():
                manifest = data.get("manifest", {})
                required_vars = manifest.get("requires_variables", [])
                for var_info in required_vars:
                    var_name = var_info.get("name")
                    if var_name and var_name not in self._variables_data:
                        self.logger(f"  -> Discovered new required variable '{var_name}' from component '{component_id}'. Adding to list.", "INFO") # English Log
                        self._variables_data[var_name] = {
                            "value": "PLEASE_EDIT_ME",
                            "values": [],
                            "mode": "single",
                            "is_secret": var_info.get("is_secret", False),
                            "is_enabled": True,
                            "sequential_index": 0
                        }
                        found_new = True
        if found_new:
            self._save_variables_to_file()
            self.logger("VariableManager: Autodiscovery complete. New variables have been saved.", "SUCCESS") # English Log
        else:
            self.logger("VariableManager: Autodiscovery complete. No new variables needed.", "INFO") # English Log
    def load_variables(self):
        with self._lock:
            requires_save = False
            try:
                if os.path.exists(self.variables_file_path):
                    with open(self.variables_file_path, 'r', encoding='utf-8') as f:
                        self._variables_data = json.load(f)
                else:
                    self._variables_data = {}
                default_vars = {
                    "FLOWORK_API_KEY": {
                        "value_generator": lambda: ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(10)),
                        "is_secret": False
                    },
                    "SUPABASE_URL": {
                        "value_generator": lambda: "https://kmzumshczfkmcijxllps.supabase.co",
                        "is_secret": False
                    },
                    "SUPABASE_KEY": {
                        "value_generator": lambda: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImttenVtc2hjemZrbWNpanhsbHBzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTYxMzI3MjAsImV4cCI6MjA3MTcwODcyMH0.QN1tKaXEo9shGQjU8cKiRAiGJSQTHLtC4ifozV3Qs10",
                        "is_secret": True # Kita anggap secret agar bisa disembunyikan di UI
                    }
                }
                for var_name, var_details in default_vars.items():
                    if var_name not in self._variables_data:
                        self.kernel.write_to_log(f"'{var_name}' not found. Generating a new default value.", "WARN") # English Log
                        self._variables_data[var_name] = {
                            "value": var_details["value_generator"](),
                            "values": [],
                            "mode": "single",
                            "is_secret": var_details["is_secret"],
                            "is_enabled": True,
                            "sequential_index": 0
                        }
                        requires_save = True
                for name, data in self._variables_data.items():
                    if 'mode' not in data: data['mode'] = 'single'; requires_save = True
                    if 'values' not in data: data['values'] = []; requires_save = True
                    if 'sequential_index' not in data: data['sequential_index'] = 0; requires_save = True
            except (IOError, json.JSONDecodeError) as e:
                self.kernel.write_to_log(f"VariableManager: Failed to load variables from file: {e}. Using empty state.", "ERROR") # English Log
                self._variables_data = {}
                requires_save = True # Force creation of defaults
            if requires_save:
                self._save_variables_to_file()
    def _save_variables_to_file(self):
        try:
            with open(self.variables_file_path, 'w', encoding='utf-8') as f:
                json.dump(self._variables_data, f, indent=4)
        except IOError as e:
            self.kernel.write_to_log(f"VariableManager: Failed to save variables to file: {e}", "ERROR") # English Log
    def get_all_variables_for_api(self):
        with self._lock:
            api_safe_vars = json.loads(json.dumps(self._variables_data))
            for name, data in api_safe_vars.items():
                if data.get('is_secret'):
                    if data.get('mode', 'single') == 'single':
                        data['value'] = ""
                    else:
                        data['values'] = []
            return [dict(data, **{'name': name}) for name, data in sorted(api_safe_vars.items())]
    def get_all_variables_for_ui(self):
        api_data = self.get_all_variables_for_api()
        ui_list = []
        for var_data in api_data:
            value_for_display = ""
            if var_data.get('mode', 'single') != 'single':
                value_for_display = f"[Pool: {len(var_data.get('values', []))} keys] - Mode: {var_data.get('mode', '').capitalize()}"
            elif var_data.get('is_secret'):
                value_for_display = '*****'
            else:
                value_for_display = var_data.get('value')
            ui_list.append({
                "name": var_data["name"],
                "value": value_for_display,
                "is_secret": var_data.get('is_secret', False),
                "is_enabled": var_data.get('is_enabled', True),
            })
        return ui_list
    def get_variable(self, name):
        with self._lock:
            var_data = self._variables_data.get(name)
            if not var_data or not var_data.get('is_enabled', True):
                return None
            mode = var_data.get('mode', 'single')
            value_to_return = None
            if mode == 'single':
                value_to_return = var_data.get('value')
            elif mode in ['random', 'sequential']:
                values_list = var_data.get('values', [])
                if not values_list:
                    return None
                if mode == 'random':
                    value_to_return = random.choice(values_list)
                elif mode == 'sequential':
                    current_index = var_data.get('sequential_index', 0)
                    value_to_return = values_list[current_index]
                    var_data['sequential_index'] = (current_index + 1) % len(values_list)
                    self._save_variables_to_file() # (IMPORTANT) Save the new index state
            if var_data.get('is_secret') and value_to_return:
                try:
                    decoded_bytes = base64.b64decode(str(value_to_return).encode('utf-8'))
                    return decoded_bytes.decode('utf-8')
                except Exception:
                    return None
            else:
                return value_to_return
    def set_variable(self, name, value, is_secret, is_enabled=True, mode='single'):
        if not name.isupper() or not name.replace('_', '').isalnum():
             raise ValueError("Variable name must only contain uppercase letters (A-Z), numbers (0-9), and underscores (_).")
        with self._lock:
            if mode == 'single':
                processed_value = value
                if is_secret and value and value != "PLEASE_EDIT_ME":
                    processed_value = base64.b64encode(str(value).encode('utf-8')).decode('utf-8')
                self._variables_data[name] = {
                    "value": processed_value,
                    "values": [],
                    "mode": "single",
                    "is_secret": is_secret,
                    "is_enabled": is_enabled,
                    "sequential_index": 0
                }
            else:
                if not isinstance(value, list):
                    raise ValueError("Value for a pooled variable must be a list of strings.")
                processed_values = []
                if is_secret:
                    for val in value:
                        if val: processed_values.append(base64.b64encode(str(val).encode('utf-8')).decode('utf-8'))
                else:
                    processed_values = value
                self._variables_data[name] = {
                    "value": None,
                    "values": processed_values,
                    "mode": mode,
                    "is_secret": is_secret,
                    "is_enabled": is_enabled,
                    "sequential_index": 0
                }
            self._save_variables_to_file()
    def set_variable_enabled_state(self, name, is_enabled: bool):
        with self._lock:
            if name in self._variables_data:
                self._variables_data[name]['is_enabled'] = is_enabled
                self._save_variables_to_file()
                return True
            return False
    def delete_variable(self, name):
        with self._lock:
            if name in self._variables_data:
                del self._variables_data[name]
                self._save_variables_to_file()
                return True
            else:
                return False
