#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\services\widget_manager_service\widget_manager_service.py
# JUMLAH BARIS : 251
#######################################################################

import os
import json
import importlib.util
import subprocess
import sys
from importlib.machinery import ExtensionFileLoader
import importlib.metadata
from ..base_service import BaseService
import zipfile
import tempfile
import shutil
import hashlib
class WidgetManagerService(BaseService):
    """
    Manages the discovery, loading, and access to all custom dashboard widgets.
    (MODIFIED V2) Now loads compiled widgets with the '.widget.flowork' extension.
    """
    def __init__(self, kernel, service_id: str):
        super().__init__(kernel, service_id)
        self.widgets_dir = self.kernel.widgets_path
        self.loaded_widgets = {}
        self.paused_status_file = os.path.join(self.kernel.data_path, 'paused_widgets.json')
        self.cache_file = os.path.join(self.kernel.data_path, 'widget_index.cache')
        self.kernel.write_to_log("Service 'WidgetManager' initialized.", "DEBUG") # English Log
    def _is_cache_valid(self):
        if not os.path.exists(self.cache_file):
            return False
        cache_mod_time = os.path.getmtime(self.cache_file)
        if os.path.exists(self.widgets_dir):
            if os.path.getmtime(self.widgets_dir) > cache_mod_time:
                return False
            for root, dirs, _ in os.walk(self.widgets_dir):
                for d in dirs:
                    if os.path.getmtime(os.path.join(root, d)) > cache_mod_time:
                        return False
        return True
    def discover_and_load_widgets(self):
        self.kernel.write_to_log("WidgetManager: Starting discovery and loading of custom widgets...", "INFO") # English Log
        auto_compiler = self.kernel.get_service("auto_compiler_service")
        if auto_compiler and self.kernel.is_dev_mode:
            auto_compiler.initial_scan()
        self.loaded_widgets.clear()
        paused_ids = self._load_paused_status()
        if self._is_cache_valid():
            self.kernel.write_to_log("WidgetManager: Valid cache found. Loading widgets from index...", "INFO") # English Log
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            for widget_id, widget_data in cached_data.items():
                self._process_single_widget(
                    widget_dir=widget_data['path'],
                    widget_id=widget_id,
                    paused_ids=paused_ids,
                    manifest_override=widget_data['manifest']
                )
            self.kernel.write_to_log(f"WidgetManager: Widget loading from cache complete. Total loaded: {len(self.loaded_widgets)}", "INFO") # English Log
            return
        self.kernel.write_to_log("WidgetManager: Cache not found or stale. Discovering from disk...", "WARN") # English Log
        discovered_data_for_cache = {}
        if not os.path.exists(self.widgets_dir):
            return
        for widget_id in os.listdir(self.widgets_dir):
            widget_dir = os.path.join(self.widgets_dir, widget_id)
            if os.path.isdir(widget_dir) and widget_id != '__pycache__':
                manifest = self._process_single_widget(widget_dir, widget_id, paused_ids)
                if manifest:
                    discovered_data_for_cache[widget_id] = {
                        'manifest': manifest,
                        'path': widget_dir
                    }
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(discovered_data_for_cache, f)
            self.kernel.write_to_log(f"WidgetManager: Widget index cache created at {self.cache_file}", "SUCCESS") # English Log
        except Exception as e:
            self.kernel.write_to_log(f"WidgetManager: Failed to write widget cache file: {e}", "ERROR") # English Log
        self.kernel.write_to_log(f"WidgetManager: Custom widget loading complete. Total loaded: {len(self.loaded_widgets)}", "INFO") # English Log
    def _process_single_widget(self, widget_dir, widget_id, paused_ids, manifest_override=None):
        self.kernel.write_to_log(f" -> Processing widget: '{widget_id}'", "DEBUG") # English Log
        manifest = manifest_override
        if manifest is None:
            manifest_path = os.path.join(widget_dir, "manifest.json")
            if not os.path.exists(manifest_path):
                return None
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
            except Exception as e:
                self.kernel.write_to_log(f"   ! Failed to read manifest for widget '{widget_id}': {e}", "WARN") # English Log
                return None
        try:
            self._install_dependencies_locally(widget_dir, manifest.get('name', widget_id))
            entry_point = manifest.get("entry_point")
            if not entry_point:
                raise ValueError("entry_point not found in manifest.json")
            module_filename, class_name = entry_point.split('.')
            native_file_path = os.path.join(widget_dir, f"{module_filename}.widget.flowork")
            source_file_path = os.path.join(widget_dir, f"{module_filename}.py")
            path_to_load = native_file_path if os.path.exists(native_file_path) else source_file_path
            is_native_module = path_to_load.endswith(".widget.flowork")
            if not os.path.exists(path_to_load):
                self.kernel.write_to_log(f"   ! Failed: No source or protected file found for widget '{widget_id}'.", "ERROR") # English Log
                return manifest
            if is_native_module:
                self.logger(f"  -> Found locked native file for widget '{widget_id}'. Prioritizing it.", "DEBUG") # English Log
                module_full_name = f"widgets.{widget_id}.{module_filename}"
                loader = ExtensionFileLoader(module_full_name, path_to_load)
                spec = importlib.util.spec_from_loader(loader.name, loader)
            else:
                safe_widget_id = widget_id.replace('-', '_')
                module_full_name = f"widgets.{safe_widget_id}.{module_filename}"
                spec = importlib.util.spec_from_file_location(module_full_name, source_file_path)
            module_lib = importlib.util.module_from_spec(spec)
            if module_full_name not in sys.modules:
                 sys.modules[module_full_name] = module_lib
            spec.loader.exec_module(module_lib)
            widget_class = getattr(module_lib, class_name)
            self.loaded_widgets[widget_id] = {
                "class": widget_class,
                "name": manifest.get('name', widget_id),
                "manifest": manifest,
                "path": widget_dir,
                "is_paused": widget_id in paused_ids
            }
            self.kernel.write_to_log(f" + Success: Widget '{widget_id}' loaded.", "SUCCESS") # English Log
        except Exception as e:
            self.kernel.write_to_log(f" ! Failed to load widget '{widget_id}': {e}", "ERROR") # English Log
        return manifest
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
        self.kernel.write_to_log(f"Widget '{component_name}' has local dependencies. Installing into 'vendor' folder...", "INFO") # English Log
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
            self.kernel.write_to_log(f"Successfully installed local dependencies for '{component_name}'.", "SUCCESS") # English Log
            return True
        except subprocess.CalledProcessError as e:
            self.kernel.write_to_log(f"FAILED to install local dependencies for '{component_name}'. Pip Error: {e.stderr.decode('utf-8', 'ignore')}", "CRITICAL") # English Log
            return False
        except Exception as e:
            self.kernel.write_to_log(f"An unexpected error occurred during local dependency installation for '{component_name}': {e}", "CRITICAL") # English Log
            return False
    def _load_paused_status(self):
        if os.path.exists(self.paused_status_file):
            try:
                with open(self.paused_status_file, 'r') as f: return json.load(f)
            except (json.JSONDecodeError, IOError): return []
        return []
    def _save_paused_status(self):
        paused_ids = [wid for wid, data in self.loaded_widgets.items() if data.get("is_paused")]
        try:
            with open(self.paused_status_file, 'w') as f: json.dump(paused_ids, f, indent=4)
        except IOError as e:
            self.kernel.write_to_log(f" ! Failed to save widget paused status: {e}", "ERROR") # English Log
    def set_widget_paused(self, widget_id, is_paused):
        if widget_id in self.loaded_widgets:
            self.loaded_widgets[widget_id]["is_paused"] = is_paused
            self._save_paused_status()
            if self.kernel.root:
                self.kernel.root.refresh_ui_components()
            return True
        return False
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
                    error_msg = f"Installation failed. This widget requires a '{required_tier.capitalize()}' license or higher. Your current tier is '{self.kernel.license_tier.capitalize()}'."
                    self.kernel.write_to_log(error_msg, "ERROR") # English Log
                    return False, error_msg
                component_id = manifest.get('id')
                if not component_id:
                    return False, "Component 'id' is missing from manifest.json."
                final_path = os.path.join(self.widgets_dir, component_id)
                if os.path.exists(final_path):
                    return False, f"Widget '{component_id}' is already installed."
                shutil.move(component_root_path, final_path)
                self.kernel.write_to_log(f"Widget '{component_id}' installed successfully.", "SUCCESS") # English Log
                return True, f"Widget '{manifest.get('name', component_id)}' installed successfully."
            except Exception as e:
                self.kernel.write_to_log(f"Widget installation failed: {e}", "ERROR") # English Log
                return False, f"An error occurred during widget installation: {e}"
    def uninstall_component(self, component_id: str) -> (bool, str):
        if component_id not in self.loaded_widgets:
            return False, f"Widget '{component_id}' is not currently loaded or does not exist."
        component_data = self.loaded_widgets[component_id]
        component_path = component_data.get('path')
        if not component_path or not os.path.isdir(component_path):
            return False, f"Path for widget '{component_id}' not found or is invalid."
        try:
            shutil.rmtree(component_path)
            del self.loaded_widgets[component_id]
            self.kernel.write_to_log(f"Widget '{component_id}' folder deleted successfully.", "SUCCESS") # English Log
            return True, f"Widget '{component_id}' uninstalled. A restart is required to fully clear it."
        except Exception as e:
            self.kernel.write_to_log(f"Failed to delete widget folder '{component_path}': {e}", "ERROR") # English Log
            return False, f"Could not delete widget folder: {e}"
