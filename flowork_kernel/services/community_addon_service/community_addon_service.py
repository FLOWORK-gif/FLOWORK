#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\services\community_addon_service\community_addon_service.py
# (Full code for the modified file)
#######################################################################

import os
import tempfile
import zipfile
import shutil
import base64
import requests
import json
import uuid
from datetime import datetime, timedelta
from ..base_service import BaseService
import hashlib
from flowork_kernel.api_client import ApiClient

class CommunityAddonService(BaseService):
    """
    (REMASTERED V3) Handles all interactions with the community addon repository.
    This version now EXCLUDES the 'vendor' directory during the packaging process
    to create lightweight, efficient uploads.
    """
    def __init__(self, kernel, service_id: str):
        super().__init__(kernel, service_id)
        self.logger = self.kernel.write_to_log
        self.api_client = ApiClient(kernel=self.kernel)
        self.core_component_ids = self._load_core_component_ids()

    def _load_core_component_ids(self):
        core_ids = set()
        manifest_path = os.path.join(self.kernel.project_root_path, "core_integrity.json")
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
            for path in manifest_data.keys():
                parts = path.split('/')
                if len(parts) > 1 and parts[0] in ['modules', 'plugins', 'widgets', 'triggers', 'ai_providers']:
                    core_ids.add(parts[1])
            self.logger(f"CommunityAddonService loaded {len(core_ids)} core component IDs for protection.", "INFO")
        except Exception as e:
            self.logger(f"CommunityAddonService could not load core component IDs: {e}", "WARN")
        return core_ids

    def upload_component(self, comp_type, component_id, description, tier):
        self.logger(f"CommunityAddonService: Starting upload for {comp_type} '{component_id}' via Supabase...", "INFO")
        if component_id in self.core_component_ids:
            return False, self.loc.get('api_core_component_upload_error')
        if not self.kernel.current_user or not self.kernel.current_user.get('session_token'):
            return False, "You must be logged in to upload a component."

        manager_map = {
            "modules": "module_manager_service", "plugins": "module_manager_service",
            "widgets": "widget_manager_service", "triggers": "trigger_manager_service",
            "ai_providers": "ai_provider_manager_service", "presets": "preset_manager_service"
        }
        manager_service_name = manager_map.get(comp_type)
        if not manager_service_name: return False, f"Could not find a manager for component type '{comp_type}'."
        manager = self.kernel.get_service(manager_service_name)
        if not manager: return False, f"Manager service '{manager_service_name}' not found."

        component_path = None
        manifest_data = None

        if comp_type == 'presets':
            component_path = os.path.join(self.kernel.data_path, "presets", f"{component_id}.json")
            manifest_data = {"id": component_id, "name": component_id, "description": description, "version": "1.0", "tier": tier}
        else:
            component_dirs = {
                'modules': self.kernel.modules_path, 'plugins': self.kernel.plugins_path,
                'widgets': self.kernel.widgets_path, 'triggers': self.kernel.triggers_path,
                'ai_providers': self.kernel.ai_providers_path
            }
            base_path = component_dirs.get(comp_type)
            if base_path:
                potential_path = os.path.join(base_path, component_id)
                if os.path.exists(potential_path):
                    component_path = potential_path
                    manifest_file = os.path.join(component_path, 'manifest.json')
                    if os.path.exists(manifest_file):
                        with open(manifest_file, 'r', encoding='utf-8') as f:
                            manifest_data = json.load(f)

        if not component_path or not os.path.exists(component_path) or not manifest_data:
            return False, f"Component path or manifest not found for: {component_id}"

        diagnostics_plugin = self.kernel.get_service("module_manager_service").get_instance("system_diagnostics_plugin")
        if not diagnostics_plugin: return False, "System Diagnostics plugin not found, cannot perform pre-flight scan."

        scan_successful, scan_report = diagnostics_plugin.scan_single_component_and_get_status(component_path)
        if not scan_successful: return False, f"Pre-upload scan failed:\n{scan_report}"

        self.logger(f"Pre-flight scan passed. Packaging and delegating to Supabase function...", "INFO")

        with tempfile.TemporaryDirectory() as temp_dir:
            zip_filename = f"{component_id}.zip"
            zip_path = os.path.join(temp_dir, zip_filename)
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if os.path.isdir(component_path):
                    for root, dirs, files in os.walk(component_path):
                        # (MODIFIED) This is the magic line. It tells os.walk to NOT go into the 'vendor' directory.
                        if 'vendor' in dirs:
                            dirs.remove('vendor')
                            self.logger(f"Packaging: Skipping 'vendor' directory inside '{os.path.basename(root)}'.", "DEBUG")

                        for file in files:
                            file_full_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_full_path, component_path)
                            zipf.write(file_full_path, arcname)
                else:
                    zipf.write(component_path, os.path.basename(component_path))

            try:
                upload_endpoint = f"{self.api_client.supabase_url.rstrip('/')}/functions/v1/upload-addon"
                session_token = self.kernel.current_user.get('session_token')
                headers = {
                    'Authorization': f'Bearer {session_token}',
                    'apikey': self.api_client.supabase_key,
                }
                form_data = {
                    "comp_type": comp_type,
                    "component_id": component_id,
                    "description": description,
                    "tier": tier,
                    "manifest_data": json.dumps(manifest_data)
                }

                with open(zip_path, 'rb') as f:
                    files = {'file': (zip_filename, f, 'application/zip')}
                    response = requests.post(upload_endpoint, data=form_data, files=files, headers=headers, timeout=120)

                response.raise_for_status()
                response_json = response.json()
                self.logger(f"Supabase function response: {response_json.get('message')}", "SUCCESS")
                return True, response_json.get('message', "Upload successful!")

            except requests.exceptions.HTTPError as e:
                error_detail = "Unknown server error."
                try:
                    error_detail = e.response.json().get("error", e.response.text)
                except json.JSONDecodeError:
                    error_detail = e.response.text
                if e.response.status_code == 409:
                    self.logger(f"Duplicate component upload detected by server for '{component_id}'.", "WARN")
                    return False, self.loc.get('marketplace_upload_duplicate_error', fallback=f"This component '{component_id}' already exists in the repository.")
                self.logger(f"HTTP error connecting to Supabase function: {e}", "ERROR")
                return False, f"Server error: {error_detail}"
            except Exception as e:
                error_message = f"An unexpected error occurred during upload delegation."
                self.logger(f"Full unexpected error: {e}", "ERROR")
                return False, error_message

    def upload_model(self, model_filepath: str, model_id: str, description: str, tier: str):
        self.logger("Model upload function is not yet refactored for Supabase.", "WARN")
        return False, "Model upload functionality is not yet migrated to the new system."