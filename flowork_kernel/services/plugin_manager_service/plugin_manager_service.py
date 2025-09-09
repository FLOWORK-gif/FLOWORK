#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\services\plugin_manager_service\plugin_manager_service.py
# JUMLAH BARIS : 234
#######################################################################

import os
import json
import importlib.util
import subprocess
import sys
import traceback
from flowork_kernel.api_contract import BaseUIProvider, BaseModule
from importlib.machinery import ExtensionFileLoader
from ..base_service import BaseService
import zipfile
import tempfile
import shutil
import hashlib
from flowork_kernel.exceptions import PermissionDeniedError
class PluginManagerService(BaseService):
    """
    Manages the discovery, loading, and access to all plugins (UI Providers, Services).
    (MODIFIED) Now supports hybrid loading of source (.py) and compiled (.plugin.flowork) files.
    """
    def __init__(self, kernel, service_id: str):
        super().__init__(kernel, service_id)
        self.plugins_dir = self.kernel.plugins_path
        self.system_plugins_dir = self.kernel.system_plugins_path
        self.loaded_plugins = {}
        self.instance_cache = {}
        self.paused_status_file = os.path.join(self.kernel.data_path, 'paused_plugins.json')
        self.logger(f"Service 'PluginManagerService' initialized.", "DEBUG") # English Log
    def discover_and_load_plugins(self):
        self.logger("PluginManager: Starting discovery and loading...", "INFO") # English Log
        auto_compiler = self.kernel.get_service("auto_compiler_service")
        if auto_compiler and self.kernel.is_dev_mode:
            auto_compiler.initial_scan()
        self.loaded_plugins.clear()
        self.instance_cache.clear()
        paused_ids = self._load_paused_status()
        paths_to_scan = [
            (self.plugins_dir, "plugin")
        ]
        for base_path, base_type in paths_to_scan:
            if not os.path.exists(base_path): continue
            for item_id in os.listdir(base_path):
                item_dir = os.path.join(base_path, item_id)
                if os.path.isdir(item_dir) and item_id != '__pycache__':
                    manifest_path = os.path.join(item_dir, "manifest.json")
                    if not os.path.exists(manifest_path): continue
                    self.logger(f"[MATA-MATA] PluginManager: Found potential plugin '{item_id}'. Reading manifest...", "DEBUG") # English Log
                    try:
                        with open(manifest_path, 'r', encoding='utf-8') as f:
                            manifest = json.load(f)
                        if manifest.get("type") not in ["PLUGIN", "SERVICE"]:
                            continue
                        self.logger(f"[MATA-MATA] PluginManager: Manifest for '{item_id}' is valid. Type: {manifest.get('type')}", "INFO") # English Log
                        self._install_dependencies_locally(item_dir, manifest.get('name', item_id))
                        is_paused = item_id in paused_ids
                        is_ui_provider = "ui_provider" in manifest.get("permissions", [])
                        is_service_plugin = manifest.get("is_service", False)
                        module_data = {
                            "manifest": manifest, "path": item_dir,
                            "installed_as": base_type, "is_paused": is_paused,
                            "permissions": manifest.get("permissions", []),
                            "tier": manifest.get('tier', 'free').lower()
                        }
                        self.loaded_plugins[item_id] = module_data
                        if not is_paused and (is_ui_provider or is_service_plugin):
                            self.logger(f"[MATA-MATA] Eager Load: Attempting to instantiate critical plugin '{item_id}' now.", "WARN") # English Log
                            self.get_instance(item_id)
                    except Exception as e:
                        self.logger(f"   ! Failed to process manifest for plugin '{item_id}': {e}", "WARN") # English Log
        self.logger(f"PluginManager: Discovery complete. Found {len(self.loaded_plugins)} plugins.", "INFO") # English Log
    def get_instance(self, plugin_id):
        self.logger(f"[MATA-MATA] get_instance called for plugin_id: '{plugin_id}'", "DEBUG") # English Log
        if plugin_id in self.instance_cache:
            return self.instance_cache[plugin_id]
        if plugin_id not in self.loaded_plugins:
            self.logger(f"Attempted to get instance for unknown plugin_id: {plugin_id}", "ERROR") # English Log
            return None
        plugin_data = self.loaded_plugins[plugin_id]
        if plugin_data.get("is_paused", False):
            return None
        self.logger(f"Just-In-Time Load: Instantiating plugin '{plugin_id}' for the first time.", "DEBUG") # English Log
        vendor_path = os.path.join(plugin_data["path"], 'vendor')
        is_path_added = False
        try:
            if os.path.isdir(vendor_path):
                if vendor_path not in sys.path:
                    sys.path.insert(0, vendor_path)
                    is_path_added = True
            manifest = plugin_data["manifest"]
            entry_point = manifest.get("entry_point")
            if not entry_point: raise ValueError(f"'entry_point' not found for '{plugin_id}'.")
            module_filename, class_name = entry_point.split('.')
            source_file_path = os.path.join(plugin_data["path"], f"{module_filename}.py")
            native_file_path = os.path.join(plugin_data["path"], f"{module_filename}.plugin.flowork")
            path_to_load = None
            is_native_module = False
            if os.path.exists(native_file_path):
                path_to_load = native_file_path
                is_native_module = True
                self.logger(f"  -> Found compiled native file for plugin '{plugin_id}'. Prioritizing it.", "DEBUG") # English Log
            elif os.path.exists(source_file_path):
                path_to_load = source_file_path
            if not path_to_load:
                 raise FileNotFoundError(f"Entry point file not found for '{plugin_id}'.")
            safe_plugin_id = plugin_id.replace('-', '_')
            base_folder = os.path.basename(os.path.dirname(plugin_data["path"]))
            parent_package_name = f"{base_folder}.{safe_plugin_id}"
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
                if base_folder not in sys.modules:
                    spec_base = importlib.util.spec_from_loader(base_folder, loader=None, is_package=True)
                    module_base = importlib.util.module_from_spec(spec_base)
                    sys.modules[base_folder] = module_base
                spec_parent = importlib.util.spec_from_loader(parent_package_name, loader=None, is_package=True)
                module_parent = importlib.util.module_from_spec(spec_parent)
                module_parent.__path__ = [plugin_data["path"]]
                sys.modules[parent_package_name] = module_parent
            sys.modules[module_full_name] = module_lib
            self.logger(f"[MATA-MATA] Executing module '{module_full_name}' for plugin '{plugin_id}'...", "DEBUG") # English Log
            spec.loader.exec_module(module_lib)
            self.logger(f"[MATA-MATA] Module execution successful for '{plugin_id}'.", "SUCCESS") # English Log
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
            self.logger(f"[MATA-MATA] Initializing class '{class_name}' for plugin '{plugin_id}'...", "DEBUG") # English Log
            plugin_instance = ProcessorClass(plugin_id, services_to_inject)
            self.logger(f"[MATA-MATA] Class initialization successful for '{plugin_id}'.", "SUCCESS") # English Log
            if hasattr(plugin_instance, 'on_load'):
                plugin_instance.on_load()
            self.instance_cache[plugin_id] = plugin_instance
            self.loaded_plugins[plugin_id]['instance'] = plugin_instance
            return plugin_instance
        except PermissionDeniedError as e:
            self.logger(f"Skipping instantiation of plugin '{plugin_id}' due to insufficient permissions: {e}", "WARN") # English Log
            return None
        except Exception as e:
            self.logger(f"CRITICAL FAILURE during Just-In-Time instantiation of plugin '{plugin_id}': {e}", "CRITICAL") # English Log
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
        self.logger(f"Plugin '{component_name}' has outdated or missing local dependencies. Installing...", "INFO") # English Log
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
            self.logger(f"FAILED to install local dependencies for plugin '{component_name}': {e}", "CRITICAL") # English Log
            return False
    def get_manifest(self, plugin_id):
        return self.loaded_plugins.get(plugin_id, {}).get("manifest")
    def _load_paused_status(self):
        if os.path.exists(self.paused_status_file):
            try:
                with open(self.paused_status_file, 'r') as f: return json.load(f)
            except (json.JSONDecodeError, IOError): return []
        return []
    def _save_paused_status(self):
        paused_ids = [pid for pid, data in self.loaded_plugins.items() if data.get("is_paused")]
        try:
            with open(self.paused_status_file, 'w') as f: json.dump(paused_ids, f, indent=4)
        except IOError as e:
            self.kernel.write_to_log(f"Failed to save plugin paused status: {e}", "ERROR") # English Log
    def set_plugin_paused(self, plugin_id, is_paused):
        if plugin_id in self.loaded_plugins:
            instance = self.instance_cache.get(plugin_id)
            if is_paused and instance:
                if hasattr(instance, 'on_unload'):
                    instance.on_unload()
                del self.instance_cache[plugin_id]
            self.loaded_plugins[plugin_id]["is_paused"] = is_paused
            self._save_paused_status()
            return True
        return False
