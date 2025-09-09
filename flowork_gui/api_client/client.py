import requests
import json
import os
import threading
import time
# GUI_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "gui_config.json")
# API_KEY_FILE = os.path.join(os.path.dirname(__file__), "..", "api_key.json")
# COMMENT: Path definitions moved inside the class to avoid potential circular import issues with a mock kernel during testing.
class ApiClient:
    """
    Handles all HTTP communication with the FLOWORK server kernel.
    (REFACTORED) Now reads the server URL from a config file to be fully portable.
    """
    def __init__(self, kernel=None):
        # ADDED: Lazy initialization for paths to improve stability.
        self.GUI_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "gui_config.json")
        self.API_KEY_FILE = os.path.join(os.path.dirname(__file__), "..", "api_key.json")
        self.base_url = self._load_server_url()
        self.api_key = self._load_api_key()
        self.marketplace_repo_owner = "FLOWORK-gif" # This could be configurable in the future
        self.marketplace_repo_name = "addon"
        self.marketplace_branch = "main"
        self.cache = {}
        self.cache_lock = threading.Lock()
        print(f"ApiClient initialized for server at {self.base_url}") # English Log
    def _load_server_url(self):
        """
        ADDED: Loads the server URL from gui_config.json.
        Creates a default if it doesn't exist.
        """
        default_url = "http://127.0.0.1:8989"
        try:
            if os.path.exists(self.GUI_CONFIG_FILE):
                with open(self.GUI_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    url = config.get("server_url")
                    if url:
                        return url.rstrip('/') # Ensure no trailing slash
            with open(self.GUI_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump({"server_url": default_url}, f, indent=4)
            return default_url
        except (IOError, json.JSONDecodeError) as e:
            print(f"[API_CLIENT_ERROR] Could not read or create gui_config.json: {e}. Using default URL.") # English Log
            return default_url
    def _load_api_key(self):
        """Loads the API key from a local JSON file."""
        try:
            if os.path.exists(self.API_KEY_FILE):
                with open(self.API_KEY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    key = data.get("api_key")
                    if key:
                        print("[INFO] Secure API key loaded from local file.") # English Log
                        return key
        except (IOError, json.JSONDecodeError) as e:
            print(f"[API_CLIENT_WARNING] Could not read API key file: {e}") # English Log
        return None
    def _get_auth_headers(self):
        """Helper function to create authentication headers."""
        if not self.api_key:
            print("[API_CLIENT_WARNING] API Key is not set. Authenticated requests will fail.") # English Log
            return {}
        return {"X-API-Key": self.api_key}
    def get_server_status(self):
        """Example endpoint to check if the server is alive. This is a public endpoint."""
        try:
            response = requests.get(f"{self.base_url}/api/v1/status", timeout=2)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            status_code = e.response.status_code if hasattr(e, 'response') and e.response is not None else "N/A"
            print(f"[API_CLIENT_ERROR] Failed to get server status ({status_code}): {e}") # English Log
            return {"status": "error", "message": str(e)}
    def _make_request(self, method, endpoint, **kwargs):
        """Makes an authenticated request to the server."""
        url = f"{self.base_url}/api/v1{endpoint}"
        headers = self._get_auth_headers()
        if not self.api_key:
            return False, {"status": "error", "message": "Authentication failed: API Key is missing."}
        if 'headers' in kwargs:
            kwargs['headers'].update(headers)
        else:
            kwargs['headers'] = headers
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            if response.status_code == 204 or not response.content:
                return True, {"status": "success", "data": {}}
            return True, response.json()
        except requests.exceptions.HTTPError as e:
            error_message = f"{e.response.status_code} Client Error: {e.response.reason} for url: {e.response.url}"
            try:
                error_detail = e.response.json().get('detail', error_message)
                return False, {"status": "error", "message": error_detail}
            except json.JSONDecodeError:
                return False, {"status": "error", "message": error_message}
        except requests.exceptions.RequestException as e:
            print(f"[API_CLIENT_ERROR] Request failed for {endpoint}: {e}") # English Log
            return False, {"status": "error", "message": str(e)}
    def get_menubar(self):
        """Fetches the dynamic menubar structure from the server."""
        return self._make_request('GET', '/ui/menubar')
    def get_tab_session(self):
        """Fetches the list of open tabs from the last session from the server."""
        return self._make_request('GET', '/uistate/session/tabs')
    def save_tab_session(self, tabs_data: list):
        """Saves the current list of open tabs to the server."""
        return self._make_request('POST', '/uistate/session/tabs', json=tabs_data)
    def get_presets(self):
        """Fetches a list of all available presets."""
        return self._make_request('GET', '/presets')
    def get_ai_models(self):
        """Fetches a list of all available local AI models."""
        return self._make_request('GET', '/ai_models')
    def get_components(self, component_type: str, component_id: str = None):
        """Fetches a list of components (modules, widgets, etc.) or a single one by ID."""
        endpoint = f"/{component_type}"
        if component_id:
            endpoint += f"/{component_id}"
        return self._make_request('GET', endpoint)
    def get_dashboard_layout(self, tab_id: str):
        """Fetches the dashboard layout for a specific tab."""
        return self._make_request('GET', f"/uistate/dashboards/{tab_id}")
    def save_dashboard_layout(self, tab_id: str, layout_data: dict):
        """Saves the dashboard layout for a specific tab."""
        return self._make_request('POST', f"/uistate/dashboards/{tab_id}", json=layout_data)
    def list_datasets(self):
        """Fetches a list of all available datasets from the server."""
        return self._make_request('GET', '/datasets')
    def get_prompts(self):
        """Fetches all prompt templates."""
        return self._make_request('GET', '/prompts')
    def get_prompt(self, prompt_id: str):
        """Fetches a single prompt template by its ID."""
        return self._make_request('GET', f'/prompts/{prompt_id}')
    def create_prompt(self, prompt_data: dict):
        """Creates a new prompt template."""
        return self._make_request('POST', '/prompts', json=prompt_data)
    def update_prompt(self, prompt_id: str, prompt_data: dict):
        """Updates an existing prompt template."""
        return self._make_request('PUT', f'/prompts/{prompt_id}', json=prompt_data)
    def delete_prompt(self, prompt_id: str):
        """Deletes a prompt template."""
        return self._make_request('DELETE', f'/prompts/{prompt_id}')
    def get_trigger_rules(self):
        """Fetches all configured trigger rules from the server."""
        return self._make_request('GET', '/triggers/rules')
    def get_trigger_definitions(self):
        """Fetches all available trigger types (definitions) from the server."""
        return self._make_request('GET', '/triggers/definitions')
    def update_trigger_rule(self, rule_id: str, rule_data: dict):
        """Updates an existing trigger rule on the server."""
        return self._make_request('PUT', f'/triggers/rules/{rule_id}', json=rule_data)
    def create_trigger_rule(self, rule_data: dict):
        """Creates a new trigger rule on the server."""
        return self._make_request('POST', '/triggers/rules', json=rule_data)
    def delete_trigger_rule(self, rule_id: str):
        """Deletes a trigger rule from the server."""
        return self._make_request('DELETE', f'/triggers/rules/{rule_id}')
    def reload_triggers(self):
        """Tells the server to reload all active triggers."""
        return self._make_request('POST', '/triggers/actions/reload')
    def generate_workflow(self, user_prompt: str):
        """Sends a prompt to the AI Architect to generate a workflow."""
        return self._make_request('POST', '/ai/architect/generate', json={"prompt": user_prompt})
    def add_new_workflow_tab_with_data(self, workflow_data, tab_title):
        """A special client-side function to signal the main app to create a new tab."""
        print(f"SIGNAL: Request to create new tab '{tab_title}' with provided data.")
    def get_all_settings(self):
        """Fetches all kernel settings."""
        return self._make_request('GET', '/settings')
    def save_settings(self, settings_data: dict):
        """Saves all kernel settings."""
        return self._make_request('PATCH', '/settings', json=settings_data)
    def get_variables(self):
        """Fetches all user-defined variables."""
        return self._make_request('GET', '/variables')
    def update_variable(self, name: str, value, is_secret: bool, is_enabled: bool, mode: str):
        """Creates or updates a user-defined variable."""
        payload = {"value": value, "is_secret": is_secret, "is_enabled": is_enabled, "mode": mode}
        return self._make_request('PUT', f'/variables/{name}', json=payload)
    def update_variable_state(self, name: str, is_enabled: bool):
        """Updates only the enabled/disabled state of a variable."""
        return self._make_request('PATCH', f'/variables/{name}/state', json={"enabled": is_enabled})
    def delete_variable(self, name: str):
        """Deletes a user-defined variable."""
        return self._make_request('DELETE', f'/variables/{name}')
    def trigger_scan_by_api(self):
        """Triggers the diagnostics scanner via an API call."""
        return self._make_request('POST', '/system/run-diagnostics')
    def get_job_status(self, job_id: str):
        """Gets the status of a long-running job."""
        return self._make_request('GET', f'/system/jobs/{job_id}')
    def get_marketplace_ads(self):
        """Fetches marketplace ad data directly from GitHub."""
        cache_key = "marketplace_ads"
        with self.cache_lock:
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if time.time() - timestamp < 3600: # Cache for 1 hour
                    return True, cached_data
        url = f"https://raw.githubusercontent.com/{self.marketplace_repo_owner}/{self.marketplace_repo_name}/{self.marketplace_branch}/ads.json"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            with self.cache_lock:
                self.cache[cache_key] = (data, time.time())
            return True, data
        except requests.exceptions.RequestException as e:
            return False, f"Network error fetching ads: {e}" # English Log
        except json.JSONDecodeError:
            return False, "Failed to parse ads.json." # English Log
    def get_marketplace_index(self, component_type: str):
        """Fetches a component index directly from the GitHub repository."""
        cache_key = f"marketplace_index_{component_type}"
        with self.cache_lock:
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if time.time() - timestamp < 3600: # Cache for 1 hour
                    return True, cached_data
        folder_map = {
            "modules": "modules", "plugins": "plugins", "widgets": "widgets", "presets": "presets",
            "triggers": "triggers", "ai_providers": "ai_providers", "ai_models": "ai_models"
        }
        folder_name = folder_map.get(component_type)
        if not folder_name: return False, f"Unknown component type for marketplace: {component_type}" # English Hardcode
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
            return False, f"Network error fetching marketplace index: {e}" # English Log
        except json.JSONDecodeError:
            return False, f"Failed to parse marketplace index.json for {component_type}." # English Hardcode