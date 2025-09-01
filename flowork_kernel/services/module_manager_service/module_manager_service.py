#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\services\module_manager_service\module_manager_service.py
# (Full code for the fixed file)
# [FIXED V3] Added intermediate virtual package creation to solve relative import errors.
#######################################################################

import os
import json
import importlib.util
import subprocess
import sys
import traceback
from flowork_kernel.api_contract import BaseUIProvider, BaseModule
import importlib.metadata
from importlib.machinery import ExtensionFileLoader
# COMMENT: py_compile is not used in this version of the file, commenting out.
# import py_compile
from ..base_service import BaseService
import threading
import zipfile
import tempfile
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from flowork_kernel.exceptions import PermissionDeniedError
# (COMMENT) build_security is no longer needed for signature verification.
# from flowork_kernel.core import build_security
import hashlib # [ADDED] For fingerprinting/stamping

class ComponentInstallHandler(FileSystemEventHandler):
    # (UNCHANGED) This class remains the same.
    def __init__(self, service_instance):
        self.service = service_instance
    def on_created(self, event):
        if event.is_directory:
            self.service.kernel.write_to_log(f"Watchdog: New component detected at {event.src_path}", "INFO") # English Log
            if self.service.kernel.root:
                self.service.kernel.root.after(500, self.service.kernel.hot_reload_components)

class ModuleManagerService(BaseService):
    """
    (REMASTERED V4) Manages the discovery, loading, and access to all modules and plugins.
    Now supports LOCALIZED DEPENDENCY INSTALLATION for true modularity.
    """
    def __init__(self, kernel, service_id: str):
        super().__init__(kernel, service_id)
        self.modules_dir = self.kernel.modules_path
        self.plugins_dir = self.kernel.plugins_path
        self.system_plugins_dir = self.kernel.system_plugins_path
        self.loaded_modules = {}
        self.instance_cache = {}
        self.paused_status_file = os.path.join(self.kernel.data_path, 'paused_modules.json')
        self._manual_approval_callbacks = {}
        self.observer = Observer()

        # (COMMENT) The virtual package creation is good for source .py files, but causes issues for compiled files.
        # We will adjust the loading logic instead of removing this.
        if "flowork_native_module" not in sys.modules:
            spec = importlib.util.spec_from_loader("flowork_native_module", loader=None, is_package=True)
            module = importlib.util.module_from_spec(spec)
            sys.modules["flowork_native_module"] = module
            spec_widget = importlib.util.spec_from_loader("flowork_native_widget", loader=None, is_package=True)
            module_widget = importlib.util.module_from_spec(spec_widget)
            sys.modules["flowork_native_widget"] = module_widget
            spec_trigger = importlib.util.spec_from_loader("flowork_native_trigger", loader=None, is_package=True)
            module_trigger = importlib.util.module_from_spec(spec_trigger)
            sys.modules["flowork_native_trigger"] = module_trigger
            self.logger("Created virtual namespaces for native components.", "DEBUG") # English Log

        self.logger("Service 'ModuleManager' initialized.", "DEBUG") # English Log


    # (UNCHANGED) start() and stop() for the watchdog
    def start(self):
        # ... (kode tidak berubah)
        event_handler = ComponentInstallHandler(self)
        paths_to_watch = [
            self.modules_dir,
            self.plugins_dir,
            self.kernel.widgets_path,
            self.kernel.triggers_path,
            self.kernel.ai_providers_path
        ]
        for path in paths_to_watch:
            if os.path.isdir(path):
                self.observer.schedule(event_handler, path, recursive=False)
        self.observer.start()
        self.logger("ModuleManager Watchdog has started monitoring component folders.", "INFO") # English Log
    def stop(self):
        # ... (kode tidak berubah)
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
        self.logger("ModuleManager Watchdog has stopped.", "INFO") # English Log

    # (UNCHANGED) Approval logic remains the same
    def register_approval_callback(self, module_id, callback):
        # ... (kode tidak berubah)
        self._manual_approval_callbacks[module_id] = callback
    def notify_approval_response(self, module_id: str, result: str):
        # ... (kode tidak berubah)
        if module_id in self._manual_approval_callbacks:
            callback = self._manual_approval_callbacks.pop(module_id)
            if callable(callback):
                threading.Thread(target=callback, args=(result,)).start()
        else:
            self.logger(f"Received approval response for an unknown or timed-out module: '{module_id}'.", "WARN") # English Log

    def discover_and_load_modules(self):
        self.logger("ModuleManager: Starting HYBRID discovery and loading...", "INFO") # English Log

        # [MODIFIED] Call the initial scan from the compiler BEFORE loading anything.
        auto_compiler = self.kernel.get_service("auto_compiler_service")
        if auto_compiler and self.kernel.is_dev_mode:
            auto_compiler.initial_scan()

        self.loaded_modules.clear()
        self.instance_cache.clear()
        paused_ids = self._load_paused_status()
        paths_to_scan = [
            (self.system_plugins_dir, "system_plugin"),
            (self.plugins_dir, "plugin"),
            (self.modules_dir, "module")
        ]
        for base_path, base_type in paths_to_scan:
            if not os.path.exists(base_path): continue
            for item_id in os.listdir(base_path):
                item_dir = os.path.join(base_path, item_id)
                if os.path.isdir(item_dir) and item_id != '__pycache__':
                    manifest_path = os.path.join(item_dir, "manifest.json")
                    if not os.path.exists(manifest_path): continue
                    try:
                        with open(manifest_path, 'r', encoding='utf-8') as f:
                            manifest = json.load(f)

                        # (MODIFIED) Run local dependency installation during discovery
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
                        self.loaded_modules[item_id] = module_data
                        if not is_paused and (is_ui_provider or is_service_plugin):
                            self.logger(f"Eager Load: Instantiating critical plugin '{item_id}' at startup.", "DEBUG") # English Log
                            self.get_instance(item_id)
                    except Exception as e:
                        self.logger(f"   ! Failed to process manifest for '{item_id}': {e}", "WARN") # English Log

        var_manager = self.kernel.get_service("variable_manager_service")
        if var_manager:
            var_manager.autodiscover_and_sync_variables()
        self.logger(f"ModuleManager: Discovery complete. Found {len(self.loaded_modules)} modules/plugins.", "INFO") # English Log

    # [NEW] Helper function to calculate hash of requirements file for the stamp.
    def _calculate_requirements_hash(self, file_path):
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Read and update hash in chunks to handle large files
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except IOError:
            return None

    # [NEW] The intelligent, fingerprint-based dependency installer. The "Stempel" logic.
    def _install_dependencies_locally(self, component_path, component_name):
        requirements_path = os.path.join(component_path, 'requirements.txt')
        if not os.path.exists(requirements_path):
            return True # NOTE: Success, nothing to install.

        vendor_path = os.path.join(component_path, 'vendor')
        # NOTE: This is our "stempel" file.
        hash_file_path = os.path.join(component_path, '.vendor_hash')

        current_hash = self._calculate_requirements_hash(requirements_path)

        # NOTE: Check if a valid, up-to-date installation (stamp) already exists.
        if os.path.isdir(vendor_path) and os.path.exists(hash_file_path):
            try:
                with open(hash_file_path, 'r') as f:
                    saved_hash = f.read().strip()
                if saved_hash == current_hash:
                    # NOTE: Stamp is valid, skip installation.
                    return True
            except IOError:
                # NOTE: If hash file is unreadable for some reason, reinstall.
                pass

        self.logger(f"'{component_name}' has outdated or missing local dependencies. Installing/Updating...", "INFO") # English Log

        # NOTE: Clean up old installation before starting a new one.
        if os.path.isdir(vendor_path):
            shutil.rmtree(vendor_path, ignore_errors=True)

        try:
            python_exe = sys.executable
            command = [
                python_exe, "-m", "pip", "install", "--target", vendor_path,
                "-r", requirements_path, "--no-user", "--disable-pip-version-check"
            ]

            # NOTE: Ensure the pip install process runs silently without a console window.
            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = subprocess.CREATE_NO_WINDOW

            subprocess.run(command, check=True, capture_output=True, creationflags=creation_flags)

            # NOTE: Write the new hash file (the "stamp") on success.
            with open(hash_file_path, 'w') as f:
                f.write(current_hash)

            self.logger(f"Successfully installed local dependencies for '{component_name}'.", "SUCCESS") # English Log
            return True
        except subprocess.CalledProcessError as e:
            self.logger(f"FAILED to install local dependencies for '{component_name}'. Pip Error: {e.stderr.decode('utf-8', 'ignore')}", "CRITICAL") # English Log
            return False
        except Exception as e:
            self.logger(f"An unexpected error occurred during local dependency installation for '{component_name}': {e}", "CRITICAL") # English Log
            return False

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
                # NOTE: This is critical. Add the local vendor path to the system path TEMPORARILY.
                sys.path.insert(0, vendor_path)
                is_path_added = True
                self.logger(f"Temporarily adding '{vendor_path}' to sys.path for '{module_id}'.", "DEBUG") # English Log

            manifest = module_data["manifest"]
            entry_point = manifest.get("entry_point")
            if not entry_point: raise ValueError(f"'entry_point' not found for '{module_id}'.")

            module_filename, class_name = entry_point.split('.')
            native_file_path = os.path.join(module_data["path"], f"{module_filename}.aola_flowork")
            source_file_path = os.path.join(module_data["path"], f"{module_filename}.py")
            path_to_load = native_file_path if os.path.exists(native_file_path) else source_file_path
            is_native_module = path_to_load.endswith(".aola_flowork")

            if not os.path.exists(path_to_load): raise FileNotFoundError(f"Entry point file not found for '{module_id}'.")

            # (FIXED V4) Final fix for relative imports and PyInit errors.
            # We create a more specific virtual package name that includes the base folder (e.g., 'plugins').
            safe_module_id = module_id.replace('-', '_')
            base_folder = os.path.basename(os.path.dirname(module_data["path"])) # e.g., 'modules', 'plugins'

            if is_native_module:
                module_full_name = module_filename
            else:
                # Create a package like 'plugins.system_diagnostics_plugin'
                parent_package_name = f"{base_folder}.{safe_module_id}"
                if parent_package_name not in sys.modules:
                    # First, ensure the top-level package (e.g., 'plugins') exists
                    if base_folder not in sys.modules:
                        spec_base = importlib.util.spec_from_loader(base_folder, loader=None, is_package=True)
                        module_base = importlib.util.module_from_spec(spec_base)
                        sys.modules[base_folder] = module_base

                    # Now create the sub-package
                    spec_parent = importlib.util.spec_from_loader(parent_package_name, loader=None, is_package=True)
                    module_parent = importlib.util.module_from_spec(spec_parent)
                    module_parent.__path__ = [module_data["path"]]
                    sys.modules[parent_package_name] = module_parent

                module_full_name = f"{parent_package_name}.{module_filename}"


            if is_native_module:
                # (COMMENTED OUT V4) The signature verification logic has been removed as per the new strategy.
                loader = ExtensionFileLoader(module_full_name, path_to_load)
                spec = importlib.util.spec_from_loader(loader.name, loader)
            else:
                spec = importlib.util.spec_from_file_location(module_full_name, source_file_path)

            if spec is None: raise ImportError(f"Could not create module spec from {path_to_load}")

            module_lib = importlib.util.module_from_spec(spec)
            if module_full_name in sys.modules and not is_native_module:
                pass
            else:
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
                    self.logger(f"Removed '{vendor_path}' from sys.path.", "DEBUG") # English Log
                except ValueError:
                    pass

    # ... (sisa dari file tidak berubah)
    def _load_paused_status(self):
        if os.path.exists(self.paused_status_file):
            try:
                with open(self.paused_status_file, 'r') as f: return json.load(f)
            except (json.JSONDecodeError, IOError): return []
        return []
    def _save_paused_status(self):
        paused_ids = [mod_id for mod_id, data in self.loaded_modules.items() if data.get("is_paused")]
        try:
            with open(self.paused_status_file, 'w') as f: json.dump(paused_ids, f, indent=4)
        except IOError as e:
            self.kernel.write_to_log(f" ! Failed to save paused status: {e}", "ERROR") # English Log
    def set_module_paused(self, module_id, is_paused):
        if module_id in self.loaded_modules:
            instance = self.instance_cache.get(module_id)
            if is_paused and instance:
                if isinstance(instance, BaseUIProvider):
                    self.kernel.write_to_log(f"UI Provider '{module_id}' is being disabled.", "INFO") # English Log
                if hasattr(instance, 'on_unload'):
                    instance.on_unload()
                del self.instance_cache[module_id]
            self.loaded_modules[module_id]["is_paused"] = is_paused
            self._save_paused_status()
            return True
        return False
    def get_manifest(self, module_id):
        if module_id in self.loaded_modules:
            return self.loaded_modules[module_id].get("manifest")
        return None
    def get_module_permissions(self, module_id):
        if module_id in self.loaded_modules:
            return self.loaded_modules[module_id].get("permissions", [])
        return []
    def get_module_tier(self, module_id):
        if module_id in self.loaded_modules:
            return self.loaded_modules[module_id].get("tier", "free")
        return "free"
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
                component_type = manifest.get('type')
                if "PLUGIN" in component_type.upper():
                    destination_dir = self.plugins_dir
                else:
                    destination_dir = self.modules_dir
                final_path = os.path.join(destination_dir, component_id)
                if os.path.exists(final_path):
                    return False, f"Component '{component_id}' is already installed."
                shutil.move(component_root_path, final_path)
                self.kernel.write_to_log(f"Component '{component_id}' installed successfully to '{destination_dir}'.", "SUCCESS") # English Log
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