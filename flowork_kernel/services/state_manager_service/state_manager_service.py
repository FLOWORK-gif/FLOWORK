#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\services\state_manager_service\state_manager_service.py
# JUMLAH BARIS : 72
#######################################################################

import os
import json
import threading
from ..base_service import BaseService
class StateManagerService(BaseService):
    """
    Manages persistent state data for the entire application in a thread-safe manner.
    Data is stored in JSON format in the data/state.json file.
    """
    STATE_FILE_NAME = "state.json"
    def __init__(self, kernel, service_id: str):
        super().__init__(kernel, service_id)
        self.data_path = self.kernel.data_path
        self.state_file_path = os.path.join(self.data_path, self.STATE_FILE_NAME)
        self._state_data = {}
        self._lock = threading.Lock()
        self.kernel.write_to_log("Service 'StateManager' initialized.", "DEBUG")
        self.load_state()
    def load_state(self):
        """Loads the state data from the JSON file into memory."""
        with self._lock:
            try:
                if os.path.exists(self.state_file_path):
                    with open(self.state_file_path, 'r', encoding='utf-8') as f:
                        self._state_data = json.load(f)
                    self.kernel.write_to_log(f"StateManager: State loaded successfully from {self.state_file_path}", "INFO")
                else:
                    self._state_data = {}
                    self.kernel.write_to_log("StateManager: state.json not found. A new state will be created.", "INFO")
            except (IOError, json.JSONDecodeError) as e:
                self.kernel.write_to_log(f"StateManager: Failed to load state from file: {e}. Using empty state.", "ERROR")
                self._state_data = {}
    def _save_state_to_file(self):
        """Saves the entire state data from memory to the JSON file."""
        self.kernel.write_to_log(f"StateManagerService: Attempting to save state to file: {self.state_file_path}", "DEBUG")
        try:
            with open(self.state_file_path, 'w', encoding='utf-8') as f:
                json.dump(self._state_data, f, indent=4)
            self.kernel.write_to_log(f"StateManagerService: State successfully saved to file.", "DEBUG")
        except IOError as e:
            self.kernel.write_to_log(f"StateManagerService: FAILED to save state to file. Error: {e}", "ERROR")
    def get(self, key, default=None):
        """Retrieves a value from the state."""
        with self._lock:
            return self._state_data.get(key, default)
    def set(self, key, value):
        """Sets or updates a value in the state and saves it to the file immediately."""
        self.kernel.write_to_log(f"StateManagerService: set() called for key '{key}'.", "DEBUG")
        with self._lock:
            self._state_data[key] = value
            self._save_state_to_file()
        self.kernel.write_to_log(f"StateManager: State for key '{key}' has been set.", "DEBUG")
    def delete(self, key):
        """Deletes a key and its value from the state and saves the changes."""
        with self._lock:
            if key in self._state_data:
                del self._state_data[key]
                self._save_state_to_file()
                self.kernel.write_to_log(f"StateManager: State for key '{key}' has been deleted.", "DEBUG")
            else:
                self.kernel.write_to_log(f"StateManager: Attempted to delete non-existent key '{key}'.", "WARN")
    def get_all(self):
        """Returns a copy of the entire state data."""
        with self._lock:
            return self._state_data.copy()
