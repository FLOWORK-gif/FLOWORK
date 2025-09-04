#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\api_client.py
# (FIXED: Re-added the missing _handle_response method)
#######################################################################

import requests
import json
import os
import threading
import time
import random
from flowork_kernel.kernel import Kernel

class ApiClient:
    """
    (REFACTORED V2) A client to interact with local and remote APIs.
    This class is now 100% clean of sensitive data. It fetches all required
    credentials dynamically from the VariableManagerService.
    """
    def __init__(self, base_url="http://localhost:8989/api/v1", kernel=None):
        self.local_base_url = base_url
        self.kernel = kernel or Kernel.instance
        self.cache = {}
        self.cache_lock = threading.Lock()
        self.marketplace_repo_owner = "FLOWORK-gif"
        self.marketplace_repo_name = "addon"
        self.marketplace_branch = "main"

    # [DITAMBAHKAN] Helper function untuk mengambil data dari VariableManager dengan aman
    def _get_variable(self, var_name):
        if self.kernel:
            variable_manager = self.kernel.get_service("variable_manager_service")
            if variable_manager:
                return variable_manager.get_variable(var_name)
        return None

    def _get_supabase_url(self):
        url = self._get_variable("SUPABASE_URL")
        if not url:
            raise ValueError("Supabase URL is not configured in Variable Manager.")
        return url

    def _get_supabase_key(self):
        key = self._get_variable("SUPABASE_KEY")
        if not key:
            raise ValueError("Supabase Anon Key is not configured in Variable Manager.")
        return key

    def _get_local_auth_headers(self):
        headers = {}
        api_key = self._get_variable("FLOWORK_API_KEY")
        if api_key:
            headers['X-API-Key'] = api_key
        return headers

    def _get_supabase_headers(self, auth_token=None):
        """Gets auth headers for Supabase. Includes Bearer token if provided."""
        headers = {
            'apikey': self._get_supabase_key(),
            'Content-Type': 'application/json'
        }
        if auth_token:
            headers['Authorization'] = f'Bearer {auth_token}'
        return headers

    # [FIX] Ini method yang hilang dan menyebabkan error. Sekarang sudah ada lagi.
    def _handle_response(self, response):
        if 200 <= response.status_code < 300:
            if response.status_code == 204 or not response.content:
                return True, {}
            return True, response.json()
        else:
            try:
                error_data = response.json()
                message = error_data.get("message") or error_data.get("msg") or error_data.get("error_description") or error_data.get("error", "Unknown API error")
            except json.JSONDecodeError:
                message = response.text
            return False, message

    def register_user(self, username, email, password):
        try:
            headers = self._get_supabase_headers()
            url = f"{self._get_supabase_url()}/auth/v1/signup"
            payload = {
                "email": email,
                "password": password,
                "data": { "username": username }
            }
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            return self._handle_response(response)
        except (requests.exceptions.RequestException, ValueError) as e:
            return False, f"Connection/Configuration error: {e}"

    def forgot_password(self, email: str):
        try:
            headers = self._get_supabase_headers()
            url = f"{self._get_supabase_url()}/functions/v1/forgot-password"
            payload = {"email": email}
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            return self._handle_response(response)
        except (requests.exceptions.RequestException, ValueError) as e:
            return False, f"Connection/Configuration error: {e}"

    def login_user(self, email, password):
        try:
            auth_headers = self._get_supabase_headers()
            supabase_url = self._get_supabase_url()
            auth_url = f"{supabase_url}/auth/v1/token?grant_type=password"
            auth_payload = {"email": email, "password": password}

            auth_response = requests.post(auth_url, headers=auth_headers, json=auth_payload, timeout=15)
            auth_success, auth_data = self._handle_response(auth_response)
            if not auth_success:
                return False, auth_data

            access_token = auth_data.get('access_token')
            user_id = auth_data.get('user', {}).get('id')
            if not access_token or not user_id:
                return False, "Login succeeded but received invalid data from server."

            profile_headers = self._get_supabase_headers(auth_token=access_token)
            profile_url = f"{supabase_url}/rest/v1/users?id=eq.{user_id}&select=tier,username"
            profile_response = requests.get(profile_url, headers=profile_headers, timeout=10)
            profile_success, profile_data = self._handle_response(profile_response)
            if not profile_success:
                return False, f"Could not fetch user profile. Server said: {profile_data}"

            if not isinstance(profile_data, list) or not profile_data:
                 return False, "Could not fetch user profile after login."

            user_profile = profile_data[0]
            final_response = {
                "message": "Login successful.",
                "session_token": access_token,
                "user_id": user_id,
                "email": email,
                "username": user_profile.get('username', ''),
                "tier": user_profile.get('tier', 'free')
            }
            return True, final_response
        except (requests.exceptions.RequestException, ValueError) as e:
            return False, f"Connection/Configuration error: {e}"

    def get_user_profile_by_token(self, session_token: str):
        try:
            auth_headers = self._get_supabase_headers(auth_token=session_token)
            supabase_url = self._get_supabase_url()
            user_url = f"{supabase_url}/auth/v1/user"
            user_response = requests.get(user_url, headers=auth_headers, timeout=10)
            user_success, user_data = self._handle_response(user_response)
            if not user_success:
                return False, user_data

            user_id = user_data.get('id')
            email = user_data.get('email')
            if not user_id:
                return False, "Token is valid but did not return a user ID."

            profile_headers = self._get_supabase_headers(auth_token=session_token)
            profile_url = f"{supabase_url}/rest/v1/users?id=eq.{user_id}&select=tier,username,license_expires_at"
            profile_response = requests.get(profile_url, headers=profile_headers, timeout=10)
            profile_success, profile_data = self._handle_response(profile_response)
            if not profile_success:
                return False, f"Could not fetch user profile. Server said: {profile_data}"

            if not isinstance(profile_data, list) or not profile_data:
                 return False, "Could not fetch user profile after validating token."

            user_profile = profile_data[0]
            final_response = {
                "message": "Auto-login successful.",
                "session_token": session_token,
                "user_id": user_id,
                "email": email,
                "username": user_profile.get('username', ''),
                "tier": user_profile.get('tier', 'free'),
                "license_expires_at": user_profile.get('license_expires_at')
            }
            return True, final_response
        except (requests.exceptions.RequestException, ValueError) as e:
            return False, f"Connection/Configuration error: {e}"

    # ... Sisa dari semua method lain (dari validate_license_activation sampai akhir) tidak perlu diubah ...
    # ... karena mereka sudah benar memanggil self._handle_response
    def validate_license_activation(self, license_key: str, machine_id: str):
        try:
            payload = {"license_key": license_key, "machine_id": machine_id}
            response = requests.post(f"{self.local_base_url}/license/validate", json=payload, headers=self._get_local_auth_headers(), timeout=20)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return False, f"Connection to local API server failed during validation: {e}"
    def activate_license(self, license_content: dict):
        try:
            payload = {"license_content": license_content}
            response = requests.post(f"{self.local_base_url}/license/activate", json=payload, headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return False, f"Connection to API server failed: {e}"
    def deactivate_license(self):
        try:
            response = requests.post(f"{self.local_base_url}/license/deactivate", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return False, f"Connection to API server failed: {e}"
    def restart_application(self):
        try:
            response = requests.post(f"{self.local_base_url}/system/actions/restart", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return False, f"Connection to API server failed: {e}"
    def get_all_settings(self):
        try:
            response = requests.get(f"{self.local_base_url}/settings", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def save_settings(self, settings_data: dict):
        try:
            response = requests.patch(f"{self.local_base_url}/settings", json=settings_data, headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def list_datasets(self):
        try:
            response = requests.get(f"{self.local_base_url}/datasets", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_dataset_data(self, dataset_name: str):
        try:
            response = requests.get(f"{self.local_base_url}/datasets/{dataset_name}/data", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def create_dataset(self, name: str):
        try:
            payload = {"name": name}
            response = requests.post(f"{self.local_base_url}/datasets", json=payload, headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def add_data_to_dataset(self, dataset_name: str, data_list: list):
        try:
            payload = {"data": data_list}
            response = requests.post(f"{self.local_base_url}/datasets/{dataset_name}/data", json=payload, headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def start_training_job(self, base_model_id, dataset_name, new_model_name, training_args):
        try:
            payload = {
                "base_model_id": base_model_id,
                "dataset_name": dataset_name,
                "new_model_name": new_model_name,
                "training_args": training_args
            }
            response = requests.post(f"{self.local_base_url}/training/start", json=payload, headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_training_job_status(self, job_id: str):
        try:
            response = requests.get(f"{self.local_base_url}/training/status/{job_id}", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def start_model_conversion(self, source_model_folder: str, output_gguf_name: str, quantize_method: str):
        try:
            payload = {
                "source_model_folder": source_model_folder,
                "output_gguf_name": output_gguf_name,
                "quantize_method": quantize_method
            }
            response = requests.post(f"{self.local_base_url}/models/convert", json=payload, headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def start_model_requantize(self, source_gguf_path: str, output_gguf_name: str, quantize_method: str):
        try:
            payload = {
                "source_gguf_path": source_gguf_path,
                "output_gguf_name": output_gguf_name,
                "quantize_method": quantize_method
            }
            response = requests.post(f"{self.local_base_url}/models/requantize", json=payload, headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_conversion_status(self, job_id: str):
        try:
            response = requests.get(f"{self.local_base_url}/models/convert/status/{job_id}", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_agents(self):
        try:
            response = requests.get(f"{self.local_base_url}/agents", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def save_agent(self, agent_data: dict):
        try:
            response = requests.post(f"{self.local_base_url}/agents", json=agent_data, headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def delete_agent(self, agent_id: str):
        try:
            response = requests.delete(f"{self.local_base_url}/agents/{agent_id}", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def run_agent(self, agent_id: str, objective: str):
        try:
            payload = {"objective": objective}
            response = requests.post(f"{self.local_base_url}/agents/{agent_id}/run", json=payload, headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_agent_run_status(self, run_id: str):
        try:
            response = requests.get(f"{self.local_base_url}/agents/run/{run_id}", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def stop_agent_run(self, run_id: str):
        try:
            response = requests.post(f"{self.local_base_url}/agents/run/{run_id}/stop", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_marketplace_ads(self):
        cache_key = "marketplace_ads"
        with self.cache_lock:
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if time.time() - timestamp < 86400:
                    return True, cached_data
        url = f"https://raw.githubusercontent.com/{self.marketplace_repo_owner}/{self.marketplace_repo_name}/{self.marketplace_branch}/ads.json"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            all_ads = response.json()
            selected_ads = random.sample(all_ads, min(6, len(all_ads)))
            with self.cache_lock:
                self.cache[cache_key] = (selected_ads, time.time())
            return True, selected_ads
        except requests.exceptions.RequestException as e:
            return False, f"Network error fetching ads: {e}"
        except (json.JSONDecodeError, ValueError):
            return False, "Failed to parse ads.json."
    def get_marketplace_index(self, component_type: str):
        cache_key = f"marketplace_index_{component_type}"
        with self.cache_lock:
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if time.time() - timestamp < 86400: # Cache for 1 day
                    return True, cached_data
        folder_map = {
            "modules": "modules", "plugins": "plugins", "widgets": "widgets", "presets": "presets",
            "triggers": "triggers", "ai_providers": "ai_providers", "ai_models": "ai_models"
        }
        folder_name = folder_map.get(component_type)
        if not folder_name: return False, f"Unknown component type for marketplace: {component_type}"
        url = f"https://raw.githubusercontent.com/{self.marketplace_repo_owner}/{self.marketplace_repo_name}/{self.marketplace_branch}/{folder_name}/index.json"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 404: return True, []
            response.raise_for_status()
            data = response.json()
            with self.cache_lock:
                self.cache[cache_key] = (data, time.time())
            return True, data
        except requests.exceptions.RequestException as e:
            return False, f"Network error fetching marketplace index: {e}"
        except json.JSONDecodeError:
            return False, f"Failed to parse marketplace index.json for {component_type}."
    def trigger_hot_reload(self):
        try:
            payload = {"action": "hot_reload"}
            response = requests.post(f"{self.local_base_url}/system/actions/hot_reload", json=payload, headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_presets(self):
        try:
            response = requests.get(f"{self.local_base_url}/presets", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_preset_data(self, preset_name):
        try:
            response = requests.get(f"{self.local_base_url}/presets/{preset_name}", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def save_preset(self, preset_name, workflow_data):
        try:
            payload = {"name": preset_name, "workflow_data": workflow_data}
            response = requests.post(f"{self.local_base_url}/presets", json=payload, headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def delete_preset(self, preset_name):
        try:
            response = requests.delete(f"{self.local_base_url}/presets/{preset_name}", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_preset_versions(self, preset_name: str):
        try:
            response = requests.get(f"{self.local_base_url}/presets/{preset_name}/versions", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def load_preset_version(self, preset_name: str, version_filename: str):
        try:
            response = requests.get(f"{self.local_base_url}/presets/{preset_name}/versions/{version_filename}", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def delete_preset_version(self, preset_name: str, version_filename: str):
        try:
            response = requests.delete(f"{self.local_base_url}/presets/{preset_name}/versions/{version_filename}", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_variables(self):
        try:
            response = requests.get(f"{self.local_base_url}/variables", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def update_variable(self, name, value, is_secret, is_enabled=True, mode=None):
        try:
            payload = {"value": value, "is_secret": is_secret, "is_enabled": is_enabled}
            if mode: payload["mode"] = mode
            response = requests.put(f"{self.local_base_url}/variables/{name}", json=payload, headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def update_variable_state(self, name: str, is_enabled: bool):
        try:
            payload = {"enabled": is_enabled}
            response = requests.patch(f"{self.local_base_url}/variables/{name}/state", json=payload, headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def delete_variable(self, name):
        try:
            response = requests.delete(f"{self.local_base_url}/variables/{name}", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_components(self, component_type: str, component_id: str = None):
        try:
            url = f"{self.local_base_url}/{component_type}"
            if component_id: url += f"/{component_id}"
            response = requests.get(url, headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def install_component(self, component_type: str, zip_filepath: str):
        try:
            with open(zip_filepath, 'rb') as f:
                headers = self._get_local_auth_headers()
                files = {'file': (os.path.basename(zip_filepath), f, 'application/zip')}
                response = requests.post(f"{self.local_base_url}/{component_type}/install", files=files, headers=headers)
            return self._handle_response(response)
        except FileNotFoundError:
            return False, f"Local file not found: {zip_filepath}"
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def delete_component(self, component_type: str, component_id: str):
        try:
            response = requests.delete(f"{self.local_base_url}/{component_type}/{component_id}", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def update_component_state(self, component_type: str, component_id: str, is_paused: bool):
        try:
            payload = {"paused": is_paused}
            response = requests.patch(f"{self.local_base_url}/{component_type}/{component_id}", json=payload, headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_dashboard_layout(self, tab_id: str):
        try:
            response = requests.get(f"{self.local_base_url}/uistate/dashboards/{tab_id}", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def save_dashboard_layout(self, tab_id: str, layout_data: dict):
        try:
            response = requests.post(f"{self.local_base_url}/uistate/dashboards/{tab_id}", json=layout_data, headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_tab_session(self):
        try:
            response = requests.get(f"{self.local_base_url}/uistate/session/tabs", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def save_tab_session(self, tabs_data: list):
        try:
            response = requests.post(f"{self.local_base_url}/uistate/session/tabs", json=tabs_data, headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def open_managed_tab(self, tab_key: str):
        try:
            payload = {"tab_key": tab_key}
            response = requests.post(f"{self.local_base_url}/ui/actions/open_tab", json=payload, headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def upload_component(self, comp_type: str, component_id: str, description: str, tier: str):
        try:
            payload = {
                "comp_type": comp_type,
                "component_id": component_id,
                "description": description,
                "tier": tier
            }
            response = requests.post(f"{self.local_base_url}/addons/upload", json=payload, headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def upload_model(self, model_path: str, description: str, tier: str):
        try:
            form_data = {
                "description": description,
                "tier": tier,
                "model_id": os.path.basename(model_path).replace('.gguf', '')
            }
            with open(model_path, 'rb') as f:
                files = {'file': (os.path.basename(model_path), f, 'application/octet-stream')}
                response = requests.post(
                    f"{self.local_base_url}/models/upload",
                    data=form_data,
                    files=files,
                    headers=self._get_local_auth_headers()
                )
            return self._handle_response(response)
        except FileNotFoundError:
            return False, f"Local model file not found: {model_path}"
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_prompts(self):
        try:
            response = requests.get(f"{self.local_base_url}/prompts", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_prompt(self, prompt_id: str):
        try:
            response = requests.get(f"{self.local_base_url}/prompts/{prompt_id}", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def create_prompt(self, prompt_data: dict):
        try:
            response = requests.post(f"{self.local_base_url}/prompts", json=prompt_data, headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def update_prompt(self, prompt_id: str, prompt_data: dict):
        try:
            response = requests.put(f"{self.local_base_url}/prompts/{prompt_id}", json=prompt_data, headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def delete_prompt(self, prompt_id: str):
        try:
            response = requests.delete(f"{self.local_base_url}/prompts/{prompt_id}", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def delete_dataset(self, name: str):
        try:
            response = requests.delete(f"{self.local_base_url}/datasets/{name}", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            return False, f"Connection to API server failed: {e}"
    def get_trigger_rules(self):
        try:
            response = requests.get(f"{self.local_base_url}/triggers/rules", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return False, f"Connection to API server failed: {e}"
    def get_trigger_definitions(self):
        try:
            response = requests.get(f"{self.local_base_url}/triggers/definitions", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return False, f"Connection to API server failed: {e}"
    def create_trigger_rule(self, rule_data: dict):
        try:
            response = requests.post(f"{self.local_base_url}/triggers/rules", json=rule_data, headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return False, f"Connection to API server failed: {e}"
    def update_trigger_rule(self, rule_id: str, rule_data: dict):
        try:
            response = requests.put(f"{self.local_base_url}/triggers/rules/{rule_id}", json=rule_data, headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return False, f"Connection to API server failed: {e}"
    def delete_trigger_rule(self, rule_id: str):
        try:
            response = requests.delete(f"{self.local_base_url}/triggers/rules/{rule_id}", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return False, f"Connection to API server failed: {e}"
    def reload_triggers(self):
        try:
            response = requests.post(f"{self.local_base_url}/triggers/actions/reload", headers=self._get_local_auth_headers())
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return False, f"Connection to API server failed: {e}"