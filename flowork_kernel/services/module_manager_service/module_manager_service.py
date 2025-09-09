#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\services\module_manager_service\module_manager_service.py
# JUMLAH BARIS : 287
#######################################################################

import os
import json
import importlib.util
import subprocess
import sys
import traceback
from flowork_kernel.api_contract import BaseModule
from importlib.machinery import ExtensionFileLoader
from ..base_service import BaseService
import zipfile
import tempfile
import shutil
from flowork_kernel.exceptions import PermissionDeniedError
import hashlib
class ModuleManagerService(BaseService):
    """
    (REMASTERED V6) Manages modules and now supports hybrid loading of source (.py)
    and compiled (.module.flowork) files.
    """
    def __init__(self, kernel, service_id: str):
        super().__init__(kernel, service_id)
        self.modules_dir = self.kernel.modules_path
        self.loaded_modules = {}
        self.instance_cache = {}
        self.paused_status_file = os.path.join(self.kernel.data_path, 'paused_modules.json')
        self._manual_approval_callbacks = {}
        self.logger("Service 'ModuleManager' initialized.", "DEBUG") # English Log
    def discover_and_load_modules(self):
        self.logger("ModuleManager: Starting discovery and loading...", "INFO") # English Log
        auto_compiler = self.kernel.get_service("auto_compiler_service")
        if auto_compiler and self.kernel.is_dev_mode:
            auto_compiler.initial_scan()
        self.loaded_modules.clear()
        self.instance_cache.clear()
        paused_ids = self._load_paused_status()
        if not os.path.exists(self.modules_dir):
            self.logger(f"Modules directory not found at {self.modules_dir}, skipping.", "WARN") # English Log
            return
        for item_id in os.listdir(self.modules_dir):
            item_dir = os.path.join(self.modules_dir, item_id)
            if os.path.isdir(item_dir) and item_id != '__pycache__':
                manifest_path = os.path.join(item_dir, "manifest.json")
                if not os.path.exists(manifest_path): continue
                try:
                    with open(manifest_path, 'r', encoding='utf-8') as f:
                        manifest = json.load(f)
                    if manifest.get("type") not in ["ACTION", "LOGIC", "CONTROL_FLOW"]:
                        continue
                    self._install_dependencies_locally(item_dir, manifest.get('name', item_id))
                    is_paused = item_id in paused_ids
                    module_data = {
                        "manifest": manifest, "path": item_dir,
                        "installed_as": "module", "is_paused": is_paused,
                        "permissions": manifest.get("permissions", []),
                        "tier": manifest.get('tier', 'free').lower()
                    }
                    self.loaded_modules[item_id] = module_data
                except Exception as e:
                    self.logger(f"   ! Failed to process manifest for module '{item_id}': {e}", "WARN") # English Log
        var_manager = self.kernel.get_service("variable_manager_service")
        if var_manager:
            var_manager.autodiscover_and_sync_variables()
        self.logger(f"ModuleManager: Discovery complete. Found {len(self.loaded_modules)} modules.", "INFO") # English Log
    def get_instance(self, module_id):
        if module_id in self.instance_cache:
            return self.instance_cache[module_id]
        if module_id not in self.loaded_modules:
            self.logger(f"Attempted to get instance for unknown module_id: {module_id}", "ERROR") # English Log
            return None
        module_data = self.loaded_modules[module_id]
        if module_data.get("is_paused", False):
            return None
        self.logger(f"Just-In-Time Load: Instantiating '{module_id}' for the first time.", "DEBUG") # English Log
        vendor_path = os.path.join(module_data["path"], 'vendor')
        is_path_added = False
        try:
            if os.path.isdir(vendor_path):
                if vendor_path not in sys.path:
                    sys.path.insert(0, vendor_path)
                    is_path_added = True
            manifest = module_data["manifest"]
            entry_point = manifest.get("entry_point")
            if not entry_point: raise ValueError(f"'entry_point' not found for '{module_id}'.")
            module_filename, class_name = entry_point.split('.')
            source_file_path = os.path.join(module_data["path"], f"{module_filename}.py")
            native_file_path = os.path.join(module_data["path"], f"{module_filename}.module.flowork")
            path_to_load = None
            is_native_module = False
            if os.path.exists(native_file_path):
                path_to_load = native_file_path
                is_native_module = True
                self.logger(f"  -> Found compiled native file for module '{module_id}'. Prioritizing it.", "DEBUG") # English Log
            elif os.path.exists(source_file_path):
                path_to_load = source_file_path
            if not path_to_load:
                 raise FileNotFoundError(f"Entry point file not found for '{module_id}'.")
            safe_module_id = module_id.replace('-', '_')
            parent_package_name = f"modules.{safe_module_id}"
            if is_native_module:
                module_full_name = f"{parent_package_name}.{module_filename}"
                loader = ExtensionFileLoader(module_full_name, path_to_load)
                spec = importlib.util.spec_from_loader(loader.name, loader)
            else:
                module_full_name = f"{parent_package_name}.{module_filename}"
                spec = importlib.util.spec_from_file_location(module_full_name, path_to_load)
            if spec is None: raise ImportError(f"Could not create module spec from {path_to_load}")
            module_lib = importlib.util.module_from_spec(spec)
            if parent_package_name not in sys.modules:
                if "modules" not in sys.modules:
                    spec_base = importlib.util.spec_from_loader("modules", loader=None, is_package=True)
                    module_base = importlib.util.module_from_spec(spec_base)
                    sys.modules["modules"] = module_base
                spec_parent = importlib.util.spec_from_loader(parent_package_name, loader=None, is_package=True)
                module_parent = importlib.util.module_from_spec(spec_parent)
                module_parent.__path__ = [module_data["path"]]
                sys.modules[parent_package_name] = module_parent
            sys.modules[module_full_name] = module_lib
            spec.loader.exec_module(module_lib)
            ProcessorClass = getattr(module_lib, class_name)
            services_to_inject = {}
            requested_services = manifest.get("requires_services", [])
            for service_alias in requested_services:
                if service_alias == "loc": services_to_inject['loc'] = self.kernel.get_service("localization_manager")
                elif service_alias == "logger": services_to_inject['logger'] = self.kernel.write_to_log
                elif service_alias == "kernel": services_to_inject['kernel'] = self.kernel
                else:
                    service_instance = self.kernel.get_service(service_alias)
                    if service_instance: services_to_inject[service_alias] = service_instance
            module_instance = ProcessorClass(module_id, services_to_inject)
            if hasattr(module_instance, 'on_load'):
                module_instance.on_load()
            self.instance_cache[module_id] = module_instance
            self.loaded_modules[module_id]['instance'] = module_instance
            return module_instance
        except PermissionDeniedError as e:
            self.logger(f"Skipping instantiation of '{module_id}' due to insufficient permissions: {e}", "WARN") # English Log
            return None
        except Exception as e:
            self.logger(f"CRITICAL FAILURE during Just-In-Time instantiation of '{module_id}': {e}", "CRITICAL") # English Log
            self.logger(traceback.format_exc(), "DEBUG")
            return None
        finally:
            if is_path_added:
                try:
                    sys.path.remove(vendor_path)
                except ValueError:
                    pass
    def _calculate_requirements_hash(self, file_path):
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except IOError:
            return None
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
        self.logger(f"'{component_name}' has outdated or missing local dependencies. Installing...", "INFO") # English Log
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
            return True
        except Exception as e:
            self.logger(f"FAILED to install local dependencies for '{component_name}': {e}", "CRITICAL") # English Log
            return False
    def get_manifest(self, module_id):
        return self.loaded_modules.get(module_id, {}).get("manifest")
    def get_module_permissions(self, module_id):
        return self.loaded_modules.get(module_id, {}).get("permissions", [])
    def get_module_tier(self, module_id):
        return self.loaded_modules.get(module_id, {}).get("tier", "free")
    def _load_paused_status(self):
        if os.path.exists(self.paused_status_file):
            try:
                with open(self.paused_status_file, 'r') as f: return json.load(f)
            except (json.JSONDecodeError, IOError): return []
        return []
    def _save_paused_status(self):
        paused_ids = [mid for mid, data in self.loaded_modules.items() if data.get("is_paused")]
        try:
            with open(self.paused_status_file, 'w') as f: json.dump(paused_ids, f, indent=4)
        except IOError as e:
            self.kernel.write_to_log(f"Failed to save paused status: {e}", "ERROR") # English Log
    def set_module_paused(self, module_id, is_paused):
        if module_id in self.loaded_modules:
            instance = self.instance_cache.get(module_id)
            if is_paused and instance:
                if hasattr(instance, 'on_unload'):
                    instance.on_unload()
                del self.instance_cache[module_id]
            self.loaded_modules[module_id]["is_paused"] = is_paused
            self._save_paused_status()
            return True
        return False
    def register_approval_callback(self, module_id, callback):
        self._manual_approval_callbacks[module_id] = callback
    def notify_approval_response(self, module_id: str, result: str):
        if module_id in self._manual_approval_callbacks:
            callback = self._manual_approval_callbacks.pop(module_id)
            if callable(callback):
                threading.Thread(target=callback, args=(result,)).start()
        else:
            self.logger(f"Received approval response for an unknown or timed-out module: '{module_id}'.", "WARN") # English Log
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
                    error_msg = f"Installation failed. This component requires a '{required_tier.capitalize()}' license or higher. Your current tier is '{self.kernel.license_tier.capitalize()}'."
                    self.kernel.write_to_log(error_msg, "ERROR") # English Log
                    return False, error_msg
                component_id = manifest.get('id')
                if not component_id:
                    return False, "Component 'id' is missing from manifest.json."
                final_path = os.path.join(self.modules_dir, component_id)
                if os.path.exists(final_path):
                    return False, f"Component '{component_id}' is already installed."
                shutil.move(component_root_path, final_path)
                self.kernel.write_to_log(f"Component '{component_id}' installed successfully to '{self.modules_dir}'.", "SUCCESS") # English Log
                return True, f"Component '{manifest.get('name', component_id)}' installed successfully."
            except Exception as e:
                self.kernel.write_to_log(f"Installation failed: {e}", "ERROR") # English Log
                return False, f"An error occurred during installation: {e}"
    def uninstall_component(self, component_id: str) -> (bool, str):
        if component_id not in self.loaded_modules:
            return False, f"Component '{component_id}' is not currently loaded or does not exist."
        component_data = self.loaded_modules[component_id]
        component_path = component_data.get('path')
        if not component_path or not os.path.isdir(component_path):
            return False, f"Path for component '{component_id}' not found or is invalid."
        try:
            shutil.rmtree(component_path)
            del self.loaded_modules[component_id]
            if component_id in self.instance_cache:
                del self.instance_cache[component_id]
            self.kernel.write_to_log(f"Component '{component_id}' folder deleted successfully.", "SUCCESS") # English Log
            return True, f"Component '{component_id}' uninstalled. A restart is required to fully clear it."
        except Exception as e:
            self.kernel.write_to_log(f"Failed to delete component folder '{component_path}': {e}", "ERROR") # English Log
            return False, f"Could not delete component folder: {e}"
