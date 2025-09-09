#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\api_contract.py
# JUMLAH BARIS : 111
#######################################################################

```py
# ADDED: This is the local contract file for the GUI.
# It defines the basic structures that GUI components must follow,
# removing the need to import from the forbidden flowork_kernel.

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Callable
import ttkbootstrap as ttk
# ADDED: Import StringVar for EnumVarWrapper
from tkinter import StringVar

class BaseUIProvider(ABC):
    """
    Local GUI contract for modules that provide UI components.
    """
    @abstractmethod
    def get_ui_tabs(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get_menu_items(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

class BaseDashboardWidget(ttk.Frame, ABC):
    """
    Local GUI contract for all custom dashboard widgets.
    """
    def __init__(self, parent, coordinator_tab, api_client, loc_service, widget_id: str, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.coordinator_tab = coordinator_tab
        self.api_client = api_client
        self.loc = loc_service
        self.widget_id = widget_id

    @abstractmethod
    def on_widget_load(self):
        pass

    @abstractmethod
    def on_widget_destroy(self):
        pass

    @abstractmethod
    def refresh_content(self):
        pass

    def get_widget_state(self) -> dict:
        return {}

    def load_widget_state(self, state: dict):
        pass

# ADDED: Copied from server contract to make GUI independent.
class IDynamicOutputSchema(ABC):
    """
    An interface for modules whose output data schema can change dynamically
    based on their current configuration.
    """
    @abstractmethod
    def get_dynamic_output_schema(self, current_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Returns a list of output schema dictionaries based on the node's config.
        Example: [{'name': 'data.user_name', 'type': 'string', 'description': '...'}]
        """
        raise NotImplementedError

# ADDED: Copied from server contract to make GUI independent.
class EnumVarWrapper:
    """
    Wrapper for a StringVar that handles conversion between UI labels (which are localized)
    and internal values for enum-type properties.
    """
    def __init__(self, string_var: StringVar, label_to_value_map: Dict[str, str], value_to_label_map: Dict[str, str]):
        self.sv = string_var
        self.label_to_value_map = label_to_value_map
        self.value_to_label_map = value_to_label_map

    def get(self):
        """Returns the actual internal value."""
        return self.label_to_value_map.get(self.sv.get(), self.sv.get())

    def set(self, value):
        """Sets the StringVar based on the given internal value."""
        self.sv.set(self.value_to_label_map.get(value, value))

    def trace_add(self, mode, callback):
        """Passes the trace call to the underlying StringVar."""
        self.sv.trace_add(mode, callback)

# ADDED: Copied from server contract to make GUI independent.
class LoopConfig:
    """
    Data structure for defining loop configuration on a step.
    This will be used in module properties or as part of the node data.
    """
    LOOP_TYPE_COUNT = "count"
    LOOP_TYPE_CONDITION = "condition"
    def __init__(self, loop_type: str = LOOP_TYPE_COUNT, iterations: int = 1, condition_var: str = None, condition_op: str = None, condition_val: Any = None,
                 enable_sleep: bool = False, sleep_type: str = "static", static_duration: int = 1, random_min: int = 1, random_max: int = 5):
        if loop_type not in [self.LOOP_TYPE_COUNT, self.LOOP_TYPE_CONDITION]:
            raise ValueError(f"Invalid loop type: {loop_type}. Must be '{self.LOOP_TYPE_COUNT}' or '{self.LOOP_TYPE_CONDITION}'.")
        self.loop_type = loop_type
        self.iterations = iterations
        self.condition_var = condition_var
        self.condition_op = condition_op
        self.condition_val = condition_val
        self.enable_sleep = enable_sleep
        self.sleep_type = sleep_type
        self.static_duration = static_duration
        self.random_min = random_min
        self.random_max = random_max
```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\backup.py
# JUMLAH BARIS : 64
#######################################################################

```py
import os
import sys

def main():
    """
    Scans the project directory for all .py files, formats them into a markdown file,
    and saves it as backup.md. This script is designed to package the current
    state of the code for analysis or sharing.
    """
    project_root = os.getcwd()
    output_filename = "GUI.md"

    # ADDED: List of directories to ignore during the scan
    ignore_dirs = {'.venv', '__pycache__', 'python','vendor'}

    all_content = []

    print("[INFO] Starting code backup process...") # English Log

    for root, dirs, files in os.walk(project_root, topdown=True):
        # ADDED: This line efficiently skips the ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for file in sorted(files):
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, project_root)

                print(f"[INFO] Processing: {relative_path}") # English Log

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        line_count = len(content.splitlines())

                    # ADDED: Header generation logic
                    header = (
                        f"#######################################################################\n"
                        f"# dev : awenk audico\n"
                        f"# EMAIL SAHIDINAOLA@GMAIL.COM\n"
                        f"# WEBSITE https://github.com/FLOWORK-gif/FLOWORK\n"
                        f"# File NAME : {os.path.abspath(file_path)}\n"
                        f"# JUMLAH BARIS : {line_count}\n"
                        f"#######################################################################\n\n"
                    )

                    # ADDED: Markdown code block formatting
                    formatted_content = f"```py\n{content}\n```"

                    all_content.append(header + formatted_content)

                except Exception as e:
                    print(f"[ERROR] Could not process file {relative_path}: {e}") # English Log

    # ADDED: Writing the final backup.md file
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write("\n\n".join(all_content))
        print(f"\n[SUCCESS] Backup complete! All code saved to '{output_filename}'") # English Log
    except Exception as e:
        print(f"\n[FATAL] Failed to write backup file: {e}") # English Log

if __name__ == "__main__":
    main()
```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\main_gui.py
# JUMLAH BARIS : 225
#######################################################################

```py
import tkinter as tk
from tkinter import ttk
import threading
import subprocess
import os
import sys
import time
import traceback
import json
import ttkbootstrap as ttk
import websocket

# ADDED: This is the correct way to set up the project path.
# It ensures all subsequent imports work correctly.
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# MODIFIED: Corrected local imports. They should not start with 'flowork_gui.'
# because the project_root is now correctly added to the path.
from api_client.client import ApiClient
from views.ui_components.menubar_manager import MenubarManager
from views.ui_components.tab_manager import UITabManager
from views.custom_widgets.draggable_notebook import DraggableNotebook

PID_FILE = os.path.join(project_root, "pre_launcher.pid")
GIF_PATH = os.path.join(project_root, "teetah.gif")
DEV_MODE_FILE = os.path.join(project_root, "devmode.on")
API_KEY_FILE = os.path.join(os.path.dirname(__file__), "api_key.json")
DEV_MODE_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAysqZG2+F82W0TgLHmF3Y
0GRPEZvXvmndTY84N/wA1ljt+JxMBVsmcVTkv8f1TrmFRD19IDzl2Yzb2lgqEbEy
GFxHhudC28leDsVEIp8B+oYWVm8Mh242YKYK8r5DAvr9CPQivnIjZ4BWgKKddMTd
harVxLF2CoSoTs00xWKd6VlXfoW9wdBvoDVifL+hCMepgLLdQQE4HbamPDJ3bpra
pCgcAD5urmVoJEUJdjd+Iic27RBK7jD1dWDO2MASMh/0IyXyM8i7RDymQ88gZier
U0OdWzeCWGyl4EquvR8lj5GNz4vg2f+oEY7h9AIC1f4ARtoihc+apSntqz7nAqa/
sQIDAQAB
-----END PUBLIC KEY-----"""

class ApplicationWindow(ttk.Window):
    def __init__(self, api_client):
        super().__init__(themename="darkly")
        self.api_client = api_client
        self.withdraw()
        self.title("FLOWORK GUI") # English Hardcode
        self.tab_manager = None
        self.menubar_manager = None
        self.websocket_thread = None
        self.websocket_connection = None
        self.preloader = ttk.Toplevel(self)
        self.preloader.overrideredirect(True)
        self.preloader.attributes('-topmost', True)
        width, height = 300, 180
        screen_width, screen_height = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = (screen_width // 2) - (width // 2), (screen_height // 2) - (height // 2)
        self.preloader.geometry(f'{width}x{height}+{x}+{y}')
        self.preloader.config(bg="#2c3e50")
        preloader_style = ttk.Style()
        preloader_style.configure("Preload.TLabel", background="#2c3e50", foreground="#ecf0f1", font=("Helvetica", 11))
        logo_label = ttk.Label(self.preloader, style="Preload.TLabel")
        logo_label.pack(pady=(20, 10))
        try:
            self.logo_photo = tk.PhotoImage(file=GIF_PATH)
            logo_label.config(image=self.logo_photo)
        except Exception:
            logo_label.config(text="Teetah") # Fallback text
        self.status_label = ttk.Label(self.preloader, text="Initializing GUI...", style="Preload.TLabel") # English Hardcode
        self.status_label.pack(pady=(5, 20), fill="x", padx=10)

    def update_status(self, text):
        if self.preloader.winfo_exists():
            self.status_label.config(text=text)

    def close_preloader(self):
        if self.preloader.winfo_exists():
            self.preloader.destroy()

    def initialize_main_ui(self):
        self.close_preloader()

        class TempLoc:
            def get(self, key, fallback=None, **kwargs):
                if fallback is None:
                    return f"[{key}]"
                return fallback.format(**kwargs)

        self.loc = TempLoc()
        self.title(self.loc.get('app_title', fallback="FLOWORK - API Driven"))
        self.geometry("1280x800")

        self.menubar_manager = MenubarManager(self, self.api_client, self.loc)
        self.menubar_manager.build_menu()

        self.create_main_widgets()

        self.tab_manager = UITabManager(self, self.notebook, self.api_client, self.loc)
        self.notebook.set_close_tab_command(lambda tab_id: self.tab_manager.close_tab(tab_id))
        self.tab_manager.load_session_state()

        self.deiconify()
        self._start_websocket_thread()

    def _start_websocket_thread(self):
        if self.websocket_thread and self.websocket_thread.is_alive():
            return
        self.websocket_thread = threading.Thread(target=self._maintain_websocket_connection, daemon=True)
        self.websocket_thread.start()

    def _maintain_websocket_connection(self):
        ws_url = self.api_client.base_url.replace("http", "ws") + "/ws/status"
        print(f"Attempting to connect to WebSocket at: {ws_url}") # English Log
        while True:
            try:
                ws = websocket.create_connection(ws_url)
                self.websocket_connection = ws
                print("WebSocket connection established successfully.") # English Log
                while True:
                    ws.recv()
            except websocket.WebSocketConnectionClosedException:
                print("WebSocket connection closed. Reconnecting in 5 seconds...") # English Log
            except ConnectionRefusedError:
                print("WebSocket connection refused. Server might be down. Retrying in 5 seconds...") # English Log
            except Exception as e:
                print(f"An unexpected WebSocket error occurred: {e}. Retrying in 5 seconds...") # English Log
            self.websocket_connection = None
            time.sleep(5)

    def create_main_widgets(self):
        tab_bar_frame = ttk.Frame(self)
        tab_bar_frame.pack(fill='x', padx=5, pady=(5, 0))

        ttk.Button(tab_bar_frame,
                   text=self.loc.get('save_session_button', fallback="Save Session & Layout"),
                   style="info.TButton").pack(side="right", anchor='n', pady=2, padx=(2, 0))

        ttk.Button(tab_bar_frame,
                   text=self.loc.get('clear_cache_button', fallback="Clear Cache"),
                   style="secondary.TButton").pack(side="right", anchor='n', pady=2, padx=(2, 0))

        ttk.Button(tab_bar_frame, text=self.loc.get('clear_layout_button', fallback="Clear Layout"),
                   style="danger.TButton").pack(side="right", anchor='n', pady=2, padx=(2, 0))

        add_button = ttk.Button(tab_bar_frame, text="+", width=2,
                                command=lambda: self.tab_manager.add_new_workflow_tab(),
                                style="success.TButton")
        add_button.pack(side="right", anchor="n", pady=2, padx=(2, 0))

        self.notebook = DraggableNotebook(self, loc=self.loc)
        self.notebook.pack(expand=True, fill="both", padx=5, pady=(0, 5))

    def check_server_status(self):
        pass

def _validate_dev_mode():
    if not os.path.exists(DEV_MODE_FILE):
        return False
    try:
        with open(DEV_MODE_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        if content == DEV_MODE_PUBLIC_KEY.strip():
            print("DEV MODE VALIDATED: Key matches.") # English log
            return True
        else:
            print("DEV MODE FAILED: Key does not match.") # English log
            return False
    except Exception as e:
        print(f"DEV MODE FAILED: Error reading file - {e}") # English log
        return False

def connect_to_server_task(app_window):
    try:
        is_dev_mode = _validate_dev_mode()
        if is_dev_mode:
            app_window.update_status("DEVELOPMENT MODE ACTIVE") # English Hardcode
            time.sleep(1)

        api_client = app_window.api_client
        max_retries = 10
        retry_delay = 2

        for attempt in range(max_retries):
            app_window.update_status(f"Connecting to server at {api_client.base_url}...\n(Attempt {attempt + 1}/{max_retries})")
            status = api_client.get_server_status()
            if status and status.get("status") == "ok":
                api_key = status.get("api_key")
                if api_key:
                    api_client.api_key = api_key
                    with open(API_KEY_FILE, 'w', encoding='utf-8') as f:
                        json.dump({"api_key": api_key}, f)
                    print(f"[INFO] Secure API key received and set for this session.") # English Log
                app_window.update_status("Connection successful!\nLaunching main window...") # English Hardcode
                time.sleep(1)
                app_window.after(100, app_window.initialize_main_ui)
                return

            time.sleep(retry_delay)

        error_message = (f"Failed to connect to the server at {api_client.base_url} after {max_retries} attempts.\n\n"
                         f"Please ensure the FLOWORK server is running and the URL in 'gui_config.json' is correct.")
        raise ConnectionError(error_message)

    except Exception as e:
        error_message = f"A fatal error occurred:\n{e}" # English Hardcode
        app_window.update_status(error_message)
        print(traceback.format_exc())
        time.sleep(15)
        app_window.destroy()

if __name__ == "__main__":
    try:
        with open(PID_FILE, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))

        client = ApiClient()
        app = ApplicationWindow(api_client=client)

        threading.Thread(target=connect_to_server_task, args=(app,), daemon=True).start()

        app.mainloop()
    finally:
        if os.path.exists(PID_FILE):
            try:
                os.remove(PID_FILE)
            except OSError:
                pass
```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\api_client\__init__.py
# JUMLAH BARIS : 0
#######################################################################

```py

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\api_client\client.py
# JUMLAH BARIS : 120
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\api_client\client.py
# JUMLAH BARIS : 119
#######################################################################

import requests
import json
import os
GUI_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "gui_config.json")
API_KEY_FILE = os.path.join(os.path.dirname(__file__), "api_key.json")
class ApiClient:
    """
    Handles all HTTP communication with the FLOWORK server kernel.
    (REFACTORED) Now reads the server URL from a config file to be fully portable.
    """
    def __init__(self): # MODIFIED: No longer takes base_url as an argument
        self.base_url = self._load_server_url()
        self.api_key = self._load_api_key()
        print(f"ApiClient initialized for server at {self.base_url}")
    def _load_server_url(self):
        """
        ADDED: Loads the server URL from gui_config.json.
        Creates a default if it doesn't exist.
        """
        default_url = "http://127.0.0.1:8989"
        try:
            if os.path.exists(GUI_CONFIG_FILE):
                with open(GUI_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    url = config.get("server_url")
                    if url:
                        return url.rstrip('/') # Ensure no trailing slash
            with open(GUI_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump({"server_url": default_url}, f, indent=4)
            return default_url
        except (IOError, json.JSONDecodeError) as e:
            print(f"[API_CLIENT_ERROR] Could not read or create gui_config.json: {e}. Using default URL.") # English Log
            return default_url
    def _load_api_key(self):
        """Loads the API key from a local JSON file."""
        try:
            if os.path.exists(API_KEY_FILE):
                with open(API_KEY_FILE, 'r', encoding='utf-8') as f:
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

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\components\__init__.py
# JUMLAH BARIS : 0
#######################################################################

```py

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\components\main_window.py
# JUMLAH BARIS : 28
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\components\main_window.py
# JUMLAH BARIS : 27
#######################################################################

import tkinter as tk
from tkinter import ttk
class MainWindow(tk.Tk):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
        self.title("FLOWORK GUI - API Driven")
        self.geometry("800x600")
        self.create_widgets()
        self.check_server_status()
    def create_widgets(self):
        self.label = ttk.Label(self, text="Connecting to FLOWORK Server...", font=("Helvetica", 16))
        self.label.pack(pady=50, padx=20)
    def check_server_status(self):
        status_data = self.api_client.get_server_status()
        if status_data and status_data.get("status") == "ok":
            self.label.config(text=f"Server Status: {status_data.get('message', 'Connected')}", foreground="green")
        else:
            message = status_data.get('message', 'Connection failed')
            self.label.config(text=f"Server Status: Error - {message}", foreground="red")

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\modules\__init__.py
# JUMLAH BARIS : 0
#######################################################################

```py

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\modules\debug_popup_module\__init__.py
# JUMLAH BARIS : 0
#######################################################################

```py

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\modules\debug_popup_module\processor.py
# JUMLAH BARIS : 72
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\modules\debug_popup_module\processor.py
# JUMLAH BARIS : 47
#######################################################################

from flowork_kernel.api_contract import BaseModule
import json
# COMMENT: UI libraries like ttkbootstrap and tkinter should not be imported in a kernel module.
# This violates the core principle of separating the kernel from the GUI.
# The kernel should only send data or simple commands, and the GUI should handle the rendering.
# import ttkbootstrap as ttk
# from tkinter import scrolledtext

class DebugPopupModule(BaseModule):
    TIER = "free"
    def __init__(self, module_id, services):
        super().__init__(module_id, services)
        self._active_popups = {}

    def _show_popup_on_ui_thread(self, node_instance_id, title, data_string):
        # COMMENT: This method defines UI-specific code (Toplevel, ScrolledText) inside a kernel module.
        # This creates a strong coupling between the kernel and a specific UI framework (Tkinter).
        # According to the rules, this logic should be moved to the GUI side.
        # The kernel should instead send a generic request via ui_callback.
        if node_instance_id in self._active_popups and self._active_popups[node_instance_id].winfo_exists():
            self._active_popups[node_instance_id].destroy()
            self.logger("An existing debug popup for this node was found and automatically closed.", "INFO") # English Log

        # COMMENT: The following code is an example of a UI-dependent implementation that should be avoided in the kernel.
        # It is left here for reference but will fail because the imports are commented out.
        #
        # popup = ttk.Toplevel(title=title)
        # popup.geometry("600x400")
        # txt_area = scrolledtext.ScrolledText(popup, wrap="word", width=70, height=20)
        # txt_area.pack(expand=True, fill="both", padx=10, pady=10)
        # txt_area.insert("1.0", data_string)
        # txt_area.config(state="disabled")
        # self._active_popups[node_instance_id] = popup
        #
        # def _on_popup_close():
        #     self.logger("Debug popup was closed manually by the user.", "DEBUG") # English Log
        #     if node_instance_id in self._active_popups:
        #         del self._active_popups[node_instance_id]
        #     popup.destroy()
        #
        # popup.protocol("WM_DELETE_WINDOW", _on_popup_close)
        # popup.transient()
        # popup.grab_set()
        pass # ADDED: Added pass to prevent syntax error after commenting out.

    def execute(self, payload, config, status_updater, ui_callback, mode='EXECUTE'):
        node_instance_id = config.get('__internal_node_id', self.module_id)
        status_updater("Preparing popup...", "INFO") # English Log
        try:
            payload_str = json.dumps(payload, indent=4, ensure_ascii=False, default=str)
        except Exception:
            payload_str = str(payload)

        popup_title = "Debug Output From Previous Node" # English Hardcode

        # COMMENT: The current implementation passes a function reference to the UI, which contains UI code.
        # A better, fully decoupled approach is to send a generic command and data payload.
        # Example of a better approach:
        # ui_callback('show_generic_popup', {'title': popup_title, 'content': payload_str, 'node_id': node_instance_id})
        # The GUI would then be responsible for interpreting 'show_generic_popup' and creating the appropriate window.
        ui_callback(self._show_popup_on_ui_thread, node_instance_id, popup_title, payload_str)

        status_updater("Popup displayed", "SUCCESS") # English Log
        return payload
```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\modules\prompt_receiver_module\__init__.py
# JUMLAH BARIS : 0
#######################################################################

```py

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\modules\prompt_receiver_module\processor.py
# JUMLAH BARIS : 93
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\modules\prompt_receiver_module\processor.py
# JUMLAH BARIS : 92
#######################################################################

from flowork_kernel.core import build_security
import ttkbootstrap as ttk
from tkinter import StringVar
from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI
from flowork_kernel.api_contract import IDataPreviewer
class PromptReceiverModule(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer):
    """
    Listens for a specific event containing a prompt and then triggers the
    workflow execution from this node onwards.
    """
    TIER = "free"
    def __init__(self, module_id, services):
        build_security.perform_runtime_check(__file__)
        super().__init__(module_id, services)
        self.parent_frame_for_clipboard = None
        self.node_instance_id = None
    def on_canvas_load(self, node_id: str):
        """
        Called by the CanvasManager right after this node is placed on the canvas.
        This is the perfect moment to start listening for events.
        """
        self.node_instance_id = node_id
        event_name = f"PROMPT_FROM_WIDGET_{self.node_instance_id}"
        subscriber_id = f"prompt_receiver_{self.node_instance_id}"
        self.event_bus.subscribe(
            event_name=event_name,
            subscriber_id=subscriber_id,
            callback=self._handle_prompt_event
        )
        self.logger(f"Receiver node '{self.node_instance_id}' is now listening for event '{event_name}'.", "SUCCESS")
    def execute(self, payload, config, status_updater, ui_callback, mode='EXECUTE'):
        """
        When this node is triggered, it simply passes the received payload
        to its output port to continue the flow.
        """
        self.node_instance_id = config.get('__internal_node_id', self.node_instance_id or self.module_id)
        status_updater(f"Passing data through...", "INFO")
        status_updater("Data received and passed.", "SUCCESS")
        return {"payload": payload, "output_name": "output"}
    def _handle_prompt_event(self, event_data):
        """
        This is the callback that gets triggered by the Event Bus.
        It starts the workflow execution from this node.
        """
        prompt = event_data.get("prompt")
        self.logger(f"Received prompt for node '{self.node_instance_id}': '{prompt[:50]}...'", "INFO")
        new_payload = {
            "data": {"prompt": prompt},
            "history": []
        }
        if self.kernel:
            self.kernel.trigger_workflow_from_node(self.node_instance_id, new_payload)
    def _copy_node_id_to_clipboard(self, node_id):
        """Copies the node ID to the clipboard."""
        if self.parent_frame_for_clipboard:
            self.parent_frame_for_clipboard.clipboard_clear()
            self.parent_frame_for_clipboard.clipboard_append(node_id)
            self.logger(f"Receiver ID '{node_id}' copied to clipboard.", "SUCCESS")
    def create_properties_ui(self, parent_frame, get_current_config, available_vars):
        """Creates the UI for the properties popup."""
        config = get_current_config()
        self.parent_frame_for_clipboard = parent_frame
        node_id = self.node_instance_id
        info_frame = ttk.LabelFrame(parent_frame, text="Receiver Info", padding=10)
        info_frame.pack(fill='x', padx=5, pady=10)
        id_info_text = f"This node listens for prompts sent to its unique ID. Copy this ID and paste it into a 'Prompt Sender' widget.\n\nID: {node_id}"
        ttk.Label(info_frame, text=id_info_text, wraplength=350, justify="left").pack(anchor='w', fill='x', expand=True, pady=(0, 10))
        copy_button = ttk.Button(
            info_frame,
            text="Copy ID",
            command=lambda: self._copy_node_id_to_clipboard(node_id),
            bootstyle="info-outline"
        )
        copy_button.pack(anchor='e')
        return {}
    def get_data_preview(self, config: dict):
        """
        TODO: Implement the data preview logic for this module.
        This method should return a small, representative sample of the data
        that the 'execute' method would produce.
        It should run quickly and have no side effects.
        """
        self.logger(f"'get_data_preview' is not yet implemented for {self.module_id}", 'WARN')
        return [{'status': 'preview not implemented'}]
_UNUSED_SIGNATURE = 'B3Ba%m#rDeKa' # Embedded Signature

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\__init__.py
# JUMLAH BARIS : 0
#######################################################################

```py

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\__init__.py
# JUMLAH BARIS : 0
#######################################################################

```py

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\ai_architect_page.py
# JUMLAH BARIS : 147
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\ai_architect_page.py
# JUMLAH BARIS : 146
#######################################################################

import ttkbootstrap as ttk
from tkinter import scrolledtext, messagebox
import threading
import re
from flowork_gui.api_client.client import ApiClient
class AiArchitectPage(ttk.Frame):
    """
    The user interface for the AI Architect feature, allowing users to generate
    workflows from natural language prompts.
    """
    def __init__(self, parent_notebook, kernel_instance):
        self.api_client = ApiClient()
        super().__init__(parent_notebook, padding=0) # MODIFIKASI: padding diatur di frame konten
        self.kernel = kernel_instance
        self.loc = self.kernel.get_service("localization_manager")
        self.guide_is_pinned = False
        self.hide_guide_job = None
        self._build_ui()
        self._populate_guide()
    def _apply_markdown_to_text_widget(self, text_widget, content):
        text_widget.config(state="normal")
        text_widget.delete("1.0", "end")
        parts = re.split(r'(\*\*.*?\*\*)', content)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                text_widget.insert("end", part[2:-2], "bold")
            else:
                text_widget.insert("end", part)
        text_widget.config(state="disabled")
    def _populate_guide(self):
        guide_content = self.loc.get("ai_architect_guide_content")
        self._apply_markdown_to_text_widget(self.guide_text, guide_content)
        self.guide_text.tag_configure("bold", font="-size 9 -weight bold")
    def _build_ui(self):
        """Builds the main widgets for the page."""
        main_content_frame = ttk.Frame(self, padding=20)
        main_content_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        main_content_frame.columnconfigure(0, weight=1)
        main_content_frame.rowconfigure(1, weight=1)
        header_frame = ttk.Frame(main_content_frame)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(header_frame, text=self.loc.get('ai_architect_page_title', fallback="AI Architect"), font=("Helvetica", 16, "bold")).pack(side="left", anchor="w")
        self.status_label = ttk.Label(header_frame, text=self.loc.get('ai_architect_status_ready', fallback="Ready."), bootstyle="secondary")
        self.status_label.pack(side="right", anchor="e")
        self.prompt_text = scrolledtext.ScrolledText(main_content_frame, wrap="word", height=10, font=("Helvetica", 11))
        self.prompt_text.grid(row=1, column=0, sticky="nsew")
        self.prompt_text.insert("1.0", self.loc.get('ai_architect_prompt_placeholder', fallback="Example: Create a workflow that gets data from a web scraper..."))
        button_container = ttk.Frame(main_content_frame)
        button_container.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        button_container.columnconfigure(0, weight=1)
        self.generate_button = ttk.Button(button_container, text=self.loc.get('ai_architect_generate_button', fallback="🚀 Generate Workflow"), command=self._start_generation_thread, bootstyle="success")
        self.generate_button.grid(row=0, column=0, sticky="ew", ipady=5)
        guide_handle = ttk.Frame(self, width=15, bootstyle="secondary")
        guide_handle.place(relx=0, rely=0, relheight=1, anchor='nw')
        handle_label = ttk.Label(guide_handle, text=">", bootstyle="inverse-secondary", font=("Helvetica", 10, "bold"))
        handle_label.pack(expand=True)
        guide_handle.bind("<Enter>", self._show_guide_panel)
        self.guide_panel = ttk.Frame(self, bootstyle="secondary")
        control_bar = ttk.Frame(self.guide_panel, bootstyle="secondary")
        control_bar.pack(fill='x', padx=5, pady=2)
        self.guide_pin_button = ttk.Button(control_bar, text="📌", bootstyle="light-link", command=self._toggle_pin_guide)
        self.guide_pin_button.pack(side='right')
        guide_frame_inner = ttk.LabelFrame(self.guide_panel, text=self.loc.get('ai_architect_guide_title'), padding=15)
        guide_frame_inner.pack(fill='both', expand=True, padx=5, pady=(0,5))
        guide_frame_inner.columnconfigure(0, weight=1)
        guide_frame_inner.rowconfigure(0, weight=1)
        self.guide_text = scrolledtext.ScrolledText(guide_frame_inner, wrap="word", height=10, state="disabled", font="-size 9")
        self.guide_text.grid(row=0, column=0, sticky="nsew")
        self.guide_panel.bind("<Leave>", self._hide_guide_panel_later)
        self.guide_panel.bind("<Enter>", self._cancel_hide_guide)
        guide_handle.lift() # Pastikan handle ada di lapisan paling atas
    def _start_generation_thread(self):
        if not self.kernel.is_tier_sufficient('architect'):
            messagebox.showwarning(
                self.loc.get('license_popup_title'),
                self.loc.get('license_popup_message', module_name="AI Architect"),
                parent=self.winfo_toplevel()
            )
            tab_manager = self.kernel.get_service("tab_manager_service")
            if tab_manager:
                tab_manager.open_managed_tab("pricing_page")
            return
        user_prompt = self.prompt_text.get("1.0", "end-1c").strip()
        if not user_prompt:
            messagebox.showwarning(
                self.loc.get('ai_architect_warn_empty_prompt_title', fallback="Empty Prompt"),
                self.loc.get('ai_architect_warn_empty_prompt_msg', fallback="Please describe the workflow you want to create.")
            )
            return
        self.generate_button.config(state="disabled")
        self.status_label.config(text=self.loc.get('ai_architect_status_thinking', fallback="Thinking..."), bootstyle="info")
        thread = threading.Thread(target=self._generate_workflow_worker, args=(user_prompt,), daemon=True)
        thread.start()
    def _generate_workflow_worker(self, user_prompt):
        try:
            architect_service = self.kernel.get_service("ai_architect_service")
            if not architect_service:
                raise RuntimeError("AiArchitectService not available.")
            workflow_json = architect_service.generate_workflow_from_prompt(user_prompt)
            self.after(0, self._on_generation_complete, True, workflow_json, user_prompt)
        except Exception as e:
            self.after(0, self._on_generation_complete, False, str(e), None)
    def _on_generation_complete(self, success, result, user_prompt):
        self.generate_button.config(state="normal")
        if success:
            self.status_label.config(text=self.loc.get('ai_architect_status_success', fallback="Success! New tab created."), bootstyle="success")
            tab_manager = self.kernel.get_service("tab_manager_service")
            new_tab = tab_manager.add_new_workflow_tab()
            self.after(100, lambda: self._populate_new_tab(new_tab, result, user_prompt))
        else:
            self.status_label.config(text=self.loc.get('ai_architect_status_failed', fallback="Failed."), bootstyle="danger")
            messagebox.showerror(
                self.loc.get('ai_architect_error_title', fallback="AI Architect Error"),
                self.loc.get('ai_architect_error_failed_to_create', error=result, fallback=f"Failed to create workflow:\n\n{result}")
            )
    def _populate_new_tab(self, new_tab_frame, workflow_json, user_prompt):
        if hasattr(new_tab_frame, 'canvas_area_instance') and new_tab_frame.canvas_area_instance:
            new_tab_frame.canvas_area_instance.canvas_manager.load_workflow_data(workflow_json)
            tab_title = user_prompt[:25] + '...' if len(user_prompt) > 25 else user_prompt
            self.kernel.get_service("tab_manager_service").notebook.tab(new_tab_frame, text=f" {tab_title} ")
        else:
            self.after(200, lambda: self._populate_new_tab(new_tab_frame, workflow_json, user_prompt))
    def _toggle_pin_guide(self):
        self.guide_is_pinned = not self.guide_is_pinned
        pin_char = "📌"
        self.guide_pin_button.config(text=pin_char)
        if not self.guide_is_pinned:
            self._hide_guide_panel_later()
    def _show_guide_panel(self, event=None):
        self._cancel_hide_guide()
        self.guide_panel.place(in_=self, relx=0, rely=0, relheight=1.0, anchor='nw', width=350)
        self.guide_panel.lift()
    def _hide_guide_panel_later(self, event=None):
        if not self.guide_is_pinned:
            self.hide_guide_job = self.after(300, lambda: self.guide_panel.place_forget())
    def _cancel_hide_guide(self, event=None):
        if self.hide_guide_job:
            self.after_cancel(self.hide_guide_job)
            self.hide_guide_job = None

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\ai_trainer_page.py
# JUMLAH BARIS : 240
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\ai_trainer_page.py
# JUMLAH BARIS : 239
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, messagebox, scrolledtext
import os
import re
import threading
import time
from widgets.dataset_manager_widget.dataset_manager_widget import DatasetManagerWidget
from flowork_gui.api_client.client import ApiClient
class AITrainerPage(ttk.Frame):
    """
    The main UI page for initiating and monitoring AI model fine-tuning jobs.
    [MODIFIED] Added a tutorial and guide panel.
    """
    def __init__(self, parent_notebook, kernel_instance):
        super().__init__(parent_notebook, padding=15)
        self.kernel = kernel_instance
        self.loc = self.kernel.get_service("localization_manager")
        self.api_client = ApiClient(kernel=self.kernel)
        self.guide_is_pinned = False
        self.hide_guide_job = None
        self.base_model_var = StringVar()
        self.dataset_var = StringVar()
        self.new_model_name_var = StringVar()
        self.epochs_var = StringVar(value="1")
        self.batch_size_var = StringVar(value="4")
        self.job_id = None
        self.is_polling = False
        self._build_ui()
        self._load_initial_data()
        self._populate_guide()
    def _apply_markdown_to_text_widget(self, text_widget, content):
        """ (ADDED) Helper function to parse simple markdown (bold). """
        text_widget.config(state="normal")
        text_widget.delete("1.0", "end")
        parts = re.split(r'(\*\*.*?\*\*)', content)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                text_widget.insert("end", part[2:-2], "bold")
            else:
                text_widget.insert("end", part)
        text_widget.config(state="disabled")
    def _populate_guide(self):
        guide_content = self.loc.get("ai_trainer_guide_content")
        self._apply_markdown_to_text_widget(self.guide_text, guide_content)
        self.guide_text.tag_configure("bold", font="-size 9 -weight bold")
    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_pane = ttk.PanedWindow(self, orient='horizontal')
        main_pane.grid(row=0, column=0, sticky="nsew")
        guide_handle = ttk.Frame(self, width=15, bootstyle="secondary")
        guide_handle.place(relx=0, rely=0, relheight=1, anchor='nw')
        handle_label = ttk.Label(guide_handle, text=">", bootstyle="inverse-secondary", font=("Helvetica", 10, "bold"))
        handle_label.pack(expand=True)
        guide_handle.bind("<Enter>", self._show_guide_panel)
        guide_handle.lift()
        self.guide_panel = ttk.Frame(self, bootstyle="secondary")
        control_bar = ttk.Frame(self.guide_panel, bootstyle="secondary")
        control_bar.pack(fill='x', padx=5, pady=2)
        self.guide_pin_button = ttk.Button(control_bar, text="📌", bootstyle="light-link", command=self._toggle_pin_guide)
        self.guide_pin_button.pack(side='right')
        guide_frame = ttk.LabelFrame(self.guide_panel, text=self.loc.get('ai_trainer_guide_title'), padding=15)
        guide_frame.pack(fill='both', expand=True, padx=5, pady=(0,5))
        guide_frame.columnconfigure(0, weight=1)
        guide_frame.rowconfigure(0, weight=1)
        self.guide_text = scrolledtext.ScrolledText(guide_frame, wrap="word", height=12, state="disabled", font="-size 9")
        self.guide_text.grid(row=0, column=0, sticky="nsew")
        self.guide_panel.bind("<Leave>", self._hide_guide_panel_later)
        self.guide_panel.bind("<Enter>", self._cancel_hide_guide)
        left_pane = ttk.Frame(main_pane, padding=10)
        main_pane.add(left_pane, weight=2)
        config_frame = ttk.LabelFrame(left_pane, text="1. Training Configuration", padding=15)
        config_frame.pack(fill='x', expand=False)
        base_model_frame = ttk.Frame(config_frame)
        base_model_frame.pack(fill='x', pady=(2, 10))
        base_model_frame.columnconfigure(1, weight=1)
        ttk.Label(base_model_frame, text="Base Model (for new training only):").grid(row=0, column=0, columnspan=3, sticky='w')
        self.model_combo = ttk.Combobox(base_model_frame, textvariable=self.base_model_var, state="readonly")
        self.model_combo.grid(row=1, column=0, columnspan=2, sticky='ew')
        refresh_model_button = ttk.Button(base_model_frame, text="⟳", width=3, command=self._load_initial_data, style="secondary.TButton")
        refresh_model_button.grid(row=1, column=2, padx=(5,0))
        ttk.Label(config_frame, text="Dataset for Training:").pack(anchor='w')
        self.dataset_combo = ttk.Combobox(config_frame, textvariable=self.dataset_var, state="readonly")
        self.dataset_combo.pack(fill='x', pady=(2, 10))
        ttk.Label(config_frame, text="New or Existing Model Name:").pack(anchor='w')
        self.new_model_name_combo = ttk.Combobox(config_frame, textvariable=self.new_model_name_var)
        self.new_model_name_combo.pack(fill='x', pady=(2, 10))
        params_frame = ttk.Frame(config_frame)
        params_frame.pack(fill='x', pady=5)
        ttk.Label(params_frame, text="Epochs:").pack(side='left')
        ttk.Entry(params_frame, textvariable=self.epochs_var, width=5).pack(side='left', padx=(5, 20))
        ttk.Label(params_frame, text="Batch Size:").pack(side='left')
        ttk.Entry(params_frame, textvariable=self.batch_size_var, width=5).pack(side='left', padx=5)
        self.dataset_manager = DatasetManagerWidget(
            left_pane,
            self.winfo_toplevel(),
            self.kernel,
            "ai_trainer_dataset_manager",
            refresh_callback=self._load_initial_data
        )
        self.dataset_manager.pack(fill='both', expand=True, pady=(10,0))
        right_pane = ttk.Frame(main_pane, padding=10)
        main_pane.add(right_pane, weight=3)
        monitor_frame = ttk.LabelFrame(right_pane, text="2. Training Monitor", padding=15)
        monitor_frame.pack(fill='both', expand=True)
        monitor_frame.rowconfigure(1, weight=1)
        monitor_frame.columnconfigure(0, weight=1)
        self.status_label = ttk.Label(monitor_frame, text="Status: Idle", font="-size 10")
        self.status_label.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        self.log_text = scrolledtext.ScrolledText(monitor_frame, wrap="word", state="disabled", height=15)
        self.log_text.grid(row=1, column=0, sticky='nsew')
        self.progress_bar = ttk.Progressbar(monitor_frame, mode='determinate')
        self.progress_bar.grid(row=2, column=0, sticky='ew', pady=(10, 10))
        self.start_button = ttk.Button(monitor_frame, text="🚀 Start Fine-Tuning Job", command=self._start_training_job, bootstyle="success")
        self.start_button.grid(row=3, column=0, sticky='ew', ipady=5)
    def _load_initial_data(self):
        threading.Thread(target=self._load_data_worker, daemon=True).start()
    def _load_data_worker(self):
        models_path = os.path.join(self.kernel.project_root_path, "ai_models", "text")
        local_models = []
        if os.path.isdir(models_path):
            local_models = [d for d in os.listdir(models_path) if os.path.isdir(os.path.join(models_path, d))]
        success, datasets_response = self.api_client.list_datasets()
        datasets = datasets_response if success else []
        self.after(0, self._populate_combos, local_models, datasets)
    def _populate_combos(self, models, datasets):
        sorted_models = sorted(models)
        self.model_combo['values'] = sorted_models
        self.new_model_name_combo['values'] = sorted_models
        if 'training' in sorted_models:
            self.base_model_var.set('training')
            self.new_model_name_var.set('training')
        elif sorted_models:
            if self.base_model_var.get() not in sorted_models:
                self.base_model_var.set(sorted_models[0])
        dataset_names = [ds['name'] for ds in datasets]
        self.dataset_combo['values'] = sorted(dataset_names)
        if dataset_names:
            if self.dataset_var.get() not in dataset_names:
                self.dataset_var.set(dataset_names[0])
        if hasattr(self, 'dataset_manager'):
            self.dataset_manager._populate_dataset_combo(True, datasets)
    def _start_training_job(self):
        base_model = self.base_model_var.get()
        dataset = self.dataset_var.get()
        new_model_name = self.new_model_name_var.get().strip()
        new_model_name = re.sub(r'[^a-zA-Z0-9_-]', '', new_model_name)
        if not all([base_model, dataset, new_model_name]):
            messagebox.showerror("Validation Error", "All fields (Base Model, Dataset, New/Existing Model Name) are required.", parent=self)
            return
        try:
            training_args = {
                "epochs": int(self.epochs_var.get()),
                "batch_size": int(self.batch_size_var.get())
            }
        except ValueError:
            messagebox.showerror("Validation Error", "Epochs and Batch Size must be numbers.", parent=self)
            return
        self.start_button.config(state="disabled")
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.insert("1.0", "Sending training job request to the server...\n")
        self.log_text.config(state="disabled")
        threading.Thread(
            target=self._start_training_worker,
            args=(base_model, dataset, new_model_name, training_args),
            daemon=True
        ).start()
    def _start_training_worker(self, base_model, dataset, new_model_name, args):
        success, response = self.api_client.start_training_job(base_model, dataset, new_model_name, args)
        self.after(0, self._on_job_started, success, response)
    def _on_job_started(self, success, response):
        if success:
            self.job_id = response.get('job_id')
            self.status_label.config(text=f"Status: Job {self.job_id} is QUEUED.")
            self._log_message(f"Training job successfully queued with ID: {self.job_id}")
            self._start_polling()
        else:
            messagebox.showerror("Job Error", f"Failed to start training job: {response}", parent=self)
            self.start_button.config(state="normal")
    def _start_polling(self):
        if not self.is_polling:
            self.is_polling = True
            self._poll_job_status()
    def _poll_job_status(self):
        if not self.job_id:
            self.is_polling = False
            return
        threading.Thread(target=self._poll_worker, daemon=True).start()
    def _poll_worker(self):
        success, response = self.api_client.get_training_job_status(self.job_id)
        self.after(0, self._update_status_ui, success, response)
    def _update_status_ui(self, success, response):
        if success:
            status = response.get('status', 'UNKNOWN')
            message = response.get('message', '')
            progress = response.get('progress', 0)
            self.status_label.config(text=f"Status: {status}")
            self._log_message(f"Update: {message}")
            self.progress_bar['value'] = progress
            if status in ["COMPLETED", "FAILED"]:
                self.is_polling = False
                self.start_button.config(state="normal")
                messagebox.showinfo("Training Finished", f"Job {self.job_id} finished with status: {status}", parent=self)
                self._load_initial_data()
            else:
                self.after(5000, self._poll_job_status)
        else:
            self._log_message(f"Error polling status: {response}")
            self.after(5000, self._poll_job_status)
    def _log_message(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
    def _toggle_pin_guide(self):
        self.guide_is_pinned = not self.guide_is_pinned
        pin_char = "📌"
        self.guide_pin_button.config(text=pin_char)
        if not self.guide_is_pinned:
            self._hide_guide_panel_later()
    def _show_guide_panel(self, event=None):
        self._cancel_hide_guide()
        self.guide_panel.place(in_=self, relx=0, rely=0, relheight=1.0, anchor='nw', width=350)
        self.guide_panel.lift()
    def _hide_guide_panel_later(self, event=None):
        if not self.guide_is_pinned:
            self.hide_guide_job = self.after(300, lambda: self.guide_panel.place_forget())
    def _cancel_hide_guide(self, event=None):
        if self.hide_guide_job:
            self.after_cancel(self.hide_guide_job)
            self.hide_guide_job = None

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\core_editor_page.py
# JUMLAH BARIS : 215
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\core_editor_page.py
# JUMLAH BARIS : 214
#######################################################################

import ttkbootstrap as ttk
from tkinter import ttk as tk_ttk
import os
import json
from tkinter import messagebox, scrolledtext, Menu, Toplevel
import re
from flowork_kernel.ui_shell.canvas_manager import CanvasManager
from flowork_gui.api_client.client import ApiClient
class CoreEditorPage(ttk.Frame):
    """
    The UI for the "Meta-Developer Mode" where core service
    workflows (.flowork files) can be visually edited.
    """
    def __init__(self, parent_notebook, kernel_instance):
        self.api_client = ApiClient()
        super().__init__(parent_notebook, padding=10)
        self.kernel = kernel_instance
        self.loc = self.kernel.get_service("localization_manager")
        self.canvas_manager = None
        self._drag_data = {}
        self.core_services_path = os.path.join(self.kernel.project_root_path, "core_services")
        self.guide_is_pinned = False
        self.hide_guide_job = None
        self._build_ui()
        self._populate_service_dropdown()
        self._populate_guide()
    def _apply_markdown_to_text_widget(self, text_widget, content):
        """ Helper function to parse simple markdown (bold). """
        text_widget.config(state="normal")
        text_widget.delete("1.0", "end")
        parts = re.split(r'(\*\*.*?\*\*)', content)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                text_widget.insert("end", part[2:-2], "bold")
            else:
                text_widget.insert("end", part)
        text_widget.config(state="disabled")
    def _populate_guide(self):
        """Populates the guide panel with localized content."""
        guide_content = self.loc.get("core_editor_guide_content")
        self._apply_markdown_to_text_widget(self.guide_text, guide_content)
        self.guide_text.tag_configure("bold", font="-size 9 -weight bold")
    def _toggle_pin_guide(self):
        """Toggles the pinned state of the guide panel."""
        self.guide_is_pinned = not self.guide_is_pinned
        pin_char = "📌" # Karakter pin solid
        self.guide_pin_button.config(text=pin_char)
        if not self.guide_is_pinned:
            self._hide_guide_panel_later()
    def _show_guide_panel(self, event=None):
        """Shows the guide panel."""
        self._cancel_hide_guide()
        self.guide_panel.place(in_=self.canvas_container, relx=0, rely=0, relheight=1.0, anchor='nw', width=350)
        self.guide_panel.lift()
    def _hide_guide_panel_later(self, event=None):
        """Schedules the guide panel to be hidden after a short delay."""
        if not self.guide_is_pinned:
            self.hide_guide_job = self.after(300, lambda: self.guide_panel.place_forget())
    def _cancel_hide_guide(self, event=None):
        """Cancels a scheduled hide job."""
        if self.hide_guide_job:
            self.after_cancel(self.hide_guide_job)
            self.hide_guide_job = None
    def _build_ui(self):
        """
        Builds the main layout with a service selector and a canvas.
        """
        control_frame = ttk.Frame(self)
        control_frame.pack(side="top", fill="x", padx=5, pady=(0, 10))
        ttk.Label(control_frame, text=self.loc.get('core_editor_select_service', fallback="Select Service to Edit:")).pack(side="left", padx=(0, 10))
        self.service_var = ttk.StringVar()
        self.service_dropdown = ttk.Combobox(control_frame, textvariable=self.service_var, state="readonly")
        self.service_dropdown.pack(side="left", fill="x", expand=True)
        self.service_dropdown.bind("<<ComboboxSelected>>", self._on_service_selected)
        self.save_button = ttk.Button(control_frame, text=self.loc.get('core_editor_save_button', fallback="Save Changes"), command=self._save_workflow_data, bootstyle="success", state="disabled")
        self.save_button.pack(side="left", padx=(10, 0))
        main_pane = ttk.PanedWindow(self, orient='horizontal')
        main_pane.pack(fill="both", expand=True)
        toolbox_frame = ttk.LabelFrame(main_pane, text="Toolbox", padding=10)
        main_pane.add(toolbox_frame, weight=1)
        self.module_tree = tk_ttk.Treeview(toolbox_frame, show="tree", selectmode="browse")
        self.module_tree.pack(expand=True, fill='both')
        self._populate_module_toolbox()
        self.module_tree.bind("<ButtonPress-1>", self._on_drag_start)
        self.module_tree.bind("<B1-Motion>", self._on_drag_motion)
        self.module_tree.bind("<ButtonRelease-1>", self._on_drag_release)
        canvas_container = ttk.LabelFrame(main_pane, text="Visual Workflow")
        main_pane.add(canvas_container, weight=4)
        self.canvas_container = canvas_container # Simpan referensi
        guide_handle = ttk.Frame(self.canvas_container, width=15, bootstyle="secondary")
        guide_handle.place(relx=0, rely=0, relheight=1, anchor='nw')
        handle_label = ttk.Label(guide_handle, text=">", bootstyle="inverse-secondary", font=("Helvetica", 10, "bold"))
        handle_label.pack(expand=True)
        guide_handle.bind("<Enter>", self._show_guide_panel)
        self.guide_panel = ttk.Frame(self.canvas_container, bootstyle="secondary")
        control_bar = ttk.Frame(self.guide_panel, bootstyle="secondary")
        control_bar.pack(fill='x', padx=5, pady=2)
        self.guide_pin_button = ttk.Button(control_bar, text="📌", bootstyle="light-link", command=self._toggle_pin_guide)
        self.guide_pin_button.pack(side='right')
        guide_frame = ttk.LabelFrame(self.guide_panel, text=self.loc.get('core_editor_guide_title'), padding=10)
        guide_frame.pack(fill='both', expand=True, padx=5, pady=(0,5))
        self.guide_text = scrolledtext.ScrolledText(guide_frame, wrap="word", height=10, state="disabled", font="-size 9")
        self.guide_text.pack(fill='both', expand=True)
        self.guide_panel.bind("<Leave>", self._hide_guide_panel_later)
        self.guide_panel.bind("<Enter>", self._cancel_hide_guide)
        class DummyCoordinatorTab(ttk.Frame):
            def __init__(self, kernel, editor_page):
                super().__init__()
                self.kernel = kernel
                self._execution_state = "IDLE"
                self.editor_page = editor_page
                self.bind = self.winfo_toplevel().bind
                self.unbind = self.winfo_toplevel().unbind
                self.unbind_all = self.winfo_toplevel().unbind_all
                self.after = self.winfo_toplevel().after
            def on_drag_release(self, event, item_id, tree_widget):
                self.editor_page._on_drag_release(event)
        dummy_tab = DummyCoordinatorTab(self.kernel, self)
        theme_manager = self.kernel.get_service("theme_manager")
        colors = theme_manager.get_colors() if theme_manager else {'bg': '#222'}
        canvas_widget = ttk.Canvas(canvas_container, background=colors.get('bg', '#222'))
        canvas_widget.pack(expand=True, fill='both')
        guide_handle.lift()
        self.canvas_manager = CanvasManager(canvas_container, dummy_tab, canvas_widget, self.kernel)
    def _populate_module_toolbox(self):
        module_manager = self.kernel.get_service("module_manager_service")
        if not module_manager: return
        logic_modules = {}
        action_modules = {}
        for mod_id, mod_data in module_manager.loaded_modules.items():
            manifest = mod_data.get("manifest", {})
            mod_type = manifest.get("type")
            if mod_type == "LOGIC":
                logic_modules[mod_id] = manifest.get("name", mod_id)
            elif mod_type == "ACTION":
                action_modules[mod_id] = manifest.get("name", mod_id)
        self.module_tree.insert('', 'end', iid='logic_category', text='Logic Modules', open=True)
        for mod_id, name in sorted(logic_modules.items(), key=lambda item: item[1]):
             self.module_tree.insert('logic_category', 'end', iid=mod_id, text=f" {name}")
        self.module_tree.insert('', 'end', iid='action_category', text='Action Modules', open=True)
        for mod_id, name in sorted(action_modules.items(), key=lambda item: item[1]):
             self.module_tree.insert('action_category', 'end', iid=mod_id, text=f" {name}")
    def _on_drag_start(self, event):
        item_id = self.module_tree.identify_row(event.y)
        if not item_id or self.module_tree.tag_has('category', item_id): return
        self._drag_data = {"item_id": item_id, "widget": ttk.Label(self.winfo_toplevel(), text=self.module_tree.item(item_id, "text").strip(), bootstyle="inverse-info", padding=5, relief="solid"), "tree_widget": self.module_tree}
    def _on_drag_motion(self, event):
        if self._drag_data.get("widget"):
            self._drag_data['widget'].place(x=event.x_root - self.winfo_toplevel().winfo_rootx() + 10, y=event.y_root - self.winfo_toplevel().winfo_rooty() + 10)
    def _on_drag_release(self, event):
        if self.canvas_manager and self._drag_data.get("item_id"):
            self.canvas_manager.interaction_manager.on_drag_release(event, self._drag_data["item_id"], self._drag_data["tree_widget"])
        if self._drag_data.get("widget"):
            self._drag_data["widget"].destroy()
        self._drag_data = {}
    def _populate_service_dropdown(self):
        if not os.path.isdir(self.core_services_path):
            self.service_dropdown['values'] = ["'core_services' folder not found!"]
            return
        service_files = [f for f in os.listdir(self.core_services_path) if f.endswith(".flowork")]
        self.service_dropdown['values'] = sorted(service_files)
        if service_files:
            self.service_dropdown.set(service_files[0])
            self._load_workflow_data(service_files[0])
    def _on_service_selected(self, event=None):
        self.save_button.config(state="disabled")
        selected_file = self.service_var.get()
        if selected_file:
            self._load_workflow_data(selected_file)
    def _load_workflow_data(self, filename):
        if not self.canvas_manager: return
        file_path = os.path.join(self.core_services_path, filename)
        self.kernel.write_to_log(f"Core Editor: Loading '{filename}'...", "INFO") # English Log
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)
            self.canvas_manager.load_workflow_data(workflow_data)
            self.kernel.write_to_log(f"Core Editor: Successfully rendered '{filename}'.", "SUCCESS") # English Log
            self.save_button.config(state="normal")
        except Exception as e:
            self.canvas_manager.clear_canvas(feedback=False)
            self.kernel.write_to_log(f"Core Editor: Failed to load or parse '{filename}': {e}", "ERROR") # English Log
            self.save_button.config(state="disabled")
            messagebox.showerror(
                self.loc.get('error_title', fallback="Error"),
                f"Failed to load service workflow '{filename}'.\nThe file might be corrupted or empty. Saving is disabled to prevent data loss.",
                parent=self
            )
    def _save_workflow_data(self):
        if not self.canvas_manager:
            messagebox.showerror("Error", "Canvas is not ready.")
            return
        selected_file = self.service_var.get()
        if not selected_file:
            messagebox.showwarning("Warning", "No service workflow is selected to save.")
            return
        workflow_data = self.canvas_manager.get_workflow_data()
        file_path = os.path.join(self.core_services_path, selected_file)
        self.kernel.write_to_log(f"Core Editor: Saving changes to '{selected_file}'...", "INFO") # English Log
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(workflow_data, f, indent=4, ensure_ascii=False)
            self.kernel.write_to_log(f"Core Editor: Successfully saved '{selected_file}'.", "SUCCESS") # English Log
            messagebox.showinfo("Success", f"Changes to '{selected_file}' have been saved.")
        except Exception as e:
            self.kernel.write_to_log(f"Core Editor: Failed to save '{selected_file}': {e}", "ERROR") # English Log
            messagebox.showerror("Error", f"Failed to save file: {e}")

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\core_ui_provider.py
# JUMLAH BARIS : 90
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\core_ui_provider.py
# JUMLAH BARIS : 101
#######################################################################

import ttkbootstrap as ttk
import re
# MODIFIED: Changed import from the forbidden flowork_kernel to the local GUI api_contract.
from api_contract import BaseUIProvider
from .ai_architect_page import AIArchitectPage
from .marketplace_page import MarketplacePage
from .pricing_page import PricingPage
from .settings_tab import SettingsTab
from .template_manager_page import TemplateManagerPage
from .trigger_manager_page import TriggerManagerPage
from .generator_page import GeneratorPage
from .core_editor_page import CoreEditorPage
from .agent_command_page import AgentCommandPage
from .model_converter_page import ModelConverterPage
from .ai_trainer_page import AITrainerPage

class CoreUIProvider(BaseUIProvider):
    """
    This is the central UI provider for all core Flowork functionalities.
    It registers all the main tabs that the user interacts with.
    """

    def __init__(self, plugin_id, services):
        """
        Initializes the CoreUIProvider.

        Args:
            plugin_id (str): The unique identifier for this plugin.
            services (dict): A dictionary of services provided by the kernel,
                             such as 'kernel', 'loc', and 'logger'.
        """
        # COMMENT: In a true GUI application, plugin_id and services would be managed differently,
        # likely passed during a more abstract initialization process.
        # For now, we assume these are provided by the GUI's main application logic.
        self.plugin_id = plugin_id
        self.kernel = services.get("kernel")
        self.loc = services.get("loc")
        self.logger = services.get("logger")
        self.logger(f"Plugin '{self.plugin_id}' initialized.", "INFO") # English Log

    def get_ui_tabs(self):
        """
        Returns a list of dictionaries, each defining a main tab for the application.
        """
        self.logger("CoreUIProvider: Providing core UI tabs.", "DEBUG") # English Log
        return [
            {'key': 'ai_architect', 'title_key': 'ai_architect_page_title', 'frame_class': AIArchitectPage},
            {'key': 'marketplace_page', 'title_key': 'marketplace_page_title', 'frame_class': MarketplacePage},
            {'key': 'pricing_page', 'title_key': 'pricing_page_title', 'frame_class': PricingPage},
            {'key': 'settings', 'title_key': 'settings_tab_title', 'frame_class': SettingsTab},
            {'key': 'template_manager', 'title_key': 'template_manager_page_title', 'frame_class': TemplateManagerPage},
            {'key': 'trigger_manager', 'title_key': 'trigger_manager_page_title', 'frame_class': TriggerManagerPage},
            {'key': 'generator_page', 'title_key': 'generator_page_title', 'frame_class': GeneratorPage}
        ]

    def get_menu_items(self):
        """
        Returns a list of dictionaries that define new items to be added to the main menubar.
        """
        self.logger("CoreUIProvider: Providing core menu items.", "DEBUG") # English Log

        # Helper function to create a lambda for opening tabs.
        # This is necessary to correctly capture the tab_key in the loop.
        def _create_open_tab_lambda(tab_key):
            return lambda: self.kernel.get_service("tab_manager_service").open_managed_tab(tab_key)

        # Base structure for menu items
        menu_items = [
            {"parent_key": "menu_file", "label_key": "menu_open_marketplace", "command": _create_open_tab_lambda('marketplace_page'), "add_separator": True},
            {"parent_key": "menu_file", "label_key": "menu_open_pricing_page", "command": _create_open_tab_lambda('pricing_page')},
            {"parent_key": "menu_tools", "label_key": "menu_agent_command_center", "command": _create_open_tab_lambda('agent_command_center')},
            {"parent_key": "menu_tools", "label_key": "menu_open_ai_architect", "command": _create_open_tab_lambda('ai_architect'), "add_separator": True},
            {"parent_key": "menu_tools", "label_key": "menu_open_ai_trainer", "command": _create_open_tab_lambda('ai_trainer')},
            {"parent_key": "menu_tools", "label_key": "menu_open_model_factory", "command": _create_open_tab_lambda('model_converter')},
            {"parent_key": "menu_developer", "label_key": "menu_open_generator", "command": _create_open_tab_lambda('generator_page')},
            {"parent_key": "menu_developer", "label_key": "menu_open_core_editor", "command": _create_open_tab_lambda('core_editor_page'), "add_separator": True},
            {"parent_key": "menu_settings", "label_key": "menu_open_settings_tab", "command": _create_open_tab_lambda('settings')},
            {"parent_key": "menu_settings", "label_key": "menu_manage_themes", "command": _create_open_tab_lambda('template_manager'), "add_separator": True},
            {"parent_key": "menu_settings", "label_key": "menu_manage_triggers", "command": _create_open_tab_lambda('trigger_manager')},
            {"parent_key": "menu_help", "label_key": "diagnostics_tab_title", "command": _create_open_tab_lambda('system_diagnostics'), "add_separator": True},
        ]
        return menu_items
```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\generator_page.py
# JUMLAH BARIS : 577
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\generator_page.py
# JUMLAH BARIS : 567
#######################################################################

import ttkbootstrap as ttk
from tkinter import ttk as tk_ttk, messagebox, Text, StringVar, BooleanVar, Toplevel, scrolledtext, Menu
import os
import json
import re
import uuid
import zipfile
import tempfile
import shutil
import importlib
import inspect
from tkinter import filedialog
from collections import OrderedDict
from .generator_components.base_component import BaseGeneratorComponent
from .generator_components.logic_builder_canvas import LogicBuilderCanvas
from flowork_gui.api_client.client import ApiClient
class GeneratorPage(ttk.Frame):
    """
    Page for the Generator Tools.
    [UPGRADE] Added a comprehensive tutorial panel to guide users through module creation.
    """
    DESIGN_STATE_KEY = "generator_page_last_state"
    def __init__(self, parent_notebook, kernel_instance):
        self.api_client = ApiClient()
        super().__init__(parent_notebook, style='TFrame')
        self.kernel = kernel_instance
        self.loc = self.kernel.get_service("localization_manager")
        self._drag_data = {}
        self.designed_components = {}
        self.selected_component_id = None
        self._is_updating_from_selection = False
        self.registered_components = {}
        self.guide_is_pinned = False
        self.hide_guide_job = None
        self.item_name_var = StringVar()
        self.item_id_var = StringVar()
        self.item_author_var = StringVar(value="Flowork Contributor")
        self.item_email_var = StringVar(value="contributor@teetah.art")
        self.item_website_var = StringVar(value="https://www.teetah.art")
        self.item_desc_text = None
        self.comp_prop_frame_content = None
        self._discover_and_load_components()
        self.create_widgets()
        self.item_name_var.trace_add("write", self._update_id_field)
        theme_manager = self.kernel.get_service("theme_manager")
        if theme_manager:
            self.apply_styles(theme_manager.get_colors())
        self.refresh_content()
        self._populate_guide()
        self.after(100, self._load_saved_design_state)
    def _apply_markdown_to_text_widget(self, text_widget, content):
        text_widget.config(state="normal")
        text_widget.delete("1.0", "end")
        parts = re.split(r'(\*\*.*?\*\*)', content)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                text_widget.insert("end", part[2:-2], "bold")
            else:
                text_widget.insert("end", part)
        text_widget.config(state="disabled")
    def _populate_guide(self):
        guide_content = self.loc.get("generator_guide_content")
        self._apply_markdown_to_text_widget(self.guide_text, guide_content)
        self.guide_text.tag_configure("bold", font="-size 9 -weight bold")
    def _save_current_design_state(self):
        state_manager = self.kernel.get_service("state_manager")
        if not state_manager:
            # MODIFIED: Changed messagebox to use loc.get and English fallbacks
            messagebox.showerror(self.loc.get('error_title', fallback="Error"), self.loc.get('generator_state_manager_unavailable', fallback="StateManager service not available."))
            return
        state_data = {
            "metadata": {
                "name": self.item_name_var.get(),
                "id": self.item_id_var.get(),
                "author": self.item_author_var.get(),
                "email": self.item_email_var.get(),
                "website": self.item_website_var.get(),
                "description": self.item_desc_text.get("1.0", "end-1c").strip()
            },
            "ui_components": [],
            "logic_definition": self.logic_builder_canvas.get_logic_data()
        }
        for comp_id, comp_data in self.designed_components.items():
            widget = comp_data['widget']
            state_data["ui_components"].append({
                "id": comp_id,
                "type": comp_data['type'],
                "config": comp_data['config'],
                "x": widget.winfo_x(),
                "y": widget.winfo_y()
            })
        state_manager.set(self.DESIGN_STATE_KEY, state_data)
        self.kernel.write_to_log("Generator design session saved successfully.", "SUCCESS")
        # MODIFIED: Changed messagebox to use loc.get and English fallbacks
        messagebox.showinfo(self.loc.get('success_title', fallback="Success"), self.loc.get('generator_design_saved_msg', fallback="Current design has been saved. It will be loaded automatically the next time you open this page."))
    def _load_saved_design_state(self):
        state_manager = self.kernel.get_service("state_manager")
        if not state_manager: return
        state_data = state_manager.get(self.DESIGN_STATE_KEY)
        if not state_data:
            self.kernel.write_to_log("No saved generator design found.", "INFO")
            return
        self.kernel.write_to_log("Loading saved generator design...", "INFO")
        try:
            self._clear_canvas(ask_confirmation=False)
            meta = state_data.get("metadata", {})
            self.item_name_var.set(meta.get("name", ""))
            self.item_id_var.set(meta.get("id", ""))
            self.item_author_var.set(meta.get("author", ""))
            self.item_email_var.set(meta.get("email", ""))
            self.item_website_var.set(meta.get("website", ""))
            self.item_desc_text.delete("1.0", "end")
            self.item_desc_text.insert("1.0", meta.get("description", ""))
            for comp_info in state_data.get("ui_components", []):
                self._add_component_to_canvas(
                    component_type=comp_info['type'],
                    x=comp_info['x'],
                    y=comp_info['y'],
                    existing_id=comp_info['id'],
                    existing_config=comp_info['config']
                )
            self.logic_builder_canvas.load_logic_data(state_data.get("logic_definition"))
            self.kernel.write_to_log("Generator design loaded successfully.", "SUCCESS")
        except Exception as e:
            self.kernel.write_to_log(f"Failed to load generator design state: {e}", "ERROR")
            # MODIFIED: Changed messagebox to use loc.get and English fallbacks
            messagebox.showerror(self.loc.get('error_title', fallback="Error"), self.loc.get('generator_load_design_error', fallback="Failed to load saved design. The state file may be corrupt.\n\nError: {error_msg}", error_msg=e))
    def _clear_saved_design_state(self):
        # MODIFIED: Changed messagebox to use loc.get and English fallbacks
        if not messagebox.askyesno(self.loc.get('confirm_title', fallback="Confirm"), self.loc.get('generator_confirm_delete_saved', fallback="Are you sure you want to delete the saved design? This cannot be undone.")):
            return
        state_manager = self.kernel.get_service("state_manager")
        if state_manager:
            state_manager.delete(self.DESIGN_STATE_KEY)
            self.kernel.write_to_log("Saved generator design has been deleted.", "WARN")
            # MODIFIED: Changed messagebox to use loc.get and English fallbacks
            messagebox.showinfo(self.loc.get('success_title', fallback="Success"), self.loc.get('generator_deleted_saved_msg', fallback="The saved design has been deleted."))

    def _discover_and_load_components(self):
        self.kernel.write_to_log("GeneratorPage: Discovering UI component generators...", "INFO")
        components_path = os.path.join(os.path.dirname(__file__), 'generator_components')
        if not os.path.exists(components_path): return
        for filename in os.listdir(components_path):
            if filename.endswith('.py') and not filename.startswith('__') and filename != 'logic_builder_canvas.py':
                module_name = f"plugins.flowork_core_ui.generator_components.{filename[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, BaseGeneratorComponent) and obj is not BaseGeneratorComponent:
                            instance = obj(self.kernel)
                            comp_type = instance.get_component_type()
                            self.registered_components[comp_type] = instance
                            self.kernel.write_to_log(f"  -> Loaded generator component: '{comp_type}'", "SUCCESS")
                except Exception as e:
                    self.kernel.write_to_log(f"Failed to load generator component from {filename}: {e}", "ERROR")
    def apply_styles(self, colors):
        style = tk_ttk.Style(self)
        if not colors: return
        style.configure('TFrame', background=colors.get('bg'))
        style.configure('TLabel', background=colors.get('bg'), foreground=colors.get('fg'))
        style.configure('TLabelframe', background=colors.get('bg'), relief="solid", borderwidth=1, bordercolor=colors.get('border'))
        style.configure('TLabelframe.Label', background=colors.get('bg'), foreground=colors.get('fg'), font=('Helvetica', 11, 'bold'))
        style.configure('Header.TLabel', font=('Helvetica', 10, 'bold'), foreground=colors.get('primary'))
        style.configure('Ghost.TLabel', background=colors.get('primary'), foreground=colors.get('fg'), padding=5, borderwidth=1, relief='solid')
        style.configure('SelectedComponent.TFrame', borderwidth=2, relief='solid', bordercolor=colors.get('info'))
        style.configure('NormalComponent.TFrame', borderwidth=1, relief='solid', bordercolor=colors.get('border'))
    def create_widgets(self):
        main_pane = ttk.PanedWindow(self, orient='horizontal')
        main_pane.pack(fill="both", expand=True, padx=15, pady=15)
        guide_handle = ttk.Frame(self, width=15, bootstyle="secondary")
        guide_handle.place(relx=0, rely=0, relheight=1, anchor='nw')
        handle_label = ttk.Label(guide_handle, text=">", bootstyle="inverse-secondary", font=("Helvetica", 10, "bold"))
        handle_label.pack(expand=True)
        guide_handle.bind("<Enter>", self._show_guide_panel)
        guide_handle.lift()
        self.guide_panel = ttk.Frame(self, bootstyle="secondary")
        control_bar = ttk.Frame(self.guide_panel, bootstyle="secondary")
        control_bar.pack(fill='x', padx=5, pady=2)
        self.guide_pin_button = ttk.Button(control_bar, text="📌", bootstyle="light-link", command=self._toggle_pin_guide)
        self.guide_pin_button.pack(side='right')
        guide_frame_inner = ttk.LabelFrame(self.guide_panel, text=self.loc.get('generator_guide_title'), padding=15)
        guide_frame_inner.pack(fill='both', expand=True, padx=5, pady=(0,5))
        guide_frame_inner.columnconfigure(0, weight=1)
        guide_frame_inner.rowconfigure(0, weight=1)
        self.guide_text = scrolledtext.ScrolledText(guide_frame_inner, wrap="word", height=10, state="disabled", font="-size 9")
        self.guide_text.grid(row=0, column=0, sticky="nsew")
        self.guide_panel.bind("<Leave>", self._hide_guide_panel_later)
        self.guide_panel.bind("<Enter>", self._cancel_hide_guide)
        left_pane = ttk.Frame(main_pane, padding=10)
        main_pane.add(left_pane, weight=2)
        design_notebook = ttk.Notebook(left_pane)
        design_notebook.pack(fill='both', expand=True)
        property_design_tab = ttk.Frame(design_notebook, padding=5)
        # MODIFIED: Replaced hardcoded Indonesian text with loc.get and English fallback
        design_notebook.add(property_design_tab, text=self.loc.get('generator_tab_ui_design', fallback=" 1. UI Properties Design "))
        toolbox_frame = ttk.LabelFrame(property_design_tab, text=self.loc.get('generator_toolbox_title', fallback="UI Component Toolbox"), padding=10)
        toolbox_frame.pack(side='left', fill='y', padx=(0, 10))
        for comp_type, component_instance in sorted(self.registered_components.items()):
            label = component_instance.get_toolbox_label()
            self._create_draggable_button(toolbox_frame, label, comp_type)
        design_container = ttk.Frame(property_design_tab)
        design_container.pack(side='left', fill='both', expand=True)
        self.design_canvas_frame = ttk.LabelFrame(design_container, text=self.loc.get('generator_canvas_title', fallback="Property Design Canvas"), padding=10)
        self.design_canvas_frame.pack(side='top', fill='both', expand=True)
        self.canvas_placeholder = ttk.Label(self.design_canvas_frame, text=self.loc.get('generator_canvas_placeholder', fallback="Drag components from the Toolbox here..."), bootstyle="secondary")
        self.canvas_placeholder.pack(expand=True)
        self.design_canvas_frame.bind("<Button-3>", self._show_context_menu)
        self.canvas_placeholder.bind("<Button-3>", self._show_context_menu)
        property_button_frame = ttk.Frame(design_container)
        property_button_frame.pack(side='bottom', fill='x', pady=(10,0))
        clear_button = ttk.Button(property_button_frame, text=self.loc.get('generator_clear_canvas_button', fallback="Clear Canvas"), command=self._clear_canvas, bootstyle="danger-outline")
        clear_button.pack(side='left', expand=True, fill='x', padx=(0,5))
        # MODIFIED: Replaced hardcoded Indonesian text with loc.get and English fallback
        save_design_button = ttk.Button(property_button_frame, text=self.loc.get('generator_save_design_button', fallback="Save Design"), command=self._save_current_design_state, bootstyle="primary-outline")
        save_design_button.pack(side='left', expand=True, fill='x', padx=(5,5))
        # MODIFIED: Replaced hardcoded Indonesian text with loc.get and English fallback
        clear_saved_button = ttk.Button(property_button_frame, text=self.loc.get('generator_clear_saved_design_button', fallback="Clear Saved Design"), command=self._clear_saved_design_state, bootstyle="secondary-outline")
        clear_saved_button.pack(side='left', expand=True, fill='x', padx=(5,0))
        logic_design_tab = ttk.Frame(design_notebook, padding=5)
        # MODIFIED: Replaced hardcoded Indonesian text with loc.get and English fallback
        design_notebook.add(logic_design_tab, text=self.loc.get('generator_tab_logic_design', fallback=" 2. Logic Design (Execute) "))
        self.logic_builder_canvas = LogicBuilderCanvas(logic_design_tab, self.kernel)
        self.logic_builder_canvas.pack(fill='both', expand=True)
        right_pane = ttk.Frame(main_pane, padding=10)
        main_pane.add(right_pane, weight=1)
        metadata_frame = ttk.LabelFrame(right_pane, text=self.loc.get('generator_meta_title', fallback="3. Module Info"), padding=15)
        metadata_frame.pack(fill='x', expand=False, pady=(0, 15))
        ttk.Label(metadata_frame, text=self.loc.get('generator_meta_name_label', fallback="Feature Name:")).pack(fill='x', anchor='w')
        ttk.Entry(metadata_frame, textvariable=self.item_name_var).pack(fill='x', pady=(0,5))
        ttk.Label(metadata_frame, text=self.loc.get('generator_meta_id_label', fallback="Unique ID (automatic):")).pack(fill='x', anchor='w')
        ttk.Entry(metadata_frame, textvariable=self.item_id_var, state="readonly").pack(fill='x', pady=(0,5))
        ttk.Label(metadata_frame, text=self.loc.get('generator_meta_author_label', fallback="Author:")).pack(fill='x', anchor='w')
        ttk.Entry(metadata_frame, textvariable=self.item_author_var).pack(fill='x', pady=(0,5))
        ttk.Label(metadata_frame, text=self.loc.get('generator_meta_email_label', fallback="Email:")).pack(fill='x', anchor='w')
        ttk.Entry(metadata_frame, textvariable=self.item_email_var).pack(fill='x', pady=(0,5))
        ttk.Label(metadata_frame, text=self.loc.get('generator_meta_website_label', fallback="Website:")).pack(fill='x', anchor='w')
        ttk.Entry(metadata_frame, textvariable=self.item_website_var).pack(fill='x', pady=(0,5))
        ttk.Label(metadata_frame, text=self.loc.get('generator_meta_desc_label', fallback="Description:")).pack(fill='x', anchor='w')
        self.item_desc_text = Text(metadata_frame, height=3, font=("Helvetica", 9))
        self.item_desc_text.pack(fill='x', pady=(0,5))
        self.comp_prop_frame = ttk.LabelFrame(right_pane, text=self.loc.get('generator_comp_prop_title', fallback="4. Selected Component Properties"), padding=15)
        self.comp_prop_frame.pack(fill='x', expand=False, pady=(0, 15))
        generate_frame = ttk.LabelFrame(right_pane, text=self.loc.get('generator_finalize_title', fallback="5. Finalize"), padding=15)
        generate_frame.pack(fill='x', expand=False)
        ttk.Button(generate_frame, text=self.loc.get('generator_generate_button', fallback="Generate Module ZIP File"), command=self._start_generation_process, style="success.TButton").pack(fill='x', ipady=5)
    def _create_draggable_button(self, parent, text, component_type):
        button = ttk.Button(parent, text=text)
        button.pack(fill='x', pady=2)
        button.bind("<ButtonPress-1>", lambda event, c_type=component_type: self._on_drag_start(event, c_type))
    def _on_drag_start(self, event, component_type):
        self._drag_data = {'widget': ttk.Label(self, text=event.widget.cget('text'), style='Ghost.TLabel'), 'component_type': component_type, 'drag_type': 'new_component'}
        self.winfo_toplevel().bind("<B1-Motion>", self._on_drag_motion)
        self.winfo_toplevel().bind("<ButtonRelease-1>", self._on_drag_release)
    def _on_drag_motion(self, event):
        drag_type = self._drag_data.get('drag_type')
        if not drag_type: return
        if drag_type == 'new_component':
            if self._drag_data.get('widget'): self._drag_data['widget'].place(x=event.x_root - self.winfo_toplevel().winfo_rootx(), y=event.y_root - self.winfo_toplevel().winfo_rooty())
        elif drag_type == 'move_component':
            if self._drag_data.get('widget'):
                dx, dy = event.x - self._drag_data['x'], event.y - self._drag_data['y']
                x, y = self._drag_data['widget'].winfo_x() + dx, self._drag_data['widget'].winfo_y() + dy
                self._drag_data['widget'].place(x=x, y=y)
    def _on_drag_release(self, event):
        drag_type = self._drag_data.get('drag_type')
        if not drag_type: return
        if drag_type == 'new_component':
            if self._drag_data.get('widget'): self._drag_data['widget'].destroy()
            canvas_x, canvas_y = self.design_canvas_frame.winfo_rootx(), self.design_canvas_frame.winfo_rooty()
            canvas_width, canvas_height = self.design_canvas_frame.winfo_width(), self.design_canvas_frame.winfo_height()
            if canvas_x < event.x_root < canvas_x + canvas_width and canvas_y < event.y_root < canvas_y + canvas_height:
                drop_x, drop_y = event.x_root - canvas_x - 10, event.y_root - canvas_y - 30
                self._add_component_to_canvas(self._drag_data['component_type'], drop_x, drop_y)
        self._drag_data = {}
        self.winfo_toplevel().unbind("<B1-Motion>")
        self.winfo_toplevel().unbind("<ButtonRelease-1>")
    def _add_component_to_canvas(self, component_type, x, y, existing_id=None, existing_config=None):
        if self.canvas_placeholder: self.canvas_placeholder.destroy(); self.canvas_placeholder = None
        component_generator = self.registered_components.get(component_type)
        if not component_generator: self.kernel.write_to_log(f"Attempted to add unknown component type: {component_type}", "ERROR"); return
        comp_id = existing_id or f"comp_{str(uuid.uuid4())[:8]}"
        comp_frame = ttk.Frame(self.design_canvas_frame, padding=5, style='NormalComponent.TFrame')
        if existing_config:
            config = existing_config
        else:
            var_id = f"{component_type.replace('_input','')}_{str(uuid.uuid4())[:4]}"
            config = {'label': f"My {component_type.replace('_', ' ').title()}", 'id': var_id, 'default': '', 'options': []}
            if component_type == 'checkbox': config['default'] = False
        label_widget = component_generator.create_canvas_widget(comp_frame, comp_id, config)
        for widget in [comp_frame] + comp_frame.winfo_children():
            if widget:
                widget.bind("<ButtonPress-1>", lambda e, cid=comp_id: self._on_component_press(e, cid))
                widget.bind("<B1-Motion>", self._on_drag_motion)
                widget.bind("<ButtonRelease-1>", self._on_component_release)
        comp_frame.place(x=x, y=y)
        self.designed_components[comp_id] = {'widget': comp_frame, 'label_widget': label_widget, 'type': component_type, 'config': config}
        if not existing_id:
            self.kernel.write_to_log(f"Component '{component_type}' added to design canvas.", "INFO")
            self._on_canvas_component_selected(None, comp_id)
    def _on_component_press(self, event, component_id):
        self._on_canvas_component_selected(event, component_id)
        widget_to_move = self.designed_components[component_id]['widget']
        self._drag_data = {'widget': widget_to_move, 'x': event.x, 'y': event.y, 'drag_type': 'move_component'}
        return "break"
    def _on_component_release(self, event):
        self._drag_data = {}
    def _on_canvas_component_selected(self, event, component_id):
        self._is_updating_from_selection = True
        if self.selected_component_id and self.selected_component_id in self.designed_components:
            if self.designed_components[self.selected_component_id]['widget'].winfo_exists():
                self.designed_components[self.selected_component_id]['widget'].config(style='NormalComponent.TFrame')
        self.selected_component_id = component_id
        component_data = self.designed_components.get(component_id)
        if not component_data: self._is_updating_from_selection = False; return
        component_data['widget'].config(style='SelectedComponent.TFrame')
        if self.comp_prop_frame_content and self.comp_prop_frame_content.winfo_exists(): self.comp_prop_frame_content.destroy()
        self.comp_prop_frame_content = ttk.Frame(self.comp_prop_frame)
        self.comp_prop_frame_content.pack(fill='both', expand=True)
        comp_type, config = component_data.get('type'), component_data.get('config', {})
        component_generator = self.registered_components.get(comp_type)
        if component_generator:
            prop_vars = component_generator.create_properties_ui(self.comp_prop_frame_content, config)
            if prop_vars:
                component_data['prop_vars'] = prop_vars
                for var in prop_vars.values():
                    if isinstance(var, (StringVar, BooleanVar)): var.trace_add('write', self._update_component_properties)
                    elif isinstance(var, Text): var.bind("<<Modified>>", self._update_component_properties)
        self._is_updating_from_selection = False
        if event: return "break"
    def _update_component_properties(self, *args):
        if self._is_updating_from_selection or not self.selected_component_id: return
        component_data = self.designed_components.get(self.selected_component_id)
        if not component_data or not component_data.get('prop_vars'): return
        prop_vars = component_data['prop_vars']
        for key, var in prop_vars.items():
            if isinstance(var, (StringVar, BooleanVar)):
                component_data['config'][key] = var.get()
            elif isinstance(var, Text):
                component_data['config'][key] = var.get('1.0', 'end-1c')
        if 'options' in component_data['config'] and isinstance(component_data['config']['options'], str):
            options_list = component_data['config']['options'].strip().split('\n')
            component_data['config']['options'] = [opt.strip() for opt in options_list if opt.strip()]
            visual_widget = next((w for w in component_data['widget'].winfo_children() if isinstance(w, ttk.Combobox)), None)
            if visual_widget: visual_widget['values'] = component_data['config']['options']
        label_widget, new_label_text = component_data.get('label_widget'), component_data['config'].get('label', '')
        if label_widget and label_widget.winfo_exists(): label_widget.config(text=new_label_text)
        if 'options' in prop_vars and isinstance(prop_vars.get('options'), Text): prop_vars['options'].edit_modified(False)
    def _show_context_menu(self, event):
        context_menu = Menu(self, tearoff=0)
        add_menu = Menu(context_menu, tearoff=0)
        canvas_x, canvas_y = self.design_canvas_frame.winfo_rootx(), self.design_canvas_frame.winfo_rooty()
        drop_x, drop_y = event.x_root - canvas_x, event.y_root - canvas_y
        for comp_type, comp_instance in sorted(self.registered_components.items()):
            add_menu.add_command(label=comp_instance.get_toolbox_label(), command=lambda ct=comp_type: self._add_component_to_canvas(ct, drop_x, drop_y))
        context_menu.add_cascade(label=self.loc.get('generator_context_add', fallback="Add Component"), menu=add_menu)
        context_menu.add_separator()
        delete_state = "normal" if self.selected_component_id else "disabled"
        context_menu.add_command(label=self.loc.get('generator_context_delete', fallback="Delete Selected"), command=self._delete_selected_component, state=delete_state)
        try: context_menu.tk_popup(event.x_root, event.y_root)
        finally: context_menu.grab_release()
    def _delete_selected_component(self):
        if not self.selected_component_id: return
        component_to_delete = self.designed_components.pop(self.selected_component_id, None)
        if component_to_delete: component_to_delete['widget'].destroy()
        self.selected_component_id = None
        if self.comp_prop_frame_content and self.comp_prop_frame_content.winfo_exists():
            for child in self.comp_prop_frame_content.winfo_children(): child.destroy()
        if not self.designed_components and (not self.canvas_placeholder or not self.canvas_placeholder.winfo_exists()):
            self.canvas_placeholder = ttk.Label(self.design_canvas_frame, text=self.loc.get('generator_canvas_placeholder', fallback="Drag components from the Toolbox here..."), bootstyle="secondary")
            self.canvas_placeholder.pack(expand=True)
            self.canvas_placeholder.bind("<Button-3>", self._show_context_menu)
    def _clear_canvas(self, ask_confirmation=True):
        do_clear = False
        if ask_confirmation:
            if messagebox.askyesno(self.loc.get('messagebox_confirm_title', fallback="Confirm"), self.loc.get('generator_confirm_clear_canvas', fallback="Are you sure you want to clear all components from the canvas?")):
                do_clear = True
        else:
            do_clear = True
        if do_clear:
            for comp_id in list(self.designed_components.keys()):
                self.designed_components[comp_id]['widget'].destroy()
                del self.designed_components[comp_id]
            self._delete_selected_component()
    def refresh_content(self):
        self.kernel.write_to_log("Generator page refreshed.", "DEBUG")
    def _update_id_field(self, *args):
        name_text = self.item_name_var.get().lower()
        sanitized_name = re.sub(r'[^a-z0-9_]', '', name_text.replace(' ', '_'))
        if sanitized_name:
            if not hasattr(self, '_current_random_suffix'): self._current_random_suffix = str(uuid.uuid4())[:4]
            id_text = f"{sanitized_name}_{self._current_random_suffix}"
            self.item_id_var.set(id_text)
        else: self.item_id_var.set("")
    def _sync_ui_to_config(self):
        if not self.selected_component_id: return
        self._is_updating_from_selection = False
        self._update_component_properties()
    def _start_generation_process(self):
        if not self.kernel.is_tier_sufficient('pro'):
            messagebox.showwarning(
                self.loc.get('license_popup_title'),
                self.loc.get('license_popup_message', module_name="Module Generator"),
                parent=self.winfo_toplevel()
            )
            tab_manager = self.kernel.get_service("tab_manager_service")
            if tab_manager:
                tab_manager.open_managed_tab("pricing_page")
            return
        self._sync_ui_to_config()
        module_info = {'id': self.item_id_var.get(), 'name': self.item_name_var.get(), 'author': self.item_author_var.get(), 'email': self.item_email_var.get(), 'website': self.item_website_var.get(), 'description': self.item_desc_text.get("1.0", "end-1c").strip(), 'components': list(self.designed_components.values())}
        if not module_info['id'] or not module_info['name']:
            messagebox.showerror(self.loc.get('generator_err_missing_info_title', fallback="Info Missing"), self.loc.get('generator_err_missing_info_msg', fallback="Module Name and ID are required."))
            return
        save_path = filedialog.asksaveasfilename(title=self.loc.get('generator_save_zip_title', fallback="Save Module ZIP File"), initialfile=f"{module_info['id']}.zip", defaultextension=".zip", filetypes=[("ZIP files", "*.zip")])
        if not save_path: return
        try:
            logic_data = self.logic_builder_canvas.get_logic_data()
            manifest_content = self._generate_manifest_content(module_info)
            processor_content = self._generate_processor_content(module_info, logic_data)
            with tempfile.TemporaryDirectory() as temp_dir:
                module_root_path = os.path.join(temp_dir, module_info['id'])
                os.makedirs(os.path.join(module_root_path, 'locales'))
                with open(os.path.join(module_root_path, 'manifest.json'), 'w', encoding='utf-8') as f: json.dump(manifest_content, f, indent=4)
                with open(os.path.join(module_root_path, 'processor.py'), 'w', encoding='utf-8') as f: f.write(processor_content)
                with open(os.path.join(module_root_path, 'locales', 'id.json'), 'w', encoding='utf-8') as f: json.dump({"module_name": module_info['name']}, f, indent=4)
                with open(os.path.join(module_root_path, 'locales', 'en.json'), 'w', encoding='utf-8') as f: json.dump({"module_name": module_info['name']}, f, indent=4)
                with open(os.path.join(module_root_path, 'requirements.txt'), 'w', encoding='utf-8') as f: f.write("# Add any required Python packages here, one per line\n")
                shutil.make_archive(os.path.splitext(save_path)[0], 'zip', temp_dir)
            messagebox.showinfo(self.loc.get('messagebox_success_title', fallback="Success"), self.loc.get('generator_zip_success_msg', fallback=f"Module '{module_info['name']}' has been successfully packaged!"))
            self.kernel.write_to_log(f"Successfully generated and saved module ZIP to {save_path}", "SUCCESS")
        except Exception as e:
            messagebox.showerror(self.loc.get('messagebox_error_title', fallback="Error"), self.loc.get('generator_zip_error_msg', fallback=f"An error occurred while generating the ZIP file: {e}"))
            self.kernel.write_to_log(f"Failed to generate module ZIP: {e}", "ERROR")
    def _generate_manifest_content(self, info):
        class_name = "".join(word.capitalize() for word in info['id'].replace('_', ' ').split()).replace(' ', '') + "Module"
        properties = []
        for comp_data in info['components']:
            comp_type, comp_config = comp_data['type'], comp_data['config']
            component_generator = self.registered_components.get(comp_type)
            if component_generator:
                entry = component_generator.generate_manifest_entry(comp_config)
                if entry: properties.append(entry)
        manifest = OrderedDict()
        ideal_order = ["id", "name", "version", "icon_file", "author", "email", "website", "description", "type", "entry_point", "behaviors", "requires_services", "properties", "output_ports"]
        manifest_data = {"id": info['id'], "name": info['name'], "version": "1.0", "icon_file": "icon.png", "author": info['author'], "email": info['email'], "website": info['website'],"description": info['description'], "type": "ACTION", "entry_point": f"processor.{class_name}", "behaviors": ["loop", "retry"], "requires_services": ["logger", "loc"],"properties": properties, "output_ports": [{"name": "success", "display_name": "Success"}, {"name": "error", "display_name": "Error"}]}
        for key in ideal_order:
            if key in manifest_data: manifest[key] = manifest_data[key]
        return manifest
    def _generate_processor_content(self, info, logic_data):
        class_name = "".join(word.capitalize() for word in info['id'].replace('_', ' ').split()).replace(' ', '') + "Module"
        all_imports = {
            "from flowork_kernel.api_contract import BaseModule, IExecutable, IConfigurableUI, IDataPreviewer",
            "import ttkbootstrap as ttk",
            "from flowork_kernel.ui_shell import shared_properties",
            "from flowork_kernel.utils.payload_helper import get_nested_value",
            "import json"
        }
        for comp_data in info['components']:
            comp_type = comp_data['type']
            component_generator = self.registered_components.get(comp_type)
            if component_generator: all_imports.update(component_generator.get_required_imports())
        imports_str = "\n".join(sorted(list(all_imports)))
        execute_lines = [
            "    def execute(self, payload: dict, config: dict, status_updater, ui_callback, mode='EXECUTE'):",
            f"        self.logger(f\"Executing '{info['name']}' module logic...\", \"INFO\")",
            "        # This logic was visually generated by the Logic Builder Canvas.",
            "        internal_payload = payload.copy()",
            "        node_results = {}",
            "        module_manager = self.kernel.get_service(\"module_manager_service\")",
            "",
            "        def run_logic_node(node_id, current_payload, node_config_str):",
            "            # Replace config placeholders with actual values from the main module's config",
            "            for key, value in config.items():",
            "                placeholder = f'{{{{config.{key}}}}}'",
            "                node_config_str = node_config_str.replace(placeholder, str(value))",
            "            node_config = json.loads(node_config_str)",
            "            module_id = node_config.get('module_id')",
            "            instance = module_manager.get_instance(module_id)",
            "            if not instance: raise Exception(f'Logic node module {{module_id}} not found')",
            "            return instance.execute(current_payload, node_config.get('config_values', {}), lambda m, l: None, ui_callback, mode)",
            ""
        ]
        nodes = {node['id']: node for node in logic_data['nodes']}
        connections = logic_data['connections']
        all_node_ids = set(nodes.keys())
        nodes_with_incoming = set(conn['to'] for conn in connections)
        start_nodes = list(all_node_ids - nodes_with_incoming)
        execution_flow = {}
        for conn in connections:
            if conn['from'] not in execution_flow:
                execution_flow[conn['from']] = []
            execution_flow[conn['from']].append(conn)
        nodes_to_process = start_nodes[:]
        processed_nodes = set()
        while nodes_to_process:
            node_id = nodes_to_process.pop(0)
            if node_id in processed_nodes:
                continue
            node_info = nodes[node_id]
            node_var = f"node_results['{node_id}']"
            incoming_conns = [c for c in connections if c['to'] == node_id]
            if not incoming_conns:
                input_payload = "internal_payload"
            else:
                prev_node_id = incoming_conns[0]['from']
                input_payload = f"node_results.get('{prev_node_id}', {{}})"
            execute_lines.append(f"        # --- Executing Logic Node: {node_info.get('name')} ---")
            execute_lines.append(f"        self.logger('  -> Running logic for: {node_info.get('name')}', 'DEBUG')")
            node_config_as_string_literal = repr(json.dumps(node_info))
            execute_lines.append(f"        {node_var} = run_logic_node('{node_id}', {input_payload}, {node_config_as_string_literal})")
            processed_nodes.add(node_id)
            if node_id in execution_flow:
                for conn in execution_flow[node_id]:
                    if conn['to'] not in processed_nodes:
                        nodes_to_process.append(conn['to'])
        end_nodes = list(all_node_ids - set(conn['from'] for conn in connections))
        if end_nodes:
            final_payload_source = f"node_results.get('{end_nodes[0]}', internal_payload)"
        else:
            final_payload_source = "internal_payload"
        execute_lines.append("")
        execute_lines.append(f"        final_payload = {final_payload_source}")
        execute_lines.append("        status_updater(\"Visual logic execution complete\", \"SUCCESS\")")
        execute_lines.append("        return {\"payload\": final_payload, \"output_name\": \"success\"}")
        execute_str = "\n".join(execute_lines)
        prop_ui_lines = ["    def create_properties_ui(self, parent_frame, get_current_config, available_vars):","        config = get_current_config()","        property_vars = {}","        # Custom UI elements are generated based on the visual design",]
        for comp_data in info['components']:
            comp_type, comp_config = comp_data['type'], comp_data['config']
            component_generator = self.registered_components.get(comp_type)
            if component_generator: prop_ui_lines.extend(component_generator.generate_processor_ui_code(comp_config))
        prop_ui_lines.extend(["        # Standard settings UI","        ttk.Separator(parent_frame).pack(fill='x', pady=15, padx=5)","        debug_vars = shared_properties.create_debug_and_reliability_ui(parent_frame, config, self.loc)","        property_vars.update(debug_vars)","        loop_vars = shared_properties.create_loop_settings_ui(parent_frame, config, self.loc, available_vars)","        property_vars.update(loop_vars)","        return property_vars"])
        prop_ui_str = "\n".join(prop_ui_lines)
        code = f"""{imports_str}
class {class_name}(BaseModule, IExecutable, IConfigurableUI, IDataPreviewer):
    TIER = "pro"
    \"\"\"
    Module '{info['name']}' generated by Flowork Module Factory.
    Author: {info['author']}
    \"\"\"
    def __init__(self, module_id, services):
        super().__init__(module_id, services)
        self.logger("Module '{info['name']}' initialized.", "INFO")
{execute_str}
{prop_ui_str}
    def get_data_preview(self, config: dict):
        \"\"\"
        TODO: Implement the data preview logic for this module.
        \"\"\"
        self.logger(f"'get_data_preview' is not yet implemented for {{self.module_id}}", 'WARN')
        return [{{'status': 'preview not implemented'}}]
"""
        return code
    def _toggle_pin_guide(self):
        self.guide_is_pinned = not self.guide_is_pinned
        pin_char = "📌"
        self.guide_pin_button.config(text=pin_char)
        if not self.guide_is_pinned:
            self._hide_guide_panel_later()
    def _show_guide_panel(self, event=None):
        self._cancel_hide_guide()
        self.guide_panel.place(in_=self, relx=0, rely=0, relheight=1.0, anchor='nw', width=350)
        self.guide_panel.lift()
    def _hide_guide_panel_later(self, event=None):
        if not self.guide_is_pinned:
            self.hide_guide_job = self.after(300, lambda: self.guide_panel.place_forget())
    def _cancel_hide_guide(self, event=None):
        if self.hide_guide_job:
            self.after_cancel(self.hide_guide_job)
            self.hide_guide_job = None
```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\marketplace_page.py
# JUMLAH BARIS : 497
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\marketplace_page.py
# JUMLAH BARIS : 496
#######################################################################

import ttkbootstrap as ttk
from tkinter import messagebox, filedialog
import os
import threading
from flowork_kernel.utils.performance_logger import log_performance
import json
import webbrowser
import requests
import tempfile
from .upload_dialog import UploadDialog
from flowork_gui.api_client.client import ApiClient
class MarketplacePage(ttk.Frame):
    def __init__(self, parent_notebook, kernel_instance):
        super().__init__(parent_notebook)
        self.kernel = kernel_instance
        self.loc = self.kernel.get_service("localization_manager")
        self.api_client = ApiClient()
        self.local_component_trees = {}
        self.community_component_trees = {}
        self.local_cache = {}
        self.community_cache = {}
        self.main_notebook = None
        self.ui_ready = False
        self._build_ui()
        self._fetch_all_data_and_refresh()
        event_bus = self.kernel.get_service("event_bus")
        if event_bus:
            subscriber_id = f"marketplace_page_{id(self)}"
            event_bus.subscribe("COMPONENT_LIST_CHANGED", subscriber_id, self.refresh_content)
    def _build_ui(self):
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill='both', expand=True)
        self.ads_frame = ttk.LabelFrame(main_frame, text="Community Highlights", padding=10, width=350)
        self.ads_frame.pack(side='right', fill='y', padx=(10, 0))
        self.ads_frame.pack_propagate(False)
        left_pane = ttk.Frame(main_frame)
        left_pane.pack(side='left', fill='both', expand=True)
        action_frame = ttk.Frame(left_pane)
        action_frame.pack(fill='x', pady=(0, 10))
        self.install_button = ttk.Button(action_frame, text=self.loc.get('marketplace_install_btn', fallback="Install from Zip..."), command=self._install_component, bootstyle="success")
        self.install_button.pack(side='left', padx=(0, 10))
        self.upload_button = ttk.Button(action_frame, text=self.loc.get('marketplace_upload_btn', fallback="Upload to Community..."), command=self._upload_selected_component, bootstyle="info")
        self.upload_button.pack(side='left', padx=(0,10))
        self.toggle_button = ttk.Button(action_frame, text=self.loc.get('marketplace_disable_btn', fallback="Disable Selected"), command=self._toggle_selected_component, bootstyle="warning")
        self.toggle_button.pack(side='left', padx=(0, 10))
        self.uninstall_button = ttk.Button(action_frame, text=self.loc.get('marketplace_uninstall_btn', fallback="Uninstall Selected"), command=self._uninstall_selected_component, bootstyle="danger")
        self.uninstall_button.pack(side='left')
        search_bar_frame = ttk.Frame(left_pane)
        search_bar_frame.pack(fill='x', pady=(0, 10))
        self.search_var = ttk.StringVar()
        self.search_var.trace_add("write", self._on_search)
        search_entry = ttk.Entry(search_bar_frame, textvariable=self.search_var)
        search_entry.pack(fill='x', expand=True)
        search_entry.insert(0, self.loc.get('marketplace_search_placeholder', fallback="Search by Name, ID, or Description..."))
        self.main_notebook = ttk.Notebook(left_pane)
        self.main_notebook.pack(fill='both', expand=True)
        self.main_notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)
        local_tab = ttk.Frame(self.main_notebook)
        community_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(local_tab, text=self.loc.get('marketplace_tab_local', fallback="Locally Installed"))
        self.main_notebook.add(community_tab, text=self.loc.get('marketplace_tab_community', fallback="Community"))
        self._create_component_notebook(local_tab, self.local_component_trees)
        self._create_component_notebook(community_tab, self.community_component_trees)
        self.ui_ready = True
    def refresh_content(self, event_data=None):
        self.kernel.write_to_log("MarketplacePage received a signal to refresh its content.", "INFO")
        self._fetch_all_data_and_refresh()
    def _fetch_all_data_and_refresh(self):
        threading.Thread(target=self._fetch_all_data_worker, daemon=True).start()
    def _create_component_notebook(self, parent_tab, tree_dict):
        notebook = ttk.Notebook(parent_tab)
        notebook.pack(fill='both', expand=True)
        component_types = {
            "modules": self.loc.get('marketplace_tab_modules', fallback="Modules"),
            "plugins": self.loc.get('marketplace_tab_plugins', fallback="Plugins"),
            "widgets": self.loc.get('marketplace_tab_widgets', fallback="Widgets"),
            "presets": self.loc.get('marketplace_tab_presets', fallback="Presets"),
            "triggers": "Triggers",
            "ai_providers": "AI Providers",
            "ai_models": "AI Models"
        }
        is_monet_active = self.kernel.is_monetization_active()
        for comp_type, tab_title in component_types.items():
            tab = ttk.Frame(notebook, padding=5)
            notebook.add(tab, text=tab_title)
            columns = ["name", "description"]
            if is_monet_active:
                columns.append("tier")
            if comp_type == 'ai_models':
                columns.append("downloads")
            else:
                columns.append("version")
            columns.append("status")
            tree = ttk.Treeview(tab, columns=tuple(columns), show="headings")
            tree.heading("name", text=self.loc.get('marketplace_col_name', fallback="Addon Name"))
            tree.column("name", width=250)
            tree.heading("description", text=self.loc.get('marketplace_col_desc', fallback="Description"))
            tree.column("description", width=400)
            if is_monet_active:
                tree.heading("tier", text=self.loc.get('marketplace_col_tier', fallback="Tier"))
                tree.column("tier", width=80, anchor='center')
            if comp_type == 'ai_models':
                tree.heading("downloads", text=self.loc.get('marketplace_col_downloads', fallback="Downloads"))
                tree.column("downloads", width=80, anchor='center')
            else:
                tree.heading("version", text=self.loc.get('marketplace_col_version', fallback="Version"))
                tree.column("version", width=80, anchor='center')
            tree.heading("status", text=self.loc.get('marketplace_col_status', fallback="Status"))
            tree.column("status", width=100, anchor='center')
            tree.pack(fill='both', expand=True)
            tree.bind('<<TreeviewSelect>>', self._update_button_state)
            tree_dict[comp_type] = tree
    def _populate_ads_panel(self, success, ads_data):
        if not self.winfo_exists() or not self.ads_frame.winfo_exists():
            return
        for widget in self.ads_frame.winfo_children():
            widget.destroy()
        if not success or not ads_data:
            ttk.Label(self.ads_frame, text="Cannot load highlights at the moment.").pack()
            return
        styles = ["primary", "info", "success", "warning", "danger", "secondary"]
        for i, ad in enumerate(ads_data):
            style = styles[i % len(styles)]
            ad_card = ttk.LabelFrame(self.ads_frame, text=ad.get("title", "Ad"), padding=10, bootstyle=style)
            ad_card.pack(fill="x", pady=5)
            ttk.Label(ad_card, text=ad.get("text", ""), wraplength=280).pack(anchor='w', pady=(0, 10))
            if "target_url" in ad and "button_text" in ad:
                ttk.Button(
                    ad_card,
                    text=ad.get("button_text"),
                    bootstyle=f"{style}-outline",
                    command=lambda url=ad.get("target_url"): webbrowser.open(url)
                ).pack(anchor='e')
    def _get_current_tab_info(self):
        try:
            if not self.main_notebook or not self.main_notebook.winfo_exists():
                return None, None, True
            active_main_tab_text = self.main_notebook.tab(self.main_notebook.select(), "text")
            if self.loc.get('marketplace_tab_local', fallback="Locally Installed") in active_main_tab_text:
                if not self.main_notebook.nametowidget(self.main_notebook.select()).winfo_exists():
                    return None, None, True
                notebook = self.main_notebook.nametowidget(self.main_notebook.select()).winfo_children()[0]
                tree_dict = self.local_component_trees
                is_local = True
            else:
                if not self.main_notebook.nametowidget(self.main_notebook.select()).winfo_exists():
                    return None, None, False
                notebook = self.main_notebook.nametowidget(self.main_notebook.select()).winfo_children()[0]
                tree_dict = self.community_component_trees
                is_local = False
            if not notebook.winfo_exists():
                return None, None, is_local
            tab_text = notebook.tab(notebook.select(), "text").strip()
            tab_map = {
                self.loc.get('marketplace_tab_modules', fallback="Modules"): 'modules',
                self.loc.get('marketplace_tab_plugins', fallback="Plugins"): 'plugins',
                self.loc.get('marketplace_tab_widgets', fallback="Widgets"): 'widgets',
                self.loc.get('marketplace_tab_presets', fallback="Presets"): 'presets',
                "Triggers": 'triggers',
                "AI Providers": 'ai_providers',
                "AI Models": 'ai_models'
            }
            comp_type = tab_map.get(tab_text, 'modules')
            return comp_type, tree_dict.get(comp_type), is_local
        except Exception:
            return 'modules', self.local_component_trees.get('modules'), True
    def _fetch_all_data_worker(self):
        threads = []
        def fetch_component_data(comp_type):
            success_local, local_data = self.api_client.get_components(comp_type)
            self.local_cache[comp_type] = local_data if success_local else []
            if not success_local:
                self.kernel.write_to_log(f"API Error fetching local {comp_type}: {local_data}", "ERROR")
            success_remote, remote_data = self.api_client.get_marketplace_index(comp_type)
            self.community_cache[comp_type] = remote_data if success_remote else []
            if not success_remote:
                self.kernel.write_to_log(f"API Error fetching remote {comp_type}: {remote_data}", "WARN")
        for comp_type in self.local_component_trees.keys():
            thread = threading.Thread(target=fetch_component_data, args=(comp_type,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        success_ads, ads_data = self.api_client.get_marketplace_ads()
        self.after(0, self._refresh_all_lists)
        self.after(0, self._populate_ads_panel, success_ads, ads_data)
    def _refresh_all_lists(self):
        for comp_type in self.local_component_trees.keys():
            self._refresh_list(comp_type, self.local_component_trees.get(comp_type), self.local_cache, is_local_tab=True)
        for comp_type in self.community_component_trees.keys():
            self._refresh_list(comp_type, self.community_component_trees.get(comp_type), self.community_cache, is_local_tab=False)
        self._update_button_state()
    def _refresh_list(self, component_type, tree, data_cache, is_local_tab):
        if not tree or not tree.winfo_exists():
            return
        for item in tree.get_children():
            tree.delete(item)
        search_query = self.search_var.get().lower()
        if search_query == self.loc.get('marketplace_search_placeholder', fallback="Search by Name, ID, or Description...").lower():
            search_query = ""
        search_keywords = search_query.split()
        data = data_cache.get(component_type, [])
        all_local_ids = set()
        for c_type in self.local_cache.keys():
            for item in self.local_cache.get(c_type, []):
                all_local_ids.add(item['id'])
        is_monet_active = self.kernel.is_monetization_active()
        for component in sorted(data, key=lambda x: x.get('name', '').lower()):
            searchable_string = (f"{component.get('name', '').lower()} {component.get('id', '').lower()} {component.get('description', '').lower()}")
            if all(keyword in searchable_string for keyword in search_keywords):
                status = ""
                if is_local_tab:
                    status = self.loc.get('status_disabled') if component.get('is_paused') else self.loc.get('status_enabled')
                else:
                    if component.get('id') in all_local_ids:
                        status = self.loc.get('marketplace_status_installed', fallback="Installed")
                    else:
                        status = self.loc.get('marketplace_status_not_installed', fallback="Not Installed")
                tags = ('paused',) if component.get('is_paused') and is_local_tab else ('enabled',)
                values = [
                    component.get('name', ''),
                    component.get('description', '')
                ]
                if is_monet_active:
                    values.append(component.get('tier', 'N/A').capitalize())
                if component_type == 'ai_models':
                    values.append(component.get('downloads', 0))
                else:
                    values.append(component.get('version', ''))
                values.append(status)
                tree.insert("", "end", iid=component['id'], values=tuple(values), tags=tags)
        theme_manager = self.kernel.get_service("theme_manager")
        colors = theme_manager.get_colors() if theme_manager else {}
        tree.tag_configure('paused', foreground='grey')
        tree.tag_configure('enabled', foreground=colors.get('fg', 'white'))
    def _on_search(self, *args):
        if not self.ui_ready: return
        self._refresh_all_lists()
    def _on_tab_change(self, event=None):
        self._update_button_state()
        self._refresh_all_lists()
    def _update_button_state(self, event=None):
        if not self.ui_ready or not self.winfo_exists():
            return
        comp_type, tree, is_local = self._get_current_tab_info()
        if not tree or not tree.winfo_exists():
            return
        selected_items = tree.selection()
        all_buttons_exist = all(hasattr(self, btn) and getattr(self, btn).winfo_exists() for btn in ['install_button', 'toggle_button', 'uninstall_button', 'upload_button'])
        if not all_buttons_exist:
            return
        if is_local:
            self.install_button.config(text=self.loc.get('marketplace_install_btn', fallback="Install from Zip..."), state="normal")
            self.toggle_button.config(state="disabled", text=self.loc.get('marketplace_disable_btn', fallback="Disable Selected"))
            self.uninstall_button.config(state="disabled")
            self.upload_button.config(state="disabled")
            if not selected_items: return
            selected_id = selected_items[0]
            component_data = next((item for item in self.local_cache.get(comp_type, []) if item['id'] == selected_id), None)
            if not component_data: return
            is_core = component_data.get('is_core', False)
            if not is_core:
                self.uninstall_button.config(state="normal")
                can_upload = self.kernel.current_user is not None
                self.upload_button.config(state="normal" if can_upload else "disabled")
                is_preset = comp_type == 'presets'
                is_model = comp_type == 'ai_models'
                self.toggle_button.config(state="normal" if not is_preset and not is_model else "disabled")
                tags = tree.item(selected_id, "tags")
                if 'paused' in tags:
                    self.toggle_button.config(text=self.loc.get('marketplace_enable_btn', fallback="Enable Selected"))
                else:
                    self.toggle_button.config(text=self.loc.get('marketplace_disable_btn', fallback="Disable Selected"))
        else: # Community tab
            install_text = self.loc.get('marketplace_install_model_btn', fallback="Download Model") if comp_type == 'ai_models' else self.loc.get('marketplace_install_community_btn', fallback="Install from Community")
            self.install_button.config(text=install_text, state="normal" if selected_items else "disabled")
            self.toggle_button.config(state="disabled")
            self.uninstall_button.config(state="disabled")
            self.upload_button.config(state="disabled")
    def _upload_selected_component(self):
        if not self.kernel.current_user:
            messagebox.showwarning("Login Required", "You must be logged in to upload components to the marketplace.", parent=self)
            if hasattr(self.kernel.root, '_open_authentication_dialog'):
                self.kernel.root._open_authentication_dialog()
            return
        comp_type, tree, is_local = self._get_current_tab_info()
        if not is_local or not tree: return
        selected_items = tree.selection()
        if not selected_items: return
        component_id = selected_items[0]
        component_name = tree.item(component_id, "values")[0]
        dialog = UploadDialog(self, self.kernel, component_name)
        if not dialog.result:
            self.kernel.write_to_log("Upload process cancelled by user.", "INFO")
            return
        upload_details = dialog.result
        if not messagebox.askyesno(
            self.loc.get('marketplace_upload_confirm_title'),
            self.loc.get('marketplace_upload_confirm_message', component_name=component_name)
        ):
            return
        self.kernel.write_to_log(f"UI: Sending upload request for '{component_name}' to the API server...", "INFO")
        if comp_type == 'ai_models':
            model_path = os.path.join(self.kernel.project_root_path, "ai_models", f"{component_id}.gguf")
            threading.Thread(target=self._upload_model_worker, args=(model_path, upload_details), daemon=True).start()
        else:
            threading.Thread(target=self._upload_worker, args=(comp_type, component_id, upload_details), daemon=True).start()
    def _upload_model_worker(self, model_path, upload_details):
        self.after(0, self.upload_button.config, {"state": "disabled", "text": "Uploading Model..."})
        success, response = self.api_client.upload_model(
            model_path=model_path,
            description=upload_details['description'],
            tier=upload_details['tier']
        )
        if success:
            self.after(0, messagebox.showinfo, self.loc.get('messagebox_success_title'), self.loc.get('marketplace_upload_success'))
        else:
            error_message = response if isinstance(response, str) else response.get('error', 'Unknown error occurred.')
            self.after(0, messagebox.showerror, self.loc.get('messagebox_error_title'), self.loc.get('marketplace_upload_failed', error=error_message))
        self.after(0, self.upload_button.config, {"state": "normal", "text": self.loc.get('marketplace_upload_btn')})
        self.after(0, self._fetch_all_data_and_refresh)
    def _upload_worker(self, comp_type, component_id, upload_details):
        self.after(0, self.upload_button.config, {"state": "disabled", "text": "Uploading..."})
        success, response = self.api_client.upload_component(
            comp_type=comp_type,
            component_id=component_id,
            description=upload_details['description'],
            tier=upload_details['tier']
        )
        if success:
            self.after(0, messagebox.showinfo, self.loc.get('messagebox_success_title'), self.loc.get('marketplace_upload_success'))
        else:
            error_message = response if isinstance(response, str) else response.get('error', 'Unknown error occurred.')
            self.after(0, messagebox.showerror, self.loc.get('messagebox_error_title'), self.loc.get('marketplace_upload_failed', error=error_message))
        self.after(0, self.upload_button.config, {"state": "normal", "text": self.loc.get('marketplace_upload_btn')})
        self.after(0, self._fetch_all_data_and_refresh)
    def _toggle_selected_component(self):
        comp_type, tree, is_local = self._get_current_tab_info()
        if not is_local or not tree: return
        selected_items = tree.selection()
        if not selected_items: return
        component_id = selected_items[0]
        tags = tree.item(component_id, "tags")
        is_currently_paused = 'paused' in tags
        new_paused_state = not is_currently_paused
        success, response = self.api_client.update_component_state(comp_type, component_id, new_paused_state)
        if success:
            action = "disabled" if new_paused_state else "enabled"
            self.kernel.write_to_log(f"Component '{component_id}' has been {action}.", "SUCCESS")
            if messagebox.askyesno(
                self.loc.get('marketplace_hot_reload_prompt_title', fallback="Reload Required"),
                self.loc.get('marketplace_toggle_hot_reload_prompt_message', fallback="State changed successfully. Reload all components now to apply?")
            ):
                threading.Thread(target=self.api_client.trigger_hot_reload, daemon=True).start()
        else:
            messagebox.showerror(self.loc.get("messagebox_error_title"), f"API Error: {response}")
    def _uninstall_selected_component(self):
        comp_type, tree, is_local = self._get_current_tab_info()
        if not is_local or not tree: return
        selected_items = tree.selection()
        if not selected_items: return
        component_id = selected_items[0]
        component_name = tree.item(component_id, "values")[0]
        if not messagebox.askyesno(self.loc.get('messagebox_confirm_title'), self.loc.get('marketplace_uninstall_confirm', component_name=component_name)):
            return
        success, response = self.api_client.delete_component(comp_type, component_id)
        if success:
            self.kernel.write_to_log(f"Component '{component_id}' has been uninstalled.", "SUCCESS")
            if messagebox.askyesno(
                self.loc.get('marketplace_hot_reload_prompt_title', fallback="Reload Required"),
                self.loc.get('marketplace_uninstall_hot_reload_prompt_message', fallback="Uninstallation successful. Reload all components now to apply changes?")
            ):
                threading.Thread(target=self.api_client.trigger_hot_reload, daemon=True).start()
        else:
            messagebox.showerror(self.loc.get("messagebox_error_title"), f"API Error: {response}")
    def _install_component(self):
        comp_type, tree, is_local = self._get_current_tab_info()
        if not is_local: # Community Tab Logic
            if not self.kernel.is_monetization_active():
                if not self.kernel.current_user:
                    messagebox.showwarning("Login Required", "You must be logged in to download components from the community.", parent=self)
                    if hasattr(self.kernel.root, '_open_authentication_dialog'):
                        self.kernel.root._open_authentication_dialog()
                    return # Stop the install process
            if not tree: return
            selected_items = tree.selection()
            if not selected_items:
                messagebox.showwarning(
                    self.loc.get('marketplace_warn_no_selection_title', fallback="Warning"),
                    self.loc.get('marketplace_warn_no_selection_msg', fallback="Please select a component from the community list to install.")
                )
                return
            component_id = selected_items[0]
            component_data = next((item for item in self.community_cache.get(comp_type, []) if item['id'] == component_id), None)
            if not component_data: return
            required_tier = component_data.get('tier', 'free').lower()
            if not self.kernel.is_tier_sufficient(required_tier):
                messagebox.showerror(
                    self.loc.get('marketplace_install_failed_title', fallback="Installation Failed"),
                    self.loc.get('marketplace_install_tier_error', tier=required_tier.capitalize(), userTier=self.kernel.license_tier.capitalize(), fallback=f"This component requires a '{required_tier.capitalize()}' tier license, but your current tier is '{self.kernel.license_tier.capitalize()}'.")
                )
                return
            if comp_type == 'presets':
                threading.Thread(target=self._download_and_install_preset_worker, args=(component_data,), daemon=True).start()
                return
            if comp_type == 'ai_models':
                threading.Thread(target=self._download_and_install_model_worker, args=(component_data,), daemon=True).start()
                return
            download_url = component_data.get('download_url')
            if not download_url:
                messagebox.showerror(self.loc.get('error_title', fallback="Error"), self.loc.get('marketplace_install_no_url_error', fallback="The download URL for this component is not available."))
                return
            threading.Thread(target=self._download_and_install_worker, args=(comp_type, component_data), daemon=True).start()
        else: # Local Tab Logic
            filepath = filedialog.askopenfilename(
                title=self.loc.get('marketplace_install_dialog_title'),
                filetypes=[("Zip files", "*.zip")]
            )
            if not filepath:
                return
            success, response = self.api_client.install_component(comp_type, filepath)
            self._on_install_complete(success, response)
    def _download_and_install_model_worker(self, model_data):
        download_url = model_data.get('download_url')
        model_name = model_data.get('id')
        self.after(0, self.install_button.config, {"state": "disabled", "text": f"Downloading {model_name}..."})
        try:
            with requests.get(download_url, stream=True) as r:
                r.raise_for_status()
                save_path = os.path.join(self.kernel.project_root_path, "ai_models", f"{model_name}.gguf")
                with open(save_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            self.api_client.trigger_hot_reload()
            self.after(0, messagebox.showinfo, self.loc.get('messagebox_success_title'), f"Model '{model_name}' downloaded successfully to your ai_models folder.")
            self.after(0, self._fetch_all_data_and_refresh)
        except Exception as e:
            self.after(0, messagebox.showerror, self.loc.get('messagebox_error_title'), f"Failed to download model: {e}")
        finally:
            self.after(0, self.install_button.config, {"state": "normal", "text": self.loc.get('marketplace_install_model_btn')})
    def _download_and_install_preset_worker(self, preset_data):
        download_url = preset_data.get('download_url')
        preset_name = preset_data.get('id')
        self.after(0, self.install_button.config, {"state": "disabled", "text": f"Downloading {preset_name}..."})
        try:
            response = requests.get(download_url, timeout=20)
            response.raise_for_status()
            preset_content = response.json()
            success, save_response = self.api_client.save_preset(preset_name, preset_content)
            if success:
                self.after(0, messagebox.showinfo, self.loc.get('messagebox_success_title'), f"Preset '{preset_name}' was installed successfully.")
                self.after(0, self._fetch_all_data_and_refresh)
            else:
                self.after(0, messagebox.showerror, self.loc.get('messagebox_error_title'), f"Failed to save preset: {save_response}")
        except requests.exceptions.RequestException as e:
            self.after(0, messagebox.showerror, self.loc.get('messagebox_error_title'), f"Failed to download preset: {e}")
        except json.JSONDecodeError:
            self.after(0, messagebox.showerror, self.loc.get('messagebox_error_title'), "Downloaded preset file is not valid JSON.")
        except Exception as e:
            self.after(0, messagebox.showerror, self.loc.get('messagebox_error_title'), f"An unexpected error occurred: {e}")
        finally:
            self.after(0, self.install_button.config, {"state": "normal", "text": "Install from Community"})
    def _download_and_install_worker(self, comp_type, component_data):
        download_url = component_data.get('download_url')
        component_name = component_data.get('name')
        self.after(0, self.install_button.config, {"state": "disabled", "text": f"Downloading {component_name}..."})
        try:
            with requests.get(download_url, stream=True) as r:
                r.raise_for_status()
                with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_file:
                    temp_filepath = tmp_file.name
                    for chunk in r.iter_content(chunk_size=8192):
                        tmp_file.write(chunk)
            success, response = self.api_client.install_component(comp_type, temp_filepath)
            os.unlink(temp_filepath)
            self.after(0, self._on_install_complete, success, response)
        except Exception as e:
            self.after(0, self._on_install_complete, False, str(e))
    def _on_install_complete(self, success, response):
        if success:
            self.kernel.write_to_log(f"Component installed via community tab.", "SUCCESS")
            if messagebox.askyesno(
                self.loc.get('marketplace_hot_reload_prompt_title', fallback="Reload Required"),
                self.loc.get('marketplace_install_hot_reload_prompt_message', fallback="Installation successful. Reload all components now to use the new component?")
            ):
                threading.Thread(target=self.api_client.trigger_hot_reload, daemon=True).start()
        else:
            messagebox.showerror(self.loc.get("messagebox_error_title"), f"API Error: {response}")
        self._update_button_state()

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\model_converter_page.py
# JUMLAH BARIS : 232
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\model_converter_page.py
# JUMLAH BARIS : 231
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, messagebox, scrolledtext, filedialog
import os
import re
import threading
import time
from flowork_gui.api_client.client import ApiClient
class ModelConverterPage(ttk.Frame):
    """
    The user interface for the Model Factory, allowing users to convert
    fine-tuned models into the efficient GGUF format.
    [MODIFIED] Added a tutorial and guide panel.
    [FIXED] Correctly identifies the notebook widget to get the active tab.
    """
    TIER = "pro" # (ADDED) Define the required license tier for this feature
    def __init__(self, parent_notebook, kernel_instance):
        super().__init__(parent_notebook, padding=0)
        self.kernel = kernel_instance
        self.loc = self.kernel.get_service("localization_manager")
        self.api_client = ApiClient(kernel=self.kernel)
        self.guide_is_pinned = False
        self.hide_guide_job = None
        self.source_model_var = StringVar()
        self.output_name_var = StringVar()
        self.source_gguf_var = StringVar()
        self.requantize_output_name_var = StringVar()
        self.quantize_method_var = StringVar(value="Q4_K_M")
        self.job_id = None
        self.is_polling = False
        self.main_notebook = None # (ADDED) Initialize main_notebook attribute
        self._build_ui()
        self._load_initial_data()
        self._populate_guide()
    def _apply_markdown_to_text_widget(self, text_widget, content):
        text_widget.config(state="normal")
        text_widget.delete("1.0", "end")
        parts = re.split(r'(\*\*.*?\*\*)', content)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                text_widget.insert("end", part[2:-2], "bold")
            else:
                text_widget.insert("end", part)
        text_widget.config(state="disabled")
    def _populate_guide(self):
        guide_content = self.loc.get("model_converter_guide_content")
        self._apply_markdown_to_text_widget(self.guide_text, guide_content)
        self.guide_text.tag_configure("bold", font="-size 9 -weight bold")
    def _build_ui(self):
        """Builds the main widgets for the page."""
        main_content_frame = ttk.Frame(self, padding=20)
        main_content_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        main_content_frame.columnconfigure(0, weight=1)
        main_content_frame.rowconfigure(1, weight=1)
        self.main_notebook = ttk.Notebook(main_content_frame) # (MODIFIED) Assign to self.main_notebook
        self.main_notebook.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        convert_tab = ttk.Frame(self.main_notebook, padding=15)
        self.main_notebook.add(convert_tab, text="Convert HF to GGUF")
        convert_tab.columnconfigure(1, weight=1)
        ttk.Label(convert_tab, text=self.loc.get('model_converter_source_label', fallback="Fine-Tuned Model Folder:")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.model_combo = ttk.Combobox(convert_tab, textvariable=self.source_model_var, state="readonly")
        self.model_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(convert_tab, text=self.loc.get('model_converter_output_label', fallback="New .gguf Filename (no extension):")).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.output_entry = ttk.Entry(convert_tab, textvariable=self.output_name_var)
        self.output_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        requantize_tab = ttk.Frame(self.main_notebook, padding=15)
        self.main_notebook.add(requantize_tab, text="Re-Quantize Existing GGUF")
        requantize_tab.columnconfigure(1, weight=1)
        ttk.Label(requantize_tab, text="Source .gguf File:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        source_gguf_frame = ttk.Frame(requantize_tab)
        source_gguf_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        source_gguf_frame.columnconfigure(0, weight=1)
        self.source_gguf_entry = ttk.Entry(source_gguf_frame, textvariable=self.source_gguf_var)
        self.source_gguf_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(source_gguf_frame, text="Browse...", command=self._browse_gguf_file).pack(side="left", padx=(5,0))
        ttk.Label(requantize_tab, text="New Quantized Filename (no extension):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.requantize_output_entry = ttk.Entry(requantize_tab, textvariable=self.requantize_output_name_var)
        self.requantize_output_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self._add_common_settings_to_tab(convert_tab, 2)
        self._add_common_settings_to_tab(requantize_tab, 2)
        monitor_frame = ttk.LabelFrame(main_content_frame, text=self.loc.get('model_converter_monitor_title', fallback="2. Conversion Monitor"), padding=15)
        monitor_frame.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        monitor_frame.rowconfigure(0, weight=1)
        monitor_frame.columnconfigure(0, weight=1)
        self.log_text = scrolledtext.ScrolledText(monitor_frame, wrap="word", state="disabled", height=15, font=("Consolas", 9))
        self.log_text.grid(row=0, column=0, sticky="nsew")
        self.start_button = ttk.Button(main_content_frame, text=self.loc.get('model_converter_start_btn', fallback="Start Conversion Job"), command=self._start_job, bootstyle="success")
        self.start_button.grid(row=2, column=0, sticky="ew", pady=(10, 0), ipady=5)
        guide_handle = ttk.Frame(self, width=15, bootstyle="secondary")
        guide_handle.place(relx=0, rely=0, relheight=1, anchor='nw')
        handle_label = ttk.Label(guide_handle, text=">", bootstyle="inverse-secondary", font=("Helvetica", 10, "bold"))
        handle_label.pack(expand=True)
        guide_handle.bind("<Enter>", self._show_guide_panel)
        self.guide_panel = ttk.Frame(self, bootstyle="secondary")
        control_bar = ttk.Frame(self.guide_panel, bootstyle="secondary")
        control_bar.pack(fill='x', padx=5, pady=2)
        self.guide_pin_button = ttk.Button(control_bar, text="📌", bootstyle="light-link", command=self._toggle_pin_guide)
        self.guide_pin_button.pack(side='right')
        guide_frame_inner = ttk.LabelFrame(self.guide_panel, text=self.loc.get('model_converter_guide_title'), padding=15)
        guide_frame_inner.pack(fill='both', expand=True, padx=5, pady=(0,5))
        guide_frame_inner.columnconfigure(0, weight=1)
        guide_frame_inner.rowconfigure(0, weight=1)
        self.guide_text = scrolledtext.ScrolledText(guide_frame_inner, wrap="word", height=10, state="disabled")
        self.guide_text.grid(row=0, column=0, sticky="nsew")
        self.guide_panel.bind("<Leave>", self._hide_guide_panel_later)
        self.guide_panel.bind("<Enter>", self._cancel_hide_guide)
        guide_handle.lift()
    def _add_common_settings_to_tab(self, parent_tab, start_row):
        ttk.Label(parent_tab, text=self.loc.get('model_converter_quant_label', fallback="Quantization Method:")).grid(row=start_row, column=0, sticky="w", padx=5, pady=5)
        quant_methods = ["Q2_K", "Q3_K_M", "Q4_0", "Q4_K_M", "Q5_0", "Q5_K_M", "Q6_K", "Q8_0", "F16", "F32"]
        self.quant_combo = ttk.Combobox(parent_tab, textvariable=self.quantize_method_var, values=quant_methods, state="readonly")
        self.quant_combo.grid(row=start_row, column=1, sticky="ew", padx=5, pady=5)
    def _browse_gguf_file(self):
        filepath = filedialog.askopenfilename(title="Select GGUF model file", filetypes=[("GGUF Model", "*.gguf")])
        if filepath:
            self.source_gguf_var.set(filepath)
            base_name = os.path.basename(filepath).replace(".gguf", "")
            self.requantize_output_name_var.set(f"{base_name}-quantized")
    def _load_initial_data(self):
        models_path = os.path.join(self.kernel.project_root_path, "ai_models", "text")
        local_models = []
        if os.path.isdir(models_path):
            local_models = [d for d in os.listdir(models_path) if os.path.isdir(os.path.join(models_path, d))]
        self.model_combo['values'] = sorted(local_models)
        if local_models:
            self.source_model_var.set(local_models[0])
    def _start_job(self):
        if not self.kernel.is_tier_sufficient(self.TIER):
            messagebox.showwarning(
                self.loc.get('license_popup_title'),
                self.loc.get('license_popup_message', module_name="Model Factory"),
                parent=self.winfo_toplevel()
            )
            tab_manager = self.kernel.get_service("tab_manager_service")
            if tab_manager:
                tab_manager.open_managed_tab("pricing_page")
            return
        selected_tab_index = self.main_notebook.index("current") # (FIXED) Correctly get the index from the notebook widget instance.
        quant_method = self.quantize_method_var.get()
        if selected_tab_index == 0:
            source_model = self.source_model_var.get()
            output_name = self.output_name_var.get().strip()
            if not source_model or not output_name:
                messagebox.showerror("Validation Error", "Source Model and Output Filename are required.", parent=self)
                return
            self.start_button.config(state="disabled")
            self._log_message("Sending conversion job request to the server...")
            threading.Thread(target=self._start_conversion_worker, args=(source_model, output_name, quant_method), daemon=True).start()
        elif selected_tab_index == 1:
            source_gguf = self.source_gguf_var.get()
            output_name = self.requantize_output_name_var.get().strip()
            if not source_gguf or not output_name:
                messagebox.showerror("Validation Error", "Source GGUF File and Output Filename are required.", parent=self)
                return
            self.start_button.config(state="disabled")
            self._log_message("Sending re-quantization job request to the server...")
            threading.Thread(target=self._start_requantize_worker, args=(source_gguf, output_name, quant_method), daemon=True).start()
    def _start_conversion_worker(self, source, output, method):
        success, response = self.api_client.start_model_conversion(source, output, method)
        self.after(0, self._on_job_started, success, response)
    def _start_requantize_worker(self, source, output, method):
        success, response = self.api_client.start_model_requantize(source, output, method)
        self.after(0, self._on_job_started, success, response)
    def _on_job_started(self, success, response):
        if success:
            self.job_id = response.get('job_id')
            self._log_message(f"Job successfully queued with ID: {self.job_id}")
            self._start_polling()
        else:
            messagebox.showerror("Job Error", f"Failed to start job: {response}", parent=self)
            self.start_button.config(state="normal")
    def _start_polling(self):
        if not self.is_polling:
            self.is_polling = True
            self._poll_job_status()
    def _poll_job_status(self):
        if not self.job_id:
            self.is_polling = False
            return
        threading.Thread(target=self._poll_worker, daemon=True).start()
    def _poll_worker(self):
        success, response = self.api_client.get_conversion_status(self.job_id)
        self.after(0, self._update_status_ui, success, response)
    def _update_status_ui(self, success, response):
        if success:
            status = response.get('status', 'UNKNOWN')
            full_log = response.get('log', [])
            self.log_text.config(state="normal")
            self.log_text.delete("1.0", "end")
            self.log_text.insert("1.0", f"Current Status: {status}\n--- LOG ---\n")
            for line in full_log:
                self.log_text.insert("end", f"{line}\n")
            self.log_text.see("end")
            self.log_text.config(state="disabled")
            if status in ["COMPLETED", "FAILED"]:
                self.is_polling = False
                self.start_button.config(state="normal")
                messagebox.showinfo("Job Finished", f"Job {self.job_id} finished with status: {status}", parent=self)
            else:
                self.after(5000, self._poll_job_status)
        else:
            self._log_message(f"Error polling status: {response}")
            self.after(5000, self._poll_job_status)
    def _log_message(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
    def _toggle_pin_guide(self):
        self.guide_is_pinned = not self.guide_is_pinned
        pin_char = "📌"
        self.guide_pin_button.config(text=pin_char)
        if not self.guide_is_pinned:
            self._hide_guide_panel_later()
    def _show_guide_panel(self, event=None):
        self._cancel_hide_guide()
        self.guide_panel.place(in_=self, relx=0, rely=0, relheight=1.0, anchor='nw', width=350)
        self.guide_panel.lift()
    def _hide_guide_panel_later(self, event=None):
        if not self.guide_is_pinned:
            self.hide_guide_job = self.after(300, lambda: self.guide_panel.place_forget())
    def _cancel_hide_guide(self, event=None):
        if self.hide_guide_job:
            self.after_cancel(self.hide_guide_job)
            self.hide_guide_job = None

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\pricing_page.py
# JUMLAH BARIS : 154
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\pricing_page.py
# JUMLAH BARIS : 153
#######################################################################

import ttkbootstrap as ttk
import webbrowser
import os
from dotenv import load_dotenv
from flowork_gui.api_client.client import ApiClient
class PricingPage(ttk.Frame):
    """
    A UI frame that displays the different license tiers and their features,
    with dynamic buttons based on the user's current license.
    (MODIFIED) Redesigned with a more persuasive, benefit-driven, and cinematic narrative.
    """
    def __init__(self, parent_notebook, kernel_instance):
        self.api_client = ApiClient()
        super().__init__(parent_notebook, padding=20)
        self.kernel = kernel_instance
        self.loc = self.kernel.get_service("localization_manager")
        self.feature_groups = {
            "foundation": {
                "title_key": "feature_group_foundation",
                "features": ["feature_visual_editor", "feature_basic_modules", "feature_manual_install", "feature_theme_customization", "feature_limited_api"]
            },
            "connectivity": {
                "title_key": "feature_group_connectivity",
                "features": ["feature_unlimited_api", "feature_headless_mode"]
            },
            "powerhouse": {
                "title_key": "feature_group_powerhouse",
                "features": ["feature_time_travel_debugger", "feature_preset_versioning", "screen_recorder", "web_scraping_advanced"]
            },
            "intelligence": {
                "title_key": "feature_group_intelligence",
                "features": ["feature_ai_copilot", "ai:provider_access", "ai:local_models", "feature_marketplace_upload", "video_processing"]
            },
            "creator": {
                "title_key": "feature_group_creator",
                "features": ["feature_ai_architect", "core_compiler", "module_generator"]
            },
            "enterprise": {
                "title_key": "feature_group_enterprise",
                "features": ["feature_advanced_security", "feature_priority_support", "feature_team_collaboration"]
            }
        }
        self.tier_data = {
            "free": {
                "title_key": "tier_pemula_title", "tagline_key": "tier_pemula_tagline", "desc_key": "tier_pemula_desc_detail", "style": "secondary",
                "features": ["foundation"]
            },
            "basic": {
                "title_key": "tier_profesional_title", "tagline_key": "tier_profesional_tagline", "desc_key": "tier_profesional_desc_detail", "style": "info",
                "features": ["connectivity", "powerhouse"]
            },
            "pro": {
                "title_key": "tier_arsitek_ai_title", "tagline_key": "tier_arsitek_ai_tagline", "desc_key": "tier_arsitek_ai_desc_detail", "style": "success",
                "features": ["intelligence"]
            },
            "architect": {
                "title_key": "tier_maestro_title", "tagline_key": "tier_maestro_tagline", "desc_key": "tier_maestro_desc_detail", "style": "primary",
                "features": ["creator"]
            },
            "enterprise": {
                "title_key": "tier_titan_title", "tagline_key": "tier_titan_tagline", "desc_key": "tier_titan_desc_detail", "style": "dark",
                "features": ["enterprise"]
            }
        }
        self.base_upgrade_urls = {
            "basic": "https://www.flowork.art/harga/basic",
            "pro": "https://www.flowork.art/harga/pro",
            "architect": "https://www.flowork.art/harga/architect",
            "enterprise": "https://www.flowork.art/kontak"
        }
        self.affiliate_id = None
        affiliate_file_path = os.path.join(self.kernel.data_path, ".flowork_id")
        if os.path.exists(affiliate_file_path):
            load_dotenv(dotenv_path=affiliate_file_path)
            self.affiliate_id = os.getenv("ID_USER")
            if self.affiliate_id:
                self.kernel.write_to_log(f"Affiliate ID '{self.affiliate_id}' loaded successfully.", "SUCCESS")
        self._build_ui()
    def _build_ui(self):
        for widget in self.winfo_children():
            widget.destroy()
        container = ttk.Frame(self)
        container.pack(fill='both', expand=True)
        container.columnconfigure(0, weight=2)
        container.columnconfigure(1, weight=2)
        container.columnconfigure(2, weight=3)
        container.columnconfigure(3, weight=2)
        container.columnconfigure(4, weight=2)
        container.rowconfigure(0, weight=1)
        tier_order = ["free", "basic", "pro", "architect", "enterprise"]
        for i, tier_key in enumerate(tier_order):
            data = self.tier_data[tier_key]
            is_highlighted = (tier_key == "pro")
            self._create_tier_card(container, tier_key, data, is_highlighted).grid(row=0, column=i, sticky="nsew", padx=10, pady=10)
    def _create_tier_card(self, parent, tier_key, data, is_highlighted=False):
        style = f"{data['style']}"
        card = ttk.LabelFrame(parent, text=self.loc.get(data['title_key']), padding=20, bootstyle=style)
        if is_highlighted:
            banner = ttk.Label(card, text=self.loc.get('btn_most_popular', fallback="MOST POPULAR"), bootstyle=f"inverse-{data['style']}", padding=(10, 2), font="-weight bold")
            banner.place(relx=0.5, rely=0, anchor="n", y=-15)
        tagline_text = self.loc.get(data['tagline_key'])
        ttk.Label(card, text=tagline_text, font="-size 12 -weight bold", anchor="center").pack(fill='x', pady=(10, 5))
        desc_text = self.loc.get(data['desc_key'])
        ttk.Label(card, text=desc_text, wraplength=250, justify='center', anchor='center').pack(fill='x', pady=(0, 20))
        all_features_in_tier = set()
        tier_hierarchy_keys = list(self.kernel.TIER_HIERARCHY.keys())
        current_tier_index = tier_hierarchy_keys.index(tier_key)
        for i in range(current_tier_index + 1):
            tier_to_include = tier_hierarchy_keys[i]
            for group_key in self.tier_data[tier_to_include]['features']:
                all_features_in_tier.add(group_key)
        for group_key, group_data in self.feature_groups.items():
            if group_key in all_features_in_tier:
                ttk.Label(card, text=self.loc.get(group_data['title_key']), font="-weight bold", bootstyle="secondary").pack(anchor='w', pady=(10, 2))
                for feature_key in group_data['features']:
                    if feature_key == "feature_limited_api" and self.kernel.TIER_HIERARCHY[tier_key] >= self.kernel.TIER_HIERARCHY['basic']:
                        continue
                    if feature_key == "feature_unlimited_api" and self.kernel.TIER_HIERARCHY[tier_key] < self.kernel.TIER_HIERARCHY['basic']:
                        continue
                    feature_text = self.loc.get(feature_key, fallback=feature_key.replace('_', ' ').title())
                    ttk.Label(card, text=f"✓ {feature_text}", anchor='w').pack(fill='x', padx=10)
        ttk.Frame(card).pack(fill='y', expand=True) # Spacer
        user_tier_level = self.kernel.TIER_HIERARCHY[self.kernel.license_tier]
        card_tier_level = self.kernel.TIER_HIERARCHY[tier_key]
        btn_command = None
        if user_tier_level == card_tier_level:
            btn_text = self.loc.get('btn_current_plan')
            btn_state = "disabled"
            btn_bootstyle = f"outline-{data['style']}"
        elif user_tier_level > card_tier_level:
            btn_text = self.loc.get('btn_included')
            btn_state = "disabled"
            btn_bootstyle = f"outline-{data['style']}"
        else:
            base_url = self.base_upgrade_urls.get(tier_key, "https://www.flowork.art")
            final_url = f"{base_url}?aff={self.affiliate_id}" if self.affiliate_id else base_url
            btn_command = lambda url=final_url: webbrowser.open(url)
            if tier_key == "enterprise":
                btn_text = self.loc.get('btn_contact_us')
            else:
                btn_text = self.loc.get(f'btn_upgrade_{tier_key}', fallback=f"Upgrade to {tier_key.capitalize()}")
            btn_state = "normal"
            btn_bootstyle = data['style']
        action_button = ttk.Button(card, text=btn_text, state=btn_state, command=btn_command, bootstyle=btn_bootstyle)
        action_button.pack(fill='x', ipady=8, pady=(15, 0))
        return card

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\prompt_manager_page.py
# JUMLAH BARIS : 165
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\prompt_manager_page.py
# JUMLAH BARIS : 164
#######################################################################

import ttkbootstrap as ttk
from tkinter import messagebox, scrolledtext, StringVar, Toplevel
import re
from flowork_gui.api_client.client import ApiClient
class PromptManagerPage(ttk.Frame):
    def __init__(self, parent, kernel, **kwargs):
        super().__init__(parent, **kwargs)
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        self.api_client = ApiClient(kernel=self.kernel)
        self.current_prompt_id = None
        self.guide_is_pinned = False
        self.hide_guide_job = None
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        left_pane = ttk.Frame(self, padding=10)
        left_pane.grid(row=0, column=0, sticky="ns", padx=(0, 5))
        left_pane.rowconfigure(1, weight=1)
        list_toolbar = ttk.Frame(left_pane)
        list_toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        new_button = ttk.Button(list_toolbar, text=self.loc.get("button_new", fallback="New"), command=self._new_prompt)
        new_button.pack(side="left")
        delete_button = ttk.Button(list_toolbar, text=self.loc.get("button_delete", fallback="Delete"), command=self._delete_prompt, bootstyle="danger")
        delete_button.pack(side="left", padx=5)
        self.prompt_tree = ttk.Treeview(left_pane, columns=("name",), show="tree", selectmode="browse")
        self.prompt_tree.grid(row=1, column=0, sticky="ns")
        self.prompt_tree.bind("<<TreeviewSelect>>", self._on_prompt_select)
        self.right_pane = ttk.Frame(self, padding=10)
        self.right_pane.grid(row=0, column=1, sticky="nsew")
        self.right_pane.columnconfigure(0, weight=1)
        self.right_pane.rowconfigure(0, weight=1) # MODIFIKASI: Editor sekarang di row 0
        editor_frame = ttk.LabelFrame(self.right_pane, text=self.loc.get("prompt_manager_editor_title", fallback="Prompt Editor"))
        editor_frame.grid(row=0, column=0, sticky="nsew") # MODIFIKASI: Editor sekarang di row 0
        editor_frame.columnconfigure(0, weight=1)
        editor_frame.rowconfigure(3, weight=1)
        self.name_var = StringVar()
        ttk.Label(editor_frame, text=self.loc.get("prompt_manager_name_label", fallback="Template Name:")).grid(row=0, column=0, sticky="w", padx=10, pady=(10,2))
        ttk.Entry(editor_frame, textvariable=self.name_var).grid(row=1, column=0, sticky="ew", padx=10, pady=(0,10))
        ttk.Label(editor_frame, text=self.loc.get("prompt_manager_content_label", fallback="Template Content:")).grid(row=2, column=0, sticky="nw", padx=10, pady=(0,2))
        self.content_text = scrolledtext.ScrolledText(editor_frame, wrap="word", height=15, font=("Consolas", 10))
        self.content_text.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0,10))
        save_button = ttk.Button(self.right_pane, text=self.loc.get("button_save_changes", fallback="Save Changes"), command=self._save_prompt, bootstyle="success")
        save_button.grid(row=1, column=0, sticky="e", pady=10) # MODIFIKASI: Save button sekarang di row 1
        self._build_guide_panel()
        self._load_prompt_list()
        self._populate_tutorial()
    def _build_guide_panel(self):
        guide_handle = ttk.Frame(self.right_pane, width=15, bootstyle="secondary")
        guide_handle.place(relx=0, rely=0, relheight=1, anchor='nw')
        handle_label = ttk.Label(guide_handle, text=">", bootstyle="inverse-secondary", font=("Helvetica", 10, "bold"))
        handle_label.pack(expand=True)
        guide_handle.bind("<Enter>", self._show_guide_panel)
        guide_handle.lift()
        self.guide_panel = ttk.Frame(self.right_pane, bootstyle="secondary")
        control_bar = ttk.Frame(self.guide_panel, bootstyle="secondary")
        control_bar.pack(fill='x', padx=5, pady=2)
        self.guide_pin_button = ttk.Button(control_bar, text="📌", bootstyle="light-link", command=self._toggle_pin_guide)
        self.guide_pin_button.pack(side='right')
        tutorial_frame = ttk.LabelFrame(self.guide_panel, text=self.loc.get("prompt_manager_tutorial_title", fallback="Guide & How-To"))
        tutorial_frame.pack(fill='both', expand=True, padx=5, pady=(0,5))
        tutorial_frame.columnconfigure(0, weight=1)
        tutorial_frame.rowconfigure(0, weight=1)
        self.tutorial_text = scrolledtext.ScrolledText(tutorial_frame, wrap="word", height=10, state="disabled", font="-size 9")
        self.tutorial_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.tutorial_text.tag_configure("bold", font="-size 9 -weight bold")
        self.guide_panel.bind("<Leave>", self._hide_guide_panel_later)
        self.guide_panel.bind("<Enter>", self._cancel_hide_guide)
    def _populate_tutorial(self):
        tutorial_content = self.loc.get("prompt_manager_tutorial_content")
        self._apply_markdown_to_text_widget(self.tutorial_text, tutorial_content)
    def _apply_markdown_to_text_widget(self, text_widget, content):
        text_widget.config(state="normal")
        text_widget.delete("1.0", "end")
        parts = re.split(r'(\*\*.*?\*\*)', content)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                text_widget.insert("end", part[2:-2], "bold")
            else:
                text_widget.insert("end", part)
        text_widget.config(state="disabled")
    def _load_prompt_list(self):
        for i in self.prompt_tree.get_children():
            self.prompt_tree.delete(i)
        success, data = self.api_client.get_prompts()
        if success:
            if isinstance(data, list):
                for prompt in data:
                    self.prompt_tree.insert("", "end", iid=prompt['id'], text=prompt['name'])
            else:
                self.prompt_tree.insert("", "end", text="Error: Invalid data format from API.")
        else:
            self.prompt_tree.insert("", "end", text="Error loading prompts...")
    def _on_prompt_select(self, event):
        selected_items = self.prompt_tree.selection()
        if not selected_items:
            return
        self.current_prompt_id = selected_items[0]
        success, data = self.api_client.get_prompt(self.current_prompt_id)
        if success:
            self.name_var.set(data.get('name', ''))
            self.content_text.delete("1.0", "end")
            self.content_text.insert("1.0", data.get('content', ''))
        else:
            error_message = data if isinstance(data, str) else data.get('error', 'Unknown error')
            messagebox.showerror("Error", f"Could not load prompt details: {error_message}", parent=self)
    def _new_prompt(self):
        self.current_prompt_id = None
        self.name_var.set("")
        self.content_text.delete("1.0", "end")
        self.prompt_tree.selection_set("")
    def _save_prompt(self):
        name = self.name_var.get().strip()
        content = self.content_text.get("1.0", "end-1c").strip()
        if not name or not content:
            messagebox.showwarning("Input Required", "Template Name and Content cannot be empty.", parent=self)
            return
        prompt_data = {"name": name, "content": content}
        if self.current_prompt_id:
            success, response = self.api_client.update_prompt(self.current_prompt_id, prompt_data)
        else:
            success, response = self.api_client.create_prompt(prompt_data)
        if success:
            messagebox.showinfo("Success", "Prompt template saved successfully.", parent=self)
            self._load_prompt_list()
        else:
            error_message = response if isinstance(response, str) else response.get('error', 'Unknown error')
            messagebox.showerror("Error", f"Failed to save prompt: {error_message}", parent=self)
    def _delete_prompt(self):
        if not self.current_prompt_id:
            messagebox.showwarning("Selection Required", "Please select a template to delete.", parent=self)
            return
        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this prompt template?", parent=self):
            success, response = self.api_client.delete_prompt(self.current_prompt_id)
            if success:
                messagebox.showinfo("Success", "Prompt template deleted.", parent=self)
                self._new_prompt()
                self._load_prompt_list()
            else:
                error_message = response if isinstance(response, str) else response.get('error', 'Unknown error')
                messagebox.showerror("Error", f"Failed to delete prompt: {error_message}", parent=self)
    def _toggle_pin_guide(self):
        self.guide_is_pinned = not self.guide_is_pinned
        pin_char = "📌"
        self.guide_pin_button.config(text=pin_char)
        if not self.guide_is_pinned:
            self._hide_guide_panel_later()
    def _show_guide_panel(self, event=None):
        self._cancel_hide_guide()
        self.guide_panel.place(in_=self.right_pane, relx=0, rely=0, relheight=1.0, anchor='nw', width=350)
        self.guide_panel.lift()
    def _hide_guide_panel_later(self, event=None):
        if not self.guide_is_pinned:
            self.hide_guide_job = self.after(300, lambda: self.guide_panel.place_forget())
    def _cancel_hide_guide(self, event=None):
        if self.hide_guide_job:
            self.after_cancel(self.hide_guide_job)
            self.hide_guide_job = None

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\settings_tab.py
# JUMLAH BARIS : 132
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\settings_tab.py
# JUMLAH BARIS : 131
#######################################################################

import ttkbootstrap as ttk
from tkinter import messagebox
from .settings_components.general_settings_frame import GeneralSettingsFrame
from .settings_components.webhook_settings_frame import WebhookSettingsFrame
from .settings_components.notification_settings_frame import NotificationSettingsFrame
from .settings_components.license_management_frame import LicenseManagementFrame
from .settings_components.error_handler_frame import ErrorHandlerFrame
from .settings_components.variable_manager_frame import VariableManagerFrame
from .settings_components.ai_provider_settings_frame import AiProviderSettingsFrame
from .settings_components.recorder_settings_frame import RecorderSettingsFrame
import threading
from flowork_kernel.ui_shell.custom_widgets.scrolled_frame import ScrolledFrame
from flowork_kernel.exceptions import PermissionDeniedError
from flowork_gui.api_client.client import ApiClient
class SettingsTab(ttk.Frame):
    """
    Acts as a container and coordinator for all the individual settings frames.
    [REFACTORED] Now fetches all settings from the API and orchestrates saving.
    """
    def __init__(self, parent_notebook, kernel_instance):
        super().__init__(parent_notebook, padding=15)
        self.kernel = kernel_instance
        self.loc = self.kernel.get_service("localization_manager")
        self.api_client = ApiClient(kernel=self.kernel)
        self.all_settings_frames = []
        self._content_initialized = False
        ttk.Label(self, text="Loading Settings...").pack(expand=True)
    def _initialize_content(self):
        if self._content_initialized:
            return
        for widget in self.winfo_children():
            widget.destroy()
        self._build_ui()
        self._load_all_settings_from_api()
        self._content_initialized = True
    def refresh_content(self):
        """Refreshes the content and state of all child setting frames."""
        self.kernel.write_to_log("SettingsTab: Refreshing content.", "DEBUG")
        for frame in self.all_settings_frames:
            if hasattr(frame, 'refresh_content'):
                frame.refresh_content()
        if hasattr(self, 'variable_manager_frame'):
            self.variable_manager_frame.load_variables_to_ui()
    def _build_ui(self):
        paned_window = ttk.PanedWindow(self, orient='horizontal')
        paned_window.pack(fill='both', expand=True)
        left_scrolled_frame = ScrolledFrame(paned_window)
        paned_window.add(left_scrolled_frame, weight=1)
        right_frame = ttk.Frame(paned_window, padding=5)
        paned_window.add(right_frame, weight=1)
        self._build_left_panel(left_scrolled_frame.scrollable_frame)
        self._build_right_panel(right_frame)
    def _build_left_panel(self, parent_frame):
        self.general_frame = GeneralSettingsFrame(parent_frame, self.kernel)
        self.general_frame.pack(fill="x", pady=5, padx=5)
        self.all_settings_frames.append(self.general_frame)
        self.ai_provider_frame = AiProviderSettingsFrame(parent_frame, self.kernel)
        self.ai_provider_frame.pack(fill="x", pady=5, padx=5)
        self.all_settings_frames.append(self.ai_provider_frame)
        self.recorder_frame = RecorderSettingsFrame(parent_frame, self.kernel)
        self.recorder_frame.pack(fill="x", pady=5, padx=5)
        self.all_settings_frames.append(self.recorder_frame)
        self.webhook_frame = WebhookSettingsFrame(parent_frame, self.kernel)
        self.webhook_frame.pack(fill="x", pady=5, padx=5)
        self.all_settings_frames.append(self.webhook_frame)
        self.notification_frame = NotificationSettingsFrame(parent_frame, self.kernel)
        self.notification_frame.pack(fill="x", pady=5, padx=5)
        self.all_settings_frames.append(self.notification_frame)
        license_manager = self.kernel.get_service("license_manager_service")
        self.license_frame = LicenseManagementFrame(parent_frame, self.kernel)
        self.all_settings_frames.append(self.license_frame)
        if license_manager and license_manager.remote_permission_rules and license_manager.remote_permission_rules.get("monetization_active"):
            self.license_frame.pack(fill="x", pady=5, padx=5)
        else:
            pass
        self.error_handler_frame = ErrorHandlerFrame(parent_frame, self.kernel)
        self.error_handler_frame.pack(fill="x", pady=5, padx=5, expand=True, anchor="n")
        self.all_settings_frames.append(self.error_handler_frame)
        save_button = ttk.Button(parent_frame, text=self.loc.get("settings_save_button", fallback="Save All Settings"), command=self._save_all_settings, bootstyle="success")
        save_button.pack(pady=10, padx=5, side="bottom", anchor="e")
    def _build_right_panel(self, parent_frame):
        self.variable_manager_frame = VariableManagerFrame(parent_frame, self.kernel)
        self.variable_manager_frame.pack(fill="both", expand=True, pady=5, padx=5)
    def _load_all_settings_from_api(self):
        threading.Thread(target=self._load_settings_worker, daemon=True).start()
    def _load_settings_worker(self):
        success, settings_data = self.api_client.get_all_settings()
        self.after(0, self._populate_settings_ui, success, settings_data)
    def _populate_settings_ui(self, success, settings_data):
        if success:
            for frame in self.all_settings_frames:
                try:
                    if hasattr(frame, 'load_settings_data'):
                        frame.load_settings_data(settings_data)
                except PermissionDeniedError:
                    self.kernel.write_to_log(f"Hiding settings frame '{frame.__class__.__name__}' due to insufficient permissions.", "WARN")
                    frame.pack_forget()
                except Exception as e:
                    self.kernel.write_to_log(f"Error loading settings for frame '{frame.__class__.__name__}': {e}", "ERROR")
                    frame.pack_forget()
        else:
            messagebox.showerror(self.loc.get("messagebox_error_title"), f"Failed to load settings from API: {settings_data}")
    def _save_all_settings(self):
        all_new_settings = {}
        try:
            for frame in self.all_settings_frames:
                if frame.winfo_ismapped() and hasattr(frame, 'get_settings_data'):
                    all_new_settings.update(frame.get_settings_data())
            threading.Thread(target=self._save_settings_worker, args=(all_new_settings,), daemon=True).start()
        except ValueError as e:
            messagebox.showerror(self.loc.get("messagebox_error_title"), str(e))
        except Exception as e:
            messagebox.showerror(self.loc.get("messagebox_error_title"), f"{self.loc.get('settings_save_error_msg')}: {e}")
    def _save_settings_worker(self, settings_to_save):
        success, response = self.api_client.save_settings(settings_to_save)
        self.after(0, self._on_save_settings_complete, success, response)
    def _on_save_settings_complete(self, success, response):
        if success:
            messagebox.showinfo(self.loc.get("messagebox_success_title"), self.loc.get("settings_save_success_msg"))
            self._load_all_settings_from_api()
            if self.kernel.root and hasattr(self.kernel.root, 'refresh_ui_components'):
                self.kernel.root.refresh_ui_components()
        else:
             messagebox.showerror(self.loc.get("messagebox_error_title"), f"API Error: {response}")

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\template_manager_page.py
# JUMLAH BARIS : 200
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\template_manager_page.py
# JUMLAH BARIS : 199
#######################################################################

import ttkbootstrap as ttk
from tkinter import ttk as tk_ttk, messagebox, filedialog, scrolledtext
import os
import shutil
import json
import platform
import subprocess
import re
from flowork_kernel.ui_shell.custom_widgets.tooltip import ToolTip
from flowork_gui.api_client.client import ApiClient
class TemplateManagerPage(ttk.Frame):
    def __init__(self, parent_notebook, kernel_instance):
        self.api_client = ApiClient()
        super().__init__(parent_notebook, style='TFrame', padding=0)
        self.kernel = kernel_instance
        self.loc = self.kernel.get_service("localization_manager")
        self.guide_is_pinned = False
        self.hide_guide_job = None
        self.create_widgets()
        theme_manager = self.kernel.get_service("theme_manager")
        if theme_manager:
            self.apply_styles(theme_manager.get_colors())
        self.populate_template_list()
        self._populate_guide()
    def apply_styles(self, colors):
        style = tk_ttk.Style(self)
        style.configure('TFrame', background=colors.get('bg'))
        style.configure('TLabel', background=colors.get('bg'), foreground=colors.get('fg'))
        style.configure('TLabelframe', background=colors.get('bg'), borderwidth=1, relief='solid', bordercolor=colors.get('border'))
        style.configure('TLabelframe.Label', background=colors.get('bg'), foreground=colors.get('fg'), font=('Helvetica', 10, 'bold'))
    def _apply_markdown_to_text_widget(self, text_widget, content):
        text_widget.config(state="normal")
        text_widget.delete("1.0", "end")
        parts = re.split(r'(\*\*.*?\*\*)', content)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                text_widget.insert("end", part[2:-2], "bold")
            else:
                text_widget.insert("end", part)
        text_widget.config(state="disabled")
    def _populate_guide(self):
        guide_content = self.loc.get("theme_manager_guide_content")
        self._apply_markdown_to_text_widget(self.guide_text, guide_content)
        self.guide_text.tag_configure("bold", font="-size 9 -weight bold")
    def create_widgets(self):
        main_content_frame = ttk.Frame(self, padding=20, style='TFrame')
        main_content_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        theme_frame = ttk.LabelFrame(main_content_frame, text=self.loc.get('theme_management_title'), padding=15, style='TLabelframe')
        theme_frame.pack(fill="both", expand=True, pady=(0, 20))
        upload_theme_button = ttk.Button(theme_frame, text=self.loc.get('upload_theme_button'), command=self.upload_theme, style="info.TButton")
        upload_theme_button.pack(fill='x', pady=5)
        self.theme_list_frame = ttk.Frame(theme_frame, style='TFrame')
        self.theme_list_frame.pack(fill='both', expand=True, pady=(10,0))
        guide_handle = ttk.Frame(self, width=15, bootstyle="secondary")
        guide_handle.place(relx=0, rely=0, relheight=1, anchor='nw')
        handle_label = ttk.Label(guide_handle, text=">", bootstyle="inverse-secondary", font=("Helvetica", 10, "bold"))
        handle_label.pack(expand=True)
        guide_handle.bind("<Enter>", self._show_guide_panel)
        self.guide_panel = ttk.Frame(self, bootstyle="secondary")
        control_bar = ttk.Frame(self.guide_panel, bootstyle="secondary")
        control_bar.pack(fill='x', padx=5, pady=2)
        self.guide_pin_button = ttk.Button(control_bar, text="📌", bootstyle="light-link", command=self._toggle_pin_guide)
        self.guide_pin_button.pack(side='right')
        guide_frame_inner = ttk.LabelFrame(self.guide_panel, text=self.loc.get('theme_manager_guide_title'), padding=15)
        guide_frame_inner.pack(fill='both', expand=True, padx=5, pady=(0,5))
        guide_frame_inner.columnconfigure(0, weight=1)
        guide_frame_inner.rowconfigure(0, weight=1)
        self.guide_text = scrolledtext.ScrolledText(guide_frame_inner, wrap="word", height=10, state="disabled", font="-size 9")
        self.guide_text.grid(row=0, column=0, sticky="nsew")
        self.guide_panel.bind("<Leave>", self._hide_guide_panel_later)
        self.guide_panel.bind("<Enter>", self._cancel_hide_guide)
        guide_handle.lift()
    def populate_template_list(self):
        self.kernel.write_to_log(self.loc.get('log_populating_theme_list'), "DEBUG")
        for widget in self.theme_list_frame.winfo_children():
            widget.destroy()
        theme_manager = self.kernel.get_service("theme_manager")
        themes = theme_manager.get_all_themes() if theme_manager else {}
        if not themes:
            ttk.Label(self.theme_list_frame, text=self.loc.get('no_themes_installed_message'), style='TLabel').pack()
            self.kernel.write_to_log(self.loc.get('log_no_themes_found'), "INFO")
            return
        sorted_themes = sorted(themes.items(), key=lambda item: item[1].get('name', item[0]).lower())
        for theme_id, theme_data in sorted_themes:
            theme_name = theme_data.get('name', theme_id)
            item_frame = ttk.Frame(self.theme_list_frame, style='TFrame')
            item_frame.pack(fill='x', pady=2)
            label_text = self.loc.get('theme_list_item_format', name=theme_name, id=theme_id)
            ttk.Label(item_frame, text=label_text, style='TLabel').pack(side='left', anchor='w', fill='x', expand=True)
            buttons_frame = ttk.Frame(item_frame, style='TFrame')
            buttons_frame.pack(side='right')
            is_removable = (theme_id != "flowork_default")
            if is_removable:
                uninstall_button = ttk.Button(buttons_frame, text=self.loc.get('uninstall_button'), style="link", width=2, command=lambda tid=theme_id, tname=theme_name: self.uninstall_theme(tid, tname))
                ToolTip(uninstall_button).update_text(self.loc.get('tooltip_delete_theme'))
                uninstall_button.pack(side='right', padx=(5,0))
            edit_button = ttk.Button(buttons_frame, text=self.loc.get('edit_button'), style="info-link", width=2, command=lambda tid=theme_id: self.edit_theme(tid))
            ToolTip(edit_button).update_text(self.loc.get('tooltip_edit_theme'))
            edit_button.pack(side='right', padx=(5,0))
            self.kernel.write_to_log(self.loc.get('log_theme_added_to_list', name=theme_name, id=theme_id), "DEBUG")
        self.kernel.write_to_log(self.loc.get('log_theme_list_populated_success'), "INFO")
    def _open_path_in_explorer(self, path):
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
            self.kernel.write_to_log(self.loc.get('log_opening_folder', path=path), "INFO")
        except Exception as e:
            error_msg = self.loc.get('log_failed_to_open_folder', path=path, error=str(e))
            self.kernel.write_to_log(error_msg, "ERROR")
            messagebox.showerror(self.loc.get('error_title'), error_msg)
    def edit_theme(self, theme_id):
        theme_manager = self.kernel.get_service("theme_manager")
        if not theme_manager: return
        all_themes = theme_manager.get_all_themes()
        theme_data = all_themes.get(theme_id)
        if theme_data and 'path' in theme_data:
            self._open_path_in_explorer(theme_data['path'])
        else:
            messagebox.showerror(self.loc.get('error_title'), self.loc.get('theme_not_found_error', name=theme_id))
    def uninstall_theme(self, theme_id, theme_name):
        self.kernel.write_to_log(self.loc.get('log_uninstall_theme_attempt', name=theme_name, id=theme_id), "INFO")
        theme_manager = self.kernel.get_service("theme_manager")
        if not theme_manager: return
        all_themes = theme_manager.get_all_themes()
        theme_data = all_themes.get(theme_id)
        if not theme_data:
            messagebox.showerror(self.loc.get('error_title'), self.loc.get('theme_not_found_error', name=theme_name))
            self.kernel.write_to_log(self.loc.get('log_theme_not_found_for_uninstall', fallback="ERROR: Tema '{name}' ({id}) tidak ditemukan untuk di-uninstall.", name=theme_name, id=theme_id), "ERROR")
            return
        theme_path_to_delete = theme_data['path']
        if messagebox.askyesno(self.loc.get('confirm_delete_title'), self.loc.get('confirm_delete_theme_message', name=theme_name)):
            try:
                os.remove(theme_path_to_delete)
                self.kernel.write_to_log(self.loc.get('log_theme_deleted_success', name=theme_name), "SUCCESS")
                messagebox.showinfo(self.loc.get('success_title'), self.loc.get('theme_deleted_success_message', name=theme_name))
                self.populate_template_list()
                self.kernel.root.refresh_ui_components()
            except Exception as e:
                error_msg = self.loc.get('theme_delete_failed_error', name=theme_name, error=e)
                self.kernel.write_to_log(error_msg, "ERROR")
                messagebox.showerror(self.loc.get('failed_title'), error_msg)
        else:
            self.kernel.write_to_log(self.loc.get('log_theme_uninstall_cancelled', name=theme_name), "INFO")
    def upload_theme(self):
        self.kernel.write_to_log(self.loc.get('log_upload_theme_started'), "INFO")
        filepath = filedialog.askopenfilename(
            title=self.loc.get('select_theme_file_title'),
            filetypes=[(self.loc.get('json_files_label'), "*.json")]
        )
        if not filepath:
            self.kernel.write_to_log(self.loc.get('theme_upload_cancelled'), "WARN")
            return
        theme_manager = self.kernel.get_service("theme_manager")
        if not theme_manager: return
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
                if "name" not in theme_data or "colors" not in theme_data:
                    raise ValueError(self.loc.get('invalid_theme_format_error'))
            theme_filename = os.path.basename(filepath)
            target_path = os.path.join(self.kernel.themes_path, theme_filename)
            shutil.copyfile(filepath, target_path)
            success_msg = self.loc.get('theme_upload_success', name=theme_data['name'])
            messagebox.showinfo(self.loc.get('success_title'), success_msg)
            self.populate_template_list()
            self.kernel.root.refresh_ui_components()
        except Exception as e:
            error_msg_detail = str(e)
            error_msg_localized = self.loc.get('theme_upload_failed_error', filename=os.path.basename(filepath), error=error_msg_detail)
            self.kernel.write_to_log(error_msg_localized, "ERROR")
            messagebox.showerror(self.loc.get('theme_upload_failed_title'), error_msg_localized)
    def _toggle_pin_guide(self):
        self.guide_is_pinned = not self.guide_is_pinned
        pin_char = "📌"
        self.guide_pin_button.config(text=pin_char)
        if not self.guide_is_pinned:
            self._hide_guide_panel_later()
    def _show_guide_panel(self, event=None):
        self._cancel_hide_guide()
        self.guide_panel.place(in_=self, relx=0, rely=0, relheight=1.0, anchor='nw', width=350)
        self.guide_panel.lift()
    def _hide_guide_panel_later(self, event=None):
        if not self.guide_is_pinned:
            self.hide_guide_job = self.after(300, lambda: self.guide_panel.place_forget())
    def _cancel_hide_guide(self, event=None):
        if self.hide_guide_job:
            self.after_cancel(self.hide_guide_job)
            self.hide_guide_job = None

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\trigger_manager_page.py
# JUMLAH BARIS : 345
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\trigger_manager_page.py
# JUMLAH BARIS : 344
#######################################################################

import ttkbootstrap as ttk
from tkinter import messagebox, Toplevel, scrolledtext
import uuid
from datetime import datetime, timezone
import threading
from flowork_kernel.utils.performance_logger import log_performance
import re # (ADDED) Import regex for markdown parsing
from flowork_gui.api_client.client import ApiClient
class TriggerManagerPage(ttk.Frame):
    """
    [REFACTORED V5] Complete UI overhaul for trigger management.
    Features a three-pane layout: a trigger toolbox, a details panel
    with localized descriptions and tutorials, and the active rules area.
    [FIXED] Text color in details panel now respects the current theme.
    """
    def __init__(self, parent, kernel):
        super().__init__(parent)
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        self.api_client = ApiClient()
        self.countdown_updater_id = None
        self.countdown_jobs = {}
        self._drag_data = {}
        self.trigger_definitions = {}
        self.right_pane = None
        self._build_ui_v3()
        self._load_initial_data()
        self._start_countdown_updater()
        event_bus = self.kernel.get_service("event_bus")
        if event_bus:
            subscriber_id = f"trigger_manager_page_{id(self)}"
            event_bus.subscribe("CRON_JOB_EXECUTED", subscriber_id, self._on_cron_job_executed)
            self.kernel.write_to_log(f"TriggerManagerPage is now listening for cron job executions.", "DEBUG")
    def _build_ui_v3(self):
        """Builds the new three-pane, drag-and-drop UI with details panel."""
        main_pane = ttk.PanedWindow(self, orient='horizontal')
        main_pane.pack(fill='both', expand=True, padx=15, pady=15)
        left_pane_container = ttk.Frame(main_pane)
        main_pane.add(left_pane_container, weight=1)
        left_vertical_pane = ttk.PanedWindow(left_pane_container, orient='vertical')
        left_vertical_pane.pack(fill='both', expand=True)
        toolbox_frame = ttk.LabelFrame(left_vertical_pane, text="Available Triggers", padding=10)
        left_vertical_pane.add(toolbox_frame, weight=1)
        self.trigger_toolbox_tree = ttk.Treeview(toolbox_frame, show="tree", selectmode="browse")
        self.trigger_toolbox_tree.pack(expand=True, fill='both')
        self.trigger_toolbox_tree.bind("<ButtonPress-1>", self._on_drag_start)
        self.trigger_toolbox_tree.bind("<B1-Motion>", self._on_drag_motion)
        self.trigger_toolbox_tree.bind("<ButtonRelease-1>", self._on_drag_release)
        self.trigger_toolbox_tree.bind("<<TreeviewSelect>>", self._on_toolbox_select)
        details_frame = ttk.LabelFrame(left_vertical_pane, text="Trigger Details", padding=10)
        left_vertical_pane.add(details_frame, weight=2)
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(2, weight=1)
        theme_manager = self.kernel.get_service("theme_manager")
        colors = theme_manager.get_colors() if theme_manager else {}
        fg_color = colors.get('fg', 'white')
        bg_color = colors.get('bg', '#222222')
        text_bg_color = colors.get('dark', '#333333')
        self.detail_title = ttk.Label(details_frame, text="Select a trigger to see details", font="-weight bold", wraplength=250)
        self.detail_title.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        self.detail_desc = ttk.Label(details_frame, text="", wraplength=280, justify="left", foreground=fg_color, background=bg_color)
        self.detail_desc.grid(row=1, column=0, sticky="nsew", pady=(0,10))
        self.detail_usage = scrolledtext.ScrolledText(
            details_frame,
            wrap="word",
            height=8,
            state="disabled",
            font="-size 9",
            background=text_bg_color,
            foreground=fg_color,
            borderwidth=0,
            highlightthickness=0,
            insertbackground=fg_color # (ADDED) Makes the cursor visible if editable
        )
        self.detail_usage.grid(row=2, column=0, sticky="nsew")
        self.detail_usage.tag_configure("bold", font="-size 9 -weight bold")
        self.right_pane = ttk.Frame(main_pane, padding=10)
        main_pane.add(self.right_pane, weight=3)
        self.right_pane.rowconfigure(1, weight=1)
        self.right_pane.columnconfigure(0, weight=1)
        button_frame = ttk.Frame(self.right_pane)
        button_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Button(button_frame, text=self.loc.get('trigger_btn_new', fallback="New Rule..."), command=self._open_rule_editor, style="success.TButton").pack(side="left")
        ttk.Button(button_frame, text=self.loc.get('trigger_btn_edit', fallback="Edit..."), command=self._edit_selected_rule).pack(side="left", padx=10)
        ttk.Button(button_frame, text=self.loc.get('trigger_btn_delete', fallback="Delete"), command=self._delete_selected_rule, style="danger.TButton").pack(side="left")
        rules_frame = ttk.LabelFrame(self.right_pane, text="Active Trigger Rules")
        rules_frame.grid(row=1, column=0, sticky="nsew")
        rules_frame.rowconfigure(0, weight=1)
        rules_frame.columnconfigure(0, weight=1)
        columns = ("name", "trigger_type", "preset", "status", "next_run")
        self.rules_tree = ttk.Treeview(rules_frame, columns=columns, show="headings", style="Custom.Treeview")
        self.rules_tree.heading("name", text=self.loc.get('trigger_col_name', fallback="Rule Name"))
        self.rules_tree.heading("trigger_type", text=self.loc.get('trigger_col_type', fallback="Trigger Type"))
        self.rules_tree.heading("preset", text=self.loc.get('trigger_col_preset', fallback="Preset to Run"))
        self.rules_tree.heading("status", text=self.loc.get('trigger_col_status', fallback="Status"))
        self.rules_tree.heading("next_run", text=self.loc.get('trigger_col_next_run', fallback="Next Schedule"))
        self.rules_tree.column("name", width=250)
        self.rules_tree.column("trigger_type", width=150)
        self.rules_tree.column("preset", width=200)
        self.rules_tree.column("status", width=80, anchor='center')
        self.rules_tree.column("next_run", width=150, anchor='center')
        self.rules_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(rules_frame, orient="vertical", command=self.rules_tree.yview)
        self.rules_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")
    def _apply_markdown_to_text_widget(self, text_widget, content):
        text_widget.config(state="normal")
        text_widget.delete("1.0", "end")
        parts = re.split(r'(\*\*.*?\*\*)', content)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                text_widget.insert("end", part[2:-2], "bold")
            else:
                text_widget.insert("end", part)
        text_widget.config(state="disabled")
    def _on_toolbox_select(self, event=None):
        selected_items = self.trigger_toolbox_tree.selection()
        if not selected_items:
            return
        trigger_id = selected_items[0]
        trigger_def = self.trigger_definitions.get(trigger_id)
        if trigger_def:
            name = self.loc.get(trigger_def.get('name_key'), fallback=trigger_def.get('id'))
            desc = self.loc.get(trigger_def.get('description_key'), fallback='No description available.')
            usage = self.loc.get(trigger_def.get('tutorial_key'), fallback='No tutorial available.')
            self.detail_title.config(text=name)
            self.detail_desc.config(text=desc)
            self._apply_markdown_to_text_widget(self.detail_usage, usage)
    def _populate_trigger_toolbox(self, success, definitions):
        for item in self.trigger_toolbox_tree.get_children():
            self.trigger_toolbox_tree.delete(item)
        self.trigger_definitions.clear()
        if success:
            for trigger_def in sorted(definitions, key=lambda x: self.loc.get(x.get('name_key'), fallback=x.get('id', ''))):
                trigger_id = trigger_def['id']
                display_name = self.loc.get(trigger_def.get('name_key'), fallback=trigger_id)
                self.trigger_definitions[trigger_id] = trigger_def
                self.trigger_toolbox_tree.insert("", "end", iid=trigger_id, text=display_name)
        else:
            self.trigger_toolbox_tree.insert("", "end", text="Error loading triggers.")
    def _on_drag_start(self, event):
        item_id = self.trigger_toolbox_tree.identify_row(event.y)
        if not item_id: return
        item_text = self.trigger_toolbox_tree.item(item_id, "text")
        self._drag_data = {
            "item_id": item_id,
            "widget": ttk.Label(self.winfo_toplevel(), text=item_text, bootstyle="inverse-info", padding=5, relief="solid"),
            "tree_widget": self.trigger_toolbox_tree
        }
    def _on_drag_motion(self, event):
        if self._drag_data.get("widget"):
            self._drag_data['widget'].place(x=event.x_root - self.winfo_toplevel().winfo_rootx() + 15, y=event.y_root - self.winfo_toplevel().winfo_rooty() + 15)
    def _on_drag_release(self, event):
        if self._drag_data.get("widget"):
            self._drag_data["widget"].destroy()
        drop_x, drop_y = event.x_root, event.y_root
        right_pane = self.right_pane
        if right_pane and right_pane.winfo_rootx() < drop_x < right_pane.winfo_rootx() + right_pane.winfo_width() and \
           right_pane.winfo_rooty() < drop_y < right_pane.winfo_rooty() + right_pane.winfo_height():
            dropped_trigger_id = self._drag_data.get("item_id")
            if dropped_trigger_id:
                self.kernel.write_to_log(f"Trigger type '{dropped_trigger_id}' dropped. Opening editor.", "INFO")
                prefilled_data = {'trigger_id': dropped_trigger_id}
                self._open_rule_editor(rule_data=prefilled_data)
        self._drag_data = {}
    def _load_initial_data(self):
        self.rules_tree.insert("", "end", values=("Loading rules from API...", "", "", "", ""), tags=("loading",))
        self.trigger_toolbox_tree.insert("", "end", text="Loading triggers...", tags=("loading",))
        threading.Thread(target=self._load_data_worker, daemon=True).start()
    @log_performance("Fetching all trigger data for TriggerManagerPage")
    def _load_data_worker(self):
        success_rules, rules = self.api_client.get_trigger_rules()
        success_defs, defs = self.api_client.get_trigger_definitions()
        self.after(0, self._populate_rules_list_from_data, success_rules, rules)
        self.after(0, self._populate_trigger_toolbox, success_defs, defs)
    def _populate_rules_list_from_data(self, success, rules):
        for item in self.rules_tree.get_children():
            self.rules_tree.delete(item)
        self.countdown_jobs.clear()
        if not success:
            messagebox.showerror(self.loc.get('error_title'), f"Failed to load trigger rules: {rules}")
            self.rules_tree.insert("", "end", values=("Failed to load rules.", "", "", "", ""), tags=("error",))
            return
        for rule_data in sorted(rules, key=lambda r: r.get('name', '')):
            status = self.loc.get('status_enabled') if rule_data.get("is_enabled") else self.loc.get('status_disabled')
            next_run_text = "-"
            if rule_data.get("is_enabled") and rule_data.get('next_run_time'):
                next_run_text = self.loc.get('status_calculating')
            values = (
                rule_data.get("name", "No Name"),
                rule_data.get("trigger_name", "Unknown"),
                rule_data.get("preset_to_run", "-"),
                status,
                next_run_text
            )
            item_id = self.rules_tree.insert("", "end", values=values, iid=rule_data['id'])
            if rule_data.get("is_enabled") and rule_data.get('next_run_time'):
                self.countdown_jobs[item_id] = rule_data['next_run_time']
    def _start_countdown_updater(self):
        if self.countdown_updater_id is None:
            self._update_countdowns()
    def _update_countdowns(self):
        if not self.winfo_exists(): return
        for item_id, next_run_iso in self.countdown_jobs.items():
            if not self.rules_tree.exists(item_id): continue
            try:
                next_run_time = datetime.fromisoformat(next_run_iso)
                now_utc = datetime.now(timezone.utc)
                delta = next_run_time - now_utc
                if delta.total_seconds() > 0:
                    hours, remainder = divmod(int(delta.total_seconds()), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    countdown_str = f"{hours:02}:{minutes:02}:{seconds:02}"
                    self.rules_tree.set(item_id, "next_run", countdown_str)
                else:
                    self.rules_tree.set(item_id, "next_run", self.loc.get('status_waiting_schedule'))
            except (ValueError, TypeError):
                 self.rules_tree.set(item_id, "next_run", self.loc.get('status_not_scheduled'))
        self.countdown_updater_id = self.after(1000, self._update_countdowns)
    def destroy(self):
        if self.countdown_updater_id:
            self.after_cancel(self.countdown_updater_id)
        event_bus = self.kernel.get_service("event_bus")
        if event_bus:
            subscriber_id = f"trigger_manager_page_{id(self)}"
        super().destroy()
    def _on_cron_job_executed(self, event_data):
        self.kernel.write_to_log("Cron job executed, TriggerManagerPage is refreshing its data.", "DEBUG")
        self.after(1000, self._load_initial_data)
    def _edit_selected_rule(self):
        selected_items = self.rules_tree.selection()
        if not selected_items:
            messagebox.showwarning(self.loc.get('warning_title'), self.loc.get('trigger_warn_select_to_edit'))
            return
        success, all_rules = self.api_client.get_trigger_rules()
        if not success:
            messagebox.showerror(self.loc.get('error_title'), "Could not fetch rule details for editing.")
            return
        rule_data = next((r for r in all_rules if r['id'] == selected_items[0]), None)
        if rule_data:
            self._open_rule_editor(rule_id=selected_items[0], rule_data=rule_data)
    def _delete_selected_rule(self):
        selected_items = self.rules_tree.selection()
        if not selected_items:
            messagebox.showwarning(self.loc.get('warning_title'), self.loc.get('trigger_warn_select_to_delete'))
            return
        rule_id = selected_items[0]
        rule_name = self.rules_tree.item(rule_id, 'values')[0]
        if messagebox.askyesno(self.loc.get('confirm_delete_title'), self.loc.get('trigger_confirm_delete', name=rule_name)):
            success, response = self.api_client.delete_trigger_rule(rule_id)
            if success:
                self._save_and_reload()
            else:
                messagebox.showerror(self.loc.get('error_title'), f"Failed to delete rule: {response}")
    def _save_and_reload(self):
        self._load_initial_data()
        self.api_client.reload_triggers()
    def _open_rule_editor(self, rule_id=None, rule_data=None):
        rule_data = rule_data or {}
        editor_window = Toplevel(self)
        editor_window.transient(self)
        editor_window.grab_set()
        editor_window.title(self.loc.get('trigger_editor_title_edit' if rule_id else 'trigger_editor_title_new'))
        _, trigger_defs = self.api_client.get_trigger_definitions()
        _, presets = self.api_client.get_presets()
        form_vars = {
            'name': ttk.StringVar(value=rule_data.get('name', '')),
            'trigger_id': ttk.StringVar(value=rule_data.get('trigger_id', '')),
            'preset_to_run': ttk.StringVar(value=rule_data.get('preset_to_run', '')),
            'is_enabled': ttk.BooleanVar(value=rule_data.get('is_enabled', True)),
        }
        main_frame = ttk.Frame(editor_window, padding=20)
        main_frame.pack(fill="both", expand=True)
        ttk.Label(main_frame, text=self.loc.get('trigger_form_name')).pack(anchor='w', pady=(0,2))
        ttk.Entry(main_frame, textvariable=form_vars['name']).pack(fill='x', pady=(0, 10))
        ttk.Label(main_frame, text=self.loc.get('trigger_form_type')).pack(anchor='w', pady=(0,2))
        trigger_display_names = {self.loc.get(tdef.get('name_key'), fallback=tdef['id']): tdef['id'] for tdef in trigger_defs}
        trigger_combobox = ttk.Combobox(main_frame, state="readonly", values=list(sorted(trigger_display_names.keys())))
        if form_vars['trigger_id'].get():
            id_to_display = {v: k for k, v in trigger_display_names.items()}
            display_name = id_to_display.get(form_vars['trigger_id'].get())
            if display_name:
                trigger_combobox.set(display_name)
            else:
                self.kernel.write_to_log(f"Cannot set trigger in UI, ID '{form_vars['trigger_id'].get()}' not found in loaded definitions.", "WARN")
        trigger_combobox.pack(fill='x', pady=(0, 10))
        ttk.Label(main_frame, text=self.loc.get('trigger_form_preset')).pack(anchor='w', pady=(0,2))
        ttk.Combobox(main_frame, textvariable=form_vars['preset_to_run'], values=presets, state="readonly").pack(fill='x', pady=(0, 10))
        config_frame_container = ttk.Frame(main_frame)
        config_frame_container.pack(fill="both", expand=True, pady=5)
        def on_trigger_selected(event=None):
            for widget in config_frame_container.winfo_children(): widget.destroy()
            trigger_manager_service = self.kernel.get_service("trigger_manager_service")
            if not trigger_manager_service: return
            selected_display_name = trigger_combobox.get()
            selected_trigger_id = trigger_display_names.get(selected_display_name)
            if not selected_trigger_id: return
            form_vars['trigger_id'].set(selected_trigger_id)
            ConfigUIClass = trigger_manager_service.get_config_ui_class(selected_trigger_id)
            if ConfigUIClass:
                config_frame_container.configure(padding=(0, 10))
                config_ui_instance = ConfigUIClass(config_frame_container, self.loc, rule_data.get('config', {}))
                config_ui_instance.pack(fill='both', expand=True)
                form_vars['config_ui'] = config_ui_instance
            else:
                config_frame_container.configure(padding=(0, 0))
        trigger_combobox.bind("<<ComboboxSelected>>", on_trigger_selected)
        if form_vars['trigger_id'].get(): on_trigger_selected()
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(side='bottom', fill='x', pady=(10,0))
        ttk.Checkbutton(bottom_frame, text=self.loc.get('trigger_form_enable'), variable=form_vars['is_enabled']).pack(side='left')
        button_container = ttk.Frame(bottom_frame)
        button_container.pack(side='right')
        def _save_rule():
            if not form_vars['trigger_id'].get():
                messagebox.showerror(self.loc.get('error_title'), self.loc.get('trigger_err_no_type_selected'))
                return
            new_rule_data = {
                "name": form_vars['name'].get(),
                "trigger_id": form_vars['trigger_id'].get(),
                "preset_to_run": form_vars['preset_to_run'].get(),
                "is_enabled": form_vars['is_enabled'].get(),
                "config": {}
            }
            if 'config_ui' in form_vars and hasattr(form_vars['config_ui'], 'get_config'):
                new_rule_data['config'] = form_vars['config_ui'].get_config()
            if rule_id:
                success, _ = self.api_client.update_trigger_rule(rule_id, new_rule_data)
            else:
                success, _ = self.api_client.create_trigger_rule(new_rule_data)
            if success:
                self._save_and_reload()
                editor_window.destroy()
            else:
                messagebox.showerror(self.loc.get('error_title'), "Failed to save the rule via API.")
        ttk.Button(button_container, text=self.loc.get('button_save'), command=_save_rule, style="success.TButton").pack(side="right")
        ttk.Button(button_container, text=self.loc.get('button_cancel'), command=editor_window.destroy, style="secondary.TButton").pack(side="right", padx=10)

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\upload_dialog.py
# JUMLAH BARIS : 60
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\upload_dialog.py
# JUMLAH BARIS : 59
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, messagebox
from tkinter.scrolledtext import ScrolledText
from flowork_gui.api_client.client import ApiClient
class UploadDialog(ttk.Toplevel):
    """
    A dialog for users to enter details before uploading a component to the marketplace.
    """
    def __init__(self, parent, kernel, component_name):
        self.api_client = ApiClient()
        super().__init__(parent)
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        self.title(self.loc.get('marketplace_upload_dialog_title', fallback="Upload to Community"))
        self.result = None
        self.description_var = StringVar()
        self.tier_var = StringVar()
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        ttk.Label(main_frame, text=self.loc.get('marketplace_upload_dialog_header', component_name=component_name, fallback=f"You are about to upload: {component_name}")).pack(pady=(0, 10))
        ttk.Label(main_frame, text=self.loc.get('marketplace_upload_dialog_desc_label', fallback="Description:")).pack(anchor='w')
        self.description_text = ScrolledText(main_frame, height=5, wrap="word")
        self.description_text.pack(fill="x", pady=(0, 10))
        self.description_text.insert("1.0", f"A great component: {component_name}")
        ttk.Label(main_frame, text=self.loc.get('marketplace_upload_dialog_tier_label', fallback="Select Tier:")).pack(anchor='w')
        tier_options = list(self.kernel.TIER_HIERARCHY.keys())
        tier_combo = ttk.Combobox(main_frame, textvariable=self.tier_var, values=tier_options, state="readonly")
        tier_combo.pack(fill="x")
        tier_combo.set("free") # Default to free tier
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        upload_button = ttk.Button(button_frame, text=self.loc.get('marketplace_upload_btn', fallback="Upload"), command=self._on_upload, bootstyle="success")
        upload_button.pack(side="right")
        cancel_button = ttk.Button(button_frame, text=self.loc.get('button_cancel', fallback="Cancel"), command=self.destroy, bootstyle="secondary")
        cancel_button.pack(side="right", padx=(0, 10))
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)
    def _on_upload(self):
        """
        Validates the input and sets the result.
        """
        description = self.description_text.get("1.0", "end-1c").strip()
        tier = self.tier_var.get()
        if not description or not tier:
            messagebox.showwarning(self.loc.get('warning_title', fallback="Warning"), self.loc.get('marketplace_upload_dialog_validation_error', fallback="Description and Tier cannot be empty."), parent=self)
            return
        self.result = {
            "description": description,
            "tier": tier
        }
        self.destroy()

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\components\recorder_control_panel.py
# JUMLAH BARIS : 108
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\components\recorder_control_panel.py
# JUMLAH BARIS : 107
#######################################################################

import ttkbootstrap as ttk
import pyaudio
import mss
from flowork_kernel.ui_shell.custom_widgets.tooltip import ToolTip
from flowork_gui.api_client.client import ApiClient
class RecorderControlPanel(ttk.Toplevel):
    """
    The control panel for the screen recorder.
    [V5] Added a gain/amplification slider.
    """
    def __init__(self, parent, kernel, recorder_service):
        self.api_client = ApiClient()
        super().__init__(parent)
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        self.recorder_service = recorder_service
        self.transient(parent)
        self.title(self.loc.get("recorder_panel_title", fallback="Tutorial Studio"))
        self.geometry("400x320") # (MODIFIED) A bit taller for the gain slider
        self.resizable(False, False)
        self.selected_screen = ttk.IntVar(value=1)
        self.record_audio_var = ttk.BooleanVar(value=True)
        self.gain_var = ttk.DoubleVar(value=1.5) # Default gain is 1.5x
        self.mic_device_map = {}
        self._build_widgets()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._refresh_audio_devices()
    def _build_widgets(self):
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)
        screen_frame = ttk.Frame(main_frame)
        screen_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(screen_frame, text=self.loc.get("recorder_select_screen", fallback="Record Screen:")).pack(side="left")
        with mss.mss() as sct:
            monitors = sct.monitors
        self.screen_combo = ttk.Combobox(screen_frame, textvariable=self.selected_screen, state="readonly", values=list(range(1, len(monitors))))
        self.screen_combo.pack(side="right", fill="x", expand=True, padx=(10,0))
        if len(monitors) > 1:
            self.screen_combo.set(1)
        audio_frame = ttk.Frame(main_frame)
        audio_frame.pack(fill='x', pady=(0, 5))
        self.audio_check = ttk.Checkbutton(
            audio_frame,
            text=self.loc.get("recorder_use_default_mic", fallback="Record Audio (uses default microphone)"),
            variable=self.record_audio_var,
            command=self._toggle_gain_slider_state # (ADDED) Link to toggle function
        )
        self.audio_check.pack(anchor='w')
        self.gain_frame = ttk.Frame(main_frame)
        self.gain_frame.pack(fill='x', pady=(0, 15), padx=20)
        self.gain_label = ttk.Label(self.gain_frame, text=self.loc.get("recorder_gain_label", fallback="Amplification (Gain):"))
        self.gain_label.pack(side="left")
        self.gain_slider = ttk.Scale(self.gain_frame, from_=1.0, to=5.0, variable=self.gain_var)
        self.gain_slider.pack(side="left", fill="x", expand=True, padx=10)
        self.gain_value_label = ttk.Label(self.gain_frame, text=f"{self.gain_var.get():.1f}x", width=4)
        self.gain_value_label.pack(side="left")
        self.gain_slider.config(command=lambda val: self.gain_value_label.config(text=f"{float(val):.1f}x"))
        self.start_button = ttk.Button(main_frame, text=self.loc.get("recorder_start_button", fallback="Start Recording"), command=self._start_recording, bootstyle="danger")
        self.start_button.pack(fill="x", ipady=10, side="bottom")
    def _toggle_gain_slider_state(self):
        """(ADDED) Enables/disables the gain slider based on the checkbox."""
        if self.record_audio_var.get():
            self.gain_label.config(state="normal")
            self.gain_slider.config(state="normal")
            self.gain_value_label.config(state="normal")
        else:
            self.gain_label.config(state="disabled")
            self.gain_slider.config(state="disabled")
            self.gain_value_label.config(state="disabled")
    def _refresh_audio_devices(self):
        try:
            p = pyaudio.PyAudio()
            mic_count = 0
            for i in range(p.get_device_count()):
                if p.get_device_info_by_index(i).get('maxInputChannels') > 0:
                    mic_count += 1
            p.terminate()
            if mic_count == 0:
                self.audio_check.config(state="disabled")
                self.record_audio_var.set(False)
                self._toggle_gain_slider_state()
        except Exception as e:
            self.kernel.write_to_log(f"CRITICAL: Failed to query audio devices with PyAudio: {e}", "CRITICAL")
            self.audio_check.config(state="disabled")
            self.record_audio_var.set(False)
            self._toggle_gain_slider_state()
    def _start_recording(self):
        record_audio = self.record_audio_var.get()
        monitor_number = self.selected_screen.get()
        gain = self.gain_var.get()
        self.recorder_service.start_recording(
            monitor_num=monitor_number,
            record_audio=record_audio,
            gain=gain
        )
        self.destroy()
    def _on_close(self):
        if self.recorder_service.floating_widget:
            self.recorder_service.floating_widget.control_panel_closed()
        self.destroy()

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\generator_components\__init__.py
# JUMLAH BARIS : 0
#######################################################################

```py

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\generator_components\base_component.py
# JUMLAH BARIS : 52
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\generator_components\base_component.py
# JUMLAH BARIS : 51
#######################################################################

from abc import ABC, abstractmethod
from flowork_gui.api_client.client import ApiClient
class BaseGeneratorComponent(ABC):
    """
    The abstract contract that all UI component definitions for the Generator must implement.
    Each component knows how to draw itself and generate its own code snippets.
    """
    def __init__(self, kernel):
        self.api_client = ApiClient()
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
    @abstractmethod
    def get_toolbox_label(self) -> str:
        """Returns the text for the button in the toolbox."""
        pass
    @abstractmethod
    def get_component_type(self) -> str:
        """Returns the unique string identifier for this component type (e.g., 'text_input')."""
        pass
    @abstractmethod
    def create_canvas_widget(self, parent_frame, component_id, config):
        """Creates and returns the visual representation of the component on the design canvas."""
        pass
    @abstractmethod
    def create_properties_ui(self, parent_frame, config):
        """Creates the specific UI for the properties panel and returns a dict of tk.Vars."""
        pass
    @abstractmethod
    def generate_manifest_entry(self, config) -> dict:
        """Generates the dictionary entry for this property for the manifest.json file."""
        pass
    @abstractmethod
    def generate_processor_ui_code(self, config) -> list:
        """
        Generates a list of strings, where each string is a line of Python code
        for creating the properties UI in the final processor.py file.
        """
        pass
    def get_required_imports(self) -> set:
        """
        Returns a set of import strings required by this component.
        e.g., {"from tkinter import filedialog"}
        """
        return set()

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\generator_components\checkbox.py
# JUMLAH BARIS : 54
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\generator_components\checkbox.py
# JUMLAH BARIS : 53
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, BooleanVar
from .base_component import BaseGeneratorComponent
from flowork_gui.api_client.client import ApiClient
class CheckboxComponent(BaseGeneratorComponent):
    def get_toolbox_label(self) -> str:
        return self.loc.get('generator_toolbox_checkbox', fallback="Checkbox")
    def get_component_type(self) -> str:
        return 'checkbox'
    def create_canvas_widget(self, parent_frame, component_id, config):
        label_text = config.get('label', "My Checkbox")
        label = ttk.Checkbutton(parent_frame, text=label_text)
        label.pack(anchor='w')
        return label
    def create_properties_ui(self, parent_frame, config):
        prop_vars = {}
        prop_vars['id'] = StringVar(value=config.get('id', ''))
        prop_vars['label'] = StringVar(value=config.get('label', ''))
        default_value = config.get('default', False)
        if not isinstance(default_value, bool):
            default_value = str(default_value).lower() in ['true', '1', 'yes']
        prop_vars['default'] = BooleanVar(value=default_value)
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_id', fallback="Variable ID:")).pack(fill='x', anchor='w')
        ttk.Entry(parent_frame, textvariable=prop_vars['id']).pack(fill='x', pady=(0,10))
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_label', fallback="Display Label:")).pack(fill='x', anchor='w')
        ttk.Entry(parent_frame, textvariable=prop_vars['label']).pack(fill='x', pady=(0,10))
        ttk.Checkbutton(parent_frame, text=self.loc.get('generator_comp_prop_checked_by_default', fallback="Checked by default?"), variable=prop_vars['default']).pack(fill='x', pady=(0,10))
        return prop_vars
    def generate_manifest_entry(self, config) -> dict:
        return {
            "id": config['id'],
            "type": "boolean",
            "label": config['label'],
            "default": config.get('default', False)
        }
    def generate_processor_ui_code(self, config) -> list:
        comp_id = config['id']
        comp_label = config['label']
        return [
            f"        # --- {comp_label} ---",
            f"        property_vars['{comp_id}'] = BooleanVar(value=config.get('{comp_id}'))",
            f"        ttk.Checkbutton(parent_frame, text=\"{comp_label}\", variable=property_vars['{comp_id}']).pack(anchor='w', padx=5, pady=5)",
            ""
        ]
    def get_required_imports(self) -> set:
        return {"from tkinter import BooleanVar, StringVar"}

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\generator_components\dropdown.py
# JUMLAH BARIS : 62
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\generator_components\dropdown.py
# JUMLAH BARIS : 61
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, Text
from .base_component import BaseGeneratorComponent
from flowork_gui.api_client.client import ApiClient
class DropdownComponent(BaseGeneratorComponent):
    def get_toolbox_label(self) -> str:
        return self.loc.get('generator_toolbox_dropdown', fallback="Dropdown")
    def get_component_type(self) -> str:
        return 'dropdown'
    def create_canvas_widget(self, parent_frame, component_id, config):
        label_text = config.get('label', "My Dropdown")
        options = config.get('options', ['Option 1', 'Option 2'])
        label = ttk.Label(parent_frame, text=label_text)
        label.pack(anchor='w')
        ttk.Combobox(parent_frame, values=options).pack(fill='x')
        return label
    def create_properties_ui(self, parent_frame, config):
        prop_vars = {}
        prop_vars['id'] = StringVar(value=config.get('id', ''))
        prop_vars['label'] = StringVar(value=config.get('label', ''))
        prop_vars['default'] = StringVar(value=config.get('default', ''))
        options_text = Text(parent_frame, height=4, font=("Helvetica", 9))
        options_text.insert('1.0', "\n".join(config.get('options', [])))
        prop_vars['options'] = options_text
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_id', fallback="Variable ID:")).pack(fill='x', anchor='w')
        ttk.Entry(parent_frame, textvariable=prop_vars['id']).pack(fill='x', pady=(0,10))
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_label', fallback="Display Label:")).pack(fill='x', anchor='w')
        ttk.Entry(parent_frame, textvariable=prop_vars['label']).pack(fill='x', pady=(0,10))
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_default', fallback="Default Value:")).pack(fill='x', anchor='w')
        ttk.Entry(parent_frame, textvariable=prop_vars['default']).pack(fill='x', pady=(0,10))
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_options', fallback="Options (one per line):")).pack(fill='x', anchor='w')
        options_text.pack(fill='x', pady=(0,10))
        return prop_vars
    def generate_manifest_entry(self, config) -> dict:
        return {
            "id": config['id'],
            "type": "enum",
            "label": config['label'],
            "default": config['default'],
            "options": config.get('options', [])
        }
    def generate_processor_ui_code(self, config) -> list:
        comp_id = config['id']
        comp_label = config['label']
        options = config.get('options', [])
        return [
            f"        # --- {comp_label} ---",
            f"        property_vars['{comp_id}'] = StringVar(value=config.get('{comp_id}'))",
            f"        ttk.Label(parent_frame, text=\"{comp_label}\").pack(fill='x', padx=5, pady=(5,0))",
            f"        ttk.Combobox(parent_frame, textvariable=property_vars['{comp_id}'], values={options}, state='readonly').pack(fill='x', padx=5, pady=(0, 5))",
            ""
        ]
    def get_required_imports(self) -> set:
        return {"from tkinter import StringVar, Text"}

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\generator_components\file_path.py
# JUMLAH BARIS : 63
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\generator_components\file_path.py
# JUMLAH BARIS : 62
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, filedialog
from .base_component import BaseGeneratorComponent
from flowork_gui.api_client.client import ApiClient
class FilePathComponent(BaseGeneratorComponent):
    def get_toolbox_label(self) -> str:
        return self.loc.get('generator_toolbox_file_path', fallback="File/Folder Path")
    def get_component_type(self) -> str:
        return 'file_path'
    def create_canvas_widget(self, parent_frame, component_id, config):
        label_text = config.get('label', "My File Path")
        label = ttk.Label(parent_frame, text=label_text)
        label.pack(anchor='w')
        path_frame = ttk.Frame(parent_frame)
        path_frame.pack(fill='x')
        ttk.Entry(path_frame).pack(side='left', fill='x', expand=True)
        ttk.Button(path_frame, text="...").pack(side='left')
        return label
    def create_properties_ui(self, parent_frame, config):
        prop_vars = {}
        prop_vars['id'] = StringVar(value=config.get('id', ''))
        prop_vars['label'] = StringVar(value=config.get('label', ''))
        prop_vars['default'] = StringVar(value=config.get('default', ''))
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_id', fallback="Variable ID:")).pack(fill='x', anchor='w')
        ttk.Entry(parent_frame, textvariable=prop_vars['id']).pack(fill='x', pady=(0,10))
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_label', fallback="Display Label:")).pack(fill='x', anchor='w')
        ttk.Entry(parent_frame, textvariable=prop_vars['label']).pack(fill='x', pady=(0,10))
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_default', fallback="Default Path:")).pack(fill='x', anchor='w')
        ttk.Entry(parent_frame, textvariable=prop_vars['default']).pack(fill='x', pady=(0,10))
        return prop_vars
    def generate_manifest_entry(self, config) -> dict:
        return {
            "id": config['id'],
            "type": "filepath",
            "label": config['label'],
            "default": config['default']
        }
    def generate_processor_ui_code(self, config) -> list:
        comp_id = config['id']
        comp_label = config['label']
        return [
            f"        # --- {comp_label} ---",
            f"        ttk.Label(parent_frame, text=\"{comp_label}\").pack(fill='x', padx=5, pady=(5,0))",
            f"        path_frame_{comp_id} = ttk.Frame(parent_frame)",
            f"        path_frame_{comp_id}.pack(fill='x', padx=5, pady=(0, 5))",
            f"        property_vars['{comp_id}'] = StringVar(value=config.get('{comp_id}'))",
            f"        ttk.Entry(path_frame_{comp_id}, textvariable=property_vars['{comp_id}']).pack(side='left', fill='x', expand=True)",
            f"        def _browse_{comp_id}():",
            f"            path = filedialog.askdirectory() # or askopenfilename()",
            f"            if path: property_vars['{comp_id}'].set(path)",
            f"        ttk.Button(path_frame_{comp_id}, text='...', command=_browse_{comp_id}, width=4).pack(side='left', padx=(5,0))",
            ""
        ]
    def get_required_imports(self) -> set:
        return {"from tkinter import filedialog", "from tkinter import StringVar"}

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\generator_components\info_label.py
# JUMLAH BARIS : 39
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\generator_components\info_label.py
# JUMLAH BARIS : 38
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar
from .base_component import BaseGeneratorComponent
from flowork_gui.api_client.client import ApiClient
class InfoLabelComponent(BaseGeneratorComponent):
    def get_toolbox_label(self) -> str:
        return self.loc.get('generator_toolbox_info_label', fallback="Info Label")
    def get_component_type(self) -> str:
        return 'info_label'
    def create_canvas_widget(self, parent_frame, component_id, config):
        label_text = config.get('label', "This is an informational message.")
        label = ttk.Label(parent_frame, text=label_text, bootstyle="secondary", wraplength=200)
        label.pack(anchor='w', pady=5)
        return label
    def create_properties_ui(self, parent_frame, config):
        prop_vars = {}
        prop_vars['label'] = StringVar(value=config.get('label', ''))
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_info_text', fallback="Informational Text:")).pack(fill='x', anchor='w')
        ttk.Entry(parent_frame, textvariable=prop_vars['label']).pack(fill='x', pady=(0,10))
        return prop_vars
    def generate_manifest_entry(self, config) -> dict:
        return None # InfoLabel doesn't create a manifest property
    def generate_processor_ui_code(self, config) -> list:
        comp_label = config['label']
        return [
            f"        # --- Info Label ---",
            f"        ttk.Label(parent_frame, text=\"{comp_label}\", wraplength=400, justify='left', bootstyle='secondary').pack(fill='x', padx=5, pady=5)",
            ""
        ]
    def get_required_imports(self) -> set:
        return {"from tkinter import StringVar"}

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\generator_components\logic_builder_canvas.py
# JUMLAH BARIS : 116
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\generator_components\logic_builder_canvas.py
# JUMLAH BARIS : 115
#######################################################################

import ttkbootstrap as ttk
from tkinter import ttk as tk_ttk
from flowork_kernel.ui_shell.canvas_manager import CanvasManager
from flowork_gui.api_client.client import ApiClient
class LogicBuilderCanvas(ttk.Frame):
    """
    Kanvas visual untuk merancang logika 'execute' dari sebuah modul baru.
    Ini adalah implementasi dari "Logic Builder Canvas" pada Manifesto Flowork.
    [FIXED V2] Toolbox now dynamically loads all available LOGIC and ACTION modules.
    """
    def __init__(self, parent, kernel):
        self.api_client = ApiClient()
        super().__init__(parent)
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        self.canvas_manager = None
        self._drag_data = {}
        self._create_widgets()
    def _create_widgets(self):
        main_pane = ttk.PanedWindow(self, orient='horizontal')
        main_pane.pack(fill="both", expand=True)
        toolbox_frame = ttk.LabelFrame(main_pane, text="Node Logika Dasar", padding=10)
        main_pane.add(toolbox_frame, weight=0)
        self.logic_node_tree = tk_ttk.Treeview(toolbox_frame, show="tree", selectmode="browse")
        self.logic_node_tree.pack(expand=True, fill='both')
        self._populate_logic_toolbox()
        canvas_container = ttk.Frame(main_pane)
        main_pane.add(canvas_container, weight=4)
        theme_manager = self.kernel.get_service("theme_manager")
        colors = theme_manager.get_colors() if theme_manager else {'bg': '#222'}
        class DummyCoordinatorTab(ttk.Frame):
            def __init__(self, kernel, logic_builder_instance):
                super().__init__(logic_builder_instance)
                self.kernel = kernel
                self._execution_state = "IDLE"
                self.logic_builder_instance = logic_builder_instance
            def on_drag_start(self, event):
                self.logic_builder_instance.on_drag_start(event)
            def on_drag_motion(self, event):
                self.logic_builder_instance.on_drag_motion(event)
            def on_drag_release(self, event):
                self.logic_builder_instance.on_drag_release(event)
        dummy_tab = DummyCoordinatorTab(self.kernel, self)
        self.canvas = ttk.Canvas(canvas_container, background=colors.get('bg', '#222'))
        self.canvas.pack(expand=True, fill='both')
        self.canvas_manager = CanvasManager(canvas_container, dummy_tab, self.canvas, self.kernel)
        self.logic_node_tree.bind("<ButtonPress-1>", self.on_drag_start)
    def _populate_logic_toolbox(self):
        module_manager = self.kernel.get_service("module_manager_service")
        if not module_manager:
            self.logic_node_tree.insert('', 'end', text="Error: ModuleManager not found.")
            return
        logic_modules = {}
        action_modules = {}
        for mod_id, mod_data in module_manager.loaded_modules.items():
            manifest = mod_data.get("manifest", {})
            mod_type = manifest.get("type")
            if mod_type == "LOGIC" or mod_type == "CONTROL_FLOW":
                logic_modules[mod_id] = manifest.get("name", mod_id)
            elif mod_type == "ACTION":
                action_modules[mod_id] = manifest.get("name", mod_id)
        if logic_modules:
            logic_category = self.logic_node_tree.insert('', 'end', iid='logic_category', text='Logic & Control Flow', open=True)
            for mod_id, name in sorted(logic_modules.items(), key=lambda item: item[1]):
                 self.logic_node_tree.insert(logic_category, 'end', iid=mod_id, text=f" {name}")
        if action_modules:
            action_category = self.logic_node_tree.insert('', 'end', iid='action_category', text='Actions', open=True)
            for mod_id, name in sorted(action_modules.items(), key=lambda item: item[1]):
                 self.logic_node_tree.insert(action_category, 'end', iid=mod_id, text=f" {name}")
    def get_logic_data(self):
        """Mengambil data dari kanvas untuk disimpan."""
        if self.canvas_manager:
            return self.canvas_manager.get_workflow_data()
        return {"nodes": [], "connections": []}
    def load_logic_data(self, logic_data):
        """Memuat data ke kanvas."""
        if self.canvas_manager and logic_data:
            self.canvas_manager.load_workflow_data(logic_data)
    def on_drag_start(self, event):
        tree_widget = event.widget
        item_id = tree_widget.identify_row(event.y)
        if not item_id or 'category' in tree_widget.item(item_id, "tags") or not tree_widget.parent(item_id):
            return
        self._drag_data = {
            "item_id": item_id,
            "widget": ttk.Label(self.winfo_toplevel(), text=tree_widget.item(item_id, "text").strip(), style='Ghost.TLabel'),
            "tree_widget": tree_widget
        }
        self.winfo_toplevel().bind("<B1-Motion>", self.on_drag_motion)
        self.winfo_toplevel().bind("<ButtonRelease-1>", self.on_drag_release)
    def on_drag_motion(self, event):
        if self._drag_data.get("widget"):
            self._drag_data['widget'].place(
                x=event.x_root - self.winfo_toplevel().winfo_rootx(),
                y=event.y_root - self.winfo_toplevel().winfo_rooty()
            )
    def on_drag_release(self, event):
        if self._drag_data.get("widget"):
            self._drag_data["widget"].destroy()
        if self.canvas_manager and self._drag_data.get("item_id"):
            self.canvas_manager.interaction_manager.on_drag_release(
                event,
                self._drag_data["item_id"],
                self._drag_data["tree_widget"]
            )
        self._drag_data = {}
        self.winfo_toplevel().unbind("<B1-Motion>")
        self.winfo_toplevel().unbind("<ButtonRelease-1>")

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\generator_components\separator.py
# JUMLAH BARIS : 30
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\generator_components\separator.py
# JUMLAH BARIS : 29
#######################################################################

import ttkbootstrap as ttk
from .base_component import BaseGeneratorComponent
from flowork_gui.api_client.client import ApiClient
class SeparatorComponent(BaseGeneratorComponent):
    def get_toolbox_label(self) -> str:
        return self.loc.get('generator_toolbox_separator', fallback="Separator")
    def get_component_type(self) -> str:
        return 'separator'
    def create_canvas_widget(self, parent_frame, component_id, config):
        label = ttk.Separator(parent_frame, orient='horizontal')
        label.pack(fill='x', pady=10, padx=5)
        return label
    def create_properties_ui(self, parent_frame, config):
        ttk.Label(parent_frame, text=self.loc.get('generator_no_props', fallback="No properties to configure."), bootstyle="secondary").pack(pady=10)
        return {} # No properties
    def generate_manifest_entry(self, config) -> dict:
        return None # Separator doesn't create a manifest property
    def generate_processor_ui_code(self, config) -> list:
        return [
            "        ttk.Separator(parent_frame).pack(fill='x', pady=10, padx=5)",
            ""
        ]

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\generator_components\text_input.py
# JUMLAH BARIS : 57
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\generator_components\text_input.py
# JUMLAH BARIS : 56
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar
from .base_component import BaseGeneratorComponent
from flowork_gui.api_client.client import ApiClient
class TextInputComponent(BaseGeneratorComponent):
    def get_toolbox_label(self) -> str:
        return self.loc.get('generator_toolbox_text_input', fallback="Text Input")
    def get_component_type(self) -> str:
        return 'text_input'
    def create_canvas_widget(self, parent_frame, component_id, config):
        label_text = config.get('label', "My Text Input")
        label = ttk.Label(parent_frame, text=label_text)
        label.pack(anchor='w')
        ttk.Entry(parent_frame).pack(fill='x')
        return label # Return the primary widget for label updates
    def create_properties_ui(self, parent_frame, config):
        prop_vars = {}
        prop_vars['id'] = StringVar(value=config.get('id', ''))
        prop_vars['label'] = StringVar(value=config.get('label', ''))
        prop_vars['default'] = StringVar(value=config.get('default', ''))
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_id', fallback="Variable ID:")).pack(fill='x', anchor='w')
        ttk.Entry(parent_frame, textvariable=prop_vars['id']).pack(fill='x', pady=(0,10))
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_label', fallback="Display Label:")).pack(fill='x', anchor='w')
        ttk.Entry(parent_frame, textvariable=prop_vars['label']).pack(fill='x', pady=(0,10))
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_default', fallback="Default Value:")).pack(fill='x', anchor='w')
        ttk.Entry(parent_frame, textvariable=prop_vars['default']).pack(fill='x', pady=(0,10))
        return prop_vars
    def generate_manifest_entry(self, config) -> dict:
        return {
            "id": config['id'],
            "type": "string", # Text input produces a string
            "label": config['label'],
            "default": config['default']
        }
    def generate_processor_ui_code(self, config) -> list:
        comp_id = config['id']
        comp_label = config['label']
        return [
            f"        # --- {comp_label} ---",
            f"        property_vars['{comp_id}'] = StringVar(value=config.get('{comp_id}'))",
            f"        ttk.Label(parent_frame, text=\"{comp_label}\").pack(fill='x', padx=5, pady=(5,0))",
            f"        ttk.Entry(parent_frame, textvariable=property_vars['{comp_id}']).pack(fill='x', padx=5, pady=(0, 5))",
            "" # Add a blank line for spacing
        ]
    def get_required_imports(self) -> set:
        """
        Declares that this component requires 'StringVar' from tkinter.
        """
        return {"from tkinter import StringVar"}

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\generator_components\textarea.py
# JUMLAH BARIS : 61
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\generator_components\textarea.py
# JUMLAH BARIS : 60
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, scrolledtext
from .base_component import BaseGeneratorComponent
from flowork_gui.api_client.client import ApiClient
class TextAreaComponent(BaseGeneratorComponent):
    def get_toolbox_label(self) -> str:
        return self.loc.get('generator_toolbox_textarea', fallback="Text Area")
    def get_component_type(self) -> str:
        return 'textarea'
    def create_canvas_widget(self, parent_frame, component_id, config):
        label_text = config.get('label', "My Text Area")
        label = ttk.Label(parent_frame, text=label_text)
        label.pack(anchor='w')
        text_widget = scrolledtext.ScrolledText(parent_frame, height=3, font=("Helvetica", 9))
        text_widget.pack(fill='x')
        text_widget.insert('1.0', str(config.get('default', '')))
        text_widget.config(state='disabled')
        return label
    def create_properties_ui(self, parent_frame, config):
        prop_vars = {}
        prop_vars['id'] = StringVar(value=config.get('id', ''))
        prop_vars['label'] = StringVar(value=config.get('label', ''))
        default_text = scrolledtext.ScrolledText(parent_frame, height=4, font=("Helvetica", 9))
        default_text.insert('1.0', str(config.get('default', '')))
        prop_vars['default'] = default_text
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_id', fallback="Variable ID:")).pack(fill='x', anchor='w')
        ttk.Entry(parent_frame, textvariable=prop_vars['id']).pack(fill='x', pady=(0,10))
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_label', fallback="Display Label:")).pack(fill='x', anchor='w')
        ttk.Entry(parent_frame, textvariable=prop_vars['label']).pack(fill='x', pady=(0,10))
        ttk.Label(parent_frame, text=self.loc.get('generator_comp_prop_default', fallback="Default Value:")).pack(fill='x', anchor='w')
        default_text.pack(fill='x', pady=(0,10))
        return prop_vars
    def generate_manifest_entry(self, config) -> dict:
        return {
            "id": config['id'],
            "type": "textarea",
            "label": config['label'],
            "default": config['default']
        }
    def generate_processor_ui_code(self, config) -> list:
        comp_id = config['id']
        comp_label = config['label']
        return [
            f"        # --- {comp_label} ---",
            f"        ttk.Label(parent_frame, text=\"{comp_label}\").pack(fill='x', padx=5, pady=(5,0))",
            f"        {comp_id}_widget = scrolledtext.ScrolledText(parent_frame, height=8, font=(\"Consolas\", 10))",
            f"        {comp_id}_widget.pack(fill=\"both\", expand=True, padx=5, pady=(0, 5))",
            f"        {comp_id}_widget.insert('1.0', config.get('{comp_id}', ''))",
            f"        property_vars['{comp_id}'] = {comp_id}_widget",
            ""
        ]
    def get_required_imports(self) -> set:
        return {"from tkinter import scrolledtext, StringVar"}

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\settings_components\__init__.py
# JUMLAH BARIS : 0
#######################################################################

```py

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\settings_components\agent_dialog.py
# JUMLAH BARIS : 113
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\settings_components\agent_dialog.py
# JUMLAH BARIS : 112
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, messagebox, scrolledtext
from flowork_kernel.ui_shell.custom_widgets.DualListbox import DualListbox
import os
from flowork_gui.api_client.client import ApiClient
class AgentDialog(ttk.Toplevel):
    """
    A dialog for creating and editing an AI Agent's properties.
    (MODIFIED) Now fetches ALL available AI endpoints (local models and providers) for the brain.
    """
    DEFAULT_PROMPT_TEMPLATE = "" # It's better to provide an empty default or a minimal placeholder.
    def __init__(self, parent, kernel, agent_data=None):
        super().__init__(parent)
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        self.api_client = ApiClient(kernel=self.kernel)
        self.agent_data = agent_data or {}
        self.result = None
        title = self.loc.get('agent_dialog_title_edit' if self.agent_data else 'agent_dialog_title_new')
        self.title(title)
        self.geometry("800x850")
        self.name_var = StringVar(value=self.agent_data.get('name', ''))
        self.brain_display_name_var = StringVar()
        self._build_ui()
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)
    def _build_ui(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        main_frame.rowconfigure(5, weight=1)
        main_frame.columnconfigure(0, weight=1)
        ttk.Label(main_frame, text=self.loc.get('agent_dialog_name_label')).grid(row=0, column=0, sticky="w", pady=(0,2))
        ttk.Entry(main_frame, textvariable=self.name_var).grid(row=1, column=0, sticky="ew", pady=(0,10))
        ttk.Label(main_frame, text=self.loc.get('agent_dialog_desc_label')).grid(row=2, column=0, sticky="w", pady=(0,2))
        self.desc_text = scrolledtext.ScrolledText(main_frame, height=3, wrap="word")
        self.desc_text.grid(row=3, column=0, sticky="ew", pady=(0,10))
        self.desc_text.insert("1.0", self.agent_data.get('description', ''))
        config_pane = ttk.PanedWindow(main_frame, orient='horizontal')
        config_pane.grid(row=4, column=0, sticky="ew", pady=(0,15))
        brain_frame = ttk.LabelFrame(config_pane, text=self.loc.get('agent_dialog_brain_label'), padding=10)
        config_pane.add(brain_frame, weight=1)
        ai_manager = self.kernel.get_service("ai_provider_manager_service")
        all_endpoints = ai_manager.get_available_providers() if ai_manager else {}
        self.id_to_display_map = {endpoint_id: display_name for endpoint_id, display_name in all_endpoints.items()}
        self.display_to_id_map = {display_name: endpoint_id for endpoint_id, display_name in all_endpoints.items()}
        available_brains_display = sorted(list(self.display_to_id_map.keys()))
        self.brain_combo = ttk.Combobox(brain_frame, textvariable=self.brain_display_name_var, values=available_brains_display, state="readonly")
        self.brain_combo.pack(fill="x")
        saved_brain_id = self.agent_data.get('brain_model_id', '')
        if saved_brain_id in self.id_to_display_map:
            self.brain_display_name_var.set(self.id_to_display_map[saved_brain_id])
        tools_frame = ttk.LabelFrame(config_pane, text=self.loc.get('agent_dialog_tools_label'), padding=10)
        config_pane.add(tools_frame, weight=2)
        modules_success, modules_data = self.api_client.get_components('modules')
        plugins_success, plugins_data = self.api_client.get_components('plugins')
        if not modules_success:
            self.kernel.write_to_log(f"AgentDialog: Failed to get modules from API: {modules_data}", "ERROR")
            modules_data = []
        if not plugins_success:
            self.kernel.write_to_log(f"AgentDialog: Failed to get plugins from API: {plugins_data}", "ERROR")
            plugins_data = []
        all_tools_dict = {item['id']: item['name'] for item in modules_data + plugins_data}
        available_tools = sorted(all_tools_dict.values())
        selected_tool_ids = self.agent_data.get('tool_ids', [])
        selected_tool_names = [all_tools_dict[tid] for tid in selected_tool_ids if tid in all_tools_dict]
        self.tool_selector = DualListbox(tools_frame, self.kernel, available_items=available_tools, selected_items=selected_tool_names)
        self.tool_selector.pack(fill="both", expand=True)
        prompt_frame = ttk.LabelFrame(main_frame, text="Agent Prompt Template", padding=10)
        prompt_frame.grid(row=5, column=0, sticky="nsew", pady=(0,15))
        prompt_frame.rowconfigure(0, weight=1)
        prompt_frame.columnconfigure(0, weight=1)
        self.prompt_text = scrolledtext.ScrolledText(prompt_frame, wrap="word", height=15)
        self.prompt_text.grid(row=0, column=0, sticky="nsew")
        prompt_placeholder = self.agent_data.get('prompt_template') or "# The prompt template is now managed by the 'Prompt Engineer' module.\n# This field is for reference or overrides."
        self.prompt_text.insert("1.0", prompt_placeholder)
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, sticky="e")
        save_button = ttk.Button(button_frame, text=self.loc.get("button_save"), command=self._on_save, bootstyle="success")
        save_button.pack(side="right")
        cancel_button = ttk.Button(button_frame, text=self.loc.get("button_cancel"), command=self.destroy, bootstyle="secondary")
        cancel_button.pack(side="right", padx=(0, 10))
    def _on_save(self):
        name = self.name_var.get().strip()
        brain_display_name = self.brain_display_name_var.get()
        brain_id = self.display_to_id_map.get(brain_display_name)
        selected_tool_names = self.tool_selector.get_selected_items()
        if not name or not brain_id:
            messagebox.showerror("Validation Error", "Agent Name and Brain Model are required.", parent=self)
            return
        modules_success, modules_data = self.api_client.get_components('modules')
        plugins_success, plugins_data = self.api_client.get_components('plugins')
        safe_modules = modules_data if modules_success else []
        safe_plugins = plugins_data if plugins_success else []
        name_to_id_map = {item['name']: item['id'] for item in safe_modules + safe_plugins}
        selected_tool_ids = [name_to_id_map[name] for name in selected_tool_names if name in name_to_id_map]
        self.result = {
            "id": str(self.agent_data.get('id', '')),
            "name": name,
            "description": self.desc_text.get("1.0", "end-1c").strip(),
            "brain_model_id": brain_id,
            "tool_ids": selected_tool_ids,
            "prompt_template": self.prompt_text.get("1.0", "end-1c").strip()
        }
        self.destroy()

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\settings_components\ai_model_manager_frame.py
# JUMLAH BARIS : 56
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\settings_components\ai_model_manager_frame.py
# JUMLAH BARIS : 55
#######################################################################

import ttkbootstrap as ttk
from tkinter import messagebox
import os
import threading
from flowork_gui.api_client.client import ApiClient
class AiModelManagerFrame(ttk.LabelFrame):
    """UI component for managing the on-demand download of AI models."""
    def __init__(self, parent, kernel):
        self.api_client = ApiClient()
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        super().__init__(parent, text="Manajemen Model AI Lokal", padding=15)
        self.status_label = ttk.Label(self, text="Mengecek status...", anchor="center")
        self.status_label.pack(pady=5, fill="x")
        self.download_button = ttk.Button(self, text="Download Model AI (~70 GB)", command=self._start_download_action)
        self.download_button.pack(pady=5, fill="x", ipady=5)
        self.progress_bar = ttk.Progressbar(self, mode='determinate')
        self.progress_bar.pack(pady=5, fill="x")
        self.progress_bar.pack_forget() # Sembunyikan dulu
        self.check_status()
    def check_status(self):
        """Checks if models are installed and updates the UI accordingly."""
        ai_models_path = os.path.join(self.kernel.project_root_path, "ai_models")
        if os.path.isdir(ai_models_path):
            self.status_label.config(text="Model AI Lokal sudah terinstall.", bootstyle="success")
            self.download_button.pack_forget()
            self.progress_bar.pack_forget()
        else:
            self.status_label.config(text="Model AI Lokal belum terinstall.", bootstyle="warning")
            self.download_button.pack(pady=5, fill="x", ipady=5) # Tampilkan tombol
            if self.kernel.is_tier_sufficient('pro'):
                self.download_button.config(state="normal")
            else:
                self.download_button.config(state="disabled")
                self.status_label.config(text="Model AI membutuhkan lisensi PRO atau lebih tinggi.")
    def _start_download_action(self):
        """Starts the download process in a background thread."""
        if messagebox.askyesno("Konfirmasi Download", "Proses ini akan mengunduh file berukuran sangat besar (~70 GB) dan mungkin memakan waktu lama. Lanjutkan?"):
            self.download_button.config(state="disabled")
            self.progress_bar.pack(pady=5, fill="x")
            self.status_label.config(text="Fitur download sedang dalam pengembangan...")
            self.kernel.write_to_log("TODO: Implement asset downloader service call.", "WARN")
    def load_settings_data(self, settings_data):
        """This component is stateful and doesn't load from settings."""
        self.check_status()
    def get_settings_data(self):
        """This component doesn't save any settings."""
        return {}

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\settings_components\ai_provider_settings_frame.py
# JUMLAH BARIS : 98
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\settings_components\ai_provider_settings_frame.py
# JUMLAH BARIS : 97
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar
import os
from flowork_gui.api_client.client import ApiClient
class AiProviderSettingsFrame(ttk.LabelFrame):
    """
    [MODIFIED V2] Displays a granular, task-based configuration for default AI models
    instead of a single master AI. Each task type can be mapped to a different provider.
    """
    def __init__(self, parent, kernel):
        self.api_client = ApiClient()
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        super().__init__(parent, text=self.loc.get('setting_ai_config_title', fallback="Default AI Model Configuration"), padding=15)
        self.provider_vars = {}
        self.endpoint_display_to_id_map = {}
        self.task_types = {
            "text": "setting_ai_for_text",
            "music": "setting_ai_for_music",
            "tts": "setting_ai_for_tts",
            "image": "setting_ai_for_image",
            "video": "setting_ai_for_video",
            "other": "setting_ai_for_other"
        }
        self.gpu_layers_var = StringVar()
        self._build_widgets()
    def _build_widgets(self):
        """Builds the UI components for this frame."""
        self.columnconfigure(1, weight=1)
        help_text = ttk.Label(self, text=self.loc.get('setting_ai_config_help', fallback="Select the default AI model for each task type. Features like AI Architect will use these settings."), wraplength=400, justify="left", bootstyle="secondary")
        help_text.grid(row=0, column=0, columnspan=2, padx=5, pady=(0,15), sticky="w")
        row_counter = 1
        for key, label_key in self.task_types.items():
            self.provider_vars[key] = StringVar()
            label_text = self.loc.get(label_key, fallback=f"{key.title()}:")
            label = ttk.Label(self, text=label_text)
            label.grid(row=row_counter, column=0, padx=(0, 10), pady=5, sticky="w")
            provider_combo = ttk.Combobox(self, textvariable=self.provider_vars[key], state="readonly")
            provider_combo.grid(row=row_counter, column=1, padx=5, pady=5, sticky="ew")
            row_counter += 1
        ttk.Separator(self).grid(row=row_counter, column=0, columnspan=2, sticky="ew", pady=10)
        row_counter += 1
        gpu_label = ttk.Label(self, text="GPU Offload Layers (GGUF):") # English Hardcode
        gpu_label.grid(row=row_counter, column=0, padx=5, pady=5, sticky="w")
        gpu_entry = ttk.Entry(self, textvariable=self.gpu_layers_var, width=10)
        gpu_entry.grid(row=row_counter, column=1, padx=5, pady=5, sticky="w")
    def load_settings_data(self, settings_data):
        """Loads the list of endpoints and sets the current settings for each task type."""
        self.gpu_layers_var.set(str(settings_data.get("ai_gpu_layers", 40)))
        ai_manager = self.kernel.get_service("ai_provider_manager_service")
        if not ai_manager:
            for i, (key, label_key) in enumerate(self.task_types.items()):
                combo = self.grid_slaves(row=i + 1, column=1)[0]
                combo['values'] = ["AI Manager Service not found"]
            return
        all_endpoints = ai_manager.get_available_providers()
        self.endpoint_display_to_id_map.clear()
        display_names = []
        for endpoint_id, display_name in all_endpoints.items():
             self.endpoint_display_to_id_map[display_name] = endpoint_id
             display_names.append(display_name)
        sorted_display_names = sorted(display_names)
        for i, (key, label_key) in enumerate(self.task_types.items()):
            combo = self.grid_slaves(row=i + 1, column=1)[0]
            combo['values'] = sorted_display_names
            setting_key = f"ai_model_for_{key}"
            saved_endpoint_id = settings_data.get(setting_key)
            found_saved = False
            if saved_endpoint_id:
                for display, endpoint_id in self.endpoint_display_to_id_map.items():
                    if endpoint_id == saved_endpoint_id:
                        self.provider_vars[key].set(display)
                        found_saved = True
                        break
            if not found_saved and sorted_display_names:
                self.provider_vars[key].set(sorted_display_names[0])
    def get_settings_data(self):
        """Returns all the configured AI settings to be saved."""
        settings_to_save = {}
        for key, var in self.provider_vars.items():
            selected_display_name = var.get()
            if selected_display_name in self.endpoint_display_to_id_map:
                endpoint_id_to_save = self.endpoint_display_to_id_map[selected_display_name]
                setting_key = f"ai_model_for_{key}"
                settings_to_save[setting_key] = endpoint_id_to_save
        try:
            settings_to_save["ai_gpu_layers"] = int(self.gpu_layers_var.get())
        except (ValueError, TypeError):
            settings_to_save["ai_gpu_layers"] = 40
        return settings_to_save

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\settings_components\error_handler_frame.py
# JUMLAH BARIS : 40
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\settings_components\error_handler_frame.py
# JUMLAH BARIS : 39
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, BooleanVar
from flowork_gui.api_client.client import ApiClient
class ErrorHandlerFrame(ttk.LabelFrame):
    def __init__(self, parent, kernel):
        self.api_client = ApiClient()
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        super().__init__(parent, text=self.loc.get("settings_error_handler_title", fallback="Global Error Handler Settings"), padding=15)
        self.error_handler_enabled_var = BooleanVar()
        self.error_handler_preset_var = StringVar()
        self._build_widgets()
    def _build_widgets(self):
        enabled_check = ttk.Checkbutton(self, text=self.loc.get("settings_error_handler_enable_label", fallback="Enable Global Error Handler"), variable=self.error_handler_enabled_var)
        enabled_check.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        preset_label = ttk.Label(self, text=self.loc.get("settings_error_handler_preset_label", fallback="Select Error Handler Preset:"))
        preset_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        preset_manager = self.kernel.get_service("preset_manager")
        preset_list = [""] + preset_manager.get_preset_list() if preset_manager else [""]
        preset_combo = ttk.Combobox(self, textvariable=self.error_handler_preset_var, values=preset_list, state="readonly")
        preset_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.columnconfigure(1, weight=1)
    def load_settings_data(self, settings_data):
        """Loads error handler settings from the provided data dictionary."""
        self.error_handler_enabled_var.set(settings_data.get("global_error_handler_enabled", False))
        self.error_handler_preset_var.set(settings_data.get("global_error_workflow_preset", ""))
    def get_settings_data(self):
        """Returns the current error handler settings from the UI."""
        return {
            "global_error_handler_enabled": self.error_handler_enabled_var.get(),
            "global_error_workflow_preset": self.error_handler_preset_var.get()
        }

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\settings_components\general_settings_frame.py
# JUMLAH BARIS : 56
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\settings_components\general_settings_frame.py
# JUMLAH BARIS : 55
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar
from flowork_gui.api_client.client import ApiClient
class GeneralSettingsFrame(ttk.LabelFrame):
    def __init__(self, parent, kernel):
        self.api_client = ApiClient()
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        super().__init__(parent, text=self.loc.get("settings_general_title", fallback="General Settings"), padding=15)
        self.lang_var = StringVar()
        self.theme_var = StringVar()
        self.available_themes = {}
        self._build_widgets()
    def _build_widgets(self):
        lang_label = ttk.Label(self, text=self.loc.get("settings_language_label", fallback="Interface Language:"))
        lang_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        lang_combo = ttk.Combobox(self, textvariable=self.lang_var, values=self.loc.get_available_languages_display(), state="readonly")
        lang_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        theme_label = ttk.Label(self, text=self.loc.get("settings_theme_label", fallback="Application Theme:"))
        theme_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.theme_combo = ttk.Combobox(self, textvariable=self.theme_var, values=[], state="readonly")
        self.theme_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.columnconfigure(1, weight=1)
    def load_settings_data(self, settings_data):
        """Loads settings data provided by the parent coordinator."""
        theme_manager = self.kernel.get_service("theme_manager")
        if theme_manager:
            self.available_themes = theme_manager.get_all_themes()
            theme_names = [d.get('name', 'Unknown') for d in self.available_themes.values()]
            self.theme_combo['values'] = sorted(theme_names)
        else:
            self.available_themes = {}
        active_theme_id = settings_data.get("theme", "flowork_default")
        active_theme_name = self.available_themes.get(active_theme_id, {}).get('name', '')
        lang_code = settings_data.get("language", "id")
        lang_display_name = self.loc.language_map.get(lang_code, "Bahasa Indonesia")
        self.lang_var.set(lang_display_name)
        self.theme_var.set(active_theme_name)
    def get_settings_data(self) -> dict:
        """Returns the current settings from the UI as a dictionary."""
        selected_theme_name = self.theme_var.get()
        theme_id_to_save = next((tid for tid, data in self.available_themes.items() if data.get('name') == selected_theme_name), "flowork_default")
        selected_lang_display = self.lang_var.get()
        lang_code_to_save = next((code for code, display in self.loc.language_map.items() if display == selected_lang_display), "id")
        return {
            "language": lang_code_to_save,
            "theme": theme_id_to_save
        }

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\settings_components\license_management_frame.py
# JUMLAH BARIS : 72
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\settings_components\license_management_frame.py
# JUMLAH BARIS : 71
#######################################################################

import ttkbootstrap as ttk
from tkinter import messagebox
import os
import threading
from flowork_gui.api_client.client import ApiClient
class LicenseManagementFrame(ttk.LabelFrame):
    def __init__(self, parent, kernel):
        self.kernel = kernel
        self.loc = self.kernel.loc
        super().__init__(parent, text=self.loc.get("settings_license_title", fallback="License Management"), padding=15)
        self.api_client = ApiClient(kernel=self.kernel)
        self._build_widgets()
        self.load_settings_data(None)
    def _build_widgets(self):
        self.deactivate_button = ttk.Button(
            self,
            text=self.loc.get("settings_license_deactivate_button", fallback="Deactivate License on This Computer"),
            command=self._deactivate_license_action,
            bootstyle="danger-outline"
        )
        self.deactivate_button.pack(pady=5, padx=5, fill='x')
    def refresh_content(self):
        """Refreshes the UI state of the component based on the current kernel license status."""
        if hasattr(self, 'deactivate_button') and self.deactivate_button.winfo_exists():
            if self.kernel.current_user and self.kernel.is_premium_user():
                self.deactivate_button.config(state="normal")
            else:
                self.deactivate_button.config(state="disabled")
    def _deactivate_license_action(self):
        """
        Prompts for confirmation and then runs the license deactivation in a thread.
        """
        if messagebox.askyesno(
            self.loc.get("settings_license_deactivate_confirm_title", fallback="Confirm Deactivation"),
            self.loc.get("settings_license_deactivate_confirm_message"),
            parent=self
        ):
            self.deactivate_button.config(state="disabled")
            threading.Thread(target=self._deactivate_worker, daemon=True).start()
    def _deactivate_worker(self):
        """
        Worker function to call the deactivation method via ApiClient.
        """
        success, message = self.api_client.deactivate_license()
        self.after(0, self._on_deactivate_complete, success, message)
    def _on_deactivate_complete(self, success, message):
        """
        (MODIFIKASI) UI callback yang disederhanakan untuk mencegah race condition.
        """
        if success:
            messagebox.showinfo(
                self.loc.get("messagebox_success_title", fallback="Success"),
                message
            )
        else:
            messagebox.showerror(self.loc.get("messagebox_error_title", fallback="Failed"), message, parent=self)
            if hasattr(self, 'deactivate_button') and self.deactivate_button.winfo_exists():
                self.deactivate_button.config(state="normal")
    def load_settings_data(self, settings_data):
        """This frame's UI is updated based on kernel state, not settings data."""
        self.refresh_content()
    def get_settings_data(self):
        """This frame doesn't save any settings, it only performs actions."""
        return {}

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\settings_components\notification_settings_frame.py
# JUMLAH BARIS : 48
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\settings_components\notification_settings_frame.py
# JUMLAH BARIS : 47
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, BooleanVar
from flowork_gui.api_client.client import ApiClient
class NotificationSettingsFrame(ttk.LabelFrame):
    def __init__(self, parent, kernel):
        self.api_client = ApiClient()
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        super().__init__(parent, text=self.loc.get("settings_notifications_title", fallback="Popup Notification Settings"), padding=15)
        self.notifications_enabled_var = BooleanVar()
        self.notifications_duration_var = StringVar()
        self.notifications_position_var = StringVar()
        self._build_widgets()
    def _build_widgets(self):
        enabled_check = ttk.Checkbutton(self, text=self.loc.get("settings_notifications_enable_label", fallback="Enable Popup Notifications"), variable=self.notifications_enabled_var)
        enabled_check.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        duration_label = ttk.Label(self, text=self.loc.get("settings_notifications_duration_label", fallback="Display Duration (seconds):"))
        duration_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        duration_entry = ttk.Entry(self, textvariable=self.notifications_duration_var, width=10)
        duration_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        position_label = ttk.Label(self, text=self.loc.get("settings_notifications_position_label", fallback="Popup Position:"))
        position_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        position_combo = ttk.Combobox(self, textvariable=self.notifications_position_var, values=["bottom_right", "top_right", "bottom_left", "top_left"], state="readonly")
        position_combo.grid(row=2, column=1, padx=5, pady=5, sticky="w")
    def load_settings_data(self, settings_data):
        """Loads notification settings from the provided data dictionary."""
        self.notifications_enabled_var.set(settings_data.get("notifications_enabled", True))
        self.notifications_duration_var.set(str(settings_data.get("notifications_duration_seconds", 5)))
        self.notifications_position_var.set(settings_data.get("notifications_position", "bottom_right"))
    def get_settings_data(self):
        """Returns the current notification settings from the UI."""
        try:
            duration = int(self.notifications_duration_var.get())
            return {
                "notifications_enabled": self.notifications_enabled_var.get(),
                "notifications_duration_seconds": duration,
                "notifications_position": self.notifications_position_var.get()
            }
        except ValueError:
            raise ValueError("Duration must be a valid number.")

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\settings_components\recorder_settings_frame.py
# JUMLAH BARIS : 50
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\settings_components\recorder_settings_frame.py
# JUMLAH BARIS : 49
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, filedialog
import os
from flowork_gui.api_client.client import ApiClient
class RecorderSettingsFrame(ttk.LabelFrame):
    """
    Manages the UI for screen recorder settings.
    """
    def __init__(self, parent, kernel):
        self.api_client = ApiClient()
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        super().__init__(parent, text="Screen Recorder Settings", padding=15)
        self.save_path_var = StringVar()
        self._build_widgets()
    def _build_widgets(self):
        """Builds the UI components for this frame."""
        path_label = ttk.Label(self, text="Default Save Location:")
        path_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        entry_frame = ttk.Frame(self)
        entry_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5)
        entry_frame.columnconfigure(0, weight=1)
        path_entry = ttk.Entry(entry_frame, textvariable=self.save_path_var)
        path_entry.pack(side="left", fill="x", expand=True)
        browse_button = ttk.Button(entry_frame, text="Browse...", command=self._browse_folder, width=10)
        browse_button.pack(side="left", padx=(5, 0))
        self.columnconfigure(1, weight=1)
    def _browse_folder(self):
        """Opens a dialog to select a folder."""
        default_path = os.path.join(os.path.expanduser("~"), "Videos")
        folder_selected = filedialog.askdirectory(initialdir=default_path)
        if folder_selected:
            self.save_path_var.set(folder_selected)
    def load_settings_data(self, settings_data):
        """Loads recorder settings from the provided data dictionary."""
        default_path = os.path.join(os.path.expanduser("~"), "Videos", "Flowork Tutorials")
        self.save_path_var.set(settings_data.get("recorder_save_path", default_path))
    def get_settings_data(self) -> dict:
        """Returns the current recorder settings from the UI."""
        return {
            "recorder_save_path": self.save_path_var.get()
        }

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\settings_components\variable_dialog.py
# JUMLAH BARIS : 90
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\settings_components\variable_dialog.py
# JUMLAH BARIS : 89
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, BooleanVar, messagebox, scrolledtext
from flowork_gui.api_client.client import ApiClient
class VariableDialog(ttk.Toplevel):
    def __init__(self, parent, title, kernel, existing_name=None, existing_data=None):
        self.api_client = ApiClient()
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.loc = kernel.get_service("localization_manager")
        self.result = None
        existing_data = existing_data or {}
        self.name_var = StringVar(value=existing_name or "")
        initial_mode = existing_data.get('mode', 'single')
        initial_value_text = ""
        if initial_mode == 'single':
            if existing_data.get('is_secret'):
                 initial_value_text = self.loc.get("settings_variables_dialog_secret_placeholder")
            else:
                 initial_value_text = existing_data.get('value', '')
        else: # (ADDED) For 'random' or 'sequential', join the list with newlines
            initial_value_text = "\n".join(existing_data.get('values', []))
        self.value_var_text = initial_value_text # (COMMENT) We use this to populate the text widget directly
        self.is_secret_var = BooleanVar(value=existing_data.get('is_secret', False))
        self.mode_var = StringVar(value=initial_mode)
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)
        name_label = ttk.Label(main_frame, text=self.loc.get("settings_variables_dialog_name", fallback="Name:"))
        name_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        self.name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=50)
        self.name_entry.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        if existing_name:
            self.name_entry.config(state="readonly")
        value_label = ttk.Label(main_frame, text=self.loc.get("settings_variables_dialog_value", fallback="Value:"))
        value_label.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        self.value_entry = scrolledtext.ScrolledText(main_frame, width=50, height=8, wrap="word")
        self.value_entry.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.value_entry.insert("1.0", self.value_var_text)
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=4, column=0, columnspan=2, pady=(10,0), sticky="ew")
        secret_check = ttk.Checkbutton(options_frame, text=self.loc.get("settings_variables_dialog_secret_check", fallback="Mask this value (secret)"), variable=self.is_secret_var)
        secret_check.pack(side="left", anchor="w")
        if existing_name:
            secret_check.config(state="disabled")
        mode_combo = ttk.Combobox(options_frame, textvariable=self.mode_var, values=["single", "random", "sequential"], state="readonly", width=12)
        mode_combo.pack(side="right", anchor="e")
        ttk.Label(options_frame, text="Retrieval Mode:").pack(side="right", padx=(0, 5)) # English Hardcode
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(20,0), sticky="e")
        ok_button = ttk.Button(button_frame, text=self.loc.get("button_save", fallback="Save"), command=self._on_ok, bootstyle="success")
        ok_button.pack(side="right", padx=5)
        cancel_button = ttk.Button(button_frame, text=self.loc.get("button_cancel", fallback="Cancel"), command=self.destroy, bootstyle="secondary")
        cancel_button.pack(side="right")
        self.wait_window(self)
    def _on_ok(self):
        name = self.name_var.get().strip().upper()
        value_str = self.value_entry.get("1.0", "end-1c").strip()
        is_secret = self.is_secret_var.get()
        mode = self.mode_var.get()
        if not name:
            messagebox.showerror(self.loc.get("messagebox_error_title", fallback="Error"), self.loc.get("settings_variables_warn_name_empty", fallback="Name cannot be empty."), parent=self)
            return
        if not name.replace('_', '').isalnum():
            messagebox.showerror(self.loc.get("messagebox_error_title", fallback="Error"), self.loc.get("settings_variables_warn_name_format"), parent=self)
            return
        if value_str == "" or (self.name_entry.cget('state') == 'readonly' and value_str == self.loc.get("settings_variables_dialog_secret_placeholder")):
             messagebox.showerror(self.loc.get("messagebox_error_title", fallback="Error"), self.loc.get("settings_variables_warn_value_empty", fallback="Value cannot be empty."), parent=self)
             return
        final_value = None
        if mode == 'single':
            if '\n' in value_str:
                messagebox.showerror(self.loc.get("messagebox_error_title", fallback="Error"), "Single value mode cannot contain multiple lines.", parent=self)
                return
            final_value = value_str
        else: # random or sequential
            final_value = [line.strip() for line in value_str.split('\n') if line.strip()]
            if not final_value:
                messagebox.showerror(self.loc.get("messagebox_error_title", fallback="Error"), "Please provide at least one value for the pool.", parent=self)
                return
        self.result = (name, final_value, is_secret, mode)
        self.destroy()

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\settings_components\variable_manager_frame.py
# JUMLAH BARIS : 163
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\settings_components\variable_manager_frame.py
# JUMLAH BARIS : 162
#######################################################################

import ttkbootstrap as ttk
from tkinter import messagebox
from .variable_dialog import VariableDialog
import threading
import base64
from flowork_gui.api_client.client import ApiClient
class VariableManagerFrame(ttk.LabelFrame):
    def __init__(self, parent, kernel):
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        super().__init__(parent, text=self.loc.get("settings_variables_title", fallback="Variable & Secret Management"), padding=15)
        self.variables_data_cache = []
        self.api_client = ApiClient(kernel=self.kernel)
        self._build_widgets()
        self.load_variables_to_ui()
    def _build_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=0, column=0, sticky="nsew", columnspan=3)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        columns = ("name", "value", "status")
        self.var_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        self.var_tree.heading("name", text=self.loc.get("settings_variables_col_name", fallback="Variable Name"))
        self.var_tree.heading("value", text=self.loc.get("settings_variables_col_value", fallback="Value"))
        self.var_tree.heading("status", text=self.loc.get("settings_variables_col_status", fallback="Status"))
        self.var_tree.column("name", width=150, anchor="w")
        self.var_tree.column("value", width=300, anchor="w")
        self.var_tree.column("status", width=80, anchor="center")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.var_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.var_tree.xview)
        self.var_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.var_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        button_frame = ttk.Frame(self)
        button_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(10,0))
        add_button = ttk.Button(button_frame, text=self.loc.get("settings_variables_btn_add", fallback="Add"), command=self._add_variable)
        add_button.pack(side="left", padx=5)
        edit_button = ttk.Button(button_frame, text=self.loc.get("settings_variables_btn_edit", fallback="Edit"), command=self._edit_variable, bootstyle="info")
        edit_button.pack(side="left", padx=5)
        self.toggle_button = ttk.Button(button_frame, text=self.loc.get("settings_variables_btn_disable", fallback="Disable"), command=self._toggle_variable_state, bootstyle="warning")
        self.toggle_button.pack(side="left", padx=5)
        delete_button = ttk.Button(button_frame, text=self.loc.get("settings_variables_btn_delete", fallback="Delete"), command=self._delete_variable, bootstyle="danger")
        delete_button.pack(side="left", padx=5)
        copy_button = ttk.Button(button_frame, text=self.loc.get("settings_variables_action_copy", fallback="[ Copy ]"), command=self._copy_variable_placeholder, bootstyle="secondary-outline")
        copy_button.pack(side="right", padx=5)
        self.var_tree.bind('<<TreeviewSelect>>', self._update_button_state)
    def load_variables_to_ui(self):
        for item in self.var_tree.get_children():
            self.var_tree.delete(item)
        threading.Thread(target=self._load_variables_worker, daemon=True).start()
    def _load_variables_worker(self):
        success, data = self.api_client.get_variables()
        self.after(0, self._populate_tree_from_data, success, data)
    def _populate_tree_from_data(self, success, data):
        for item in self.var_tree.get_children():
            self.var_tree.delete(item)
        if success:
            self.variables_data_cache = data
            for var_data in self.variables_data_cache:
                is_enabled = var_data.get('is_enabled', True)
                status_text = self.loc.get("status_enabled") if is_enabled else self.loc.get("status_disabled")
                value_for_display = ""
                mode = var_data.get('mode', 'single')
                if mode != 'single':
                    count = len(var_data.get('values', []))
                    value_for_display = f"[Pool: {count} keys] - Mode: {mode.capitalize()}"
                elif var_data.get('is_secret'):
                    value_for_display = '*****'
                else:
                    value_for_display = var_data.get('value')
                tags = ('secret' if var_data.get('is_secret') else 'normal',)
                if not is_enabled:
                    tags += ('disabled',)
                self.var_tree.insert("", "end", iid=var_data["name"], values=(var_data["name"], value_for_display, status_text), tags=tags)
        else:
            messagebox.showerror(self.loc.get("messagebox_error_title"), f"Failed to load variables from API: {data}")
        self.var_tree.tag_configure('secret', foreground='orange')
        self.var_tree.tag_configure('disabled', foreground='grey')
        self._update_button_state()
    def _add_variable(self):
        dialog = VariableDialog(self, title=self.loc.get("settings_variables_dialog_add_title", fallback="Add New Variable"), kernel=self.kernel)
        if dialog.result:
            name, value, is_secret, mode = dialog.result
            success, response = self.api_client.update_variable(name, value, is_secret, is_enabled=True, mode=mode)
            if success:
                self.load_variables_to_ui()
            else:
                messagebox.showerror(self.loc.get("messagebox_error_title"), f"API Error: {response}")
    def _edit_variable(self):
        selected_item = self.var_tree.focus()
        if not selected_item:
            messagebox.showwarning(self.loc.get("messagebox_warning_title"), self.loc.get("settings_variables_warn_select_to_edit"), parent=self)
            return
        var_name = selected_item
        var_backend_data = next((vc for vc in self.variables_data_cache if vc['name'] == var_name), None)
        if not var_backend_data:
            messagebox.showerror(self.loc.get("messagebox_error_title"), "Could not find variable data to edit. Please refresh.")
            return
        dialog = VariableDialog(self, title=self.loc.get("settings_variables_dialog_edit_title"), kernel=self.kernel, existing_name=var_name, existing_data=var_backend_data)
        if dialog.result:
            _name, value, is_secret, mode = dialog.result
            success, response = self.api_client.update_variable(var_name, value, is_secret, var_backend_data.get('is_enabled', True), mode=mode)
            if success:
                self.load_variables_to_ui()
            else:
                messagebox.showerror(self.loc.get("messagebox_error_title"), f"API Error: {response}")
    def _toggle_variable_state(self):
        selected_item = self.var_tree.focus()
        if not selected_item: return
        var_name = selected_item
        var_cache = next((vc for vc in self.variables_data_cache if vc['name'] == var_name), None)
        if not var_cache: return
        new_state = not var_cache.get('is_enabled', True)
        success, response = self.api_client.update_variable_state(var_name, new_state)
        if success:
            self.load_variables_to_ui()
        else:
            messagebox.showerror(self.loc.get("messagebox_error_title"), f"API Error: {response}")
    def _update_button_state(self, event=None):
        selected_item = self.var_tree.focus()
        if not selected_item:
            self.toggle_button.config(state="disabled")
            return
        self.toggle_button.config(state="normal")
        var_cache = next((vc for vc in self.variables_data_cache if vc['name'] == selected_item), None)
        if var_cache:
            if var_cache.get('is_enabled', True):
                self.toggle_button.config(text=self.loc.get("settings_variables_btn_disable", fallback="Disable"))
            else:
                self.toggle_button.config(text=self.loc.get("settings_variables_btn_enable", fallback="Enable"))
    def _delete_variable(self):
        selected_item = self.var_tree.focus()
        if not selected_item:
            messagebox.showwarning(self.loc.get("messagebox_warning_title"), self.loc.get("settings_variables_warn_select_to_delete"), parent=self)
            return
        var_name = selected_item
        if messagebox.askyesno(self.loc.get("messagebox_confirm_title"), self.loc.get("settings_variables_confirm_delete", var_name=var_name), parent=self):
            success, response = self.api_client.delete_variable(var_name)
            if success:
                self.load_variables_to_ui()
            else:
                 messagebox.showerror(self.loc.get("messagebox_error_title"), f"API Error: {response}")
    def _copy_variable_placeholder(self):
        selected_item = self.var_tree.focus()
        if not selected_item:
            messagebox.showwarning(self.loc.get("messagebox_warning_title"), self.loc.get("settings_variables_warn_select_to_copy"), parent=self)
            return
        var_name = selected_item
        placeholder = f"{{{{vars.{var_name}}}}}"
        self.clipboard_clear()
        self.clipboard_append(placeholder)
        self.kernel.write_to_log(self.loc.get("settings_variables_copy_success", fallback=f"Placeholder '{placeholder}' has been copied to clipboard."), "SUCCESS")

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\settings_components\webhook_settings_frame.py
# JUMLAH BARIS : 41
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\flowork_core_ui\settings_components\webhook_settings_frame.py
# JUMLAH BARIS : 40
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar, BooleanVar
from flowork_gui.api_client.client import ApiClient
class WebhookSettingsFrame(ttk.LabelFrame):
    def __init__(self, parent, kernel):
        self.api_client = ApiClient()
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        super().__init__(parent, text=self.loc.get("settings_webhook_title", fallback="Webhook Settings"), padding=15)
        self.webhook_enabled_var = BooleanVar()
        self.webhook_port_var = StringVar()
        self._build_widgets()
    def _build_widgets(self):
        webhook_check = ttk.Checkbutton(self, text=self.loc.get("settings_webhook_enable_label", fallback="Enable Webhook/API Server"), variable=self.webhook_enabled_var)
        webhook_check.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        port_label = ttk.Label(self, text=self.loc.get("settings_webhook_port_label", fallback="Server Port:"))
        port_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        port_entry = ttk.Entry(self, textvariable=self.webhook_port_var, width=10)
        port_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
    def load_settings_data(self, settings_data):
        """Loads webhook settings from the provided data dictionary."""
        self.webhook_enabled_var.set(settings_data.get("webhook_enabled", False))
        self.webhook_port_var.set(str(settings_data.get("webhook_port", 8989)))
    def get_settings_data(self) -> dict:
        """Returns the current webhook settings from the UI."""
        try:
            port = int(self.webhook_port_var.get())
            return {
                "webhook_enabled": self.webhook_enabled_var.get(),
                "webhook_port": port
            }
        except ValueError:
            raise ValueError("Port must be a valid number.")

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\metrics_dashboard\__init__.py
# JUMLAH BARIS : 1
#######################################################################

```py
from flowork_gui.api_client.client import ApiClient

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\metrics_dashboard\processor.py
# JUMLAH BARIS : 51
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\metrics_dashboard\processor.py
# JUMLAH BARIS : 50
#######################################################################

from flowork_kernel.api_contract import BaseModule, BaseUIProvider
from flowork_gui.api_client.client import ApiClient
class MetricsDashboardModule(BaseModule, BaseUIProvider):
    TIER = "free"  # ADDED BY SCANNER: Default tier
    """
    Plugin yang menyediakan UI untuk menampilkan metrik eksekusi workflow.
    """
    def __init__(self, module_id, services):
        self.api_client = ApiClient()
        super().__init__(module_id, services)
        self.kernel.write_to_log(f"Plugin Dashboard Metrik ({self.module_id}) berhasil diinisialisasi.", "SUCCESS")
    def execute(self, payload, config, status_updater, ui_callback, mode='EXECUTE'):
        status_updater("Tidak ada aksi", "INFO")
        return payload
    def get_ui_tabs(self):
        """
        Mendaftarkan halaman dashboard metrik ke Kernel.
        """
        self.kernel.write_to_log(f"MetricsDashboard: Kernel meminta tab UI dari saya.", "DEBUG")
        return []
        """
        return [
            {
                'key': 'metrics_dashboard',
                'title': self.loc.get('metrics_dashboard_title', fallback="Dashboard Metrik"),
                'frame_class': MetricsDashboardView
            }
        ]
        """
    def get_menu_items(self):
        """
        Menambahkan item menu untuk membuka dashboard metrik.
        """
        return []
        """
        return [
            {
                "parent": "Bantuan",
                "label": self.loc.get('menu_open_metrics_dashboard', fallback="Buka Dashboard Metrik"),
                "command": lambda: self.kernel.create_ui_tab_by_key('metrics_dashboard')
            }
        ]
        """

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\metrics_logger_plugin\__init__.py
# JUMLAH BARIS : 1
#######################################################################

```py
from flowork_gui.api_client.client import ApiClient

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\metrics_logger_plugin\metrics_logger.py
# JUMLAH BARIS : 46
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\plugins\metrics_logger_plugin\metrics_logger.py
# JUMLAH BARIS : 45
#######################################################################

import os
import json
import time
from flowork_kernel.api_contract import BaseModule
from flowork_gui.api_client.client import ApiClient
class MetricsLogger(BaseModule):
    TIER = "free"  # ADDED BY SCANNER: Default tier
    """
    Service that runs in the background, listens for NODE_EXECUTION_METRIC events,
    and logs them to a file for later analysis by other widgets.
    """
    def __init__(self, module_id, services):
        self.api_client = ApiClient()
        super().__init__(module_id, services)
        self.history_file_path = os.path.join(self.kernel.data_path, "metrics_history.jsonl")
    def on_load(self):
        """When the plugin loads, subscribe to the event bus."""
        self.logger("Metrics Logger: Ready to record detailed execution metrics.", "INFO")
        self.event_bus.subscribe(
            event_name="NODE_EXECUTION_METRIC",
            subscriber_id=self.module_id,
            callback=self.on_metrics_updated
        )
    def on_metrics_updated(self, metrics_data):
        """
        Callback executed whenever a NODE_EXECUTION_METRIC event occurs.
        """
        log_entry = {
            "timestamp": time.time(),
            "metrics": metrics_data
        }
        try:
            with open(self.history_file_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            self.logger(f"Metrics Logger: Failed to write to history file: {e}", "ERROR")
    def execute(self, payload, config, status_updater, ui_callback, mode):
        return payload

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\tools\backup_system\archiver.py
# JUMLAH BARIS : 193
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\Users\User\Desktop\FLOWORK\tools\backup_system\archiver.py
# PERBAIKAN : - Menambahkan 'absolute_path = os.path.abspath(file_path)' untuk
#               mendefinisikan variabel yang hilang di dalam scope fungsi.
# 			- Memperbaiki variabel 'total_lines_after_write' dengan cara yang sama.
#######################################################################
import os
import time
import logging
import shutil
import re
import traceback

class Archiver:
    """Encapsulates all logic for cleaning source files and creating the backup.md archive."""

    def __init__(self, project_root):
        self.project_root = project_root

        self.backup_filename = "backup.md"
        self.backup_dir = os.path.join(self.project_root, "data", "plan")
        self.backup_file_path = os.path.join(self.backup_dir, self.backup_filename)

        # MODIFIED: Added 'ai_models' to the exclusion list.
        self.excluded_dirs_entirely = {'.git', '.idea', '__pycache__', 'build', 'dist', 'flowork.egg-info', 'tools', 'generated_services','.venv', 'data', 'ai_models','docs','vendor','python','supabase','logs','.venv'}

        self.excluded_files = {self.backup_filename, '.gitignore', 'refactor_scanners.py', 'run_scanners_cli.py', '__init__.py','get-pip.py','.flowork'}

        self.allowed_extensions_for_content = {'.py', '.json','.bat'}

        self.included_specific_files_for_content = set()
        self.excluded_extensions_for_map = {'.awenkaudico', '.teetah', '.pyd', '.aola', '.so', '.c', '.egg-info','.flowork'}

    def _get_line_count(self, file_path):
        """
        Counts the total number of lines in a file, including empty ones.
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                line_count = sum(1 for line in f)
            return line_count
        except Exception as e:
            logging.error(f"ARCHIVER: Could not count lines for {file_path}: {e}")
            return 0

    def clean_pycache(self):
        logging.info("Starting Python cache cleanup...")
        cleaned_count = 0
        for root, dirs, _ in os.walk(self.project_root):
            if '__pycache__' in dirs:
                pycache_path = os.path.join(root, '__pycache__')
                try:
                    shutil.rmtree(pycache_path)
                    cleaned_count += 1
                except Exception as e:
                    logging.error(f"FAILED TO DELETE CACHE: {pycache_path} | Error: {e}")
        if cleaned_count > 0:
            logging.info(f"Cache cleanup complete. {cleaned_count} __pycache__ folders deleted.")
        else:
            logging.info("No __pycache__ folders found.")

    def clean_python_comments(self, content):
        pattern = re.compile(r"^\s*#.*$")
        return "\n".join([line for line in content.splitlines() if not pattern.match(line)])

    def fix_file_spacing(self, source_code: str) -> str:
        lines = source_code.splitlines()
        non_blank_lines = [line for line in lines if line.strip()]
        return "\n".join(non_blank_lines)

    def process_source_files(self):
        logging.info("--- STARTING SOURCE FILE FIX & STAMP OPERATION (EDIT MASAL UNTUK .PY) ---")
        files_to_process = [f for f in self.get_content_backup_files() if f.endswith('.py')]

        old_header_footer_pattern = re.compile(r"#######################################################################.*?awenk audico.*?#######################################################################\n?", re.DOTALL)

        for file_path in files_to_process:
            if os.path.abspath(file_path) == os.path.abspath(__file__):
                continue
            try:
                logging.info(f"PROCESSING .PY FILE: {os.path.basename(file_path)}")
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    original_content = f.read()

                core_code = old_header_footer_pattern.sub("", original_content).strip()

                if not core_code:
                    logging.info(f"Skipping .py file with no core code: {os.path.basename(file_path)}")
                    continue

                content_no_comments = self.clean_python_comments(core_code)
                content_fixed_spacing = self.fix_file_spacing(content_no_comments)

                absolute_path = os.path.abspath(file_path)
                core_code_line_count = len(content_fixed_spacing.splitlines())
                total_lines_after_write = 7 + core_code_line_count

                header_footer_block = (
                    "#######################################################################\n"
                    f"# dev : awenk audico\n"
                    f"# EMAIL SAHIDINAOLA@GMAIL.COM\n"
                    f"# WEBSITE https://github.com/FLOWORK-gif/FLOWORK\n"
                    f"# File NAME : {absolute_path}\n"
                    f"# JUMLAH BARIS : {total_lines_after_write}\n"
                    "#######################################################################"
                )

                final_content = f"{header_footer_block}\n\n{content_fixed_spacing}\n"

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(final_content)
            except Exception as e:
                logging.error(f"MODIFICATION FAILED: {os.path.basename(file_path)} | Error: {e}")
                logging.error(traceback.format_exc())
        logging.info("--- SOURCE FILE FIX & STAMP OPERATION COMPLETE ---")

    def get_content_backup_files(self):
        content_files = []

        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in self.excluded_dirs_entirely]

            for file in files:
                if file in self.excluded_files:
                    continue
                file_path = os.path.join(root, file)
                file_extension = os.path.splitext(file)[1]
                if file_extension in self.allowed_extensions_for_content:
                    content_files.append(file_path)
        return content_files

    def format_backup_content(self, file_path):
        file_extension = os.path.splitext(file_path)[1].lstrip('.')
        # ADDED: Define the missing variables within the correct scope.
        absolute_path = os.path.abspath(file_path)
        total_lines_after_write = self._get_line_count(file_path)

        line_count = self._get_line_count(file_path)
        header_block = (
                    "#######################################################################\n"
                    f"# dev : awenk audico\n"
                    f"# EMAIL SAHIDINAOLA@GMAIL.COM\n"
                    f"# WEBSITE https://github.com/FLOWORK-gif/FLOWORK\n"
                    f"# File NAME : {absolute_path}\n"
                    f"# JUMLAH BARIS : {total_lines_after_write}\n"
                    "#######################################################################"
        )

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().strip()

            if file_path.endswith('.py'):
                old_header_pattern = re.compile(r"#######################################################################.*?awenk audico.*?#######################################################################\n?", re.DOTALL)
                content = old_header_pattern.sub("", content).strip()

            if content:
                return f"{header_block}\n\n```{file_extension}\n{content}\n```"
            else:
                return None
        except Exception as e:
            logging.error(f"FAILED TO READ (for backup): {file_path} | Error: {e}")
            return None

    def run_backup_cycle(self):
        logging.info("--- STARTING MAIN CYCLE ---")
        self.clean_pycache()
        logging.info("Waiting 1 second after cache cleanup.")
        time.sleep(1)

        self.process_source_files()
        logging.info("Waiting 1 second after source file modification.")
        time.sleep(1)

        logging.info(f"Starting archive creation process to '{self.backup_file_path}'...")
        os.makedirs(self.backup_dir, exist_ok=True)

        files_to_archive = self.get_content_backup_files()

        with open(self.backup_file_path, 'w', encoding='utf-8') as backup_f:
            all_content_blocks = []
            for file_path in files_to_archive:
                formatted_content = self.format_backup_content(file_path)
                if formatted_content:
                    all_content_blocks.append(formatted_content)

            backup_f.write("\n\n".join(all_content_blocks))

        logging.info(f"Archive '{self.backup_filename}' successfully created in data/plan folder. {len(all_content_blocks)} file contents were archived.")
        logging.info("--- MAIN CYCLE COMPLETE ---\n")
```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\tools\guardian_angel\event_handler.py
# JUMLAH BARIS : 56
#######################################################################

```py
# dev: awenk audico
# EMAIL: SAHIDINAOLA@GMAIL.COM
# WEBSITE: WWW.TEETAH.ART
# File NAME: tools/guardian_angel/event_handler.py

import os
import time
import logging
from watchdog.events import FileSystemEventHandler

class BackupEventHandler(FileSystemEventHandler):
    """
    A specialized event handler that detects file system changes
    and triggers the backup cycle via the archiver.
    Its single responsibility is to handle watchdog events.
    """
    def __init__(self, archiver):
        """
        Initializes the event handler.
        Args:
            archiver: An instance of the Archiver class to run backups.
        """
        self.archiver = archiver
        self.last_triggered = 0
        self.debounce_period = 5  # seconds

    def on_any_event(self, event):
        """
        This method is called by the watchdog observer when any file event occurs.
        Args:
            event: The event object representing the file system change.
        """
        # Note: Do not trigger a backup for changes to the backup file itself.
        if os.path.abspath(event.src_path) == os.path.abspath(self.archiver.backup_file_path):
            return

        # Note: Check if the path is in one of the fully excluded directories.
        path_str_for_dir_check = event.src_path.replace(os.sep, '/')
        if any(f"/{excluded_dir}/" in f"/{path_str_for_dir_check}/" or path_str_for_dir_check.endswith(f"/{excluded_dir}") for excluded_dir in self.archiver.excluded_dirs_entirely):
             return

        # Note: Exclude specific file names.
        if os.path.basename(event.src_path) in self.archiver.excluded_files:
            return

        # Note: Ignore events for directories.
        if event.is_directory:
            return

        # Note: Debounce to prevent rapid firing for a single save action.
        current_time = time.time()
        if current_time - self.last_triggered > self.debounce_period:
            logging.info(f"CHANGE DETECTED in: {event.src_path}. Rerunning backup cycle...")
            self.last_triggered = current_time
            # Note: The handler's only job is to delegate the action to the archiver.
            self.archiver.run_backup_cycle()
```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\tools\guardian_angel\guardian.py
# JUMLAH BARIS : 52
#######################################################################

```py
# dev: awenk audico
# EMAIL: SAHIDINAOLA@GMAIL.COM
# WEBSITE: WWW.TEETAH.ART
# File NAME: tools/guardian_angel/guardian.py

import time
import logging
from watchdog.observers import Observer
from .event_handler import BackupEventHandler

class GuardianAngel:
    """
    The main orchestrator for the backup system.
    Its single responsibility is to set up and run the file system observer.
    """
    def __init__(self, project_root: str, archiver_instance):
        """
        Initializes the Guardian Angel.
        Args:
            project_root (str): The root directory of the project to watch.
            archiver_instance: An instance of the Archiver to perform backups.
        """
        self.project_root = project_root
        self.archiver = archiver_instance
        self.observer = Observer()

    def start(self):
        """
        Starts the Guardian Angel's watch.
        It runs the initial backup and then monitors for changes indefinitely.
        """
        # Note: Run one backup cycle on startup.
        self.archiver.run_backup_cycle()

        # Note: Create the specialized event handler.
        event_handler = BackupEventHandler(archiver=self.archiver)

        # Note: Schedule the observer to watch the project root recursively.
        self.observer.schedule(event_handler, self.project_root, recursive=True)
        self.observer.start()

        logging.info(f"Guardian Angel is active. Watching for changes in: {self.project_root}")
        logging.info("Press Ctrl+C to stop watching.")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
            logging.info("Guardian Angel stopped by user.")

        self.observer.join()
```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\utils\__init__.py
# JUMLAH BARIS : 0
#######################################################################

```py

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\utils\performance_logger.py
# JUMLAH BARIS : 22
#######################################################################

```py
# File: flowork_gui/utils/performance_logger.py
import time
from functools import wraps

def log_performance(log_message: str):
    """
    A decorator that logs the execution time of a function.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            log_entry = f"PERF-GUI: {log_message} - Execution Time: {duration_ms:.2f} ms"
            print(log_entry) # Simple print for GUI-side logging

            return result
        return wrapper
    return decorator
```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\__init__.py
# JUMLAH BARIS : 0
#######################################################################

```py

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\authentication_dialog.py
# JUMLAH BARIS : 138
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\authentication_dialog.py
# JUMLAH BARIS : 137
#######################################################################

import ttkbootstrap as ttk
from tkinter import messagebox, simpledialog # (DITAMBAHKAN)
import threading
from flowork_gui.api_client.client import ApiClient
class AuthenticationDialog(ttk.Toplevel):
    """
    A single dialog window that handles both Login and Registration forms.
    (MODIFIED) Now stores user data in the kernel and publishes an event on successful login.
    """
    def __init__(self, parent, kernel):
        super().__init__(parent)
        self.kernel = kernel
        self.api_client = ApiClient(kernel=self.kernel)
        self.title("Login or Register")
        self.geometry("400x520") # (MODIFIKASI) Ditinggikan sedikit untuk tombol baru
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.login_email_var = ttk.StringVar()
        self.login_password_var = ttk.StringVar()
        self.reg_username_var = ttk.StringVar()
        self.reg_email_var = ttk.StringVar()
        self.reg_password_var = ttk.StringVar()
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.login_frame = self._create_login_frame(self.container)
        self.register_frame = self._create_register_frame(self.container)
        self.show_login()
        self.wait_window()
    def show_login(self):
        self.register_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True)
    def show_register(self):
        self.login_frame.pack_forget()
        self.register_frame.pack(fill="both", expand=True)
    def _create_login_frame(self, parent):
        frame = ttk.Frame(parent, padding=40)
        ttk.Label(frame, text="FLOWORK", font=("-size 24 -weight bold"), bootstyle="primary").pack(pady=(0, 10))
        ttk.Label(frame, text="Welcome Back!", font=("-size 12"), bootstyle="secondary").pack(pady=(0, 30))
        ttk.Label(frame, text="Email", font=("-size 10")).pack(fill="x", pady=(0,2))
        ttk.Entry(frame, textvariable=self.login_email_var).pack(fill="x", pady=(0,15))
        ttk.Label(frame, text="Password", font=("-size 10")).pack(fill="x", pady=(0,2))
        ttk.Entry(frame, textvariable=self.login_password_var, show="*").pack(fill="x", pady=(0,25))
        self.login_button = ttk.Button(frame, text="Login", command=self._perform_login_thread, bootstyle="primary")
        self.login_button.pack(fill="x", ipady=8, pady=(0,10))
        links_frame = ttk.Frame(frame)
        links_frame.pack(fill='x', pady=5)
        register_link = ttk.Button(links_frame, text="Don't have an account? Register", command=self.show_register, bootstyle="link-secondary")
        register_link.pack(side="left")
        forgot_password_link = ttk.Button(links_frame, text="Forgot Password?", command=self._prompt_for_password_reset, bootstyle="link-primary")
        forgot_password_link.pack(side="right")
        return frame
    def _create_register_frame(self, parent):
        frame = ttk.Frame(parent, padding=40)
        ttk.Label(frame, text="Create Account", font=("-size 24 -weight bold"), bootstyle="success").pack(pady=(0, 20))
        ttk.Label(frame, text="Username:", font=("-size 10")).pack(fill="x", pady=(0,2))
        ttk.Entry(frame, textvariable=self.reg_username_var).pack(fill="x", pady=(0,10))
        ttk.Label(frame, text="Email:", font=("-size 10")).pack(fill="x", pady=(0,2))
        ttk.Entry(frame, textvariable=self.reg_email_var).pack(fill="x", pady=(0,10))
        ttk.Label(frame, text="Password:", font=("-size 10")).pack(fill="x", pady=(0,2))
        ttk.Entry(frame, textvariable=self.reg_password_var, show="*").pack(fill="x", pady=(0,20))
        self.register_button = ttk.Button(frame, text="Register", command=self._perform_register_thread, bootstyle="success")
        self.register_button.pack(fill="x", ipady=8, pady=(0,10))
        login_link = ttk.Button(frame, text="Already have an account? Login", command=self.show_login, bootstyle="link-secondary")
        login_link.pack()
        return frame
    def _prompt_for_password_reset(self):
        """Asks the user for their email to send a reset link."""
        email = simpledialog.askstring("Password Reset", "Please enter your registered email address:", parent=self)
        if email and email.strip():
            threading.Thread(target=self._perform_password_reset, args=(email.strip(),), daemon=True).start()
    def _perform_password_reset(self, email):
        """Calls the API client to initiate the password reset process."""
        self.kernel.write_to_log(f"Initiating password reset for email: {email}", "INFO")
        success, response = self.api_client.forgot_password(email)
        self.after(0, messagebox.showinfo, "Request Sent", "If an account exists for that email, a password reset link has been sent.")
    def _perform_login_thread(self):
        self.login_button.config(state="disabled", text="Logging in...")
        threading.Thread(target=self._perform_login, daemon=True).start()
    def _perform_login(self):
        email = self.login_email_var.get().strip()
        password = self.login_password_var.get().strip()
        if not email or not password:
            self.after(0, self._on_login_failed, "Email and Password are required.")
            return
        success, response = self.api_client.login_user(email, password)
        if success:
            response['email'] = email
            self.after(0, self._on_login_success, response)
        else:
            self.after(0, self._on_login_failed, response)
    def _on_login_success(self, login_data):
        self.kernel.write_to_log(f"User '{self.login_email_var.get()}' logged in successfully.", "SUCCESS")
        self.kernel.current_user = login_data
        user_tier = login_data.get('tier', 'free')
        self.kernel.license_tier = user_tier
        self.kernel.is_premium = self.kernel.TIER_HIERARCHY.get(user_tier, 0) > 0
        state_manager = self.kernel.get_service("state_manager")
        if state_manager:
            state_manager.set("user_session_token", login_data.get('session_token'))
        event_bus = self.kernel.get_service("event_bus")
        if event_bus:
            event_bus.publish("USER_LOGGED_IN", login_data)
        messagebox.showinfo("Login Success", f"Welcome back! You are logged in with '{user_tier}' tier access.", parent=self.master)
        self.destroy()
    def _on_login_failed(self, error_message):
        messagebox.showerror("Login Failed", f"Error: {error_message}", parent=self)
        self.login_button.config(state="normal", text="Login")
    def _perform_register_thread(self):
        self.register_button.config(state="disabled", text="Registering...")
        threading.Thread(target=self._perform_register, daemon=True).start()
    def _perform_register(self):
        username = self.reg_username_var.get().strip()
        email = self.reg_email_var.get().strip()
        password = self.reg_password_var.get().strip()
        if not all([username, email, password]):
            self.after(0, self._on_register_failed, "All fields are required.")
            return
        success, response = self.api_client.register_user(username, email, password)
        if success:
            self.after(0, self._on_register_success)
        else:
            self.after(0, self._on_register_failed, response)
    def _on_register_success(self):
        self.register_button.config(state="normal", text="Register")
        messagebox.showinfo("Success", "Registration successful! You can now log in.", parent=self)
        self.show_login()
    def _on_register_failed(self, error_message):
        messagebox.showerror("Registration Failed", f"Error: {error_message}", parent=self)
        self.register_button.config(state="normal", text="Register")

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\canvas_manager.py
# JUMLAH BARIS : 229
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\canvas_manager.py
# JUMLAH BARIS : 228
#######################################################################

import ttkbootstrap as ttk
from tkinter import Menu, messagebox, TclError, Text, simpledialog, scrolledtext
import uuid
import json
import re
from .properties_popup import PropertiesPopup # MODIFIED: Corrected relative import
from .custom_widgets.tooltip import ToolTip # MODIFIED: Corrected relative import
from flowork_gui.api_contract import LoopConfig, EnumVarWrapper # MODIFIED: Using the new local contract
from .canvas_components.node_manager import NodeManager
from .canvas_components.connection_manager import ConnectionManager
from .canvas_components.interaction_manager import InteractionManager
from .canvas_components.visual_manager import VisualManager
from .canvas_components.properties_manager import PropertiesManager
from flowork_gui.api_client.client import ApiClient
class _TextEditorPopup(ttk.Toplevel):
    """A custom Toplevel window for multi-line text input."""
    def __init__(self, parent, loc_service, title, prompt, initial_text=""):
        super().__init__(parent)
        self.loc = loc_service
        self.title(title)
        self.result = None
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)
        ttk.Label(main_frame, text=prompt, wraplength=380).pack(fill='x', pady=(0, 10))
        self.text_widget = scrolledtext.ScrolledText(main_frame, wrap="word", height=10, width=50)
        self.text_widget.pack(fill="both", expand=True)
        self.text_widget.insert("1.0", initial_text)
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        ttk.Button(button_frame, text=self.loc.get('button_save', fallback="Save"), command=self._on_save, bootstyle="success").pack(side="right")
        ttk.Button(button_frame, text=self.loc.get('button_cancel', fallback="Cancel"), command=self.destroy, bootstyle="secondary").pack(side="right", padx=(0, 10))
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)
    def _on_save(self):
        self.result = self.text_widget.get("1.0", "end-1c")
        self.destroy()
class CanvasManager:
    """
    Manages all specialized managers for the canvas.
    Holds the primary state (nodes, connections, labels) and delegates tasks.
    """
    def __init__(self, visual_container, coordinator_tab, canvas_widget, kernel):
        self.parent_widget = visual_container
        self.coordinator_tab = coordinator_tab
        self.canvas = canvas_widget
        self.kernel = kernel
        self.loc = self.kernel.loc
        self.canvas_nodes = {}
        self.canvas_connections = {}
        self.canvas_labels = {}
        self.tooltips = {}
        self.selected_node_id = None
        self.colors = {} # ADDED: Using fallback
        self.node_manager = NodeManager(self, self.kernel, self.canvas)
        self.connection_manager = ConnectionManager(self, self.kernel, self.canvas)
        self.interaction_manager = InteractionManager(self, self.kernel, self.canvas)
        self.visual_manager = VisualManager(self, self.kernel, self.canvas)
        self.properties_manager = PropertiesManager(self, self.kernel)
        self.interaction_manager.bind_events()
        self.visual_manager.draw_watermark()
    def _apply_markdown_to_text_widget(self, text_widget, content):
        text_widget.config(state="normal")
        text_widget.delete("1.0", "end")
        parts = re.split(r'(\*\*.*?\*\*)', content)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                text_widget.insert("end", part[2:-2], "bold")
            else:
                text_widget.insert("end", part)
        text_widget.config(state="disabled")
    def get_workflow_data(self):
        nodes_data = [{"id": n_id, "name": d["name"], "x": d["x"], "y": d["y"], "description": d.get("description", ""), "module_id": d.get("module_id"), "config_values": d.get("config_values", {})} for n_id, d in self.canvas_nodes.items()]
        connections_data = [
            {
                "id": c_id,
                "from": d["from"],
                "to": d["to"],
                "source_port_name": d.get("source_port_name"),
                "target_port_name": d.get("target_port_name"),
                "type": d.get("type", "data")
            } for c_id, d in self.canvas_connections.items()
        ]
        labels_data = [{"id": l_id, "text": d["text"], "x": d["x"], "y": d["y"], "width": d["widget"].winfo_width(), "height": d["widget"].winfo_height()} for l_id, d in self.canvas_labels.items()]
        return {"nodes": nodes_data, "connections": connections_data, "labels": labels_data}
    def load_workflow_data(self, workflow_data):
        self.clear_canvas(feedback=False)
        for node_data in workflow_data.get("nodes", []):
            self.node_manager.create_node_on_canvas(
                name=node_data.get("name"),
                x=node_data.get("x"),
                y=node_data.get("y"),
                existing_id=node_data.get("id"),
                description=node_data.get("description", ""),
                module_id=node_data.get("module_id"),
                config_values=node_data.get("config_values")
            )
        for label_data in workflow_data.get("labels", []):
            self.create_label(
                x=label_data.get("x"),
                y=label_data.get("y"),
                text=label_data.get("text"),
                existing_id=label_data.get("id"),
                width=label_data.get("width", 200),
                height=label_data.get("height", 80)
            )
        self.coordinator_tab.after(50, lambda: self.connection_manager.recreate_connections(workflow_data.get("connections", [])))
        if not self.canvas_nodes and not self.canvas_labels:
            self.visual_manager.draw_watermark()
    def clear_canvas(self, feedback=True):
        if self.coordinator_tab._execution_state != "IDLE":
            messagebox.showwarning("Action Denied", "Cannot clear the canvas while a workflow is running.") # English Hardcode
            return
        if feedback: print("INFO: Clearing the canvas...") # English Log
        for node_id in list(self.canvas_nodes.keys()):
            self.node_manager.delete_node(node_id, feedback=False)
        for label_id in list(self.canvas_labels.keys()):
            self.delete_label(label_id, feedback=False)
        self.canvas.delete("all")
        self.visual_manager.draw_grid()
        if self.interaction_manager:
            self.interaction_manager._reset_all_actions()
        self.canvas_nodes.clear()
        self.canvas_connections.clear()
        self.canvas_labels.clear()
        self.selected_node_id = None
        self.visual_manager.draw_watermark()
    def create_label(self, x, y, text=None, existing_id=None, width=200, height=80):
        label_id = existing_id or str(uuid.uuid4())
        initial_text = text or self.loc.get('canvas_new_label_text', fallback="Double click to edit...")
        label_frame = ttk.Frame(self.canvas, width=width, height=height, style="success.TFrame", borderwidth=1, relief="solid")
        label_frame.pack_propagate(False)
        text_widget = ttk.Text(label_frame, wrap="word", relief="flat", borderwidth=0,
                               foreground="black", background="#D4EDDA",
                               font=("Helvetica", 10, "normal"),
                               padx=5, pady=5)
        text_widget.pack(fill="both", expand=True)
        text_widget.tag_configure("bold", font=("Helvetica", 10, "bold"))
        self._apply_markdown_to_text_widget(text_widget, initial_text)
        sizegrip = ttk.Sizegrip(label_frame, style='success.TSizegrip')
        sizegrip.place(relx=1.0, rely=1.0, anchor="se")
        self.canvas.create_window(x, y, window=label_frame, anchor="nw", tags=("label_widget", label_id))
        self.canvas_labels[label_id] = {
            "widget": label_frame,
            "text_widget": text_widget,
            "text": initial_text,
            "x": x,
            "y": y
        }
        for widget in [label_frame, text_widget]:
            widget.bind("<ButtonPress-1>", lambda e, lid=label_id: self._on_label_press(e, lid))
            widget.bind("<B1-Motion>", lambda e, lid=label_id: self._on_label_drag(e, lid))
            widget.bind("<ButtonRelease-1>", lambda e, lid=label_id: self._on_label_release(e, lid))
            widget.bind("<Double-1>", lambda e, lid=label_id: self._edit_label_text(e, lid))
            widget.bind("<Button-3>", lambda e, lid=label_id: self._show_label_context_menu(e, lid))
        sizegrip.bind("<ButtonPress-1>", lambda e, lid=label_id: self._start_label_resize(e, lid))
        sizegrip.bind("<B1-Motion>", lambda e, lid=label_id: self._on_label_resize_drag(e, lid))
        sizegrip.bind("<ButtonRelease-1>", lambda e, lid=label_id: self._on_label_resize_release(e, lid))
        self.visual_manager.hide_watermark()
        return label_id
    def delete_label(self, label_id, feedback=True):
        if label_id in self.canvas_labels:
            widget = self.canvas_labels[label_id]['widget']
            if widget.winfo_exists():
                widget.destroy()
            del self.canvas_labels[label_id]
            self.canvas.delete(label_id)
            if feedback:
                print(f"INFO: Text note '{label_id[:8]}' deleted.") # English Log
    def _on_label_press(self, event, label_id):
        self.interaction_manager._drag_data = {"x": event.x, "y": event.y, "id": label_id}
        widget = self.canvas_labels[label_id]['widget']
        widget.lift()
    def _on_label_drag(self, event, label_id):
        if self.interaction_manager._drag_data.get("id") != label_id: return
        new_x = self.canvas.canvasx(event.x_root - self.canvas.winfo_rootx()) - self.interaction_manager._drag_data['x']
        new_y = self.canvas.canvasy(event.y_root - self.canvas.winfo_rooty()) - self.interaction_manager._drag_data['y']
        self.canvas.coords(label_id, new_x, new_y)
    def _on_label_release(self, event, label_id):
        if self.interaction_manager._drag_data.get("id") != label_id: return
        coords = self.canvas.coords(label_id)
        self.canvas_labels[label_id]['x'] = coords[0]
        self.canvas_labels[label_id]['y'] = coords[1]
        self.interaction_manager._drag_data = {}
    def _edit_label_text(self, event, label_id):
        current_text = self.canvas_labels[label_id]['text']
        popup = _TextEditorPopup(
            parent=self.canvas, loc_service=self.loc,
            title=self.loc.get('edit_note_title', fallback="Edit Note"),
            prompt=self.loc.get('edit_note_prompt', fallback="Enter new text for the note:"),
            initial_text=current_text
        )
        new_text = popup.result
        if new_text is not None:
            self.canvas_labels[label_id]['text'] = new_text
            text_widget = self.canvas_labels[label_id]['text_widget']
            self._apply_markdown_to_text_widget(text_widget, new_text)
    def _show_label_context_menu(self, event, label_id):
        context_menu = Menu(self.canvas, tearoff=0)
        context_menu.add_command(label=self.loc.get('context_menu_edit_note', fallback="Edit Note..."), command=lambda: self._edit_label_text(event, label_id))
        context_menu.add_command(label=self.loc.get('context_menu_delete_note', fallback="Delete Note"), command=lambda: self.delete_label(label_id))
        context_menu.tk_popup(event.x_root, event.y_root)
    def _start_label_resize(self, event, label_id):
        widget = self.canvas_labels[label_id]['widget']
        self.interaction_manager._resize_data = {
            'widget': widget,
            'start_x': event.x_root,
            'start_y': event.y_root,
            'start_width': widget.winfo_width(),
            'start_height': widget.winfo_height()
        }
    def _on_label_resize_drag(self, event, label_id):
        resize_data = self.interaction_manager._resize_data
        if not resize_data.get('widget'): return
        dx = event.x_root - resize_data['start_x']
        dy = event.y_root - resize_data['start_y']
        new_width = max(100, resize_data['start_width'] + dx)
        new_height = max(50, resize_data['start_height'] + dy)
        resize_data['widget'].configure(width=new_width, height=new_height)
    def _on_label_resize_release(self, event, label_id):
        self.interaction_manager._resize_data = {}

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\custom_tab.py
# JUMLAH BARIS : 74
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\custom_tab.py
# JUMLAH BARIS : 73
#######################################################################

import ttkbootstrap as ttk
from tkinter import Menu, messagebox
from flowork_gui.api_client.client import ApiClient
class CustomTab(ttk.Frame):
    """
    Sebuah frame kosong yang menjadi dasar untuk tab kustom.
    Berisi tombol untuk menambahkan modul.
    """
    def __init__(self, parent_notebook, kernel_instance):
        super().__init__(parent_notebook, style='TFrame')
        self.kernel = kernel_instance
        self.loc = self.kernel.get_service("localization_manager")
        self.api_client = ApiClient(kernel=self.kernel)
        placeholder_label = ttk.Label(
            self,
            text=self.loc.get('custom_tab_placeholder_text', fallback="This is Your Custom Tab.\\n\\nRight-click to add modules or other widgets."),
            font=("Helvetica", 14, "italic"),
            justify="center"
        )
        placeholder_label.pack(expand=True, padx=20, pady=20)
        watermark_label = ttk.Label(
            self,
            text=self.loc.get('custom_tab_watermark', fallback="WWW.TEETAH.ART"),
            font=("Helvetica", 10, "italic"),
            foreground="grey",
            anchor="se"
        )
        watermark_label.pack(side="bottom", fill="x", padx=10, pady=5)
        self.bind("<Button-3>", self._show_context_menu)
        placeholder_label.bind("<Button-3>", self._show_context_menu)
    def _show_context_menu(self, event):
        context_menu = Menu(self, tearoff=0)
        success, loaded_modules_data = self.api_client.get_components('modules')
        modules_to_display = []
        if success:
            modules_to_display = sorted([
                (mod_data['id'], mod_data.get('name', mod_data['id']))
                for mod_data in loaded_modules_data
            ], key=lambda x: x[1].lower())
        if not modules_to_display:
            context_menu.add_command(label=self.loc.get('no_modules_found', fallback="No modules available."))
            context_menu.entryconfig(self.loc.get('no_modules_found', fallback="No modules available."), state="disabled")
        else:
            for module_id, module_name in modules_to_display:
                context_menu.add_command(
                    label=module_name,
                    command=lambda mid=module_id, mname=module_name: self._simulate_add_module_to_canvas(mid, mname)
                )
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    def _simulate_add_module_to_canvas(self, module_id, module_name):
        messagebox.showinfo(
            self.loc.get('info_title', fallback="Information"),
            self.loc.get(
                'simulate_add_module_message',
                module_name=module_name,
                module_id=module_id,
                fallback=f"Module '{module_name}' (ID: {module_id}) would be added to the workflow canvas if this feature were fully integrated."
            )
        )
        self.kernel.write_to_log(
            self.loc.get('log_simulate_add_module', module_name=module_name, module_id=module_id, fallback=f"Simulation: Module '{module_name}' (ID: {module_id}) 'added' from CustomTab."),
            "INFO"
        )

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\dashboard_frame.py
# JUMLAH BARIS : 58
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\dashboard_frame.py
# JUMLAH BARIS : 57
#######################################################################

import ttkbootstrap as ttk
from flowork_gui.api_client.client import ApiClient
class DashboardFrame(ttk.Frame):
    """
    Sebuah bingkai yang membungkus setiap widget di dashboard.
    Menyediakan title bar untuk dragging, tombol close, dan pegangan resize.
    [FIXED V2] Now uses an explicit 'is_docked' flag to control drag/resize behavior correctly.
    """
    def __init__(self, parent, manager, widget_id, title, content_widget_class, content_widget_id: str, is_docked=False, **kwargs): # MODIFIED: Added is_docked parameter
        self.api_client = ApiClient()
        super().__init__(parent, style='primary.TFrame', borderwidth=1, relief="solid")
        self.manager = manager
        self.widget_id = widget_id
        self.is_docked = is_docked # ADDED: Store the docked state
        title_bar = ttk.Frame(self, style='primary.TFrame', height=30)
        title_bar.pack(side="top", fill="x", padx=1, pady=1)
        title_bar.pack_propagate(False)
        close_button = ttk.Button(title_bar, text="X", width=3, style="danger.TButton", command=self.close_widget)
        close_button.pack(side="right", padx=(0, 5), pady=2)
        title_label = ttk.Label(title_bar, text=title, style="primary.inverse.TLabel", font=("Helvetica", 10, "bold"))
        title_label.pack(side="left", padx=10)
        content_frame = ttk.Frame(self, style='light.TFrame', padding=5)
        content_frame.pack(expand=True, fill="both", padx=1, pady=(0, 1))
        if not self.is_docked:
            sizegrip = ttk.Sizegrip(self, style='primary.TSizegrip')
            sizegrip.place(relx=1.0, rely=1.0, anchor="se")
            sizegrip.bind("<ButtonPress-1>", self.on_resize_press)
            sizegrip.bind("<B1-Motion>", self.on_resize_motion)
            sizegrip.bind("<ButtonRelease-1>", self.on_resize_release)
        self.content_widget = content_widget_class(content_frame, self.manager.coordinator_tab, self.manager.kernel, widget_id=content_widget_id)
        self.content_widget.pack(expand=True, fill="both")
        title_bar.bind("<ButtonPress-1>", self.on_press)
        title_bar.bind("<B1-Motion>", self.on_drag)
        title_bar.bind("<ButtonRelease-1>", self.on_release)
        title_label.bind("<ButtonPress-1>", self.on_press)
        title_label.bind("<B1-Motion>", self.on_drag)
        title_label.bind("<ButtonRelease-1>", self.on_release)
    def on_press(self, event):
        if not self.is_docked:
            self.manager.start_drag(self, event)
    def on_drag(self, event):
        if not self.is_docked:
            self.manager.drag_widget(event)
    def on_release(self, event):
        if not self.is_docked:
            self.manager.stop_drag(event)
    def on_resize_press(self, event): self.manager.start_resize(self, event)
    def on_resize_motion(self, event): self.manager.resize_widget(event)
    def on_resize_release(self, event): self.manager.stop_resize(event)
    def close_widget(self): self.manager.remove_widget(self.widget_id)

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\dashboard_manager.py
# JUMLAH BARIS : 291
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\dashboard_manager.py
# JUMLAH BARIS : 290
#######################################################################

import ttkbootstrap as ttk
from tkinter import Menu, messagebox
import uuid
from .dashboard_frame import DashboardFrame
from flowork_kernel.utils.performance_logger import log_performance
import threading
import time
from flowork_gui.widgets.canvas_area.canvas_area_widget import CanvasAreaWidget
class DashboardManager:
    """
    Manages adding, removing, moving, resizing, and saving the layout of widgets.
    (REFACTORED for GUI Independence) Now receives a mock_kernel for compatibility
    with child components that are not yet fully refactored.
    """
    def __init__(self, host_frame, coordinator_tab, kernel, tab_id, is_new_tab=False):
        self.host_frame = host_frame
        self.coordinator_tab = coordinator_tab
        self.kernel = kernel
        self.loc = self.kernel.loc # Get loc from the mock kernel
        self.api_client = self.kernel.api_client # Get api_client from the mock kernel
        self.widgets = {}
        self.tab_id = tab_id
        self.is_new_tab = is_new_tab
        self.watermark_label = None
        self._drag_data = {'widget': None, 'x': 0, 'y': 0}
        self._resize_data = {'widget': None, 'start_x': 0, 'start_y': 0, 'start_width': 0, 'start_height': 0}
        self.available_widget_classes = {
            "canvas_area": CanvasAreaWidget
        }
        self.available_widgets_from_api = {}
        self.docks = {}
        self.docked_widgets = {"left": [], "right": []}
        self.pinned_docks = {"left": False, "right": False}
        self.hide_jobs = {"left": None, "right": None}
        self._build_ui_with_docks()
        self.host_frame.after(50, self._load_initial_data_async)
    def _build_ui_with_docks(self):
        """(REFACTORED V3) Uses .place() for all main components to ensure stable geometry management."""
        self.canvas_area = ttk.Frame(self.host_frame)
        self.canvas_area.place(x=0, y=0, relwidth=1, relheight=1)
        self.canvas_area.bind("<Button-3>", self.show_context_menu)
        self.docks['left'] = self._create_dock_structure('left', '>')
        self.docks['right'] = self._create_dock_structure('right', '<')
        self.docks['left']['handle'].place(relx=0, rely=0, relheight=1)
        self.docks['right']['handle'].place(relx=1.0, rely=0, relheight=1, anchor='ne')
    def _create_dock_structure(self, side, handle_text):
        """(MODIFIED) Now creates handle as a direct child of host_frame for stable placement."""
        handle = ttk.Frame(self.host_frame, width=20, bootstyle="secondary")
        handle_label = ttk.Label(handle, text=handle_text, bootstyle="inverse-secondary", font=("Helvetica", 12, "bold"))
        handle_label.pack(expand=True)
        content_frame = ttk.Frame(self.host_frame, width=300, bootstyle="secondary")
        control_bar = ttk.Frame(content_frame, bootstyle="secondary")
        control_bar.pack(fill='x', padx=5, pady=2)
        add_button = ttk.Button(control_bar, text="+", bootstyle="success-link", width=2, command=lambda s=side: self._show_add_to_dock_menu(s))
        add_button.pack(side='left')
        pin_button = ttk.Button(control_bar, text="📌", bootstyle="light-link", command=lambda s=side: self._toggle_pin(s))
        pin_button.pack(side='right')
        handle.bind("<Enter>", lambda e, s=side: self._show_dock(s))
        content_frame.bind("<Leave>", lambda e, s=side: self._hide_dock_later(s))
        return {'frame': content_frame, 'content': content_frame, 'handle': handle, 'pin_button': pin_button}
    def _show_add_to_dock_menu(self, side):
        """Creates and shows a context menu to add any available widget to the specified dock."""
        add_menu = Menu(self.host_frame, tearoff=0)
        all_docked_widget_types = {w.content_widget.widget_id for w_list in self.docked_widgets.values() for w in w_list}
        available_for_docking = {k: v for k, v in self.available_widgets_from_api.items() if k not in all_docked_widget_types}
        if not available_for_docking:
            add_menu.add_command(label=self.loc.get('dock_no_widgets_available', fallback="No more widgets to add"), state="disabled")
        else:
            for key, info in sorted(available_for_docking.items(), key=lambda item: item[1]['name'].lower()):
                add_menu.add_command(label=info['name'], command=lambda k=key, s=side: self.add_widget_and_save(k, dock_side=s))
        try:
            add_menu.tk_popup(self.host_frame.winfo_pointerx(), self.host_frame.winfo_pointery())
        finally:
            add_menu.grab_release()
    def _toggle_pin(self, side):
        """Toggles the pinned state of a dock."""
        self.pinned_docks[side] = not self.pinned_docks[side]
        pin_char = "📌"
        self.docks[side]['pin_button'].config(text=pin_char)
        if not self.pinned_docks[side]:
            self._hide_dock_later(side)
    def _show_dock(self, side):
        """Shows a dock panel."""
        if self.hide_jobs[side]:
            self.host_frame.after_cancel(self.hide_jobs[side])
            self.hide_jobs[side] = None
        relx = 0 if side == 'left' else 1.0
        anchor = 'nw' if side == 'left' else 'ne'
        self.docks[side]['frame'].place(in_=self.host_frame, relx=relx, rely=0, relheight=1.0, anchor=anchor)
        self.docks[side]['frame'].lift()
    def _hide_dock_later(self, side):
        """Schedules a dock to be hidden after a short delay."""
        if not self.pinned_docks[side]:
            self.hide_jobs[side] = self.host_frame.after(300, lambda: self.docks[side]['frame'].place_forget())
    def _load_initial_data_async(self):
        self._create_watermark()
        threading.Thread(target=self._load_initial_data_worker, daemon=True).start()
    @log_performance("Fetching all initial data for DashboardManager")
    def _load_initial_data_worker(self):
        success_widgets, widgets_data = self.api_client.get_components('widgets')
        success_layout, layout_data = self.api_client.get_dashboard_layout(self.tab_id)
        self.host_frame.after(0, self._on_initial_data_loaded, success_widgets, widgets_data, success_layout, layout_data)
    def _on_initial_data_loaded(self, success_widgets, widgets_data, success_layout, layout_data):
        if not success_widgets:
            print(f"Failed to fetch available widgets via API: {widgets_data}") # English Log
        else:
            for widget_data in widgets_data:
                widget_id = widget_data.get('id')
                if not widget_data.get('is_paused', False):
                    self.available_widgets_from_api[widget_id] = widget_data
            print(f"Dashboard Manager: {len(self.available_widgets_from_api)} widgets available from API.") # English Log
        if not success_layout:
            print(f"Failed to load layout for tab {self.tab_id}: {layout_data}") # English Log
        elif layout_data:
            self._remove_watermark()
            for widget_id, config in layout_data.items():
                widget_type = config.get("type")
                if widget_type in self.available_widget_classes: # Check if we know how to render it
                    dock_side = config.get("dock")
                    self.add_widget(
                        widget_type,
                        config.get("x", 10),
                        config.get("y", 10),
                        config.get("width", 400),
                        config.get("height", 300),
                        existing_id=widget_id,
                        dock_side=dock_side
                    )
                else:
                    print(f"Widget type '{widget_type}' from saved layout could not be loaded (class not found in GUI).") # English Log
        canvas_area_exists = any(
            hasattr(frame, 'content_widget') and frame.content_widget.widget_id == 'canvas_area'
            for frame in self.widgets.values()
        )
        if not canvas_area_exists:
            self.add_widget("canvas_area", 0, 0, 0, 0)
            print("DashboardManager: Core 'canvas_area' was not in the layout, re-initializing it.") # English Log
        if not self.widgets:
            if self.is_new_tab:
                self._load_default_layout()
            else:
                 self._create_watermark()
    def _create_watermark(self):
        if not self.canvas_area.winfo_exists(): return
        if self.watermark_label and self.watermark_label.winfo_exists(): return
        self.watermark_label = ttk.Label(
            self.canvas_area, text="www.teetah.art", font=("Helvetica", 40, "bold"),
            foreground="#3a3a3a", anchor="center"
        )
        self.watermark_label.place(relx=0.5, rely=0.5, anchor="center")
        self.watermark_label.lower()
    def _remove_watermark(self):
        if self.watermark_label and self.watermark_label.winfo_exists():
            self.watermark_label.destroy()
            self.watermark_label = None
    def clear_all_widgets(self):
        for widget_id in list(self.widgets.keys()):
            self.remove_widget(widget_id)
        self.save_layout()
        self._create_watermark()
    @log_performance("Loading default dashboard layout")
    def _load_default_layout(self):
        print(f"DashboardManager for tab {self.tab_id} is loading a default layout.") # English Log
        self._remove_watermark()
        self.add_widget("canvas_area", 0, 0, 0, 0)
        self.save_layout()
    def save_layout(self):
        layout = {}
        for widget_id, frame in self.widgets.items():
            if hasattr(frame, 'content_widget') and hasattr(frame.content_widget, 'widget_id'):
                widget_type_key = frame.content_widget.widget_id
                dock_side = None
                if frame in self.docked_widgets['left']:
                    dock_side = 'left'
                elif frame in self.docked_widgets['right']:
                    dock_side = 'right'
                if dock_side:
                    layout[widget_id] = {"type": widget_type_key, "dock": dock_side}
                elif widget_type_key != 'canvas_area':
                    if widget_type_key in self.available_widgets_from_api:
                        layout[widget_id] = {"type": widget_type_key, "x": frame.winfo_x(), "y": frame.winfo_y(), "width": frame.winfo_width(), "height": frame.winfo_height()}
        success, response = self.api_client.save_dashboard_layout(self.tab_id, layout)
        if not success:
            print(f"Failed to save layout via API: {response}") # English Log
    def add_widget(self, widget_type_key, x=0, y=0, width=400, height=300, existing_id=None, dock_side=None):
        self._remove_watermark()
        widget_info_from_api = self.available_widgets_from_api.get(widget_type_key)
        WidgetClass = self.available_widget_classes.get(widget_type_key)
        if not widget_info_from_api or not WidgetClass:
            print(f"Failed to add widget: Type '{widget_type_key}' not found or its class is not registered in the GUI.", "ERROR") # English Log
            return
        widget_id = existing_id or str(uuid.uuid4())
        frame = None
        if dock_side == 'left':
            frame = DashboardFrame(self.docks['left']['content'], self, widget_id, widget_info_from_api["name"], WidgetClass, content_widget_id=widget_type_key, is_docked=True)
            frame.pack(fill='x', pady=5)
            self.docked_widgets['left'].append(frame)
        elif dock_side == 'right':
            frame = DashboardFrame(self.docks['right']['content'], self, widget_id, widget_info_from_api["name"], WidgetClass, content_widget_id=widget_type_key, is_docked=True)
            frame.pack(fill='both', expand=True, pady=5)
            self.docked_widgets['right'].append(frame)
        else:
            is_docked = (widget_type_key == 'canvas_area')
            frame = DashboardFrame(self.canvas_area, self, widget_id, widget_info_from_api["name"], WidgetClass, content_widget_id=widget_type_key, is_docked=is_docked)
            if widget_type_key == 'canvas_area':
                frame.place(x=0, y=0, relwidth=1, relheight=1)
            else:
                frame.place(x=x, y=y, width=width, height=height)
        self.widgets[widget_id] = frame
        if hasattr(frame.content_widget, 'on_widget_load'):
            frame.content_widget.on_widget_load()
        if widget_type_key == 'canvas_area':
            self.coordinator_tab.canvas_area_instance = frame.content_widget
    def remove_widget(self, widget_id):
        if widget_id in self.widgets:
            frame_to_remove = self.widgets[widget_id]
            widget_type_key = frame_to_remove.content_widget.widget_id
            if self.coordinator_tab.canvas_area_instance == frame_to_remove.content_widget:
                self.coordinator_tab.canvas_area_instance = None
            if hasattr(frame_to_remove.content_widget, 'on_widget_destroy'):
                frame_to_remove.content_widget.on_widget_destroy()
            if frame_to_remove in self.docked_widgets['left']:
                self.docked_widgets['left'].remove(frame_to_remove)
            if frame_to_remove in self.docked_widgets['right']:
                self.docked_widgets['right'].remove(frame_to_remove)
            frame_to_remove.destroy()
            del self.widgets[widget_id]
            if not self.widgets:
                self._create_watermark()
    def start_drag(self, widget, event):
        if not widget.is_docked:
            widget.lift()
            self._drag_data['widget'] = widget
            self._drag_data['x'] = event.x
            self._drag_data['y'] = event.y
    def drag_widget(self, event):
        if self._drag_data['widget']:
            dx = event.x - self._drag_data['x']
            dy = event.y - self._drag_data['y']
            x = self._drag_data['widget'].winfo_x() + dx
            y = self._drag_data['widget'].winfo_y() + dy
            self._drag_data['widget'].place(x=x, y=y)
    def stop_drag(self, event):
        self._drag_data['widget'] = None
        self.save_layout()
    def start_resize(self, widget, event):
        self._resize_data['widget'] = widget
        self._resize_data['start_x'] = event.x_root
        self._resize_data['start_y'] = event.y_root
        self._resize_data['start_width'] = widget.winfo_width()
        self._resize_data['start_height'] = widget.winfo_height()
    def resize_widget(self, event):
        if self._resize_data['widget']:
            dx = event.x_root - self._resize_data['start_x']
            dy = event.y_root - self._resize_data['start_y']
            new_width = self._resize_data['start_width'] + dx
            new_height = self._resize_data['start_height'] + dy
            if new_width > 150 and new_height > 100:
                self._resize_data['widget'].place(width=new_width, height=new_height)
    def stop_resize(self, event):
        self._resize_data['widget'] = None
        self.save_layout()
    def _create_add_widget_menu(self, event_x=10, event_y=10):
        context_menu = Menu(self.canvas_area, tearoff=0)
        sorted_widgets = sorted(self.available_widgets_from_api.items(), key=lambda item: item[1]['name'].lower())
        dock_exclusive_widgets = {"logic_toolbox_widget", "plugin_toolbox_widget", "widget_toolbox", "log_viewer_widget"}
        has_addable_widgets = False
        for key, info in sorted_widgets:
            if key not in dock_exclusive_widgets:
                context_menu.add_command(label=info['name'], command=lambda k=key, x=event_x, y=event_y: self.add_widget_and_save(k, x=x, y=y))
                has_addable_widgets = True
        if not has_addable_widgets:
            context_menu.add_command(label="No non-dockable widgets available", state="disabled")
        return context_menu
    def show_context_menu(self, event):
        context_menu = self._create_add_widget_menu(event_x=event.x, event_y=event.y)
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    def add_widget_and_save(self, widget_type_key, x=0, y=0, dock_side=None):
        self.add_widget(widget_type_key, x, y, dock_side=dock_side)
        self.save_layout()

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\dashboard_tab.py
# JUMLAH BARIS : 39
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\dashboard_tab.py
# JUMLAH BARIS : 38
#######################################################################

import ttkbootstrap as ttk
from flowork_gui.api_client.client import ApiClient
class DashboardTab(ttk.Frame):
    """
    Frame untuk Dashboard. Sekarang berisi pengalih bahasa.
    """
    def __init__(self, parent_notebook, kernel_instance):
        self.api_client = ApiClient()
        super().__init__(parent_notebook, style='TFrame')
        self.kernel = kernel_instance
        self.loc = self.kernel.loc
        container = ttk.Frame(self, style='TFrame', padding=20)
        container.pack(expand=True, fill='both', anchor='n')
        lang_frame = ttk.Frame(container, style='TFrame')
        lang_frame.pack(pady=10, anchor='w')
        lang_label = ttk.Label(lang_frame, text="Pilih Bahasa:", font=("Helvetica", 11, "bold"))
        lang_label.pack(side='left', padx=(0, 10))
        self.lang_combobox = ttk.Combobox(
            lang_frame,
            values=["id", "en"],
            state="readonly"
        )
        self.lang_combobox.set(self.loc.current_lang)
        self.lang_combobox.pack(side='left')
        self.lang_combobox.bind("<<ComboboxSelected>>", self.change_language)
    def change_language(self, event=None):
        """Memuat bahasa baru dan memuat ulang UI."""
        selected_lang = self.lang_combobox.get()
        print(f"Bahasa diubah ke: {selected_lang}")
        self.kernel.loc.load_language(selected_lang)
        self.kernel.reload_ui()

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\main_window.py
# JUMLAH BARIS : 9
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\main_window.py
# JUMLAH BARIS : 7
#######################################################################



```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\node_properties_popup.py
# JUMLAH BARIS : 65
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\node_properties_popup.py
# JUMLAH BARIS : 64
#######################################################################

import ttkbootstrap as ttk
from tkinter import simpledialog
from flowork_gui.api_client.client import ApiClient
class NodePropertiesPopup(ttk.Toplevel):
    """
    Jendela popup generik untuk menampilkan properti node.
    Popup ini akan dibuat dan dikelola oleh PropertiesManager.
    """
    def __init__(self, parent, kernel, node_id, module_instance, get_config_func, save_config_func, available_vars):
        self.api_client = ApiClient()
        super().__init__(parent)
        self.kernel = kernel
        self.loc = self.kernel.loc
        self.node_id = node_id
        self.module_instance = module_instance
        self.get_config_func = get_config_func
        self.save_config_func = save_config_func
        self.available_vars = available_vars
        self.property_vars = {}
        self.title(self.loc.get('properties_title', fallback="Properti Node") + f" ({node_id})")
        self.transient(parent)
        self.grab_set()
        self.main_frame = ttk.Frame(self, padding=15)
        self.main_frame.pack(fill="both", expand=True)
        self._build_ui()
        self.wait_window(self)
    def _build_ui(self):
        """Membangun antarmuka pengguna untuk jendela properti."""
        content_frame = ttk.Frame(self.main_frame, style='TFrame')
        content_frame.pack(fill="both", expand=True)
        if hasattr(self.module_instance, 'create_properties_ui'):
            self.property_vars = self.module_instance.create_properties_ui(
                parent_frame=content_frame,
                get_current_config=self.get_config_func,
                available_vars=self.available_vars
            )
        else:
            ttk.Label(content_frame, text="Modul ini tidak memiliki properti yang bisa diatur.").pack(pady=20)
        action_buttons_frame = ttk.Frame(self.main_frame, style='TFrame')
        action_buttons_frame.pack(side="bottom", fill="x", pady=(10, 0), padx=5)
        save_button = ttk.Button(action_buttons_frame, text=self.loc.get("button_save", fallback="Simpan"), command=self._save_and_close, bootstyle="success")
        save_button.pack(side="right", padx=5, pady=5)
        cancel_button = ttk.Button(action_buttons_frame, text=self.loc.get("button_cancel", fallback="Batal"), command=self.destroy, bootstyle="secondary")
        cancel_button.pack(side="right", padx=5, pady=5)
    def _save_and_close(self):
        """Menyimpan konfigurasi dan menutup jendela."""
        new_config = {}
        for key, var in self.property_vars.items():
            try:
                if hasattr(var, 'get_value'): # Ini adalah EnumVarWrapper
                    new_config[key] = var.get_value()
                else: # Variabel Tkinter biasa
                    new_config[key] = var.get()
            except Exception as e:
                self.kernel.write_to_log(f"Gagal mendapatkan nilai untuk properti '{key}': {e}", "WARN")
        self.save_config_func(new_config)
        self.destroy()

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\properties_popup.py
# JUMLAH BARIS : 121
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\properties_popup.py
# JUMLAH BARIS : 120
#######################################################################

import ttkbootstrap as ttk
from tkinter import Text, TclError, Listbox
from flowork_kernel.api_contract import EnumVarWrapper, IDynamicOutputSchema # (PENAMBAHAN) Import kontrak baru
from flowork_gui.api_client.client import ApiClient
class PropertiesPopup(ttk.Toplevel):
    def __init__(self, parent_canvas_manager, node_id):
        super().__init__(parent_canvas_manager.coordinator_tab)
        self.canvas_manager = parent_canvas_manager
        self.parent_tab = parent_canvas_manager.coordinator_tab
        self.kernel = self.parent_tab.kernel
        self.loc = self.kernel.get_service("localization_manager")
        self.api_client = ApiClient(kernel=self.kernel)
        self.node_id = node_id
        self.property_vars = {}
        self.dynamic_widgets = {}
        node_data = self.canvas_manager.canvas_nodes.get(self.node_id)
        if not node_data:
            self.destroy()
            return
        node_name = node_data.get('name', 'Unknown')
        self.title(f"{self.loc.get('properties_title')} - {node_name}")
        self.geometry("450x700")
        self.transient(self.parent_tab.winfo_toplevel())
        self.grab_set()
        self._create_widgets()
    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(expand=True, fill="both")
        top_static_frame = ttk.Frame(main_frame)
        top_static_frame.pack(side="top", fill="x", expand=False)
        button_frame = ttk.Frame(self)
        button_frame.pack(side="bottom", fill="x", padx=15, pady=(5, 15))
        self.save_button = ttk.Button(button_frame, text=self.loc.get('save_changes_button'), command=self._save_changes, bootstyle="success.TButton")
        self.save_button.pack(side="right")
        ttk.Button(button_frame, text=self.loc.get('button_cancel', fallback="Cancel"), command=self.destroy, bootstyle="secondary.TButton").pack(side="right", padx=(0, 10))
        scroll_container = ttk.Frame(main_frame)
        scroll_container.pack(side="top", fill="both", expand=True, pady=(10,0))
        scroll_canvas = ttk.Canvas(scroll_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=scroll_canvas.yview)
        self.scrollable_frame = ttk.Frame(scroll_canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all")))
        scroll_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        scroll_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self._populate_static_content(top_static_frame)
        self._populate_scrollable_content(self.scrollable_frame)
    def _populate_static_content(self, parent_frame):
        style = ttk.Style()
        theme_manager = self.kernel.get_service("theme_manager")
        colors = theme_manager.get_colors() if theme_manager else {}
        style.configure('Readonly.TEntry', fieldbackground=colors.get('dark', '#333333'), insertwidth=0)
        style.map('Readonly.TEntry', foreground=[('readonly', colors.get('light', '#ffffff'))], fieldbackground=[('readonly', colors.get('dark', '#333333'))])
        id_input_frame = ttk.Frame(parent_frame)
        id_input_frame.pack(fill='x', expand=True)
        ttk.Label(id_input_frame, text=self.loc.get('node_id_label', fallback="Node ID:")).pack(fill='x', anchor='w')
        id_entry_frame = ttk.Frame(id_input_frame)
        id_entry_frame.pack(fill='x', expand=True, pady=(2,0))
        node_id_var = ttk.StringVar(value=self.node_id)
        id_entry = ttk.Entry(id_entry_frame, textvariable=node_id_var, state="readonly", style='Readonly.TEntry')
        id_entry.pack(side='left', fill='x', expand=True)
        copy_button = ttk.Button(id_entry_frame, text=self.loc.get('copy_id_button', fallback="Copy ID"), command=self._copy_node_id, style="info.Outline.TButton")
        copy_button.pack(side='left', padx=(5,0))
        ttk.Separator(parent_frame).pack(fill='x', pady=(15, 0))
    def _populate_scrollable_content(self, parent_frame):
        node_data = self.canvas_manager.canvas_nodes.get(self.node_id)
        ttk.Label(parent_frame, text=self.loc.get('module_name_label')).pack(fill='x', padx=5, pady=(5,0))
        self.property_vars['name'] = ttk.StringVar(value=node_data['name'])
        ttk.Entry(parent_frame, textvariable=self.property_vars['name']).pack(fill='x', padx=5, pady=(0, 10))
        ttk.Label(parent_frame, text=self.loc.get('description_label')).pack(fill='x', padx=5, pady=(5,0))
        desc_text = Text(parent_frame, height=3, font=("Helvetica", 9))
        desc_text.pack(fill='x', expand=True, padx=5, pady=(0, 10))
        desc_text.insert('1.0', node_data.get('description', ''))
        self.property_vars['description'] = desc_text
        ttk.Separator(parent_frame).pack(fill='x', pady=10, padx=5)
        module_manager = self.kernel.get_service("module_manager_service")
        module_instance = module_manager.get_instance(node_data['module_id']) if module_manager else None
        if module_instance and hasattr(module_instance, 'create_properties_ui'):
            get_current_config = lambda: self.canvas_manager.canvas_nodes.get(self.node_id, {}).get('config_values', {})
            available_vars_for_module = self._get_incoming_variables()
            returned_vars = module_instance.create_properties_ui(parent_frame, get_current_config, available_vars_for_module)
            if returned_vars: self.property_vars.update(returned_vars)
    def _get_incoming_variables(self):
        incoming_vars = {}
        module_manager = self.kernel.get_service("module_manager_service")
        if not module_manager: return {}
        for conn in self.canvas_manager.canvas_connections.values():
            if conn['to'] == self.node_id:
                from_node_data = self.canvas_manager.canvas_nodes.get(conn['from'])
                if from_node_data:
                    from_module_id = from_node_data['module_id']
                    from_module_instance = module_manager.get_instance(from_module_id)
                    from_module_config = from_node_data.get('config_values', {})
                    if from_module_instance and isinstance(from_module_instance, IDynamicOutputSchema):
                        self.kernel.write_to_log(f"Fetching dynamic schema from '{from_module_id}'", "DEBUG")
                        dynamic_schema = from_module_instance.get_dynamic_output_schema(from_module_config)
                        for var_info in dynamic_schema:
                            incoming_vars[var_info['name']] = var_info.get('description', '')
                    from_node_manifest = module_manager.get_manifest(from_module_id)
                    if from_node_manifest and 'output_schema' in from_node_manifest:
                        for var_info in from_node_manifest['output_schema']:
                            if var_info['name'] not in incoming_vars: # (COMMENT) Avoid duplicates
                                incoming_vars[var_info['name']] = var_info.get('description', '')
        if 'data' not in incoming_vars: incoming_vars['data'] = "Main payload data (dictionary)."
        if 'history' not in incoming_vars: incoming_vars['history'] = "Payload history (list)."
        return {k: incoming_vars[k] for k in sorted(incoming_vars.keys())}
    def _copy_node_id(self):
        self.clipboard_clear()
        self.clipboard_append(self.node_id)
        self.kernel.write_to_log(f"Node ID '{self.node_id}' copied to clipboard.", "INFO")
    def _save_changes(self):
        self.canvas_manager.properties_manager.save_node_properties(self.node_id, self.property_vars, self)
        self.destroy()

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\shared_properties.py
# JUMLAH BARIS : 157
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\shared_properties.py
# JUMLAH BARIS : 156
#######################################################################

import ttkbootstrap as ttk
from tkinter import Text, StringVar, BooleanVar, IntVar, TclError
from flowork_kernel.api_contract import LoopConfig
from flowork_kernel.ui_shell.custom_widgets.tooltip import ToolTip
from flowork_gui.api_client.client import ApiClient
def create_debug_and_reliability_ui(parent, config, loc):
    """
    Membuat bagian UI untuk pengaturan Debug (breakpoint, timeout) dan Keandalan (retry).
    """
    created_vars = {}
    debug_frame = ttk.LabelFrame(parent, text=loc.get('debug_settings_title', fallback="Pengaturan Debug & Keandalan"))
    debug_frame.pack(fill='x', padx=5, pady=10, expand=False)
    created_vars['has_breakpoint'] = ttk.BooleanVar(value=config.get('has_breakpoint', False))
    bp_check = ttk.Checkbutton(debug_frame, text=loc.get('set_breakpoint_checkbox', fallback="Set Breakpoint di Node Ini"), variable=created_vars['has_breakpoint'])
    bp_check.pack(anchor='w', pady=5, padx=10)
    ToolTip(bp_check).update_text(loc.get('set_breakpoint_tooltip'))
    timeout_frame = ttk.Frame(debug_frame)
    timeout_frame.pack(fill='x', padx=10, pady=(5,5))
    ttk.Label(timeout_frame, text=loc.get('execution_timeout_label')).pack(side='left', anchor='w')
    created_vars['timeout_seconds'] = ttk.IntVar(value=config.get('timeout_seconds', 0))
    timeout_entry = ttk.Entry(timeout_frame, textvariable=created_vars['timeout_seconds'], width=8)
    timeout_entry.pack(side='left', padx=5)
    ToolTip(timeout_entry).update_text(loc.get('execution_timeout_tooltip'))
    ttk.Separator(debug_frame).pack(fill='x', pady=5)
    retry_title_label = ttk.Label(debug_frame, text=loc.get('retry_settings_title'))
    retry_title_label.pack(anchor='w', padx=10, pady=(10,0))
    retry_frame = ttk.Frame(debug_frame)
    retry_frame.pack(fill='x', padx=10, pady=(5,10))
    ttk.Label(retry_frame, text=loc.get('retry_attempts_label')).pack(side='left', anchor='w')
    created_vars['retry_attempts'] = ttk.IntVar(value=config.get('retry_attempts', 0))
    retry_attempts_entry = ttk.Entry(retry_frame, textvariable=created_vars['retry_attempts'], width=5)
    retry_attempts_entry.pack(side='left', padx=5)
    ToolTip(retry_attempts_entry).update_text(loc.get('retry_attempts_tooltip'))
    ttk.Label(retry_frame, text=loc.get('retry_delay_label')).pack(side='left', padx=10, anchor='w')
    created_vars['retry_delay_seconds'] = ttk.IntVar(value=config.get('retry_delay_seconds', 5))
    retry_delay_entry = ttk.Entry(retry_frame, textvariable=created_vars['retry_delay_seconds'], width=5)
    retry_delay_entry.pack(side='left', padx=5)
    ToolTip(retry_delay_entry).update_text(loc.get('retry_delay_tooltip'))
    ttk.Separator(debug_frame).pack(fill='x', pady=5)
    checkpoint_title_label = ttk.Label(debug_frame, text=loc.get('checkpoint_settings_title'))
    checkpoint_title_label.pack(anchor='w', padx=10, pady=(10,0))
    created_vars['is_checkpoint'] = ttk.BooleanVar(value=config.get('is_checkpoint', False))
    checkpoint_check = ttk.Checkbutton(debug_frame, text=loc.get('enable_checkpoint_checkbox'), variable=created_vars['is_checkpoint'])
    checkpoint_check.pack(anchor='w', pady=5, padx=10)
    ToolTip(checkpoint_check).update_text(loc.get('checkpoint_tooltip'))
    return created_vars
def create_loop_settings_ui(parent, config, loc, available_vars):
    """
    Membuat bagian UI untuk pengaturan Looping dan Jeda (Sleep).
    """
    created_vars = {}
    loop_frame = ttk.LabelFrame(parent, text=loc.get('loop_settings_title', fallback="Pengaturan Looping"))
    loop_frame.pack(fill='x', padx=5, pady=10, expand=False)
    created_vars['enable_loop'] = ttk.BooleanVar(value=config.get('enable_loop', False))
    enable_loop_check = ttk.Checkbutton(loop_frame, text=loc.get('enable_loop_checkbox', fallback="Aktifkan Looping"), variable=created_vars['enable_loop'])
    enable_loop_check.pack(anchor='w', padx=5)
    loop_options_frame = ttk.Frame(loop_frame)
    created_vars['loop_type'] = ttk.StringVar(value=config.get('loop_type', LoopConfig.LOOP_TYPE_COUNT))
    count_details_frame = ttk.Frame(loop_options_frame)
    condition_details_frame = ttk.Frame(loop_options_frame)
    count_radio = ttk.Radiobutton(loop_options_frame, text=loc.get('loop_type_count_radio', fallback="Ulangi N Kali"), variable=created_vars['loop_type'], value=LoopConfig.LOOP_TYPE_COUNT)
    count_radio.pack(anchor='w')
    count_details_frame.pack(fill='x', anchor='w', padx=20, pady=2)
    created_vars['loop_iterations'] = ttk.IntVar(value=config.get('loop_iterations', 1))
    count_entry = ttk.Entry(count_details_frame, textvariable=created_vars['loop_iterations'], width=10)
    count_entry.pack(anchor='w')
    ToolTip(count_entry).update_text(loc.get('loop_iterations_tooltip', fallback="Jumlah iterasi loop."))
    condition_radio = ttk.Radiobutton(loop_options_frame, text=loc.get('loop_type_condition_radio', fallback="Ulangi Sampai Kondisi"), variable=created_vars['loop_type'], value=LoopConfig.LOOP_TYPE_CONDITION)
    condition_radio.pack(anchor='w', pady=(10,0))
    condition_details_frame.pack(fill='x', padx=20, pady=5)
    ttk.Label(condition_details_frame, text=loc.get('condition_var_label', fallback="Variabel Kondisi:")).pack(side='left', padx=(0,5))
    created_vars['loop_condition_var'] = ttk.StringVar(value=config.get('loop_condition_var', ''))
    loop_condition_var_combobox = ttk.Combobox(condition_details_frame, textvariable=created_vars['loop_condition_var'], values=list(available_vars.keys()), state="readonly")
    loop_condition_var_combobox.pack(side='left', expand=True, fill='x', padx=(0,5))
    ToolTip(loop_condition_var_combobox).update_text(loc.get('condition_var_tooltip', fallback="Variabel DataPayload yang akan dievaluasi."))
    created_vars['loop_condition_op'] = ttk.StringVar(value=config.get('loop_condition_op', '=='))
    all_operators = ['==', '!=', '>', '<', '>=', '<=', loc.get('operator_contains_text'), loc.get('operator_not_contains_text'), loc.get('operator_starts_with'), loc.get('operator_ends_with')]
    ttk.Combobox(condition_details_frame, textvariable=created_vars['loop_condition_op'], values=all_operators, state="readonly", width=15).pack(side='left', padx=(0,5))
    created_vars['loop_condition_val'] = ttk.StringVar(value=config.get('loop_condition_val', ''))
    condition_val_entry = ttk.Entry(condition_details_frame, textvariable=created_vars['loop_condition_val'])
    condition_val_entry.pack(side='left', expand=True, fill='x')
    ToolTip(condition_val_entry).update_text(loc.get('condition_val_tooltip', fallback="Nilai untuk dibandingkan."))
    ttk.Separator(loop_frame).pack(fill='x', pady=10, padx=5)
    sleep_control_frame = ttk.Frame(loop_frame)
    created_vars['enable_sleep'] = ttk.BooleanVar(value=config.get('enable_sleep', False))
    sleep_options_frame = ttk.Frame(sleep_control_frame)
    static_sleep_frame = ttk.Frame(sleep_options_frame)
    random_sleep_details_frame = ttk.Frame(sleep_options_frame)
    ttk.Checkbutton(sleep_control_frame, text=loc.get('enable_sleep_checkbox', fallback="Aktifkan Jeda Antar Iterasi"), variable=created_vars['enable_sleep']).pack(anchor='w', pady=5, padx=10)
    created_vars['sleep_type'] = ttk.StringVar(value=config.get('sleep_type', 'static'))
    static_radio = ttk.Radiobutton(sleep_options_frame, text=loc.get('sleep_type_static_radio', fallback="Jeda Statis (detik)"), variable=created_vars['sleep_type'], value="static")
    static_radio.pack(anchor='w')
    static_sleep_frame.pack(anchor='w', padx=20, pady=2)
    created_vars['static_duration'] = ttk.IntVar(value=config.get('static_duration', 1))
    static_duration_entry = ttk.Entry(static_sleep_frame, textvariable=created_vars['static_duration'], width=10)
    static_duration_entry.pack(anchor='w')
    ToolTip(static_duration_entry).update_text(loc.get('static_duration_tooltip', fallback="Durasi jeda dalam detik."))
    random_radio = ttk.Radiobutton(sleep_options_frame, text=loc.get('sleep_type_random_radio', fallback="Jeda Acak (detik)"), variable=created_vars['sleep_type'], value="random_range")
    random_radio.pack(anchor='w', pady=(10,0))
    random_sleep_details_frame.pack(fill='x', padx=20, pady=5)
    ttk.Label(random_sleep_details_frame, text=loc.get('random_min_label', fallback="Min:")).pack(side='left', padx=(0,5))
    created_vars['random_min'] = ttk.IntVar(value=config.get('random_min', 1))
    random_min_entry = ttk.Entry(random_sleep_details_frame, textvariable=created_vars['random_min'], width=5)
    random_min_entry.pack(side='left', padx=(0,5))
    ToolTip(random_min_entry).update_text(loc.get('random_min_tooltip', fallback="Durasi jeda minimum (detik)."))
    ttk.Label(random_sleep_details_frame, text=loc.get('random_max_label', fallback="Max:")).pack(side='left', padx=(0,5))
    created_vars['random_max'] = ttk.IntVar(value=config.get('random_max', 5))
    random_max_entry = ttk.Entry(random_sleep_details_frame, textvariable=created_vars['random_max'], width=5)
    random_max_entry.pack(side='left', padx=(0,5))
    ToolTip(random_max_entry).update_text(loc.get('random_max_tooltip', fallback="Durasi jeda maksimum (detik)."))
    def _toggle_sleep_details():
        is_static = created_vars['sleep_type'].get() == "static"
        if is_static:
            static_sleep_frame.pack(anchor='w', padx=20, pady=2)
            random_sleep_details_frame.pack_forget()
        else:
            static_sleep_frame.pack_forget()
            random_sleep_details_frame.pack(fill='x', padx=20, pady=5)
    def _toggle_sleep_options():
        if created_vars['enable_sleep'].get():
            sleep_options_frame.pack(fill='x', padx=10, pady=5)
            _toggle_sleep_details()
        else:
            sleep_options_frame.pack_forget()
    def _toggle_loop_details():
        is_count = created_vars['loop_type'].get() == LoopConfig.LOOP_TYPE_COUNT
        if is_count:
            count_details_frame.pack(fill='x', anchor='w', padx=20, pady=2)
            condition_details_frame.pack_forget()
        else:
            count_details_frame.pack_forget()
            condition_details_frame.pack(fill='x', padx=20, pady=5)
    def _toggle_loop_options():
        if created_vars['enable_loop'].get():
            loop_options_frame.pack(fill='x', padx=10, pady=5)
            sleep_control_frame.pack(fill='x', padx=0, pady=0)
            _toggle_loop_details()
            _toggle_sleep_options()
        else:
            loop_options_frame.pack_forget()
            sleep_control_frame.pack_forget()
    enable_loop_check.config(command=_toggle_loop_options)
    static_radio.config(command=_toggle_sleep_details)
    random_radio.config(command=_toggle_sleep_details)
    created_vars['enable_sleep'].trace_add('write', lambda *args: _toggle_sleep_options())
    count_radio.config(command=_toggle_loop_details)
    condition_radio.config(command=_toggle_loop_details)
    _toggle_loop_options()
    return created_vars

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\version_manager_popup.py
# JUMLAH BARIS : 117
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\version_manager_popup.py
# JUMLAH BARIS : 116
#######################################################################

import ttkbootstrap as ttk
from tkinter import Toplevel, messagebox, ttk as tk_ttk, Menu
from flowork_gui.api_client.client import ApiClient
class VersionManagerPopup(Toplevel):
    def __init__(self, parent_workflow_tab, kernel_instance, preset_name):
        super().__init__(parent_workflow_tab)
        self.parent_workflow_tab = parent_workflow_tab
        self.kernel = kernel_instance
        self.loc = self.kernel.get_service("localization_manager")
        self.preset_name = preset_name
        self.api_client = ApiClient(kernel=self.kernel)
        self.title(self.loc.get('version_manager_title', preset_name=self.preset_name))
        self.transient(parent_workflow_tab)
        self.grab_set()
        self.resizable(False, False)
        theme_manager = self.kernel.get_service("theme_manager")
        self.colors = theme_manager.get_colors() if theme_manager else {}
        self.apply_styles(self.colors)
        self.create_widgets()
        self.populate_versions()
        self.update_idletasks()
        x = parent_workflow_tab.winfo_x() + (parent_workflow_tab.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent_workflow_tab.winfo_y() + (parent_workflow_tab.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    def apply_styles(self, colors):
        style = tk_ttk.Style(self)
        style.configure('TFrame', background=colors.get('bg'))
        style.configure('TLabel', background=colors.get('bg'), foreground=colors.get('fg'))
        style.configure("Custom.Treeview", background=colors.get('dark'), foreground=colors.get('fg'), fieldbackground=colors.get('dark'), borderwidth=0, rowheight=25)
        style.configure("Custom.Treeview.Heading", background=colors.get('bg'), foreground=colors.get('info'), font=('Helvetica', 10, 'bold'))
        style.map('Custom.Treeview', background=[('selected', colors.get('selectbg'))], foreground=[('selected', colors.get('selectfg'))])
        self.configure(background=colors.get('bg'))
    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=15, style='TFrame')
        main_frame.pack(fill='both', expand=True)
        ttk.Label(main_frame, text=self.loc.get('version_list_label'), style='TLabel').pack(anchor='w', pady=(0, 5))
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill='both', expand=True, pady=(0, 10))
        columns = ("Nama Versi", "Tanggal & Waktu", "Aksi")
        self.version_tree = tk_ttk.Treeview(tree_frame, columns=columns, show="headings", style="Custom.Treeview")
        self.version_tree.heading("Nama Versi", text=self.loc.get('version_name_column', fallback="Version Name"))
        self.version_tree.heading("Tanggal & Waktu", text=self.loc.get('version_datetime_column', fallback="Date & Time"))
        self.version_tree.heading("Aksi", text=self.loc.get('version_actions_column', fallback="Actions"))
        self.version_tree.column("Nama Versi", width=250, anchor='w')
        self.version_tree.column("Tanggal & Waktu", width=150, anchor='center')
        self.version_tree.column("Aksi", width=120, anchor='center')
        tree_scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.version_tree.yview)
        self.version_tree.configure(yscrollcommand=tree_scrollbar_y.set)
        self.version_tree.pack(side='left', fill='both', expand=True)
        tree_scrollbar_y.pack(side='right', fill='y')
        self.version_tree.bind("<Button-1>", self._on_tree_click)
        button_frame = ttk.Frame(main_frame, style='TFrame')
        button_frame.pack(fill='x', side='bottom', pady=(5, 0))
        ttk.Button(button_frame, text=self.loc.get('button_close', fallback="Close"), command=self.destroy, style='secondary.TButton').pack(side='right')
    def populate_versions(self):
        for item in self.version_tree.get_children():
            self.version_tree.delete(item)
        self.kernel.write_to_log(f"UI: Requesting versions for '{self.preset_name}' via API.", "DEBUG")
        success, versions = self.api_client.get_preset_versions(self.preset_name)
        if not versions or not success:
            self.version_tree.insert("", "end", values=(self.loc.get('no_versions_found'), "", ""), tags=("no_data",))
            return
        for version_info in versions:
            version_display_name = self.loc.get('version_name_format', timestamp=version_info['timestamp'])
            action_placeholder = self.loc.get('version_action_column_placeholder', fallback="Click for Actions...")
            self.version_tree.insert("", "end", values=(version_display_name, version_info['timestamp'], action_placeholder), tags=(version_info['filename'],))
    def _on_tree_click(self, event):
        region = self.version_tree.identify_region(event.x, event.y)
        column_id = self.version_tree.identify_column(event.x)
        if region == "cell" and column_id == "#3":
            item_id = self.version_tree.identify_row(event.y)
            if not item_id: return
            version_filename = self.version_tree.item(item_id, "tags")[0]
            if version_filename == "no_data": return
            self._show_action_menu(event, version_filename)
    def _show_action_menu(self, event, version_filename):
        context_menu = Menu(self, tearoff=0)
        context_menu.add_command(label=self.loc.get('version_action_load'), command=lambda: self._load_selected_version(version_filename))
        context_menu.add_command(label=self.loc.get('version_action_delete'), command=lambda: self._delete_selected_version(version_filename))
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    def _load_selected_version(self, version_filename):
        if not messagebox.askyesno(
            self.loc.get('confirm_load_version_title', fallback="Load Version?"),
            self.loc.get('confirm_load_version_message', version_name=version_filename, preset_name=self.preset_name)
        ):
            return
        self.kernel.write_to_log(self.loc.get('log_loading_version', preset_name=self.preset_name, version_name=version_filename), "INFO")
        success, workflow_data = self.api_client.load_preset_version(self.preset_name, version_filename)
        if success and workflow_data:
            self.parent_workflow_tab.canvas_area_instance.canvas_manager.load_workflow_data(workflow_data)
            messagebox.showinfo(self.loc.get('success_title'), self.loc.get('log_version_loaded_success', preset_name=self.preset_name, version_name=version_filename))
            self.destroy()
        else:
            messagebox.showerror(self.loc.get('error_title'), self.loc.get('log_version_load_error', preset_name=self.preset_name, version_name=version_filename, error="Failed to load version file via API."))
    def _delete_selected_version(self, version_filename):
        if not messagebox.askyesno(
            self.loc.get('confirm_delete_version_title'),
            self.loc.get('confirm_delete_version_message', version_name=version_filename)
        ):
            return
        success, response = self.api_client.delete_preset_version(self.preset_name, version_filename)
        if success:
            messagebox.showinfo(self.loc.get('success_title'), self.loc.get('log_version_deleted_success', preset_name=self.preset_name, version_name=version_filename))
            self.populate_versions()
        else:
            messagebox.showerror(self.loc.get('error_title'), self.loc.get('log_version_delete_error', preset_name=self.preset_name, version_name=version_filename, error=response))

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\workflow_editor_tab.py
# JUMLAH BARIS : 102
#######################################################################

```py
import ttkbootstrap as ttk
from tkinter import messagebox
import json
import uuid

# MODIFIED: Corrected all imports to be relative to the project root, not the forbidden flowork_kernel.
from .canvas_manager import CanvasManager
from views.ui_components.controllers.TabActionHandler import TabActionHandler

class WorkflowEditorTab(ttk.Frame):
    """
    The main tab for creating and editing workflows.
    This is the core user-facing component for the visual editor.
    """
    def __init__(self, parent_notebook, tab_id, api_client, loc, is_new=True, preset_name=None):
        super().__init__(parent_notebook, padding=0)
        self.parent_notebook = parent_notebook
        self.tab_id = tab_id
        self.api_client = api_client
        self.loc = loc
        self.is_new = is_new
        self.preset_name = preset_name
        self.kernel_surrogate = self._create_kernel_surrogate() # ADDED
        self._content_initialized = False

        # COMMENT: Content is now loaded lazily when the tab is first viewed.
        self.bind("<Visibility>", self._on_first_visibility)

    def _on_first_visibility(self, event):
        """Callback to initialize the heavy UI components only when the tab becomes visible."""
        if not self._content_initialized:
            self.parent_notebook.config(cursor="watch")
            self.update_idletasks()
            self._initialize_content()
            self._content_initialized = True
            self.parent_notebook.config(cursor="")
            self.unbind("<Visibility>") # Only run once

    def _initialize_content(self):
        """Builds the actual UI components of the tab."""
        self.action_handler = TabActionHandler(self, self.api_client, self.loc)

        # Main Paned Window
        main_pane = ttk.PanedWindow(self, orient='horizontal')
        main_pane.pack(fill='both', expand=True)

        # Left Pane for Toolbox
        left_pane_container = ttk.Frame(main_pane, padding=0)
        main_pane.add(left_pane_container, weight=1)

        # Right Pane for Canvas and Properties
        right_pane = ttk.PanedWindow(main_pane, orient='vertical')
        main_pane.add(right_pane, weight=5)

        # Canvas Area
        self.canvas_area_instance = CanvasArea(right_pane, self.kernel_surrogate, self.loc)
        right_pane.add(self.canvas_area_instance, weight=3)

        # Properties/Log Area
        bottom_pane = ttk.Frame(right_pane, padding=0)
        right_pane.add(bottom_pane, weight=1)

        if self.preset_name:
            self.action_handler.load_workflow_by_name(self.preset_name)

    def _create_kernel_surrogate(self):
        """
        Creates a mock/surrogate kernel object that provides only the
        functionality the UI components are allowed to access (like services via API).
        This enforces the GUI-Kernel separation rule.
        """
        class KernelSurrogate:
            def __init__(self, api_client, loc):
                self.api_client = api_client
                self.loc = loc
                self.root = self # This might need to point to the actual root window.

            def get_service(self, service_name):
                # The GUI should not get services directly. It should use the API client.
                # This acts as a gateway.
                print(f"[GUI-KERNEL-BRIDGE] A component is requesting service: {service_name}") # English Log
                if service_name == "localization_manager":
                    return self.loc
                # Add other "safe" services here if absolutely necessary.
                return None

        return KernelSurrogate(self.api_client, self.loc)

    def run_on_ui_thread(self, func, *args):
        """Safely schedules a function to be run on the main UI thread."""
        self.after(0, func, *args)

class CanvasArea(ttk.Frame):
    """
    A dedicated frame to hold the workflow canvas and its related controls.
    """
    def __init__(self, parent, kernel_surrogate, loc):
        super().__init__(parent)
        self.kernel = kernel_surrogate
        self.loc = loc
        self.canvas_manager = CanvasManager(self, self.kernel, self.loc)
        self.canvas_manager.pack(fill='both', expand=True)
```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\canvas_components\connection_manager.py
# JUMLAH BARIS : 118
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\canvas_components\connection_manager.py
# JUMLAH BARIS : 117
#######################################################################

import uuid
from flowork_gui.api_client.client import ApiClient
class ConnectionManager:
    """
    Manages all aspects of connection lines on the canvas, including creation, deletion, and position updates.
    (MODIFIED) Now supports different connection types and dynamically finds port widget locations.
    (FIXED) Added update_idletasks() to ensure correct coordinates for placed port widgets.
    """
    def __init__(self, canvas_manager, kernel, canvas_widget):
        self.api_client = ApiClient()
        self.canvas_manager = canvas_manager
        self.kernel = kernel
        self.canvas = canvas_widget
        self.loc = self.kernel.get_service("localization_manager")
    def _get_port_widget_center(self, node_id, port_name, port_type):
        """(ADDED) Helper function to find the absolute center coordinates of any port widget."""
        node_data = self.canvas_manager.canvas_nodes.get(node_id)
        if not node_data: return None, None
        port_list_key = f"{port_type}_ports"
        port_list = node_data.get(port_list_key, [])
        port_widget = next((p['widget'] for p in port_list if p['name'] == port_name), None)
        if port_widget and port_widget.winfo_exists():
            self.canvas.update_idletasks()
            x = port_widget.winfo_rootx() - self.canvas.winfo_rootx() + (port_widget.winfo_width() / 2)
            y = port_widget.winfo_rooty() - self.canvas.winfo_rooty() + (port_widget.winfo_height() / 2)
            return x, y
        return None, None
    def create_connection(self, start_node_id, end_node_id, existing_id=None, source_port_name=None, connection_type='data', target_port_name=None):
        canvas_nodes = self.canvas_manager.canvas_nodes
        canvas_connections = self.canvas_manager.canvas_connections
        colors = self.canvas_manager.colors
        start_port_type = 'tool' if connection_type == 'tool' else 'output'
        start_x, start_y = self._get_port_widget_center(start_node_id, source_port_name, start_port_type)
        if start_x is None:
            start_widget = canvas_nodes[start_node_id]["widget"]
            start_x = start_widget.winfo_x() + start_widget.winfo_width()
            start_y = start_widget.winfo_y() + start_widget.winfo_height() / 2
        end_port_type = 'tool' if connection_type == 'tool' else 'input'
        end_x, end_y = self._get_port_widget_center(end_node_id, target_port_name, end_port_type)
        if end_x is None:
            end_widget = canvas_nodes[end_node_id]["widget"]
            end_x = end_widget.winfo_x()
            end_y = end_widget.winfo_y() + end_widget.winfo_height() / 2
        offset = abs(end_x - start_x) / 2
        control_x1 = start_x + offset
        control_y1 = start_y
        control_x2 = end_x - offset
        control_y2 = end_y
        line_style = {
            'fill': colors.get('info', '#17a2b8'),
            'width': 2,
            'dash': (6, 4),
            'smooth': True
        } if connection_type == 'tool' else {
            'fill': colors.get('success', '#28a745'),
            'width': 2,
            'smooth': True
        }
        line_id = self.canvas.create_line(start_x, start_y, control_x1, control_y1, control_x2, control_y2, end_x, end_y, tags=("connection_line",), **line_style)
        conn_id = existing_id or str(uuid.uuid4())
        canvas_connections[conn_id] = {
            "line_id": line_id,
            "from": start_node_id,
            "to": end_node_id,
            "source_port_name": source_port_name,
            "target_port_name": target_port_name,
            "type": connection_type
        }
        return conn_id
    def delete_connection(self, conn_id_to_delete, feedback=True):
        canvas_connections = self.canvas_manager.canvas_connections
        if conn_id_to_delete in canvas_connections:
            line_id = canvas_connections[conn_id_to_delete]['line_id']
            if self.canvas.find_withtag(line_id):
                self.canvas.delete(line_id)
            del canvas_connections[conn_id_to_delete]
            if feedback:
                self.kernel.write_to_log(self.loc.get('connection_deleted_success', conn_id=conn_id_to_delete), "INFO")
    def update_connections_for_node(self, node_id):
        canvas_nodes = self.canvas_manager.canvas_nodes
        canvas_connections = self.canvas_manager.canvas_connections
        connections_to_update = []
        for conn_id, conn_data in list(canvas_connections.items()):
            if conn_data["from"] == node_id or conn_data["to"] == node_id:
                connections_to_update.append((conn_id, conn_data))
        for conn_id, conn_data in connections_to_update:
            if conn_data["from"] in canvas_nodes and conn_data["to"] in canvas_nodes:
                self.delete_connection(conn_id, feedback=False)
                self.create_connection(
                    start_node_id=conn_data["from"],
                    end_node_id=conn_data["to"],
                    existing_id=conn_id,
                    source_port_name=conn_data.get("source_port_name"),
                    target_port_name=conn_data.get("target_port_name"),
                    connection_type=conn_data.get("type", 'data')
                )
            else:
                self.delete_connection(conn_id, feedback=False)
    def recreate_connections(self, connections_data):
        canvas_nodes = self.canvas_manager.canvas_nodes
        for conn_data in connections_data:
            if conn_data.get("from") in canvas_nodes and conn_data.get("to") in canvas_nodes:
                self.create_connection(
                    start_node_id=conn_data["from"],
                    end_node_id=conn_data["to"],
                    existing_id=conn_data.get("id"),
                    source_port_name=conn_data.get("source_port_name"),
                    target_port_name=conn_data.get("target_port_name"),
                    connection_type=conn_data.get("type", "data")
                )

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\canvas_components\interaction_manager.py
# JUMLAH BARIS : 87
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\canvas_components\interaction_manager.py
# JUMLAH BARIS : 86
#######################################################################

from tkinter import Menu
from ..properties_popup import PropertiesPopup
from .interactions.node_interaction_handler import NodeInteractionHandler
from .interactions.connection_interaction_handler import ConnectionInteractionHandler
from .interactions.canvas_navigation_handler import CanvasNavigationHandler
from flowork_gui.api_client.client import ApiClient
class InteractionManager:
    """
    Manages all user interactions with the canvas by coordinating specialized handlers.
    (FIXED) Now correctly resets the node handler's move data to the new format.
    """
    def __init__(self, canvas_manager, kernel, canvas_widget):
        self.api_client = ApiClient()
        self.canvas_manager = canvas_manager
        self.kernel = kernel
        self.canvas = canvas_widget
        self.loc = self.kernel.get_service("localization_manager")
        self.node_handler = NodeInteractionHandler(self.canvas_manager)
        self.connection_handler = ConnectionInteractionHandler(self.canvas_manager)
        self.navigation_handler = CanvasNavigationHandler(self.canvas_manager)
        self._drag_data = {}
        self._resize_data = {} # (COMMENT) Added missing initialization for resize data
    def bind_events(self):
        """Binds all canvas events to the appropriate specialized handlers."""
        self.canvas.bind("<Motion>", self.connection_handler.on_line_motion)
        self.canvas.tag_bind("connection_line", "<ButtonPress-3>", self.connection_handler.show_line_context_menu)
        self.canvas.bind("<ButtonPress-2>", self.navigation_handler.on_pan_start)
        self.canvas.bind("<B2-Motion>", self.navigation_handler.on_pan_move)
        self.canvas.bind("<ButtonRelease-2>", self.navigation_handler.on_pan_end)
        self.canvas.bind("<Delete>", self.node_handler.on_delete_key_press)
        self.canvas.bind("<ButtonPress-1>", self.canvas_manager.node_manager.deselect_all_nodes)
        self.canvas.bind("<ButtonPress-3>", self._handle_canvas_right_click)
    def _handle_canvas_right_click(self, event):
        """Decides whether to cancel line drawing or show the context menu."""
        if self.connection_handler._line_data.get("line_id"):
            self.connection_handler._cancel_line_drawing(event)
        else:
            self._show_canvas_context_menu(event)
    def _show_canvas_context_menu(self, event):
        """Displays the main canvas context menu for adding modules or text notes."""
        context_menu = Menu(self.canvas, tearoff=0)
        context_menu.add_command(
            label=self.loc.get('context_menu_add_note', fallback="Add Text Note"),
            command=lambda: self.canvas_manager.create_label(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        )
        context_menu.add_separator()
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    def on_drag_release(self, event, item_id, tree_widget):
        if item_id:
            x_root, y_root = event.x_root, event.y_root
            canvas_x0, canvas_y0 = self.canvas.winfo_rootx(), self.canvas.winfo_rooty()
            canvas_x1, canvas_y1 = canvas_x0 + self.canvas.winfo_width(), canvas_y0 + self.canvas.winfo_height()
            if canvas_x0 <= x_root <= canvas_x1 and canvas_y0 <= y_root <= canvas_y1:
                zoom_level = self.navigation_handler.zoom_level
                canvas_x = self.canvas.canvasx(x_root - canvas_x0)
                canvas_y = self.canvas.canvasy(y_root - canvas_y0)
                world_x = canvas_x / zoom_level
                world_y = canvas_y / zoom_level
                module_id = item_id
                module_manager = self.kernel.get_service("module_manager_service")
                if not module_manager: return
                manifest = module_manager.get_manifest(module_id)
                if manifest:
                    self.canvas_manager.node_manager.create_node_on_canvas(name=manifest.get('name', 'Unknown'), x=world_x, y=world_y, module_id=module_id)
            self._reset_all_actions()
    def _reset_all_actions(self):
        """Resets any ongoing user interaction state, like line drawing."""
        if hasattr(self.canvas_manager.coordinator_tab, 'unbind_all'):
            self.canvas_manager.coordinator_tab.unbind_all("<B1-Motion>")
            self.canvas_manager.coordinator_tab.unbind_all("<ButtonRelease-1>")
        if hasattr(self.canvas_manager.coordinator_tab, '_drag_data_toplevel'):
             if self.canvas_manager.coordinator_tab._drag_data_toplevel.get("widget") and self.canvas_manager.coordinator_tab._drag_data_toplevel["widget"].winfo_exists():
                self.canvas_manager.coordinator_tab._drag_data_toplevel["widget"].destroy()
             self.canvas_manager.coordinator_tab._drag_data_toplevel = {}
        self.node_handler._move_data = {"id": None, "x": 0, "y": 0}
        self.connection_handler._cancel_line_drawing()

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\canvas_components\node_manager.py
# JUMLAH BARIS : 585
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\canvas_components\node_manager.py
# JUMLAH BARIS : 584
#######################################################################

import ttkbootstrap as ttk
from tkinter import TclError, messagebox, scrolledtext
import uuid
import json
from ..custom_widgets.tooltip import ToolTip
import threading
import time
import os
from flowork_gui.api_client.client import ApiClient
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
class NodeManager:
    """
    Manages the lifecycle of nodes on the canvas.
    (MODIFIED V15) Now handles cases where a manifest is not found for a module ID in a preset, preventing crashes.
    """
    def __init__(self, canvas_manager, kernel, canvas_widget):
        self.api_client = ApiClient()
        self.canvas_manager = canvas_manager
        self.kernel = kernel
        self.canvas = canvas_widget
        self.loc = self.kernel.get_service("localization_manager")
        self.logger = self.kernel.write_to_log
        self.hovered_node_id = None
        self.icon_cache = {}
        self.animation_jobs = {}
    def move_node_by_delta(self, node_id, dx, dy):
        if self.canvas.find_withtag(node_id):
            self.canvas.move(node_id, dx, dy)
            self.canvas.update_idletasks()
            self.canvas_manager.connection_manager.update_connections_for_node(node_id)
    def _apply_style_to_node_widgets(self, node_id, frame_style_name):
        if node_id not in self.canvas_manager.canvas_nodes: return
        node_data = self.canvas_manager.canvas_nodes[node_id]
        if node_data.get("module_id") == 'agent_host_module':
             border_frame = node_data.get('border_frame')
             if not border_frame or not border_frame.winfo_exists(): return
             border_frame.config(style='AgentBorder.Selected.TFrame' if "Selected" in frame_style_name or "Hover" in frame_style_name else 'AgentBorder.Normal.TFrame')
             return
        if node_data.get('shape') in ['circle', 'icon_box', 'agent_brain']:
            shape_id = node_data.get('oval_id')
            if shape_id and self.canvas.find_withtag(shape_id):
                is_active = "Selected" in frame_style_name or "Hover" in frame_style_name
                outline_color = self.canvas_manager.colors.get('success', 'green') if is_active else self.canvas_manager.colors.get('border', 'grey')
                outline_width = 3 if is_active else 1
                if node_data.get('shape') == 'agent_brain':
                    outline_color = self.canvas_manager.colors.get('info', '#17a2b8') if is_active else "#4A00E0"
                self.canvas.itemconfig(shape_id, outline=outline_color, width=outline_width)
            return
        widget = node_data.get('widget')
        if not widget or not widget.winfo_exists(): return
        label_style_name = frame_style_name.replace('.Module.TFrame', '.TLabel')
        def _recursive_style(current_widget):
            if not current_widget.winfo_exists(): return
            if isinstance(current_widget, (ttk.Frame, ttk.LabelFrame)):
                current_widget.config(style=frame_style_name)
            elif isinstance(current_widget, ttk.Label):
                if "Port" not in current_widget.cget('style') and not hasattr(current_widget, '_is_icon_label'):
                    current_widget.config(style=label_style_name)
            for child in current_widget.winfo_children():
                _recursive_style(child)
        _recursive_style(widget)
    def _load_and_display_icon(self, parent_widget, module_id, module_manager):
        if not PIL_AVAILABLE: return None
        module_data = module_manager.loaded_modules.get(module_id)
        if not module_data: return None
        manifest = module_data.get("manifest", {})
        icon_filename = manifest.get("icon_file")
        if not icon_filename: return None
        icon_path = os.path.join(module_data.get("path"), icon_filename)
        if not os.path.exists(icon_path): return None
        icon_label = ttk.Label(parent_widget, style="Glass.TLabel")
        icon_label._is_icon_label = True # (COMMENT) Custom flag to prevent style changes.
        if icon_filename.lower().endswith('.gif'):
            self._animate_gif(icon_label, icon_path, module_id)
        else: # (COMMENT) Assume PNG or other static image
            if icon_path in self.icon_cache:
                photo_image = self.icon_cache[icon_path]
            else:
                try:
                    image = Image.open(icon_path).resize((20, 20), Image.Resampling.LANCZOS)
                    photo_image = ImageTk.PhotoImage(image)
                    self.icon_cache[icon_path] = photo_image
                except Exception as e:
                    self.logger(f"Could not load icon for {module_id}: {e}", "WARN")
                    return None
            icon_label.config(image=photo_image)
            icon_label.image = photo_image # (COMMENT) Keep a reference!
        icon_label.pack(side="left", padx=(0, 5))
        return icon_label
    def _animate_gif(self, label_widget, path, node_id, size=(20,20)):
        if node_id in self.animation_jobs:
            self._stop_gif_animation(node_id)
        try:
            gif = Image.open(path)
            frames = []
            for i in range(gif.n_frames):
                gif.seek(i)
                frame_image = gif.copy().resize(size, Image.Resampling.LANCZOS)
                frames.append(ImageTk.PhotoImage(frame_image))
            if not frames: return
            delay = gif.info.get('duration', 100)
            job_data = {
                'label': label_widget,
                'frames': frames,
                'delay': delay,
                'idx': 0,
                'job_id': None
            }
            self.animation_jobs[node_id] = job_data
            def _update_frame():
                if node_id not in self.animation_jobs or not job_data['label'].winfo_exists():
                    return
                frame = job_data['frames'][job_data['idx']]
                job_data['label'].config(image=frame)
                job_data['idx'] = (job_data['idx'] + 1) % len(job_data['frames'])
                job_data['job_id'] = self.canvas.after(job_data['delay'], _update_frame)
            _update_frame()
        except Exception as e:
            self.logger(f"Could not animate GIF for {node_id}: {e}", "ERROR")
    def _stop_gif_animation(self, node_id):
        if node_id in self.animation_jobs:
            job_data = self.animation_jobs.pop(node_id)
            if job_data.get('job_id'):
                try:
                    self.canvas.after_cancel(job_data['job_id'])
                except TclError:
                    pass
            self.logger(f"Stopped GIF animation for node {node_id}.", "DEBUG")
    def create_node_on_canvas(self, name, x, y, existing_id=None, description="", module_id=None, config_values=None):
        if module_id:
            module_manager = self.kernel.get_service("module_manager_service")
            required_tier = module_manager.get_module_tier(module_id)
            if not self.kernel.is_tier_sufficient(required_tier):
                messagebox.showwarning(self.loc.get('license_popup_title'), self.loc.get('license_popup_message', module_name=name), parent=self.canvas.winfo_toplevel())
                tab_manager = self.kernel.get_service("tab_manager_service")
                if tab_manager: tab_manager.open_managed_tab("pricing_page")
                return
        node_id = existing_id
        if module_id == 'prompt_receiver_module' and not existing_id:
            if "receiver-node-1" in self.canvas_manager.canvas_nodes:
                messagebox.showwarning("Node Already Exists", "You can only have one 'Prompt Receiver' node on the canvas. Its ID is always 'receiver-node-1'.")
                return
            node_id = "receiver-node-1"
        elif not node_id:
            node_id = str(uuid.uuid4())
        canvas_nodes = self.canvas_manager.canvas_nodes
        tooltips = self.canvas_manager.tooltips
        module_manager = self.kernel.get_service("module_manager_service")
        manifest = module_manager.get_manifest(module_id) if module_manager else {}
        if manifest is None:
            self.logger(f"Warning: Manifest for module ID '{module_id}' not found. It may have been uninstalled. Using a default empty manifest.", "WARN")
            manifest = {}
        display_props = manifest.get('display_properties', {})
        node_shape = display_props.get('shape', 'rectangle')
        zoom_level = self.canvas_manager.interaction_manager.navigation_handler.zoom_level
        scaled_x = x * zoom_level
        scaled_y = y * zoom_level
        main_label, widget_to_register = None, None
        output_ports_widgets, input_ports_widgets, tool_ports_widgets = [], [], []
        ports_frame, info_frame, border_frame, status_text, oval_id = None, None, None, None, None
        if node_shape == 'agent_brain':
            node_width = 80
            node_height = 80
            oval_id = self.canvas.create_rectangle(scaled_x, scaled_y, scaled_x + node_width, scaled_y + node_height, fill="#2E0854", outline="#4A00E0", width=1, tags=(node_id, "node_shape"))
            widget_to_register = ttk.Frame(self.canvas, width=node_width-8, height=node_height-8, style='TFrame', relief="solid", borderwidth=1)
            self.canvas.create_window(scaled_x + node_width/2, scaled_y + node_height/2, window=widget_to_register, tags=(node_id, "node_widget_container"))
            if PIL_AVAILABLE and display_props.get("icon_file"):
                icon_filename = display_props.get("icon_file")
                module_data = module_manager.loaded_modules.get(module_id)
                icon_path = os.path.join(module_data.get("path"), icon_filename) if module_data else None
                icon_label = ttk.Label(widget_to_register, style="TLabel")
                icon_label.place(relx=0.5, rely=0.5, anchor="center")
                if icon_path and os.path.exists(icon_path):
                    if icon_filename.lower().endswith('.gif'):
                        self._animate_gif(icon_label, icon_path, node_id, size=(48, 48))
                    else:
                        image = Image.open(icon_path).resize((48, 48), Image.Resampling.LANCZOS)
                        photo_image = ImageTk.PhotoImage(image)
                        self.icon_cache[icon_path] = photo_image
                        icon_label.config(image=photo_image)
                        icon_label.image = photo_image
            connection_handler = self.canvas_manager.interaction_manager.connection_handler
            for port_info in manifest.get('output_ports', []):
                port_name = port_info.get("name")
                port_type = port_info.get("type", "output")
                port_x, port_y = scaled_x + node_width/2, scaled_y
                connector = ttk.Frame(self.canvas, width=24, height=12, style="info.TFrame", relief="raised", borderwidth=1)
                self.canvas.create_window(port_x, port_y, window=connector, tags=(node_id, "node_port"), anchor="s")
                connector.node_id = node_id
                connector.port_name = port_name
                output_ports_widgets.append({"name": port_name, "widget": connector})
                connector.bind("<ButtonPress-1>", lambda e, n=node_id, p=port_name, pt=port_type: connection_handler.start_line_drawing(n, port_name=p, port_type=pt))
                connector.bind("<Enter>", lambda e, w=connector: w.config(style="success.TFrame"))
                connector.bind("<Leave>", lambda e, w=connector: w.config(style="info.TFrame"))
                ToolTip(connector).update_text(port_info.get("tooltip", port_name))
            self.canvas_manager.visual_manager.start_brain_pulse(node_id)
        elif node_shape == 'circle':
            node_width = 120
            node_height = 120
            oval_id = self.canvas.create_oval(scaled_x, scaled_y, scaled_x + node_width, scaled_y + node_height, fill=self.canvas_manager.colors.get('dark', '#343a40'), outline=self.canvas_manager.colors.get('border', 'grey'), width=1, tags=(node_id, "node_shape"))
            widget_to_register = ttk.Frame(self.canvas, width=node_width-10, height=node_height-10)
            widget_to_register.config(style='TFrame')
            self.canvas.create_window(scaled_x + node_width/2, scaled_y + node_height/2, window=widget_to_register, tags=(node_id, "node_widget_container"))
            if PIL_AVAILABLE and display_props.get("icon_file"):
                icon_filename = display_props.get("icon_file")
                all_components = {**module_manager.loaded_modules, **self.kernel.get_service("widget_manager_service").loaded_widgets}
                module_data = all_components.get(module_id)
                icon_path = os.path.join(module_data.get("path"), icon_filename) if module_data else None
                icon_label = ttk.Label(widget_to_register, style="TLabel")
                icon_label.place(relx=0.5, rely=0.4, anchor="center")
                if icon_path and os.path.exists(icon_path):
                    if icon_filename.lower().endswith('.gif'):
                        self._animate_gif(icon_label, icon_path, node_id, size=(48, 48))
                    else:
                        image = Image.open(icon_path).resize((48, 48), Image.Resampling.LANCZOS)
                        photo_image = ImageTk.PhotoImage(image)
                        self.icon_cache[icon_path] = photo_image
                        icon_label.config(image=photo_image)
                        icon_label.image = photo_image
            main_label = ttk.Label(widget_to_register, text=name, wraplength=node_width - 20, justify='center')
            main_label.place(relx=0.5, rely=0.8, anchor="center")
            connection_handler = self.canvas_manager.interaction_manager.connection_handler
            for port_info in manifest.get('output_ports', []):
                port_name = port_info.get("name")
                port_position = port_info.get("port_position", "top")
                port_type = port_info.get("type", "output")
                rely_val, anchor_val = (0.0, "n") if port_position == "top" else (1.0, "s")
                port_x, port_y = scaled_x + node_width/2, scaled_y if port_position == "top" else scaled_y + node_height
                connector = ttk.Frame(self.canvas, width=20, height=10, style="success.TFrame", relief="solid", borderwidth=1)
                self.canvas.create_window(port_x, port_y, window=connector, tags=(node_id, "node_port"), anchor=anchor_val)
                connector.node_id = node_id
                connector.port_name = port_name
                output_ports_widgets.append({"name": port_name, "widget": connector})
                connector.bind("<ButtonPress-1>", lambda e, n=node_id, p=port_name, pt=port_type: connection_handler.start_line_drawing(n, port_name=p, port_type=pt))
                connector.bind("<Enter>", lambda e, w=connector: w.config(style="info.TFrame"))
                connector.bind("<Leave>", lambda e, w=connector: w.config(style="success.TFrame"))
                ToolTip(connector).update_text(port_info.get("tooltip", port_name))
        elif node_shape == 'icon_box':
            node_width = 80
            node_height = 80
            oval_id = self.canvas.create_rectangle(scaled_x, scaled_y, scaled_x + node_width, scaled_y + node_height, fill=self.canvas_manager.colors.get('bg', '#222'), outline=self.canvas_manager.colors.get('border', 'grey'), width=1, tags=(node_id, "node_shape"))
            widget_to_register = ttk.Frame(self.canvas, width=node_width-10, height=node_height-10)
            widget_to_register.config(style='TFrame')
            self.canvas.create_window(scaled_x + node_width/2, scaled_y + node_height/2, window=widget_to_register, tags=(node_id, "node_widget_container"))
            if PIL_AVAILABLE and display_props.get("icon_file"):
                icon_filename = display_props.get("icon_file")
                module_data = module_manager.loaded_modules.get(module_id)
                icon_path = os.path.join(module_data.get("path"), icon_filename) if module_data else None
                icon_label = ttk.Label(widget_to_register, style="TLabel")
                icon_label.place(relx=0.5, rely=0.5, anchor="center")
                if icon_path and os.path.exists(icon_path):
                    if icon_filename.lower().endswith('.gif'):
                        self._animate_gif(icon_label, icon_path, node_id, size=(48, 48))
                    else:
                        image = Image.open(icon_path).resize((48, 48), Image.Resampling.LANCZOS)
                        photo_image = ImageTk.PhotoImage(image)
                        self.icon_cache[icon_path] = photo_image
                        icon_label.config(image=photo_image)
                        icon_label.image = photo_image
            connection_handler = self.canvas_manager.interaction_manager.connection_handler
            for port_info in manifest.get('output_ports', []):
                port_name = port_info.get("name")
                port_type = port_info.get("type", "output")
                port_x, port_y = scaled_x + node_width/2, scaled_y
                connector = ttk.Frame(self.canvas, width=20, height=10, style="success.TFrame", relief="solid", borderwidth=1)
                self.canvas.create_window(port_x, port_y, window=connector, tags=(node_id, "node_port"), anchor="s")
                connector.node_id = node_id
                connector.port_name = port_name
                output_ports_widgets.append({"name": port_name, "widget": connector})
                connector.bind("<ButtonPress-1>", lambda e, n=node_id, p=port_name, pt=port_type: connection_handler.start_line_drawing(n, port_name=p, port_type=pt))
                connector.bind("<Enter>", lambda e, w=connector: w.config(style="info.TFrame"))
                connector.bind("<Leave>", lambda e, w=connector: w.config(style="success.TFrame"))
                ToolTip(connector).update_text(port_info.get("tooltip", port_name))
        elif module_id == 'agent_host_module':
            style = ttk.Style()
            style.configure('AgentBorder.Normal.TFrame', background="#6A2E2E")
            style.configure('AgentBorder.Selected.TFrame', background="yellow")
            style.configure('AgentHeader.TFrame', background="#4A00E0")
            style.configure('AgentHeader.TLabel', background="#4A00E0", foreground="yellow")
            style.configure('AgentBody.TFrame', background="#6A2E2E")
            style.configure('AgentBody.TLabel', background="#6A2E2E")
            style.configure('AgentFooter.TFrame', background="#6A2E2E")
            widget_to_register = ttk.Frame(self.canvas, width=320, height=132)
            widget_to_register.pack_propagate(False)
            border_frame = ttk.Frame(widget_to_register, width=302, height=132, style='AgentBorder.Normal.TFrame')
            border_frame.place(relx=0.5, rely=0.5, anchor='center')
            node_frame = ttk.Frame(border_frame, width=300, height=130)
            node_frame.pack(padx=1, pady=1)
            node_frame.pack_propagate(False)
            header = ttk.Frame(node_frame, height=30, style='AgentHeader.TFrame')
            header.pack(side="top", fill="x")
            main_label = ttk.Label(header, text="Agent Host", font=("Arial", 12, "bold"), style='AgentHeader.TLabel')
            main_label.pack(pady=5)
            status_text = scrolledtext.ScrolledText(node_frame, height=2, wrap="word", relief="sunken", borderwidth=1, background="#4d2424", foreground="#E0E0E0", font=("Consolas", 8), state="disabled", name=f"agent_status_text_{node_id}")
            status_text.pack(fill='x', expand=True, padx=30, pady=5)
            icon_size = (24, 24)
            tool_ports_config = {'prompt_port': 'icon_prompt.png', 'brain_port': 'icon_brain.png', 'tools_port': 'icon_tools.png'}
            icon_holder_frame = ttk.Frame(node_frame, style='AgentFooter.TFrame')
            icon_holder_frame.pack(side="bottom", fill="x", pady=5)
            for port_name, icon_file in tool_ports_config.items():
                port_container = ttk.Frame(icon_holder_frame, style='AgentFooter.TFrame')
                port_container.pack(side='left', expand=True, fill='x')
                full_path = os.path.join(self.kernel.project_root_path, 'modules', 'agent_host_module', icon_file)
                if os.path.exists(full_path):
                    img = Image.open(full_path).resize(icon_size, Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    icon_label = ttk.Label(port_container, image=photo, style='AgentBody.TLabel', cursor="tcross")
                    icon_label.image = photo
                    icon_label.pack()
                    ToolTip(icon_label).update_text(f"Connect {port_name.replace('_port','').capitalize()} here")
                    icon_label.node_id = node_id
                    icon_label.port_name = port_name
                    icon_label.port_type = 'tool'
                    tool_ports_widgets.append({"name": port_name, "widget": icon_label})
            input_ports_widgets, output_ports_widgets = [], []
            input_port_connector = ttk.Frame(widget_to_register, width=10, height=20, style="success.TFrame")
            input_port_connector.place(x=0, rely=0.5, anchor='w')
            input_port_connector.node_id = node_id; input_port_connector.port_name = "payload_input"; input_port_connector.port_type = 'input'
            input_ports_widgets.append({"name": "payload_input", "widget": input_port_connector})
            output_port_success_connector = ttk.Frame(widget_to_register, width=10, height=20, style="success.TFrame")
            output_port_success_connector.place(relx=1, rely=0.4, anchor='e')
            output_port_success_connector.node_id = node_id; output_port_success_connector.port_name = "success"; output_port_success_connector.port_type = 'output'
            output_ports_widgets.append({"name": "success", "widget": output_port_success_connector})
            output_port_error_connector = ttk.Frame(widget_to_register, width=10, height=20, style="danger.TFrame")
            output_port_error_connector.place(relx=1, rely=0.6, anchor='e')
            output_port_error_connector.node_id = node_id; output_port_error_connector.port_name = "error"; output_port_error_connector.port_type = 'output'
            output_ports_widgets.append({"name": "error", "widget": output_port_error_connector})
            ports_frame, info_frame, status_label = ttk.Frame(node_frame), ttk.Frame(node_frame), ttk.Label(node_frame)
        else:
            node_frame = ttk.Frame(self.canvas, style='Glass.Module.TFrame', padding=(0,0,0,5))
            widget_to_register = node_frame
            content_frame = ttk.Frame(node_frame, style='Glass.Module.TFrame')
            content_frame.pack(side="left", fill="both", expand=True, padx=5)
            header_frame = ttk.Frame(content_frame, style='Glass.Module.TFrame')
            header_frame.pack(fill='x', expand=True, padx=5, pady=(5,0))
            self._load_and_display_icon(header_frame, module_id, module_manager)
            main_label = ttk.Label(header_frame, text=name, style="Glass.TLabel", wraplength=180)
            main_label.pack(side="left", fill='x', expand=True)
            info_frame = ttk.Frame(content_frame, style='Glass.Module.TFrame')
            info_frame.pack(fill='x', padx=10, pady=(2,0))
            status_label = ttk.Label(content_frame, text="", name=f"status_{node_id}", font=("Helvetica", 7), anchor='center', style="Glass.TLabel", wraplength=180)
            status_label.pack(fill='x', padx=10, pady=(0,5))
            ports_frame = ttk.Frame(node_frame, style='Glass.Module.TFrame')
            ports_frame.pack(side="right", fill="y", padx=(0, 5))
        if node_shape not in ['circle', 'icon_box', 'agent_brain']:
            self.canvas.create_window(scaled_x, scaled_y, window=widget_to_register, anchor="nw", tags=(node_id, "node_widget_container"))
        widget_to_register.node_id = node_id
        canvas_nodes[node_id] = {
            "widget": widget_to_register, "main_label": main_label, "name": name, "x": x, "y": y,
            "description": description, "module_id": module_id, "config_values": config_values or {},
            "output_ports": output_ports_widgets, "input_ports": input_ports_widgets, "tool_ports": tool_ports_widgets,
            "ports_widget_frame": ports_frame, "info_widget_frame": info_frame, "border_frame": border_frame,
            "status_display_widget": status_text, "shape": node_shape, "oval_id": oval_id
        }
        if module_id != 'agent_host_module' and node_shape not in ['circle', 'icon_box', 'agent_brain']:
             self.update_node_ports(node_id)
        self.update_node_visual_info(node_id)
        tooltips[node_id] = ToolTip(widget_to_register)
        tooltips[node_id].update_text(description)
        interaction_manager = self.canvas_manager.interaction_manager
        node_interaction_handler = interaction_manager.node_handler
        if node_shape in ['circle', 'icon_box', 'agent_brain']:
            def _bind_recursive_special(widget, event, command):
                 if widget and widget.winfo_exists():
                    widget.bind(event, command)
                    for child in widget.winfo_children():
                        _bind_recursive_special(child, event, command)
            _bind_recursive_special(widget_to_register, "<ButtonPress-1>", node_interaction_handler.on_node_press)
            _bind_recursive_special(widget_to_register, "<B1-Motion>", node_interaction_handler.on_node_motion)
            _bind_recursive_special(widget_to_register, "<ButtonRelease-1>", node_interaction_handler.on_node_release)
            _bind_recursive_special(widget_to_register, "<ButtonPress-3>", node_interaction_handler.show_node_context_menu)
            self.canvas.tag_bind(oval_id, "<ButtonPress-1>", node_interaction_handler.on_node_press)
            self.canvas.tag_bind(oval_id, "<B1-Motion>", node_interaction_handler.on_node_motion)
            self.canvas.tag_bind(oval_id, "<ButtonRelease-1>", node_interaction_handler.on_node_release)
            self.canvas.tag_bind(oval_id, "<ButtonPress-3>", node_interaction_handler.show_node_context_menu)
        else:
            def _bind_recursive(widget, event, command):
                if widget.winfo_exists():
                    widget.bind(event, command)
                    for child in widget.winfo_children():
                        _bind_recursive(child, event, command)
            _bind_recursive(widget_to_register, "<ButtonPress-1>", node_interaction_handler.on_node_press)
            _bind_recursive(widget_to_register, "<B1-Motion>", node_interaction_handler.on_node_motion)
            _bind_recursive(widget_to_register, "<ButtonRelease-1>", node_interaction_handler.on_node_release)
            _bind_recursive(widget_to_register, "<ButtonPress-3>", node_interaction_handler.show_node_context_menu)
        if module_id == 'agent_host_module':
            connection_handler = self.canvas_manager.interaction_manager.connection_handler
            output_port_success_connector.bind("<ButtonPress-1>", lambda e, n=node_id, p="success", pt="output": connection_handler.start_line_drawing(n, port_name=p, port_type=pt))
            output_port_error_connector.bind("<ButtonPress-1>", lambda e, n=node_id, p="error", pt="output": connection_handler.start_line_drawing(n, port_name=p, port_type=pt))
            output_port_success_connector.bind("<Enter>", lambda e, w=output_port_success_connector: w.config(style="info.TFrame"))
            output_port_success_connector.bind("<Leave>", lambda e, w=output_port_success_connector: w.config(style="success.TFrame"))
            output_port_error_connector.bind("<Enter>", lambda e, w=output_port_error_connector: w.config(style="info.TFrame"))
            output_port_error_connector.bind("<Leave>", lambda e, w=output_port_error_connector: w.config(style="danger.TFrame"))
            for port_dict in tool_ports_widgets + input_ports_widgets:
                widget = port_dict['widget']
                widget.bind("<Enter>", lambda e, w=widget: w.config(relief="raised"))
                widget.bind("<Leave>", lambda e, w=widget: w.config(relief="flat"))
                widget.bind("<ButtonPress-1>", node_interaction_handler.on_node_press)
                widget.bind("<ButtonPress-3>", node_interaction_handler.show_node_context_menu)
        if module_id and module_manager:
            instance = module_manager.get_instance(module_id)
            if instance and hasattr(instance, 'on_canvas_load'):
                instance.on_canvas_load(node_id)
        self.kernel.write_to_log(f"NODE CREATED: Name='{name}', ID='{node_id}'", "INFO")
        self.canvas_manager.visual_manager.hide_watermark()
    def _on_node_enter(self, event):
        item_ids = self.canvas.find_withtag("current")
        if not item_ids: return
        tags = self.canvas.gettags(item_ids[0])
        node_id = next((tag for tag in tags if tag in self.canvas_manager.canvas_nodes), None)
        if not node_id:
            widget = event.widget
            while widget and not hasattr(widget, 'node_id'):
                widget = widget.master
            if not widget or not widget.winfo_exists(): return
            node_id = widget.node_id
        if self.hovered_node_id == node_id: return
        self.hovered_node_id = node_id
        if node_id == self.canvas_manager.selected_node_id: return
        self._apply_style_to_node_widgets(node_id, "Hover.Glass.Module.TFrame")
    def _on_node_leave(self, event):
        if not self.hovered_node_id: return
        node_id = self.hovered_node_id
        if node_id not in self.canvas_manager.canvas_nodes: return
        self.hovered_node_id = None
        style_to_apply = "Selected.Glass.Module.TFrame" if node_id == self.canvas_manager.selected_node_id else "Glass.Module.TFrame"
        self._apply_style_to_node_widgets(node_id, style_to_apply)
    def select_node(self, node_id_to_select):
        if self.canvas_manager.selected_node_id and self.canvas_manager.selected_node_id in self.canvas_manager.canvas_nodes:
            self._apply_style_to_node_widgets(self.canvas_manager.selected_node_id, "Glass.Module.TFrame")
        self.canvas_manager.selected_node_id = node_id_to_select
        if self.canvas_manager.selected_node_id in self.canvas_manager.canvas_nodes:
            self._apply_style_to_node_widgets(self.canvas_manager.selected_node_id, "Selected.Glass.Module.TFrame")
    def deselect_all_nodes(self, event=None, from_delete=False):
        if event and self.canvas.find_withtag("current"): return
        if self.canvas_manager.selected_node_id and self.canvas_manager.selected_node_id in self.canvas_manager.canvas_nodes:
            self._apply_style_to_node_widgets(self.canvas_manager.selected_node_id, "Glass.Module.TFrame")
        self.canvas_manager.selected_node_id = None
        if not from_delete and self.canvas_manager.interaction_manager:
            self.canvas_manager.interaction_manager.connection_handler._cancel_line_drawing()
    def update_node_ports(self, node_id):
        canvas_nodes = self.canvas_manager.canvas_nodes
        if node_id not in canvas_nodes: return
        node_data = canvas_nodes[node_id]
        if node_data.get("module_id") == 'agent_host_module' or node_data.get('shape') in ['circle', 'icon_box', 'agent_brain']:
            return
        ports_frame = node_data['ports_widget_frame']
        module_manager = self.kernel.get_service("module_manager_service")
        if not module_manager: return
        manifest = module_manager.get_manifest(node_data['module_id'])
        config_values = node_data.get("config_values", {})
        for widget in ports_frame.winfo_children():
            widget.destroy()
        node_data['output_ports'] = []
        ports_to_create = []
        if manifest and "output_ports" in manifest:
            ports_to_create.extend(manifest["output_ports"])
        module_instance = module_manager.get_instance(node_data['module_id'])
        if module_instance and hasattr(module_instance, 'get_dynamic_ports'):
            dynamic_ports = module_instance.get_dynamic_ports(config_values)
            if dynamic_ports:
                ports_to_create.extend(dynamic_ports)
        for port_info in ports_to_create:
            port_name = port_info.get("name")
            port_display_name = port_info.get("display_name", port_name)
            port_type = port_info.get("type", "output")
            port_label_frame = ttk.Frame(ports_frame, style='Glass.Module.TFrame')
            port_label_frame.pack(anchor='e', pady=1)
            label = ttk.Label(port_label_frame, text=port_display_name, style="Port.Glass.TLabel", anchor='e')
            label.pack(side="left")
            connector = ttk.Frame(port_label_frame, width=10, height=10, style="success.TFrame", relief="solid", borderwidth=1)
            connector.pack(side="left", padx=(5,0))
            connector.node_id = node_id
            connector.port_name = port_name
            node_data['output_ports'].append({"name": port_name, "widget": connector})
            connection_interaction_handler = self.canvas_manager.interaction_manager.connection_handler
            connector.bind("<ButtonPress-1>", lambda e, n=node_id, p=port_name, pt=port_type: connection_interaction_handler.start_line_drawing(n, port_name=p, port_type=pt))
            connector.bind("<Enter>", lambda e, w=connector: w.config(style="info.TFrame"))
            connector.bind("<Leave>", lambda e, w=connector: w.config(style="success.TFrame"))
            ToolTip(connector).update_text(port_info.get("tooltip", port_name))
        if self.canvas_manager.connection_manager:
            self.canvas_manager.connection_manager.update_connections_for_node(node_id)
    def update_node_visual_info(self, node_id):
        if node_id not in self.canvas_manager.canvas_nodes: return
        node_data = self.canvas_manager.canvas_nodes[node_id]
        if node_data.get("module_id") == 'agent_host_module' or node_data.get('shape') in ['circle', 'icon_box', 'agent_brain']:
            status_widget = node_data.get('status_display_widget')
            if status_widget and status_widget.winfo_exists():
                objective = "Menunggu Misi..."
                status_widget.config(state="normal")
                status_widget.delete("1.0", "end")
                status_widget.insert("1.0", objective)
                status_widget.config(state="disabled")
            return
        info_frame = node_data.get("info_widget_frame")
        if not info_frame or not info_frame.winfo_exists(): return
        for widget in info_frame.winfo_children():
            widget.destroy()
        config = node_data.get("config_values", {})
        module_id = node_data.get("module_id")
        badges_frame = ttk.Frame(info_frame, style='Glass.Module.TFrame')
        badges_frame.pack(fill='x', pady=(2,0))
        if config.get('enable_loop', False):
            loop_count = config.get('loop_iterations', 1)
            loop_badge = ttk.Label(badges_frame, text=f"🔁 {loop_count}x", style="Glass.TLabel", font=("Helvetica", 7, "italic"))
            loop_badge.pack(side='left', padx=(0, 5))
            ToolTip(loop_badge).update_text(self.loc.get('badge_tooltip_loop', count=loop_count))
        retry_count = config.get('retry_attempts', 0)
        if retry_count > 0:
            retry_badge = ttk.Label(badges_frame, text=f"🔄 {retry_count}x", style="Glass.TLabel", font=("Helvetica", 7, "italic"))
            retry_badge.pack(side='left', padx=(0, 5))
            ToolTip(retry_badge).update_text(self.loc.get('badge_tooltip_retry', count=retry_count))
        summary_text = ""
        if module_id == 'if_module':
            var = config.get('variable_to_check', '?')
            op = config.get('comparison_operator', '??')
            val = config.get('value_to_compare', '?')
            summary_text = f"IF ({var} {op} {val})"
        elif module_id == 'sleep_module':
            sleep_type = config.get('sleep_type', 'static')
            if sleep_type == 'random_range':
                min_val = config.get('random_min', 1)
                max_val = config.get('random_max', 10)
                summary_text = f"Delay: {min_val}-{max_val}s (Random)"
            else:
                duration = config.get('duration_seconds', 3)
                summary_text = f"Delay: {duration}s"
        elif module_id == 'sub_workflow_module':
             presets = config.get('execution_order', [])
             if presets:
                summary_text = f"Run: {presets[0]}"
                if len(presets) > 1:
                    summary_text += f" (+{len(presets)-1} more)"
        if summary_text:
            summary_label = ttk.Label(info_frame, text=summary_text, style="Glass.TLabel", font=("Helvetica", 7), foreground="#a9a9a9", wraplength=180)
            summary_label.pack(fill='x', pady=(2,0))
    def delete_node(self, node_id_to_delete, feedback=True):
        self._stop_gif_animation(node_id_to_delete)
        node_data = self.canvas_manager.canvas_nodes.get(node_id_to_delete)
        if node_data and node_data.get('shape') == 'agent_brain':
            self.canvas_manager.visual_manager.stop_brain_pulse(node_id_to_delete)
        canvas_nodes = self.canvas_manager.canvas_nodes
        canvas_connections = self.canvas_manager.canvas_connections
        tooltips = self.canvas_manager.tooltips
        if node_id_to_delete not in canvas_nodes: return
        self.canvas.delete(node_id_to_delete)
        connections_to_remove = [cid for cid, cdata in canvas_connections.items() if cdata["from"] == node_id_to_delete or cdata["to"] == node_id_to_delete]
        for conn_id in connections_to_remove:
            self.canvas_manager.connection_manager.delete_connection(conn_id, feedback=False)
        if node_id_to_delete in tooltips:
            del tooltips[node_id_to_delete]
        if canvas_nodes[node_id_to_delete]["widget"] and canvas_nodes[node_id_to_delete]["widget"].winfo_exists():
            canvas_nodes[node_id_to_delete]["widget"].destroy()
        del canvas_nodes[node_id_to_delete]
        self.deselect_all_nodes(from_delete=True)
        if feedback:
            self.kernel.write_to_log(f"Node '{node_id_to_delete}' deleted successfully.", "INFO")
        if not canvas_nodes:
            self.canvas_manager.visual_manager.draw_watermark()
    def duplicate_node(self, node_id_to_duplicate):
        canvas_nodes = self.canvas_manager.canvas_nodes
        if node_id_to_duplicate not in canvas_nodes: return
        original_node_data = canvas_nodes[node_id_to_duplicate]
        new_config_values = json.loads(json.dumps(original_node_data.get('config_values', {})))
        new_x, new_y = original_node_data['x'] + 30, original_node_data['y'] + 30
        self.create_node_on_canvas(
            name=f"{original_node_data['name']} (Copy)",
            x=new_x, y=new_y,
            description=original_node_data.get('description', ''),
            module_id=original_node_data.get('module_id'),
            config_values=new_config_values
        )
        self.kernel.write_to_log(f"Node '{original_node_data['name']}' duplicated successfully.", "INFO")

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\canvas_components\properties_manager.py
# JUMLAH BARIS : 87
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\canvas_components\properties_manager.py
# JUMLAH BARIS : 86
#######################################################################

import json
from tkinter import messagebox, Text, TclError, Listbox
from tkinter import scrolledtext
from flowork_kernel.api_contract import EnumVarWrapper
from ..properties_popup import PropertiesPopup
from flowork_gui.api_client.client import ApiClient
class PropertiesManager:
    """
    Handles all logic related to the Node Properties window, including opening, validating, and saving data.
    (FIXED V2) Now safely handles nodes without a 'main_label' widget.
    """
    def __init__(self, canvas_manager, kernel):
        self.api_client = ApiClient()
        self.canvas_manager = canvas_manager
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
    def open_properties_popup(self, node_id):
        """Opens a Toplevel window for node properties."""
        if node_id in self.canvas_manager.canvas_nodes:
            PropertiesPopup(self.canvas_manager, node_id)
    def save_node_properties(self, node_id, property_vars, popup_window):
        """
        Saves data from the properties popup to the node's state after validation.
        """
        canvas_nodes = self.canvas_manager.canvas_nodes
        if node_id not in canvas_nodes:
            return
        node_data = canvas_nodes[node_id]
        old_name = node_data.get('name', node_id)
        new_name = property_vars.get('name').get() if 'name' in property_vars else old_name
        new_description = ""
        new_config_values = {}
        for key, var_obj in property_vars.items():
            try:
                value_to_save = None
                if isinstance(var_obj, (Text, scrolledtext.ScrolledText)):
                    value_to_save = var_obj.get('1.0', 'end-1c').strip()
                elif isinstance(var_obj, (Listbox, EnumVarWrapper)):
                    value_to_save = var_obj.get()
                elif hasattr(var_obj, 'get'):
                    value_to_save = var_obj.get()
                else:
                    continue
                if key == 'description':
                    new_description = value_to_save
                elif key == 'name':
                    pass
                else:
                    new_config_values[key] = value_to_save
            except (TclError, AttributeError) as e:
                pass # (COMMENT) It's better to ignore this minor error
        module_manager = self.kernel.get_service("module_manager_service")
        if not module_manager: return
        module_instance = module_manager.get_instance(node_data.get("module_id"))
        if module_instance and hasattr(module_instance, 'validate'):
            connected_inputs = [
                conn['source_port_name']
                for conn in self.canvas_manager.canvas_connections.values()
                if conn.get('to') == node_id
            ]
            is_valid, error_message = module_instance.validate(new_config_values, connected_inputs)
            if not is_valid:
                messagebox.showerror(
                    self.loc.get('error_title', fallback="Configuration Error"),
                    error_message,
                    parent=popup_window
                )
                return
        node_data['name'] = new_name
        node_data['description'] = new_description
        node_data["config_values"] = new_config_values
        main_label_widget = node_data.get('main_label')
        if main_label_widget and main_label_widget.winfo_exists():
            main_label_widget.config(text=new_name)
        if node_id in self.canvas_manager.tooltips:
            self.canvas_manager.tooltips[node_id].update_text(new_description)
        self.kernel.write_to_log(f"Properties for node '{new_name}' were updated.", "SUCCESS")
        self.canvas_manager.node_manager.update_node_ports(node_id)
        self.canvas_manager.node_manager.update_node_visual_info(node_id)

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\canvas_components\visual_manager.py
# JUMLAH BARIS : 346
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\canvas_components\visual_manager.py
# JUMLAH BARIS : 345
#######################################################################

import ttkbootstrap as ttk
from tkinter import TclError
from ..custom_widgets.tooltip import ToolTip
from flowork_gui.api_client.client import ApiClient
class VisualManager:
    """
    Manages all visual aspects and effects on the canvas.
    (MODIFIED V3) Added a pulsing animation for 'agent_brain' nodes and redesigned default node style.
    """
    def __init__(self, canvas_manager, kernel, canvas_widget):
        self.api_client = ApiClient()
        self.canvas_manager = canvas_manager
        self.kernel = kernel
        self.canvas = canvas_widget
        self.loc = self.kernel.get_service("localization_manager")
        self._watermark_id = None
        self._sleeping_animation_jobs = {}
        self.suggestion_indicators = {}
        self.processing_animations = {}
        self.brain_pulse_jobs = {}
        self._animation_frames = ['|', '/', '-', '\\']
        self._last_timeline_highlight_id = None
        self._define_highlight_styles()
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.draw_grid()
    def _get_original_style(self, node_id):
        """Determines the correct default style for a node (selected or normal)."""
        if node_id == self.canvas_manager.selected_node_id:
            return "Selected.Glass.Module.TFrame"
        else:
            return "Glass.Module.TFrame"
    def start_brain_pulse(self, node_id):
        if node_id in self.brain_pulse_jobs or not self.canvas.winfo_exists():
            return
        node_data = self.canvas_manager.canvas_nodes.get(node_id)
        if not node_data or node_data.get('shape') != 'agent_brain':
            return
        shape_id = node_data.get('oval_id')
        if not shape_id or not self.canvas.find_withtag(shape_id):
            return
        pulse_config = {
            'shape_id': shape_id,
            'min_width': 1.0,
            'max_width': 3.0,
            'step': 0.2,
            'direction': 1
        }
        self.brain_pulse_jobs[node_id] = pulse_config
        self._animate_brain_pulse(node_id)
    def _animate_brain_pulse(self, node_id):
        if node_id not in self.brain_pulse_jobs or not self.canvas.winfo_exists():
            return
        pulse_config = self.brain_pulse_jobs[node_id]
        shape_id = pulse_config['shape_id']
        if not self.canvas.find_withtag(shape_id):
            if node_id in self.brain_pulse_jobs:
                del self.brain_pulse_jobs[node_id]
            return
        current_width = self.canvas.itemcget(shape_id, "width")
        try:
            current_width_float = float(current_width)
        except ValueError:
            current_width_float = pulse_config['min_width']
        new_width = current_width_float + (pulse_config['step'] * pulse_config['direction'])
        if new_width >= pulse_config['max_width']:
            new_width = pulse_config['max_width']
            pulse_config['direction'] = -1
        elif new_width <= pulse_config['min_width']:
            new_width = pulse_config['min_width']
            pulse_config['direction'] = 1
        self.canvas.itemconfig(shape_id, width=new_width)
        job_id = self.canvas.after(50, self._animate_brain_pulse, node_id)
        self.brain_pulse_jobs[node_id]['job_id'] = job_id
    def stop_brain_pulse(self, node_id):
        if node_id in self.brain_pulse_jobs:
            job_id = self.brain_pulse_jobs[node_id].get('job_id')
            if job_id:
                try:
                    self.canvas.after_cancel(job_id)
                except TclError:
                    pass
            del self.brain_pulse_jobs[node_id]
    def _on_canvas_resize(self, event=None):
        self.canvas.delete("grid_dot")
        self.draw_grid()
        self.draw_watermark()
    def draw_grid(self):
        if not self.canvas.winfo_exists():
            return
        self.canvas.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width <= 1 or canvas_height <= 1:
            self.canvas_manager.coordinator_tab.after(100, self.draw_grid)
            return
        grid_spacing = 30
        dot_size = 1
        dot_color = "#4a4a4a"
        for x in range(0, canvas_width, grid_spacing):
            for y in range(0, canvas_height, grid_spacing):
                x1, y1 = x - dot_size, y - dot_size
                x2, y2 = x + dot_size, y + dot_size
                self.canvas.create_oval(x1, y1, x2, y2, fill=dot_color, outline="", tags="grid_dot")
        self.canvas.tag_lower("grid_dot")
    def _define_highlight_styles(self):
        style = ttk.Style.get_instance()
        colors = self.canvas_manager.colors
        glass_bg = '#222831'
        glass_border = '#393E46'
        style.configure('Glass.Module.TFrame', background=glass_bg, bordercolor=glass_border, borderwidth=1, relief='solid')
        style.configure('Glass.TLabel', background=glass_bg, foreground=colors.get('fg'))
        style.configure('Port.Glass.TLabel', background=glass_bg, foreground=colors.get('fg'))
        style.configure('Selected.Glass.Module.TFrame', background=glass_bg, bordercolor=colors.get('success'), borderwidth=2, relief='solid')
        style.configure('Selected.Glass.TLabel', background=glass_bg, foreground=colors.get('success'))
        style.configure('Hover.Glass.Module.TFrame', background=glass_bg, bordercolor=colors.get('info'), borderwidth=2, relief='solid')
        style.configure('Hover.Glass.TLabel', background=glass_bg, foreground=colors.get('info'))
        style.configure('Droppable.Module.TFrame', background=glass_bg, bordercolor=colors.get('success'), borderwidth=2, relief='solid')
        style.configure('Droppable.TLabel', background=glass_bg, foreground=colors.get('success'))
        style.configure('Executing.Module.TFrame', background=colors.get('warning', '#ffc107'), bordercolor=colors.get('light', '#FFFFFF'))
        style.configure('Sleeping.Module.TFrame', background=colors.get('info', '#17a2b8'), bordercolor=colors.get('light', '#FFFFFF'))
    def draw_watermark(self):
        self.hide_watermark()
        if not self.canvas.winfo_exists():
            return
        if not self.canvas_manager.canvas_nodes:
            self.canvas.update_idletasks()
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            if canvas_width <= 1 or canvas_height <= 1:
                self.canvas_manager.coordinator_tab.after(100, self.draw_watermark)
                return
            x = canvas_width / 2
            y = canvas_height / 2
            self._watermark_id = self.canvas.create_text(
                x, y,
                text="WWW.TEETAH.ART",
                font=("Helvetica", int(min(canvas_width, canvas_height) * 0.15), "bold"),
                fill="#3a3a3a",
                state="disabled",
                tags="watermark_tag",
                anchor="center"
            )
            self.canvas.tag_lower(self._watermark_id)
    def hide_watermark(self):
        if self._watermark_id:
            if self.canvas.winfo_exists() and self.canvas.find_withtag(self._watermark_id):
                self.canvas.delete(self._watermark_id)
            self._watermark_id = None
    def start_processing_animation(self, node_id):
        self.stop_processing_animation(node_id)
        if node_id not in self.canvas_manager.canvas_nodes: return
        node_widget = self.canvas_manager.canvas_nodes[node_id]['widget']
        if not node_widget.winfo_exists(): return
        light_length = 30
        light_thickness = 4
        color = self.canvas_manager.colors.get('warning', '#ffc107')
        x = node_widget.winfo_x()
        y = node_widget.winfo_y()
        light_id = self.canvas.create_rectangle(
            x, y - light_thickness / 2, x + light_length, y + light_thickness / 2,
            fill=color,
            outline=""
        )
        self.canvas.tag_raise(light_id)
        self.processing_animations[node_id] = {
            "light_id": light_id,
            "after_id": None,
            "position": 0,
            "speed": 5,
            "length": light_length,
            "thickness": light_thickness
        }
        self._animate_processing_border(node_id)
    def _animate_processing_border(self, node_id):
        if node_id not in self.processing_animations:
            return
        animation_data = self.processing_animations[node_id]
        light_id = animation_data['light_id']
        node_widget = self.canvas_manager.canvas_nodes.get(node_id, {}).get('widget')
        if not self.canvas.find_withtag(light_id) or not node_widget or not node_widget.winfo_exists():
            self.stop_processing_animation(node_id)
            return
        x, y = node_widget.winfo_x(), node_widget.winfo_y()
        w, h = node_widget.winfo_width(), node_widget.winfo_height()
        perimeter = (w * 2) + (h * 2)
        if perimeter == 0:
            after_id = self.canvas.after(50, self._animate_processing_border, node_id)
            animation_data['after_id'] = after_id
            return
        pos = (animation_data['position'] + animation_data['speed']) % perimeter
        animation_data['position'] = pos
        length = animation_data['length']
        thickness = animation_data['thickness']
        half_thick = thickness / 2
        if 0 <= pos < w:
            x1, y1 = x + pos, y - half_thick
            x2, y2 = x + pos - length, y + half_thick
            self.canvas.coords(light_id, x1, y1, x2, y2)
        elif w <= pos < w + h:
            x1, y1 = x + w - half_thick, y + (pos - w)
            x2, y2 = x + w + half_thick, y + (pos - w) - length
            self.canvas.coords(light_id, x1, y1, x2, y2)
        elif w + h <= pos < w + h + w:
            x1, y1 = x + w - (pos - (w + h)), y + h - half_thick
            x2, y2 = x + w - (pos - (w + h)) + length, y + h + half_thick
            self.canvas.coords(light_id, x1, y1, x2, y2)
        else:
            x1, y1 = x - half_thick, y + h - (pos - (w + h + w))
            x2, y2 = x + half_thick, y + h - (pos - (w + h + w)) + length
            self.canvas.coords(light_id, x1, y1, x2, y2)
        if node_id in self.processing_animations:
            after_id = self.canvas.after(20, self._animate_processing_border, node_id)
            self.processing_animations[node_id]['after_id'] = after_id
    def stop_processing_animation(self, node_id):
        if node_id in self.processing_animations:
            animation_data = self.processing_animations.pop(node_id)
            after_id = animation_data.get('after_id')
            if after_id:
                try:
                    self.canvas.after_cancel(after_id)
                except TclError:
                    pass
            if self.canvas.winfo_exists() and self.canvas.find_withtag(animation_data['light_id']):
                self.canvas.delete(animation_data['light_id'])
    def highlight_timeline_step(self, connection_id_to_highlight):
        self.clear_timeline_highlight()
        if connection_id_to_highlight in self.canvas_manager.canvas_connections:
            line_id = self.canvas_manager.canvas_connections[connection_id_to_highlight]['line_id']
            if self.canvas.find_withtag(line_id):
                colors = self.canvas_manager.colors
                highlight_color = colors.get('info', '#17a2b8')
                self.canvas.itemconfig(line_id, fill=highlight_color, width=4, dash=())
                self._last_timeline_highlight_id = line_id
    def clear_timeline_highlight(self):
        if self._last_timeline_highlight_id:
            if self.canvas.find_withtag(self._last_timeline_highlight_id):
                colors = self.canvas_manager.colors
                original_color = colors.get('success', '#76ff7b')
                self.canvas.itemconfig(self._last_timeline_highlight_id, fill=original_color, width=2, dash=(4, 4))
            self._last_timeline_highlight_id = None
    def show_suggestion_indicator(self, node_id, suggestion_text):
        self.hide_suggestion_indicator(node_id)
        canvas_nodes = self.canvas_manager.canvas_nodes
        if node_id not in canvas_nodes: return
        node_widget = canvas_nodes[node_id].get("widget")
        if not node_widget or not node_widget.winfo_exists(): return
        indicator_label = ttk.Label(node_widget, text="💡", font=("Segoe UI Emoji", 10), bootstyle="warning")
        indicator_label.place(relx=1.0, rely=0.0, x=-5, y=-5, anchor="ne")
        ToolTip(indicator_label).update_text(suggestion_text)
        self.suggestion_indicators[node_id] = indicator_label
    def hide_suggestion_indicator(self, node_id):
        if node_id in self.suggestion_indicators:
            indicator = self.suggestion_indicators.pop(node_id)
            if indicator and indicator.winfo_exists(): indicator.destroy()
    def clear_all_suggestion_indicators(self):
        for node_id in list(self.suggestion_indicators.keys()): self.hide_suggestion_indicator(node_id)
    def highlight_element(self, element_type, element_id):
        self.stop_sleeping_animation(element_id)
        if element_type == 'node':
            self.start_processing_animation(element_id)
        elif element_type == 'tool_node':
            if element_id not in self.canvas_manager.canvas_nodes: return
            node_data = self.canvas_manager.canvas_nodes[element_id]
            widget = node_data.get('widget')
            if not widget or not widget.winfo_exists(): return
            original_style = self._get_original_style(element_id)
            self.canvas_manager.node_manager._apply_style_to_node_widgets(element_id, "Executing.Module.TFrame")
            self.canvas.after(1500, lambda: self.canvas_manager.node_manager._apply_style_to_node_widgets(element_id, original_style))
        elif element_type == 'sleeping_node':
            if element_id not in self.canvas_manager.canvas_nodes: return
            widget = self.canvas_manager.canvas_nodes[element_id]['widget']
            if widget.cget('style') == 'Selected.Module.TFrame': return
            widget.config(style='Sleeping.Module.TFrame')
            self.start_sleeping_animation(element_id)
        elif element_type == 'connection':
            if element_id not in self.canvas_manager.canvas_connections: return
            line_id = self.canvas_manager.canvas_connections[element_id]['line_id']
            colors = self.canvas_manager.colors
            original_color = colors.get('success', '#76ff7b')
            highlight_color = colors.get('warning', '#ffc107')
            self.canvas.itemconfig(line_id, fill=highlight_color, width=3, dash=())
            self.canvas_manager.coordinator_tab.after(1500, lambda: self.canvas.itemconfig(line_id, fill=original_color, width=2) if self.canvas.find_withtag(line_id) else None)
    def update_node_status(self, node_id, message, level):
        if node_id not in self.canvas_manager.canvas_nodes: return
        if level.upper() in ["SUCCESS", "ERROR", "WARN"]:
            self.stop_processing_animation(node_id)
        node_frame = self.canvas_manager.canvas_nodes[node_id]['widget']
        if node_id in self._sleeping_animation_jobs and "jeda" not in message.lower() and "sleep" not in message.lower():
            self.stop_sleeping_animation(node_id)
        try:
            if not node_frame.winfo_exists():
                return
            content_frame = node_frame.winfo_children()[0]
            status_label = next((w for w in content_frame.winfo_children() if isinstance(w, ttk.Label) and 'status_' in w.winfo_name()), None)
            if status_label:
                if not hasattr(node_frame, '_original_status_message') or (status_label.cget("text").replace(" |", "").replace(" /", "").replace(" -", "").replace(" \\", "").strip() != message.strip()):
                    node_frame._original_status_message = message
                colors = self.canvas_manager.colors
                color_map = {"SUCCESS": colors.get('success'), "ERROR": colors.get('danger'), "WARN": colors.get('warning'), "INFO": colors.get('info'), "DEBUG": colors.get('secondary')}
                current_style = node_frame.cget('style')
                if current_style == 'Selected.Glass.Module.TFrame': bg_color, fg_color = colors.get('dark'), colors.get('success')
                elif current_style == 'Hover.Glass.Module.TFrame': bg_color, fg_color = colors.get('dark'), colors.get('info')
                elif current_style == 'Executing.Module.TFrame': bg_color, fg_color = colors.get('warning'), colors.get('dark')
                elif current_style == 'Sleeping.Module.TFrame': bg_color, fg_color = colors.get('info'), colors.get('light')
                else: bg_color, fg_color = colors.get('dark'), colors.get('fg')
                status_label.config(text=message, foreground=color_map.get(level, fg_color), background=bg_color)
        except (TclError, IndexError): pass
    def start_sleeping_animation(self, node_id):
        self.stop_sleeping_animation(node_id)
        node_data = self.canvas_manager.canvas_nodes.get(node_id)
        if not node_data or not node_data['widget'].winfo_exists(): return
        status_label = next((w for w in node_data['widget'].winfo_children()[0].winfo_children() if isinstance(w, ttk.Label) and 'status_' in w.winfo_name()), None)
        if not status_label: return
        if not hasattr(node_data['widget'], '_original_status_message'):
            node_data['widget']._original_status_message = status_label.cget("text")
        self._update_sleeping_animation_frame(node_id, 0)
    def _update_sleeping_animation_frame(self, node_id, frame_index):
        node_data = self.canvas_manager.canvas_nodes.get(node_id)
        if not node_data or not node_data['widget'].winfo_exists():
            self.stop_sleeping_animation(node_id)
            return
        status_label = next((w for w in node_data['widget'].winfo_children()[0].winfo_children() if isinstance(w, ttk.Label) and 'status_' in w.winfo_name()), None)
        if not status_label: return
        original_msg = getattr(node_data['widget'], '_original_status_message', "")
        animated_char = self._animation_frames[frame_index % len(self._animation_frames)]
        status_label.config(text=f"{original_msg} {animated_char}")
        next_frame_index = (frame_index + 1) % len(self._animation_frames)
        job_id = self.canvas_manager.coordinator_tab.after(150, self._update_sleeping_animation_frame, node_id, next_frame_index)
        self._sleeping_animation_jobs[node_id] = job_id
    def stop_sleeping_animation(self, node_id):
        if node_id in self._sleeping_animation_jobs:
            self.canvas_manager.coordinator_tab.after_cancel(self._sleeping_animation_jobs[node_id])
            del self._sleeping_animation_jobs[node_id]
            node_data = self.canvas_manager.canvas_nodes.get(node_id)
            if node_data and node_data['widget'].winfo_exists():
                status_label = next((w for w in node_data['widget'].winfo_children()[0].winfo_children() if isinstance(w, ttk.Label) and 'status_' in w.winfo_name()), None)
                if status_label:
                    status_label.config(text=getattr(node_data['widget'], '_original_status_message', status_label.cget("text").rstrip(' |/-\\')))

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\canvas_components\interactions\__init__.py
# JUMLAH BARIS : 12
#######################################################################

```py
from flowork_gui.api_client.client import ApiClient

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\Users\User\Desktop\FLOWORK\flowork_kernel\ui_shell\canvas_components\interactions\__init__.py
# JUMLAH BARIS : 14
#######################################################################




```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\canvas_components\interactions\canvas_navigation_handler.py
# JUMLAH BARIS : 60
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\canvas_components\interactions\canvas_navigation_handler.py
# JUMLAH BARIS : 59
#######################################################################

from flowork_gui.api_client.client import ApiClient
class CanvasNavigationHandler:
    def __init__(self, canvas_manager):
        self.api_client = ApiClient()
        self.canvas_manager = canvas_manager
        self.canvas = self.canvas_manager.canvas
        self.zoom_level = 1.0
        self.zoom_step = 0.1
    def on_pan_start(self, event):
        """Marks the starting point for panning the canvas."""
        self.canvas.scan_mark(event.x, event.y)
        self.canvas.config(cursor="fleur")
    def on_pan_move(self, event):
        """Moves the canvas based on mouse movement."""
        self.canvas.scan_dragto(event.x, event.y, gain=1)
    def on_pan_end(self, event):
        """Resets the cursor when panning ends."""
        self.canvas.config(cursor="")
        self.canvas.delete("grid_dot")
        self.canvas_manager.visual_manager.draw_grid()
    def apply_zoom(self):
        """Applies the current zoom level to all canvas elements."""
        for node_id, node_data in self.canvas_manager.canvas_nodes.items():
            original_x, original_y = node_data['x'], node_data['y']
            scaled_x = original_x * self.zoom_level
            scaled_y = original_y * self.zoom_level
            if node_data['widget'].winfo_exists():
                node_data['widget'].place(x=scaled_x, y=scaled_y)
        for node_id in self.canvas_manager.canvas_nodes.keys():
            self.canvas_manager.connection_manager.update_connections_for_node(node_id)
    def zoom_in(self, event=None):
        """Increases the zoom level."""
        self.zoom_level += self.zoom_step
        self.apply_zoom()
        self.canvas_manager.parent_widget.update_zoom_label()
    def zoom_out(self, event=None):
        """Decreases the zoom level."""
        self.zoom_level = max(0.2, self.zoom_level - self.zoom_step)
        self.apply_zoom()
        self.canvas_manager.parent_widget.update_zoom_label()
    def reset_zoom(self, event=None):
        """Resets the zoom level to 100%."""
        self.zoom_level = 1.0
        self.apply_zoom()
        self.canvas_manager.parent_widget.update_zoom_label()
    def handle_zoom_event(self, event):
        """Handles zoom events from the mouse wheel."""
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
        return "break"

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\canvas_components\interactions\connection_interaction_handler.py
# JUMLAH BARIS : 163
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\canvas_components\interactions\connection_interaction_handler.py
# JUMLAH BARIS : 162
#######################################################################

from tkinter import Menu, Toplevel, scrolledtext, messagebox
import json
import ttkbootstrap as ttk
from flowork_gui.api_client.client import ApiClient
class _ConnectionDataPopup(Toplevel):
    """(ADDED) A dedicated popup to display the payload from a connection."""
    def __init__(self, parent, kernel, title, data_to_display):
        self.api_client = ApiClient()
        super().__init__(parent)
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        self.title(title)
        self.geometry("600x450")
        self.transient(parent)
        self.grab_set()
        try:
            pretty_data = json.dumps(data_to_display, indent=4, ensure_ascii=False, default=str)
        except Exception:
            pretty_data = str(data_to_display)
        txt_area = scrolledtext.ScrolledText(self, wrap="word", width=70, height=20, font=("Consolas", 10))
        txt_area.pack(expand=True, fill="both", padx=10, pady=10)
        txt_area.insert("1.0", pretty_data)
        txt_area.config(state="disabled")
        self.wait_window(self)
class ConnectionInteractionHandler:
    def __init__(self, canvas_manager):
        self.canvas_manager = canvas_manager
        self.kernel = self.canvas_manager.kernel
        self.canvas = self.canvas_manager.canvas
        self.loc = self.kernel.get_service("localization_manager")
        self._line_data = {"start_node_id": None, "line_id": None, "source_port_name": None, "connection_type": "data"}
        self._highlighted_nodes = []
    def start_line_drawing(self, node_id, port_name=None, port_type='output'):
        if node_id not in self.canvas_manager.canvas_nodes: return
        self.canvas_manager.interaction_manager._reset_all_actions()
        self._line_data["start_node_id"] = node_id
        self._line_data["source_port_name"] = port_name
        self._line_data["connection_type"] = port_type
        port_list_key = f"{port_type}_ports"
        port_list = self.canvas_manager.canvas_nodes[node_id].get(port_list_key, [])
        port_widget = next((p['widget'] for p in port_list if p['name'] == port_name), None)
        if not port_widget:
            start_node_widget = self.canvas_manager.canvas_nodes[node_id]["widget"]
            start_x = start_node_widget.winfo_rootx() - self.canvas.winfo_rootx() + start_node_widget.winfo_width()/2
            start_y = start_node_widget.winfo_rooty() - self.canvas.winfo_rooty() + start_node_widget.winfo_height()/2
        else:
            start_x = port_widget.winfo_rootx() - self.canvas.winfo_rootx() + port_widget.winfo_width()/2
            start_y = port_widget.winfo_rooty() - self.canvas.winfo_rooty() + port_widget.winfo_height()/2
        self._line_data["line_id"] = self.canvas.create_line(start_x, start_y, start_x, start_y, fill=self.canvas_manager.colors['success'], width=2, dash=(4, 4))
        self._highlight_valid_target_nodes(node_id)
    def finish_line_drawing(self, end_node_id, target_port_name=None, target_port_type='input'):
        start_node_id = self._line_data["start_node_id"]
        source_port_name = self._line_data.get("source_port_name")
        connection_type = self._line_data.get("connection_type", "data")
        module_manager = self.kernel.get_service("module_manager_service")
        start_node_manifest = module_manager.get_manifest(self.canvas_manager.canvas_nodes[start_node_id]['module_id'])
        is_source_brain = start_node_manifest.get('subtype') == 'BRAIN_PROVIDER'
        if is_source_brain and target_port_name != 'brain_port':
            self.kernel.write_to_log("Invalid Connection: Brain can only connect to a Brain Port.", "WARN")
            messagebox.showwarning("Invalid Connection", "A 'Brain' node can only be connected to the 'Brain' port of an Agent Host.", parent=self.canvas)
            self._cancel_line_drawing()
            return
        if target_port_type == 'tool':
            connection_type = 'tool'
        if start_node_id and start_node_id != end_node_id and start_node_id in self.canvas_manager.canvas_nodes and end_node_id in self.canvas_manager.canvas_nodes:
            self.canvas_manager.connection_manager.create_connection(
                start_node_id,
                end_node_id,
                source_port_name=source_port_name,
                target_port_name=target_port_name,
                connection_type=connection_type
            )
        self._cancel_line_drawing()
    def on_line_motion(self, event):
        if not self._line_data.get("line_id"): return
        start_node_id = self._line_data["start_node_id"]
        if start_node_id not in self.canvas_manager.canvas_nodes:
            self._cancel_line_drawing()
            return
        port_name = self._line_data.get("source_port_name")
        port_type = self._line_data.get("connection_type", "output")
        port_list_key = f"{port_type}_ports"
        port_list = self.canvas_manager.canvas_nodes[start_node_id].get(port_list_key, [])
        port_widget = next((p['widget'] for p in port_list if p['name'] == port_name), None)
        if not port_widget or not port_widget.winfo_exists():
             start_node_widget = self.canvas_manager.canvas_nodes[start_node_id]["widget"]
             start_x = start_node_widget.winfo_rootx() - self.canvas.winfo_rootx() + start_node_widget.winfo_width()/2
             start_y = start_node_widget.winfo_rooty() - self.canvas.winfo_rooty() + start_node_widget.winfo_height()/2
        else:
            start_x = port_widget.winfo_rootx() - self.canvas.winfo_rootx() + port_widget.winfo_width()/2
            start_y = port_widget.winfo_rooty() - self.canvas.winfo_rooty() + port_widget.winfo_height()/2
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        module_manager = self.kernel.get_service("module_manager_service")
        start_node_manifest = module_manager.get_manifest(self.canvas_manager.canvas_nodes[start_node_id]['module_id'])
        is_source_brain = start_node_manifest.get('subtype') == 'BRAIN_PROVIDER'
        hovered_item = self.canvas.find_closest(end_x, end_y)[0]
        hovered_tags = self.canvas.gettags(hovered_item)
        if is_source_brain and hovered_tags:
            hovered_node_id = next((tag for tag in hovered_tags if tag in self.canvas_manager.canvas_nodes), None)
            if hovered_node_id and self.canvas_manager.canvas_nodes[hovered_node_id].get('module_id') == 'agent_host_module':
                snap_x, snap_y = self.canvas_manager.connection_manager._get_port_widget_center(hovered_node_id, 'brain_port', 'tool')
                if snap_x is not None:
                    end_x, end_y = snap_x, snap_y
        self.canvas.coords(self._line_data["line_id"], start_x, start_y, end_x, end_y)
    def _cancel_line_drawing(self, event=None):
        if self._line_data.get("line_id"):
            if self.canvas.find_withtag(self._line_data["line_id"]):
                self.canvas.delete(self._line_data["line_id"])
        self._line_data = {"start_node_id": None, "line_id": None, "source_port_name": None, "connection_type": "data"}
        self._clear_node_highlights()
        return "break"
    def _highlight_valid_target_nodes(self, start_node_id):
        self._clear_node_highlights()
        for node_id, node_data in self.canvas_manager.canvas_nodes.items():
            if node_id != start_node_id:
                widget = node_data['widget']
                if widget.winfo_exists():
                    widget.config(style="Droppable.Module.TFrame")
                    self._highlighted_nodes.append(widget)
    def _clear_node_highlights(self):
        for widget in self._highlighted_nodes:
            if widget.winfo_exists():
                is_selected = self.canvas_manager.selected_node_id == widget.node_id
                widget.config(style="Selected.Module.TFrame" if is_selected else "Module.TFrame")
        self._highlighted_nodes = []
    def show_line_context_menu(self, event):
        current_items = self.canvas.find_withtag("current")
        if not current_items: return
        conn_id = next((cid for cid, cdata in self.canvas_manager.canvas_connections.items() if cdata['line_id'] == current_items[0]), None)
        if conn_id:
            context_menu = Menu(self.canvas, tearoff=0)
            context_menu.add_command(label="Lihat Data Terakhir...", command=lambda: self._show_connection_data_popup(conn_id))
            context_menu.add_separator()
            context_menu.add_command(label=self.loc.get('context_menu_delete_connection'), command=lambda: self.canvas_manager.connection_manager.delete_connection(conn_id))
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
    def _show_connection_data_popup(self, conn_id):
        history_data = self.canvas_manager.coordinator_tab.canvas_area_instance.execution_history
        if not history_data or not history_data.get('steps'):
            messagebox.showinfo("Info", "No execution history is available for this run.", parent=self.canvas)
            return
        data_for_this_conn = "No data recorded for this specific connection in the last run."
        for step in reversed(history_data['steps']):
            if step.get('connection_id') == conn_id:
                data_for_this_conn = step.get('payload', {})
                break
        _ConnectionDataPopup(
            parent=self.canvas,
            kernel=self.kernel,
            title=f"Data Preview for Connection",
            data_to_display=data_for_this_conn
        )

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\canvas_components\interactions\node_interaction_handler.py
# JUMLAH BARIS : 132
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\canvas_components\interactions\node_interaction_handler.py
# JUMLAH BARIS : 131
#######################################################################

from tkinter import Menu
from flowork_gui.api_client.client import ApiClient
class NodeInteractionHandler:
    """
    (REFACTORED) Handles all node-specific interactions like pressing, dragging, releasing, and context menus.
    This version is robust for both widget-based (rectangular) and canvas-item-based (circular) nodes.
    """
    def __init__(self, canvas_manager):
        self.canvas_manager = canvas_manager
        self.kernel = self.canvas_manager.kernel
        self.canvas = self.canvas_manager.canvas
        self.loc = self.kernel.get_service("localization_manager")
        self.api_client = ApiClient(kernel=self.kernel)
        self._move_data = {"id": None, "x": 0, "y": 0}
    def on_node_press(self, event):
        item_ids = self.canvas.find_withtag("current")
        node_id = None
        if item_ids:
            tags = self.canvas.gettags(item_ids[0])
            node_id = next((tag for tag in tags if tag in self.canvas_manager.canvas_nodes), None)
        if not node_id:
            widget = event.widget
            while widget and not hasattr(widget, 'node_id'):
                widget = widget.master
            if not widget: return
            node_id = widget.node_id
        connection_handler = self.canvas_manager.interaction_manager.connection_handler
        is_drawing_line = connection_handler._line_data.get("start_node_id") is not None
        if is_drawing_line:
            self.kernel.write_to_log("Logic Builder: Left-click detected on target node, finishing connection.", "DEBUG") # English Log
            target_port_name = getattr(event.widget, 'port_name', None)
            target_port_type = getattr(event.widget, 'port_type', 'input')
            connection_handler.finish_line_drawing(node_id, target_port_name, target_port_type)
            self._move_data = {"id": None, "x": 0, "y": 0}
            return
        self.canvas_manager.node_manager.select_node(node_id)
        if hasattr(event.widget, 'port_name'): return
        self._move_data["id"] = node_id
        self._move_data["x"] = self.canvas.canvasx(event.x)
        self._move_data["y"] = self.canvas.canvasy(event.y)
        return "break"
    def on_node_motion(self, event):
        if self._move_data.get("id"):
            node_id = self._move_data["id"]
            if node_id not in self.canvas_manager.canvas_nodes: return
            new_x = self.canvas.canvasx(event.x)
            new_y = self.canvas.canvasy(event.y)
            delta_x = new_x - self._move_data["x"]
            delta_y = new_y - self._move_data["y"]
            self.canvas_manager.node_manager.move_node_by_delta(node_id, delta_x, delta_y)
            self._move_data["x"] = new_x
            self._move_data["y"] = new_y
    def on_node_release(self, event):
        if self._move_data.get("id"):
            node_id = self._move_data["id"]
            if node_id in self.canvas_manager.canvas_nodes:
                zoom_level = self.canvas_manager.interaction_manager.navigation_handler.zoom_level
                bbox = self.canvas.bbox(node_id)
                if bbox:
                    scaled_x = bbox[0]
                    scaled_y = bbox[1]
                    self.canvas_manager.canvas_nodes[node_id]["x"] = scaled_x / zoom_level
                    self.canvas_manager.canvas_nodes[node_id]["y"] = scaled_y / zoom_level
            self._move_data = {"id": None, "x": 0, "y": 0}
    def on_delete_key_press(self, event=None):
        if self.canvas_manager.selected_node_id:
            self.canvas_manager.node_manager.delete_node(self.canvas_manager.selected_node_id)
            return "break"
    def show_node_context_menu(self, event):
        closest_items = self.canvas.find_closest(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        if not closest_items: return
        item_id = closest_items[0]
        tags = self.canvas.gettags(item_id)
        node_id = next((tag for tag in tags if tag in self.canvas_manager.canvas_nodes), None)
        if not node_id:
            widget = event.widget
            while widget and not hasattr(widget, 'node_id'):
                widget = widget.master
            if not widget: return
            node_id = widget.node_id
        self.canvas_manager.node_manager.select_node(node_id)
        context_menu = Menu(self.canvas, tearoff=0)
        context_menu.add_command(label=self.loc.get('context_menu_properties', fallback="Properties"), command=lambda: self.canvas_manager.properties_manager.open_properties_popup(node_id))
        context_menu.add_separator()
        line_data = self.canvas_manager.interaction_manager.connection_handler._line_data
        node_data = self.canvas_manager.canvas_nodes[node_id]
        start_conn_state = "normal" if not line_data["start_node_id"] else "disabled"
        finish_conn_state = "disabled" if not line_data["start_node_id"] else "normal"
        module_manager = self.kernel.get_service("module_manager_service")
        manifest = (module_manager.get_manifest(node_data.get("module_id")) if module_manager else {}) or {}
        has_any_output = False
        if node_data.get("output_ports"):
            has_any_output = True
            for port_data in node_data["output_ports"]:
                port_name = port_data.get("name")
                port_info = next((p for p in manifest.get('output_ports', []) if p['name'] == port_name), {'display_name': port_name.replace("_", " ").title()})
        if node_data.get("tool_ports"):
            has_any_output = True
            for port_data in node_data["tool_ports"]:
                port_name = port_data.get("name")
                port_info = next((p for p in manifest.get('tool_ports', []) if p['name'] == port_name), {'display_name': port_name.replace("_", " ").title()})
        if has_any_output:
            start_connection_menu = Menu(context_menu, tearoff=0) # ADDED: Create the menu only if needed
            if node_data.get("output_ports"):
                for port_data in node_data["output_ports"]:
                    port_name = port_data.get("name")
                    port_info = next((p for p in manifest.get('output_ports', []) if p['name'] == port_name), {'display_name': port_name.replace("_", " ").title()})
                    start_connection_menu.add_command(label=port_info.get("display_name"), command=lambda n=node_id, p=port_name: self.canvas_manager.interaction_manager.connection_handler.start_line_drawing(n, port_name=p, port_type='output'))
            if node_data.get("tool_ports"):
                if node_data.get("output_ports"):
                    start_connection_menu.add_separator()
                for port_data in node_data["tool_ports"]:
                    port_name = port_data.get("name")
                    port_info = next((p for p in manifest.get('tool_ports', []) if p['name'] == port_name), {'display_name': port_name.replace("_", " ").title()})
                    start_connection_menu.add_command(label=f"Connect to {port_info.get('display_name')}", command=lambda n=node_id, p=port_name: self.canvas_manager.interaction_manager.connection_handler.start_line_drawing(n, port_name=p, port_type='tool'))
            context_menu.add_cascade(label=self.loc.get('context_menu_start_connection', fallback="Start Connection"), menu=start_connection_menu, state=start_conn_state)
        context_menu.add_command(label=self.loc.get('context_menu_finish_connection', fallback="Finish Connection Here"), command=lambda: self.canvas_manager.interaction_manager.connection_handler.finish_line_drawing(node_id), state=finish_conn_state)
        context_menu.add_separator()
        context_menu.add_command(label=self.loc.get('context_menu_duplicate_node', fallback="Duplicate Node"), command=lambda: self.canvas_manager.node_manager.duplicate_node(node_id))
        context_menu.add_command(label=self.loc.get('context_menu_delete_node'), command=lambda: self.canvas_manager.node_manager.delete_node(node_id))
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\components\InfoLabel.py
# JUMLAH BARIS : 17
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\components\InfoLabel.py
# JUMLAH BARIS : 16
#######################################################################

import ttkbootstrap as ttk
from flowork_gui.api_client.client import ApiClient
class InfoLabel(ttk.Frame):
    def __init__(self, parent, text: str, **kwargs):
        self.api_client = ApiClient()
        super().__init__(parent, padding=10, **kwargs)
        label = ttk.Label(self, text=text, wraplength=350, justify='left', bootstyle="secondary")
        label.pack(fill='x')
        self.pack(fill='x', pady=5)

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\components\LabelledCombobox.py
# JUMLAH BARIS : 22
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\components\LabelledCombobox.py
# JUMLAH BARIS : 21
#######################################################################

import ttkbootstrap as ttk
from tkinter import StringVar
from flowork_gui.api_client.client import ApiClient
class LabelledCombobox(ttk.Frame):
    """A reusable widget that combines a Label and a Combobox."""
    def __init__(self, parent, label_text: str, variable: StringVar, values: list, **kwargs):
        self.api_client = ApiClient()
        super().__init__(parent, **kwargs)
        self.columnconfigure(1, weight=1)
        label = ttk.Label(self, text=label_text)
        label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        combobox = ttk.Combobox(self, textvariable=variable, values=values, state="readonly")
        combobox.grid(row=0, column=1, sticky="ew")
        self.pack(fill='x', pady=5)

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\components\PropertyField.py
# JUMLAH BARIS : 18
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\components\PropertyField.py
# JUMLAH BARIS : 17
#######################################################################

import ttkbootstrap as ttk
from flowork_gui.api_client.client import ApiClient
class PropertyField(ttk.Frame):
    def __init__(self, parent, label_text: str, variable, **kwargs):
        self.api_client = ApiClient()
        super().__init__(parent, **kwargs)
        self.columnconfigure(1, weight=1)
        ttk.Label(self, text=label_text).grid(row=0, column=0, sticky="w", padx=(0, 10))
        ttk.Entry(self, textvariable=variable).grid(row=0, column=1, sticky="ew")
        self.pack(fill='x', pady=5)

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\components\Separator.py
# JUMLAH BARIS : 15
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\components\Separator.py
# JUMLAH BARIS : 14
#######################################################################

import ttkbootstrap as ttk
from flowork_gui.api_client.client import ApiClient
class Separator(ttk.Separator):
    def __init__(self, parent, **kwargs):
        self.api_client = ApiClient()
        super().__init__(parent, orient='horizontal', **kwargs)
        self.pack(fill='x', pady=15, padx=5)

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\components\__init__.py
# JUMLAH BARIS : 12
#######################################################################

```py
from flowork_gui.api_client.client import ApiClient

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\Users\User\Desktop\FLOWORK\flowork_kernel\ui_shell\components\__init__.py
# JUMLAH BARIS : 14
#######################################################################




```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\custom_widgets\DualListbox.py
# JUMLAH BARIS : 68
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\custom_widgets\DualListbox.py
# JUMLAH BARIS : 67
#######################################################################

import ttkbootstrap as ttk
from tkinter import Listbox, ANCHOR, END
from flowork_gui.api_client.client import ApiClient
class DualListbox(ttk.Frame):
    """
    A reusable widget featuring two listboxes and buttons to move items between them.
    Encapsulates the logic for selecting items from an available pool.
    """
    def __init__(self, parent, kernel, available_items: list = None, selected_items: list = None, **kwargs):
        self.api_client = ApiClient()
        super().__init__(parent, **kwargs)
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        available_items = available_items or []
        selected_items = selected_items or []
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0) # Button column should not expand
        self.columnconfigure(2, weight=1)
        self.rowconfigure(1, weight=1)
        ttk.Label(self, text=self.loc.get('duallist_available', fallback="Tersedia")).grid(row=0, column=0, sticky='w', padx=5)
        ttk.Label(self, text=self.loc.get('duallist_selected', fallback="Terpilih")).grid(row=0, column=2, sticky='w', padx=5)
        self.available_listbox = Listbox(self, selectmode='extended', exportselection=False)
        self.available_listbox.grid(row=1, column=0, sticky='nsew', padx=(0, 5))
        self.selected_listbox = Listbox(self, selectmode='extended', exportselection=False)
        self.selected_listbox.grid(row=1, column=2, sticky='nsew', padx=(5, 0))
        for item in sorted(list(set(available_items) - set(selected_items))):
            self.available_listbox.insert(END, item)
        for item in selected_items:
            self.selected_listbox.insert(END, item)
        button_frame = ttk.Frame(self)
        button_frame.grid(row=1, column=1, padx=10, sticky='ns')
        ttk.Button(button_frame, text=">", command=self._move_to_selected).pack(pady=5)
        ttk.Button(button_frame, text=">>", command=self._move_all_to_selected).pack(pady=5)
        ttk.Button(button_frame, text="<", command=self._move_to_available).pack(pady=5)
        ttk.Button(button_frame, text="<<", command=self._move_all_to_available).pack(pady=5)
    def _move_to_selected(self):
        selected_indices = self.available_listbox.curselection()
        for i in reversed(selected_indices):
            item = self.available_listbox.get(i)
            self.selected_listbox.insert(END, item)
            self.available_listbox.delete(i)
    def _move_all_to_selected(self):
        items = self.available_listbox.get(0, END)
        for item in items:
            self.selected_listbox.insert(END, item)
        self.available_listbox.delete(0, END)
    def _move_to_available(self):
        selected_indices = self.selected_listbox.curselection()
        for i in reversed(selected_indices):
            item = self.selected_listbox.get(i)
            self.available_listbox.insert(END, item)
            self.selected_listbox.delete(i)
    def _move_all_to_available(self):
        items = self.selected_listbox.get(0, END)
        for item in items:
            self.available_listbox.insert(END, item)
        self.selected_listbox.delete(0, END)
    def get_selected_items(self) -> list:
        """Returns the final list of items in the 'selected' box."""
        return list(self.selected_listbox.get(0, END))

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\custom_widgets\StandardButtons.py
# JUMLAH BARIS : 36
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\custom_widgets\StandardButtons.py
# JUMLAH BARIS : 35
#######################################################################

import ttkbootstrap as ttk
from flowork_gui.api_client.client import ApiClient
class StandardButton(ttk.Button):
    def __init__(self, parent, kernel, **kwargs):
        self.api_client = ApiClient()
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        super().__init__(parent, **kwargs)
class SaveButton(StandardButton):
    """A standard Save button that automatically gets its text and success style."""
    def __init__(self, parent, kernel, **kwargs):
        text = kernel.get_service("localization_manager").get('button_save', fallback="Simpan")
        super().__init__(parent, kernel, text=text, bootstyle="success", **kwargs)
class CancelButton(StandardButton):
    """A standard Cancel button that automatically gets its text and secondary style."""
    def __init__(self, parent, kernel, **kwargs):
        text = kernel.get_service("localization_manager").get('button_cancel', fallback="Batal")
        super().__init__(parent, kernel, text=text, bootstyle="secondary", **kwargs)
class DeleteButton(StandardButton):
    """A standard Delete button that automatically gets its text and danger style."""
    def __init__(self, parent, kernel, **kwargs):
        text = kernel.get_service("localization_manager").get('trigger_btn_delete', fallback="Hapus")
        super().__init__(parent, kernel, text=text, bootstyle="danger", **kwargs)
class EditButton(StandardButton):
    """A standard Edit button that automatically gets its text and info style."""
    def __init__(self, parent, kernel, **kwargs):
        text = kernel.get_service("localization_manager").get('trigger_btn_edit', fallback="Edit...")
        super().__init__(parent, kernel, text=text, bootstyle="info", **kwargs)

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\custom_widgets\__init__.py
# JUMLAH BARIS : 12
#######################################################################

```py
from flowork_gui.api_client.client import ApiClient

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\Users\User\Desktop\FLOWORK\flowork_kernel\ui_shell\custom_widgets\__init__.py
# JUMLAH BARIS : 14
#######################################################################




```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\custom_widgets\draggable_notebook.py
# JUMLAH BARIS : 77
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\custom_widgets\draggable_notebook.py
# JUMLAH BARIS : 76
#######################################################################

import ttkbootstrap as ttk
from tkinter import TclError, Menu, messagebox
from tkinter import ttk as tk_ttk
from flowork_gui.api_client.client import ApiClient
class DraggableNotebook(tk_ttk.Notebook):
    def __init__(self, master=None, **kw):
        self.api_client = ApiClient()
        self.loc = kw.pop('loc', None)
        super().__init__(master, **kw)
        self.bind("<ButtonPress-1>", self.on_tab_press, True)
        self.bind("<B1-Motion>", self.on_mouse_drag)
        self.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.drag_data = {"x": 0, "y": 0, "item": None, "tab_id": None}
        self.bind("<ButtonPress-3>", self.show_context_menu)
        self._close_tab_command = None
    def set_close_tab_command(self, command):
        self._close_tab_command = command
    def on_tab_press(self, event):
        try:
            index = self.index(f"@{event.x},{event.y}")
            if index == "":
                self.drag_data["item"] = None
                return
            tab_id = self.tabs()[index]
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            self.drag_data["item"] = index
            self.drag_data["tab_id"] = tab_id
        except TclError:
            self.drag_data["item"] = None
    def on_mouse_drag(self, event):
        if self.drag_data["item"] is not None:
            tab_id_to_move = self.drag_data["tab_id"]
            try:
                target_index = self.index(f"@{event.x},{event.y}")
                if target_index != "" and self.drag_data["item"] != target_index:
                    self.insert(target_index, tab_id_to_move)
                    self.drag_data["item"] = target_index
            except TclError:
                pass
    def on_mouse_release(self, event):
        self.drag_data = {"x": 0, "y": 0, "item": None, "tab_id": None}
    def show_context_menu(self, event):
        try:
            index = self.index(f"@{event.x},{event.y}")
            if index == "": return
            tab_id = self.tabs()[index]
            context_menu = Menu(self, tearoff=0)
            context_menu.add_command(label=self.loc.get('context_menu_rename_tab', fallback="Rename Tab"), command=lambda: self.rename_tab(index))
            if self._close_tab_command:
                if len(self.tabs()) > 1:
                    context_menu.add_command(label=self.loc.get('menu_close_tab', fallback="Close Tab"), command=lambda: self._close_tab_command(tab_id))
                else:
                    context_menu.add_command(label=self.loc.get('menu_close_tab', fallback="Close Tab"), state='disabled')
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
        except TclError:
            pass
    def rename_tab(self, index):
        current_name = self.tab(index, "text").strip()
        new_name = ttk.dialogs.dialogs.Querybox.get_string(
            title=self.loc.get('rename_tab_popup_title', fallback="Rename Tab"),
            prompt=self.loc.get('rename_tab_popup_label', fallback="Enter new name:"),
            initialvalue=current_name
        )
        if new_name and new_name.strip() != "":
            self.tab(index, text=f" {new_name.strip()} ")

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\custom_widgets\scrolled_frame.py
# JUMLAH BARIS : 49
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\custom_widgets\scrolled_frame.py
# JUMLAH BARIS : 48
#######################################################################

import ttkbootstrap as ttk
from flowork_gui.api_client.client import ApiClient
class ScrolledFrame(ttk.Frame):
    """
    A reusable frame that includes a vertical scrollbar.
    Widgets should be packed into the .scrollable_frame attribute.
    """
    def __init__(self, parent, *args, **kwargs):
        self.api_client = ApiClient()
        super().__init__(parent, *args, **kwargs)
        self.vscrollbar = ttk.Scrollbar(self, orient="vertical")
        self.vscrollbar.pack(fill="y", side="right", expand=False)
        self.canvas = ttk.Canvas(self, bd=0, highlightthickness=0,
                           yscrollcommand=self.vscrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.vscrollbar.config(command=self.canvas.yview)
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.interior_id = self.canvas.create_window(0, 0, window=self.scrollable_frame,
                                       anchor="nw")
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
    def destroy(self):
        """
        Custom destroy method to safely unlink canvas and scrollbar before destruction.
        This prevents race conditions and the 'invalid command name' TclError.
        """
        if self.canvas.winfo_exists():
            self.canvas.configure(yscrollcommand='')
        if self.vscrollbar.winfo_exists():
            self.vscrollbar.configure(command='')
        super().destroy()
    def _on_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        if self.canvas.winfo_exists():
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
    def _on_canvas_configure(self, event):
        """Use the canvas width to configure the inner frame's width"""
        if self.canvas.winfo_exists():
            self.canvas.itemconfig(self.interior_id, width=event.width)

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\custom_widgets\tooltip.py
# JUMLAH BARIS : 54
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\custom_widgets\tooltip.py
# JUMLAH BARIS : 53
#######################################################################

import ttkbootstrap as ttk
from tkinter import TclError
from flowork_gui.api_client.client import ApiClient
class ToolTip:
    """Membuat tooltip (hover text) untuk sebuah widget."""
    def __init__(self, widget):
        self.api_client = ApiClient()
        self.widget = widget
        self.text = "" # Inisialisasi dengan string kosong
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip_window = tw = ttk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        try:
            colors = self.widget.winfo_toplevel().kernel.theme_manager.get_colors()
            bg_color = colors.get('bg', '#222222')
            fg_color = colors.get('fg', '#FFFFFF')
        except (AttributeError, TclError):
            bg_color="#222222"
            fg_color = "#FFFFFF"
        label = ttk.Label(
            tw,
            text=self.text,
            justify='left',
            background=bg_color,
            foreground=fg_color,
            relief='solid',
            borderwidth=1,
            font=("tahoma", "8", "normal"),
            padding=4
        )
        label.pack(ipadx =1)
    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window= None
    def update_text(self, new_text):
        self.text = new_text

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\lifecycle\AppLifecycleHandler.py
# JUMLAH BARIS : 124
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\lifecycle\AppLifecycleHandler.py
# JUMLAH BARIS : 123
#######################################################################

from tkinter import messagebox
import logging
import threading
from PIL import Image
import pystray
import sys
import os
import shutil # (DITAMBAHKAN) Butuh ini untuk hapus folder
from flowork_gui.api_client.client import ApiClient
class AppLifecycleHandler:
    def __init__(self, main_window, kernel):
        self.api_client = ApiClient()
        self.main_window = main_window
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        self.tray_icon = None
        self.tray_thread = None
        event_bus = self.kernel.get_service("event_bus")
        if event_bus:
            event_bus.subscribe("RESTART_APP", "lifecycle_handler_restart", self._on_restart_request)
            event_bus.subscribe("RESTART_APP_AFTER_UPDATE", "lifecycle_handler_update_restart", self._on_restart_request)
            event_bus.subscribe("REQUEST_CLEANUP_AND_EXIT", "lifecycle_handler_deactivation", self._on_cleanup_and_exit_request)
            self.kernel.write_to_log("LifecycleHandler is now listening for RESTART and EXIT events.", "INFO")
    def on_closing_app(self):
        self.main_window.withdraw()
        self._create_or_show_tray_icon()
    def _on_restart_request(self, event_data=None):
        """Handles the application restart logic triggered by an event."""
        self.kernel.write_to_log("Restart request received via EventBus. Initiating shutdown...", "WARN")
        self.kernel.stop_all_services()
        self.main_window.destroy()
        os.execl(sys.executable, sys.executable, *sys.argv)
        sys.exit(0)
    def _on_cleanup_and_exit_request(self, event_data=None):
        """Handles the full cleanup and exit process after a license deactivation."""
        self.kernel.write_to_log("Cleanup and Exit request received. Starting process...", "WARN")
        self.main_window.after(100, self._perform_safe_cleanup_and_exit)
    def _perform_safe_cleanup_and_exit(self):
        """Contains the actual logic for clearing cache and then exiting."""
        self.kernel.write_to_log("Performing cache cleanup...", "INFO")
        deleted_folders, deleted_files = 0, 0
        current_log_file = None
        if self.kernel.file_logger and self.kernel.file_logger.handlers:
            current_log_file = self.kernel.file_logger.handlers[0].baseFilename
        for root, dirs, files in os.walk(self.kernel.project_root_path, topdown=False):
            if '__pycache__' in dirs:
                pycache_path = os.path.join(root, '__pycache__')
                try:
                    shutil.rmtree(pycache_path)
                    deleted_folders += 1
                except (OSError, PermissionError):
                    self.kernel.write_to_log(f"Could not delete cache folder (in use): {os.path.basename(pycache_path)}", "WARN")
            for name in files:
                if name.endswith(".pyc") or name.endswith(".log"):
                    file_path = os.path.join(root, name)
                    if file_path == current_log_file:
                        continue
                    try:
                        os.remove(file_path)
                        deleted_files += 1
                    except (OSError, PermissionError):
                        pass # Ignore if file is locked
        self.kernel.write_to_log(f"Cache cleanup finished. Deleted {deleted_folders} folders and {deleted_files} files.", "SUCCESS")
        self._perform_safe_exit(ask_confirmation=False) # Langsung keluar tanpa tanya lagi
    def _create_or_show_tray_icon(self):
        """Creates and runs the system tray icon in a separate thread if it's not already running."""
        if self.tray_thread and self.tray_thread.is_alive():
            return
        try:
            image = Image.open("flowork-icon.ico")
        except FileNotFoundError:
            self.kernel.write_to_log("System tray icon.png not found, using placeholder.", "ERROR")
            image = Image.new('RGB', (64, 64), color = 'blue')
        menu = (
            pystray.MenuItem(
                self.loc.get('tray_menu_show', fallback='Show Flowork'),
                self._show_window,
                default=True
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                self.loc.get('tray_menu_exit', fallback='Exit Flowork'),
                lambda: self._exit_app(ask_confirmation=True) # (MODIFIKASI) Panggil dengan konfirmasi
            )
        )
        self.tray_icon = pystray.Icon("flowork", image, "Flowork", menu)
        self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        self.tray_thread.start()
        self.kernel.write_to_log("Application minimized to system tray.", "INFO")
    def _show_window(self):
        """Shows the main window when the tray icon option is clicked."""
        if self.tray_icon:
            self.tray_icon.stop()
        self.main_window.after(0, self.main_window.deiconify)
    def _perform_safe_exit(self, ask_confirmation=True):
        """This method contains the actual shutdown logic and is designed to be called on the main UI thread."""
        should_save = True
        if ask_confirmation:
            should_save = messagebox.askyesnocancel(
                self.loc.get('confirm_exit_title', fallback="Exit Application"),
                self.loc.get('confirm_exit_save_workflow_message', fallback="Do you want to save your work before exiting?")
            )
        if should_save is None:
            self.kernel.write_to_log("Exit process cancelled by user.", "INFO")
            return
        if should_save:
            self.main_window.save_layout_and_session()
        self.kernel.write_to_log("Application exit initiated.", "INFO")
        self.kernel.stop_all_services()
        self.main_window.destroy()
        sys.exit(0)
    def _exit_app(self, ask_confirmation=True):
        """The real exit logic for the application."""
        if self.tray_icon:
            self.tray_icon.stop()
        self.main_window.after(0, self._perform_safe_exit, ask_confirmation)

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\popups\NotificationManager.py
# JUMLAH BARIS : 52
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\popups\NotificationManager.py
# JUMLAH BARIS : 51
#######################################################################

from .NotificationToast import NotificationToast
from flowork_gui.api_client.client import ApiClient
class NotificationManager:
    """
    Manages the queue, positioning, and appearance of multiple NotificationToasts.
    """
    def __init__(self, main_window, kernel):
        self.api_client = ApiClient()
        self.main_window = main_window
        self.kernel = kernel
        self.active_toasts = []
        self.padding = 10  # Jarak antar popup dan dari tepi layar
        self.toast_width = 300
        self.toast_height = 80
    def show_toast(self, title, message, level="INFO"):
        """Fungsi utama untuk menampilkan notifikasi baru."""
        loc = self.kernel.get_service("localization_manager")
        if not loc:
            return
        if not loc.get_setting("notifications_enabled", True):
            return # Jangan tampilkan jika dinonaktifkan di pengaturan
        duration_seconds = loc.get_setting("notifications_duration_seconds", 5)
        duration_ms = int(duration_seconds * 1000)
        toast = NotificationToast(self.main_window, title, message, level, duration=duration_ms)
        self.active_toasts.append(toast)
        self._reposition_toasts()
        self.main_window.after(duration_ms + 1000, lambda: self._remove_toast_from_list(toast))
    def _reposition_toasts(self):
        """Menghitung ulang dan mengatur posisi semua toast yang aktif."""
        if not self.main_window.winfo_exists():
            return
        screen_width = self.main_window.winfo_screenwidth()
        screen_height = self.main_window.winfo_screenheight()
        start_x = screen_width - self.toast_width - self.padding
        current_y = screen_height - self.toast_height - self.padding
        for toast in self.active_toasts:
            if toast.winfo_exists():
                toast.set_position(start_x, current_y)
                current_y -= (self.toast_height + self.padding)
    def _remove_toast_from_list(self, toast_to_remove):
        """Menghapus referensi toast dari daftar setelah animasinya selesai."""
        if toast_to_remove in self.active_toasts:
            self.active_toasts.remove(toast_to_remove)
        self._reposition_toasts()

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\popups\NotificationToast.py
# JUMLAH BARIS : 61
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\popups\NotificationToast.py
# JUMLAH BARIS : 60
#######################################################################

import ttkbootstrap as ttk
from tkinter import Toplevel
from flowork_gui.api_client.client import ApiClient
class NotificationToast(Toplevel):
    """
    Kelas untuk membuat jendela popup notifikasi (toast) yang bisa hilang otomatis.
    """
    def __init__(self, parent, title, message, level="INFO", duration=5000):
        self.api_client = ApiClient()
        super().__init__(parent)
        self.parent = parent
        self.duration = duration
        self.alpha = 0.0
        self.target_alpha = 0.9
        self.fade_step = 0.05
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.attributes('-alpha', self.alpha)
        style_map = {
            "SUCCESS": "success",
            "INFO": "info",
            "WARN": "warning",
            "ERROR": "danger"
        }
        bootstyle = style_map.get(level.upper(), "primary")
        main_frame = ttk.Frame(self, bootstyle=f"{bootstyle}.TFrame", padding=1, relief="solid")
        main_frame.pack(expand=True, fill="both")
        content_frame = ttk.Frame(main_frame, bootstyle="dark.TFrame", padding=(10, 5))
        content_frame.pack(expand=True, fill="both")
        title_label = ttk.Label(content_frame, text=title, font=("Helvetica", 10, "bold"), bootstyle=f"{bootstyle}.inverse")
        title_label.pack(fill="x")
        message_label = ttk.Label(content_frame, text=message, wraplength=280, font=("Helvetica", 9), bootstyle="secondary.inverse")
        message_label.pack(fill="x", pady=(2, 5))
        self.fade_in()
    def fade_in(self):
        """Animasi untuk memunculkan popup secara perlahan."""
        if self.alpha < self.target_alpha:
            self.alpha += self.fade_step
            self.attributes('-alpha', self.alpha)
            self.after(20, self.fade_in)
        else:
            self.after(self.duration, self.fade_out)
    def fade_out(self):
        """Animasi untuk menghilangkan popup secara perlahan."""
        if self.alpha > 0.0:
            self.alpha -= self.fade_step
            self.attributes('-alpha', self.alpha)
            self.after(30, self.fade_out)
        else:
            self.destroy()
    def set_position(self, x, y):
        """Menempatkan jendela popup di posisi yang ditentukan."""
        self.geometry(f"+{x}+{y}")

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\popups\PopupManager.py
# JUMLAH BARIS : 49
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\popups\PopupManager.py
# JUMLAH BARIS : 48
#######################################################################

from .approval_popup import ApprovalPopup
from .license_popup import LicensePopup
from .NotificationManager import NotificationManager
from flowork_gui.api_client.client import ApiClient
class PopupManager:
    """
    Acts as a centralized command center for all popups in the application.
    This includes manual approvals, license prompts, and notification toasts.
    """
    def __init__(self, main_window, kernel):
        self.api_client = ApiClient()
        self.main_window = main_window
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        self.notification_manager = NotificationManager(self.main_window, self.kernel)
        self._current_approval_popup = None
        self._current_approval_module_id = None
        self.current_license_popup = None
    def show_notification(self, title: str, message: str, level: str = "INFO"):
        """Displays a notification toast."""
        self.notification_manager.show_toast(title, message, level)
        self.kernel.write_to_log(f"POPUP NOTIFICATION: {title} - {message}", level)
    def show_approval(self, module_id, workflow_name, message):
        """Displays a manual approval dialog."""
        if self._current_approval_popup and self._current_approval_popup.winfo_exists():
            self.kernel.write_to_log(f"Popup request for '{module_id}' ignored, another popup is active.", "WARN")
            return
        self._current_approval_module_id = module_id
        self._current_approval_popup = ApprovalPopup(self, self.kernel, module_id, workflow_name, message)
    def handle_approval_response(self, result: str):
        """Handles the user's response from the approval dialog."""
        if self._current_approval_module_id:
            module_manager = self.kernel.get_service("module_manager_service")
            if module_manager:
                module_manager.notify_approval_response(self._current_approval_module_id, result)
        if self._current_approval_popup and self._current_approval_popup.winfo_exists():
            self._current_approval_popup.destroy()
        self._current_approval_popup, self._current_approval_module_id = None, None
    def show_license_prompt(self):
        """Displays the license activation dialog."""
        self.main_window.prompt_for_license_file()

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\popups\__init__.py
# JUMLAH BARIS : 12
#######################################################################

```py
from flowork_gui.api_client.client import ApiClient

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\Users\User\Desktop\FLOWORK\flowork_kernel\ui_shell\popups\__init__.py
# JUMLAH BARIS : 14
#######################################################################




```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\popups\approval_popup.py
# JUMLAH BARIS : 80
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\popups\approval_popup.py
# JUMLAH BARIS : 79
#######################################################################

import ttkbootstrap as ttk
from tkinter import Toplevel, Label, Button
from flowork_gui.api_client.client import ApiClient
class ApprovalPopup(Toplevel):
    """
    Kelas mandiri yang bertanggung jawab untuk membuat dan menampilkan
    jendela popup persetujuan manual.
    """
    def __init__(self, popup_manager, kernel, module_id, workflow_name, message):
        self.api_client = ApiClient()
        super().__init__(popup_manager.main_window)
        self.popup_manager = popup_manager
        self.kernel = kernel
        self.loc = kernel.get_service("localization_manager")
        self.title(self.loc.get('manual_approval_title', fallback="Persetujuan Manual Dibutuhkan"))
        self.transient(popup_manager.main_window)
        self.grab_set()
        self.resizable(False, False)
        theme_manager = self.kernel.get_service("theme_manager")
        colors = theme_manager.get_colors() if theme_manager else {'bg': '#222'}
        self.configure(background=colors.get('bg', '#222'))
        self._create_widgets(workflow_name, message, colors)
        self._center_window()
    def _create_widgets(self, workflow_name, message, colors):
        """Membangun semua elemen UI di dalam popup."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(expand=True, fill="both")
        message_text = self.loc.get('manual_approval_message', workflow_name=workflow_name, node_message=message)
        Label(
            main_frame,
            text=message_text,
            wraplength=400,
            justify="center",
            background=colors.get('bg', '#222'),
            foreground=colors.get('fg', '#fff'),
            font=("Helvetica", 10)
        ).pack(pady=(0, 20))
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        Button(
            button_frame,
            text=self.loc.get('button_reject', fallback="Tolak"),
            command=lambda: self.popup_manager.handle_approval_response('REJECTED'),
            bg=colors.get('danger', '#dc3545'),
            fg=colors.get('light', '#fff'),
            relief="flat",
            width=15
        ).grid(row=0, column=0, padx=(0, 5), sticky="e")
        Button(
            button_frame,
            text=self.loc.get('button_approve', fallback="Setuju"),
            command=lambda: self.popup_manager.handle_approval_response('APPROVED'),
            bg=colors.get('success', '#28a745'),
            fg=colors.get('light', '#fff'),
            relief="flat",
            width=15
        ).grid(row=0, column=1, padx=(5, 0), sticky="w")
    def _center_window(self):
        """Menghitung dan mengatur posisi popup agar berada di tengah parent."""
        self.update_idletasks()
        parent_window = self.popup_manager.main_window
        parent_x = parent_window.winfo_x()
        parent_y = parent_window.winfo_y()
        parent_width = parent_window.winfo_width()
        parent_height = parent_window.winfo_height()
        popup_width = self.winfo_width()
        popup_height = self.winfo_height()
        win_x = parent_x + (parent_width // 2) - (popup_width // 2)
        win_y = parent_y + (parent_height // 2) - (popup_height // 2)
        self.geometry(f"+{win_x}+{win_y}")

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\popups\forced_update_popup.py
# JUMLAH BARIS : 70
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\popups\forced_update_popup.py
# JUMLAH BARIS : 69
#######################################################################

import ttkbootstrap as ttk
from tkinter import Toplevel, scrolledtext
import webbrowser
from flowork_gui.api_client.client import ApiClient
class ForcedUpdatePopup(Toplevel):
    """
    A custom, non-closable popup that forces the user to update.
    This version is fully localized.
    """
    def __init__(self, parent, kernel, update_info):
        self.api_client = ApiClient()
        super().__init__(parent)
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        self.update_info = update_info
        self.title(self.loc.get('update_popup_title', fallback="Mandatory Update Available"))
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", lambda: None)
        theme_manager = self.kernel.get_service("theme_manager")
        colors = theme_manager.get_colors() if theme_manager else {'bg': '#222'}
        self.configure(background=colors.get('bg', '#222'))
        self._create_widgets(colors)
        self._center_window()
    def _create_widgets(self, colors):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(expand=True, fill="both")
        version = self.update_info.get('version', 'N/A')
        header_text = self.loc.get('update_popup_header', fallback="Update to Version {version} Required", version=version)
        ttk.Label(main_frame, text=header_text, font=("Helvetica", 14, "bold")).pack(pady=(0, 10))
        ttk.Label(main_frame, text=self.loc.get('update_popup_changelog_label', fallback="Changes in this version:"), justify="left").pack(anchor='w', pady=(10, 2))
        changelog_text = scrolledtext.ScrolledText(main_frame, height=8, wrap="word", font=("Helvetica", 9))
        changelog_text.pack(fill="both", expand=True, pady=(0, 15))
        changelog_content = self.update_info.get('changelog', ["No details available."])
        changelog_text.insert("1.0", "\n".join(f"- {item}" for item in changelog_content))
        changelog_text.config(state="disabled")
        self.update_button = ttk.Button(
            main_frame,
            text=self.loc.get('update_popup_button', fallback="Download Update & Exit"),
            command=self._do_update,
            bootstyle="success"
        )
        self.update_button.pack(fill='x', ipady=5)
    def _do_update(self):
        self.update_button.config(state="disabled", text=self.loc.get('update_popup_button_loading', fallback="Opening browser..."))
        download_url = self.update_info.get('download_url')
        if download_url:
            webbrowser.open(download_url)
        self.after(2000, self.kernel.root.destroy)
    def _center_window(self):
        self.update_idletasks()
        parent_window = self.master
        parent_x = parent_window.winfo_x()
        parent_y = parent_window.winfo_y()
        parent_width = parent_window.winfo_width()
        parent_height = parent_window.winfo_height()
        popup_width = self.winfo_width()
        popup_height = self.winfo_height()
        win_x = parent_x + (parent_width // 2) - (popup_width // 2)
        win_y = parent_y + (parent_height // 2) - (popup_height // 2)
        self.geometry(f"+{win_x}+{win_y}")

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\popups\license_popup.py
# JUMLAH BARIS : 91
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\popups\license_popup.py
# JUMLAH BARIS : 90
#######################################################################

import ttkbootstrap as ttk
from tkinter import Toplevel, Label, Button, StringVar
from flowork_gui.api_client.client import ApiClient
class LicensePopup(Toplevel):
    """
    Kelas mandiri yang bertanggung jawab untuk membuat dan menampilkan
    jendela popup yang meminta pengguna memasukkan kunci lisensi.
    """
    def __init__(self, parent_window, kernel, module_name, license_event, callback):
        self.api_client = ApiClient()
        super().__init__(parent_window)
        self.parent_window = parent_window
        self.kernel = kernel
        self.loc = kernel.get_service("localization_manager")
        self.license_event = license_event
        self.callback = callback
        self.license_key_var = StringVar()
        self.title(self.loc.get('license_popup_title', fallback="Aktivasi Fitur Premium"))
        self.transient(parent_window)
        self.grab_set()
        self.resizable(False, False)
        theme_manager = self.kernel.get_service("theme_manager")
        colors = theme_manager.get_colors() if theme_manager else {'bg': '#222'}
        self.configure(background=colors.get('bg', '#222'))
        self._create_widgets(module_name, colors)
        self._center_window()
    def _create_widgets(self, module_name, colors):
        """Membangun semua elemen UI di dalam popup."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(expand=True, fill="both")
        info_text = self.loc.get('license_popup_message', module_name=module_name, fallback=f"Modul '{module_name}' adalah fitur premium.\n\nSilakan masukkan kunci lisensi Anda untuk mengaktifkan.")
        Label(
            main_frame,
            text=info_text,
            wraplength=400,
            justify="center",
            background=colors.get('bg', '#222'),
            foreground=colors.get('fg', '#fff'),
            font=("Helvetica", 10)
        ).pack(pady=(0, 20))
        ttk.Label(main_frame, text=self.loc.get('license_popup_entry_label', fallback="Kunci Lisensi:")).pack(anchor='w')
        entry = ttk.Entry(main_frame, textvariable=self.license_key_var, font=("Consolas", 11))
        entry.pack(fill='x', expand=True, pady=(2, 20))
        entry.focus_set()
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        cancel_button = ttk.Button(
            button_frame,
            text=self.loc.get('button_cancel', fallback="Batal"),
            command=self._on_cancel,
            style="secondary.TButton"
        )
        cancel_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        activate_button = ttk.Button(
            button_frame,
            text=self.loc.get('license_popup_activate_button', fallback="Aktifkan"),
            command=self._on_activate,
            style="success.TButton"
        )
        activate_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))
    def _on_activate(self):
        """Dipanggil saat tombol 'Aktifkan' ditekan."""
        entered_key = self.license_key_var.get()
        self.callback(entered_key, self.license_event)
        self.destroy()
    def _on_cancel(self):
        """Dipanggil saat tombol 'Batal' ditekan."""
        self.callback("", self.license_event)
        self.destroy()
    def _center_window(self):
        """Menghitung dan mengatur posisi popup agar berada di tengah parent."""
        self.update_idletasks()
        parent_x = self.parent_window.winfo_x()
        parent_y = self.parent_window.winfo_y()
        parent_width = self.parent_window.winfo_width()
        parent_height = self.parent_window.winfo_height()
        popup_width = self.winfo_width()
        popup_height = self.winfo_height()
        win_x = parent_x + (parent_width // 2) - (popup_width // 2)
        win_y = parent_y + (parent_height // 2) - (popup_height // 2)
        self.geometry(f"+{win_x}+{win_y}")

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\ui_components\__init__.py
# JUMLAH BARIS : 0
#######################################################################

```py

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\ui_components\menubar_manager.py
# JUMLAH BARIS : 71
#######################################################################

```py
from tkinter import Menu
import webbrowser
# MODIFIED: Changed the incorrect relative import to a direct, top-level import.
# This works because main_gui.py has already set up the correct project path.
from utils.performance_logger import log_performance

class MenubarManager:
    """
    (MODIFIED) The menubar is now DYNAMIC and 100% API-DRIVEN.
    It fetches its entire structure from the server and builds the UI accordingly.
    It includes a simple command dispatcher to handle actions sent from the server.
    """
    def __init__(self, main_window, api_client, loc_service):
        self.main_window = main_window
        self.api_client = api_client
        self.loc = loc_service # The localization helper is passed in.
        self.menubar = Menu(self.main_window)
        self.main_window.config(menu=self.menubar)
        self.main_window.main_menus = {}

    def _command_dispatcher(self, command_obj):
        """
        ADDED: This is the core of the new API-driven command system.
        It interprets the command object from the server and calls the appropriate LOCAL UI function.
        """
        command_type = command_obj.get("type")
        command_value = command_obj.get("value")
        if command_type == "open_tab":
            # COMMENT: This should eventually call the tab manager.
            print(f"ACTION: Open managed tab '{command_value}'") # English Log
        elif command_type == "open_url":
            webbrowser.open(command_value)
        elif command_type == "show_about_dialog":
            # COMMENT: This should eventually open an about dialog.
            pass
        elif command_type == "exit_app":
            # COMMENT: This should eventually call the app lifecycle handler to close.
            pass
        else:
            print(f"Warning: Unknown menu command type received from server: {command_type}") # English Log

    @log_performance("Building main menubar from API")
    def build_menu(self):
        self.menubar.delete(0, 'end' )
        self.main_window.main_menus.clear()
        success, menu_data = self.api_client.get_menubar()

        if not success:
            error_menu = Menu(self.menubar, tearoff=0)
            self.menubar.add_cascade(label="Error", menu=error_menu) # English Hardcode
            error_menu.add_command(label="Could not load menu from server") # English Hardcode
            return

        for menu_dict in menu_data:
            parent_label = menu_dict.get("label")
            menu_items = menu_dict.get("items", [])

            new_menu = Menu(self.menubar, tearoff=0)
            self.menubar.add_cascade(label=parent_label, menu=new_menu)
            self.main_window.main_menus[parent_label] = new_menu

            for item in menu_items:
                if item.get("type") == "separator":
                    new_menu.add_separator()
                else:
                    item_label = item.get("label")
                    command_obj = item.get("command")
                    new_menu.add_command(
                        label=item_label,
                        command=lambda cmd=command_obj: self._command_dispatcher(cmd)
                    )
```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\ui_components\tab_manager.py
# JUMLAH BARIS : 131
#######################################################################

```py
import uuid
import json
from tkinter import messagebox

# MODIFIED: Corrected the import path.
# Instead of the incorrect absolute import 'from flowork_gui.views...',
# we now use a top-level import 'from views...' which works because main_gui.py set up the path.
from views.workflow_editor_tab import WorkflowEditorTab
from views.dashboard_tab import DashboardTab

# COMMENT: The following classes were likely meant to be imported from a local contract file.
# For now, we define them here to resolve dependencies until the local API contract is fully built out.
class BaseUIProvider:
    pass

class UITabManager:
    """
    (REFACTORED for GUI) This class now exclusively manages the UI/view aspects of tabs
    in the main application window's notebook. It communicates with the server via an API client
    to get tab data and persist session state. It no longer contains any kernel logic.
    """
    def __init__(self, main_window, notebook, api_client, loc):
        self.main_window = main_window
        self.notebook = notebook
        self.api_client = api_client
        self.loc = loc
        self.opened_tabs = {}  # Maps tab_id to the tab widget instance
        self.custom_tab_count = 0
        self.MANAGED_TAB_CLASSES = {}
        self.initialized_tabs = set()
        print("UITabManager initialized for GUI.") # English Log
        self._populate_managed_tabs()

    def _populate_managed_tabs(self):
        """
        Placeholder for discovering tabs from local GUI plugins.
        In a fully API-driven model, this might fetch tab definitions from the server.
        """
        # This is where you would discover plugins that are part of the GUI application
        # and register their tabs.
        # For now, it's empty as we build out the core functionality.
        print("UITabManager: Populating managed tabs (currently static).") # English Log
        # Example of how it might work in the future:
        # self.MANAGED_TAB_CLASSES['system_diagnostics'] = {'title_key': 'diagnostics_tab_title', 'frame_class': DiagnosticsPage}
        pass

    def add_new_workflow_tab(self, preset_name=None):
        """Adds a new, empty workflow editor tab."""
        self.custom_tab_count += 1
        new_tab_id = f"custom_{self.custom_tab_count}"
        tab_title = self.loc.get('untitled_tab_title', fallback="Untitled {count}").format(count=self.custom_tab_count)

        editor_frame = WorkflowEditorTab(self.notebook, new_tab_id, self.api_client, self.loc, is_new=True, preset_name=preset_name)
        self.notebook.add(editor_frame, text=tab_title)
        self.notebook.select(editor_frame)
        self.opened_tabs[new_tab_id] = editor_frame
        return editor_frame

    def add_dashboard_tab(self):
        """Adds the main dashboard tab."""
        tab_id = "main_dashboard"
        if tab_id in self.opened_tabs and self.opened_tabs[tab_id].winfo_exists():
            self.notebook.select(self.opened_tabs[tab_id])
            return

        tab_title = self.loc.get('workflow_editor_tab_title', fallback="Dashboard")
        dashboard_frame = DashboardTab(self.notebook, tab_id, self.api_client, self.loc)
        self.notebook.add(dashboard_frame, text=tab_title)
        self.notebook.select(dashboard_frame)
        self.opened_tabs[tab_id] = dashboard_frame

    def close_tab(self, tab_id_to_close):
        """Closes a specific tab by its ID."""
        if tab_id_to_close in self.opened_tabs:
            tab_widget = self.opened_tabs[tab_id_to_close]
            # Here you might add a "do you want to save?" check
            self.notebook.forget(tab_widget)
            del self.opened_tabs[tab_id_to_close]
            print(f"Tab '{tab_id_to_close}' closed.") # English Log
        else:
            print(f"Warning: Attempted to close a tab with an unknown ID: {tab_id_to_close}") # English Log

    def save_session_state(self):
        """Saves the state of all open tabs to the server via the API."""
        tabs_data = []
        for tab_id, widget in self.opened_tabs.items():
            tab_type = 'workflow' if isinstance(widget, WorkflowEditorTab) else 'dashboard'
            tabs_data.append({
                "tab_id": tab_id,
                "type": tab_type,
                "title": self.notebook.tab(widget, "text"),
                "is_active": self.notebook.select() == self.notebook.tabs()[self.notebook.index(widget)],
                "preset_name": getattr(widget, 'preset_name', None)
            })

        success, response = self.api_client.save_tab_session(tabs_data)
        if success:
            messagebox.showinfo(self.loc.get('success_title'), self.loc.get('layout_and_session_saved'))
        else:
            messagebox.showerror(self.loc.get('error_title'), f"Failed to save session: {response}")

    def load_session_state(self):
        """Loads the last saved tab session from the server."""
        success, tabs_data = self.api_client.get_tab_session()
        if not success or not tabs_data:
            print("No saved tab session found or failed to load. Starting with a default dashboard.") # English Log
            self.add_dashboard_tab()
            return

        active_tab_widget = None
        for tab_info in tabs_data:
            tab_id = tab_info.get("tab_id")
            tab_type = tab_info.get("type")
            tab_title = tab_info.get("title", "Untitled")

            if tab_type == 'dashboard':
                self.add_dashboard_tab()
            elif tab_type == 'workflow':
                preset_name = tab_info.get("preset_name")
                new_tab = self.add_new_workflow_tab(preset_name=preset_name)
                # We may need to update the title if it was custom
                if tab_title != self.loc.get('untitled_tab_title', fallback="Untitled {count}").format(count=self.custom_tab_count):
                    self.notebook.tab(new_tab, text=tab_title)

            if tab_info.get("is_active"):
                active_tab_widget = self.opened_tabs.get(tab_id)

        if active_tab_widget:
            self.notebook.select(active_tab_widget)
        elif not self.opened_tabs: # Failsafe in case session was empty
            self.add_dashboard_tab()
```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\ui_components\controllers\TabActionHandler.py
# JUMLAH BARIS : 143
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\views\ui_components\controllers\TabActionHandler.py
# JUMLAH BARIS : 142
#######################################################################

import ttkbootstrap as ttk
from tkinter import filedialog, messagebox, simpledialog
import threading
import os
import shutil
import json
import uuid
import time
import random
class TabActionHandler:
    """
    Acts as the 'Controller' for the WorkflowEditorTab.
    It handles all user actions like running, saving, loading workflows,
    and managing the execution state for a specific tab.
    This class was created by refactoring the massive main_window.py.
    (REFACTORED V2) Now fully API-driven and receives its dependencies via constructor.
    """
    def __init__(self, tab_instance, api_client, loc_service): # MODIFIED: Signature updated to accept api_client and loc_service
        self.tab = tab_instance
        self.api_client = api_client
        self.loc = loc_service
    def run_workflow_from_preset(self, nodes, connections, initial_payload):
        """Used by widgets to trigger a run on this tab's canvas."""
        pass
    def _on_execution_finished(self, history_data):
        """Callback after a workflow run is complete."""
        pass
    def _start_workflow_thread(self, mode: str):
        """Prepares and starts the main workflow loop in a background thread."""
        pass
    def _workflow_loop_worker(self, mode: str, loop_count: int, delay_settings: dict):
        pass
    def run_workflow(self):
        self._start_workflow_thread(mode='EXECUTE')
    def simulate_workflow(self):
        self._start_workflow_thread(mode='SIMULATE')
    def _check_workflow_completion(self, exec_thread):
        pass
    def stop_workflow(self):
        pass
    def pause_workflow(self):
        pass
    def resume_workflow(self):
        pass
    def save_workflow(self):
        if not self.tab.canvas_area_instance or not self.tab.canvas_area_instance.canvas_manager:
            return
        workflow_data = self.tab.canvas_area_instance.canvas_manager.get_workflow_data()
        if not workflow_data.get("nodes"):
            messagebox.showwarning(self.loc.get('save_workflow_empty_title', fallback="Cannot Save Empty Workflow"), self.loc.get('save_workflow_empty_message', fallback="There are no nodes on the canvas to save."))
            return
        filepath = filedialog.asksaveasfilename(
            title=self.loc.get('save_workflow_title', fallback="Save Workflow File"),
            filetypes=[(self.loc.get('flowork_workflow_filetype', fallback="Flowork Workflow (*.json)"), "*.json"), ("All files", "*.*")],
            defaultextension=".json"
        )
        if not filepath: return
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(workflow_data, f, indent=4)
            print(f"Workflow saved to: {filepath}") # English Log
        except Exception as e:
            print(f"Failed to save workflow to {filepath}: {e}") # English Log
    def load_workflow(self):
        if not self.tab.canvas_area_instance or not self.tab.canvas_area_instance.canvas_manager:
            return
        if messagebox.askyesno(self.loc.get('confirm_load_workflow_title', fallback="Load Workflow?"), self.loc.get('confirm_load_workflow_message', fallback="Loading a workflow will discard any unsaved changes on the current canvas. Continue?")):
            filepath = filedialog.askopenfilename(
                title=self.loc.get('load_workflow_title', fallback="Load Workflow File"),
                filetypes=[(self.loc.get('flowork_workflow_filetype', fallback="Flowork Workflow (*.json)"), "*.json"), ("All files", "*.*")]
            )
            if not filepath: return
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    workflow_data = json.load(f)
                self.tab.canvas_area_instance.canvas_manager.load_workflow_data(workflow_data)
                self.tab.canvas_area_instance.preset_combobox.set('')
                print(f"Workflow loaded from: {filepath}") # English Log
            except Exception as e:
                print(f"Failed to load workflow from {filepath}: {e}") # English Log
    def clear_canvas(self, feedback=True):
        if hasattr(self.tab, '_clear_all_suggestions'):
            self.tab._clear_all_suggestions()
        if self.tab.canvas_area_instance:
            self.tab.canvas_area_instance.canvas_manager.clear_canvas(feedback)
            if hasattr(self.tab.canvas_area_instance, '_update_webhook_info'):
                self.tab.canvas_area_instance._update_webhook_info()
    def on_preset_selected(self, event=None):
        if not self.tab.canvas_area_instance: return
        selected_preset = self.tab.canvas_area_instance.preset_combobox.get()
        if not selected_preset: return
        threading.Thread(target=self._load_preset_worker, args=(selected_preset,), daemon=True).start()
    def _load_preset_worker(self, preset_name):
        self.tab.after(0, self.tab._clear_all_suggestions)
        success, data = self.api_client.get_preset_data(preset_name)
        self.tab.after(0, self._on_load_preset_complete, success, data, preset_name)
    def _on_load_preset_complete(self, success, data, preset_name):
        if not self.tab.canvas_area_instance: return
        if success:
            self.tab.canvas_area_instance.canvas_manager.load_workflow_data(data)
        else:
            messagebox.showerror(self.loc.get('error_title', fallback="Error"), f"API Error: {data}")
    def save_as_preset(self):
        if not self.tab.canvas_area_instance: return
        preset_name = simpledialog.askstring(self.loc.get('save_preset_popup_title', fallback="Save As Preset"), self.loc.get('save_preset_popup_prompt', fallback="Enter a name for this preset:"), parent=self.tab)
        if not preset_name or not preset_name.strip(): return
        preset_name = preset_name.strip()
        workflow_data = self.tab.canvas_area_instance.canvas_manager.get_workflow_data()
        threading.Thread(target=self._save_preset_worker, args=(preset_name, workflow_data), daemon=True).start()
    def _save_preset_worker(self, preset_name, workflow_data):
        success, response = self.api_client.save_preset(preset_name, workflow_data)
        self.tab.after(0, self._on_save_preset_complete, success, response, preset_name)
    def _on_save_preset_complete(self, success, response, preset_name):
        if not self.tab.canvas_area_instance: return
        if success:
            self.tab.populate_preset_dropdown()
            self.tab.canvas_area_instance.preset_combobox.set(preset_name)
        else:
            messagebox.showerror(self.loc.get('error_title', fallback="Error"), f"API Error: {response}")
    def _delete_selected_preset(self):
        if not self.tab.canvas_area_instance: return
        selected_preset = self.tab.canvas_area_instance.preset_combobox.get()
        if not selected_preset: return
        if messagebox.askyesno(self.loc.get('confirm_delete_title', fallback="Confirm Deletion"), self.loc.get('confirm_delete_preset_message', fallback="Are you sure you want to delete the preset '{name}'?", name=selected_preset)):
            threading.Thread(target=self._delete_preset_worker, args=(selected_preset,), daemon=True).start()
    def _delete_preset_worker(self, preset_name):
        success, response = self.api_client.delete_preset(preset_name)
        self.tab.after(0, self._on_delete_preset_complete, success, response, preset_name)
    def _on_delete_preset_complete(self, success, response, preset_name):
        if success:
            self.tab.populate_preset_dropdown()
        else:
            messagebox.showerror(self.loc.get('error_title', fallback="Error"), f"API Error: {response}")
    def clear_cache(self):
        pass

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\widgets\__init__.py
# JUMLAH BARIS : 3
#######################################################################

```py
from flowork_gui.api_client.client import ApiClient
# COMMENT: Old direct kernel import, replaced by refactor script.
# from flowork_kernel.api_client import ApiClient

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\widgets\canvas_area\__init__.py
# JUMLAH BARIS : 3
#######################################################################

```py
from flowork_gui.api_client.client import ApiClient
# COMMENT: Old direct kernel import, replaced by refactor script.
# from flowork_kernel.api_client import ApiClient

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\widgets\canvas_area\canvas_area_widget.py
# JUMLAH BARIS : 254
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\widgets\canvas_area\canvas_area_widget.py
# JUMLAH BARIS : 253
#######################################################################

import ttkbootstrap as ttk
from tkinter import messagebox, simpledialog, scrolledtext, Menu
import urllib.parse
import json
import threading
from flowork_gui.views.version_manager_popup import VersionManagerPopup
from flowork_gui.views.custom_widgets.tooltip import ToolTip
from flowork_gui.api_contract import BaseDashboardWidget
from flowork_gui.views.canvas_manager import CanvasManager
from flowork_gui.widgets.data_canvas_widget.data_canvas_widget import DataCanvasWidget
class CanvasAreaWidget(BaseDashboardWidget):
    TIER = "free"
    """
    Widget that contains the main canvas and ALL its action buttons, including preset management.
    (REFACTORED) Now fully independent from the kernel, uses ApiClient for data.
    """
    def __init__(self, parent, coordinator_tab, kernel, widget_id: str):
        super().__init__(parent, coordinator_tab, kernel, widget_id)
        self.parent_tab = coordinator_tab
        self.canvas_manager = None
        self.execution_history = {}
        self.debugger_mode_var = ttk.BooleanVar(value=False)
        self.view_mode_var = ttk.StringVar(value="logic")
        self.loop_count_var = ttk.StringVar(value="1")
        self.loop_status_var = ttk.StringVar(value="")
        self.enable_delay_var = ttk.BooleanVar(value=True)
        self.delay_type_var = ttk.StringVar(value="static")
        self.static_delay_var = ttk.StringVar(value="1")
        self.random_min_var = ttk.StringVar(value="1")
        self.random_max_var = ttk.StringVar(value="10")
        self.hide_controls_job = None
        self._create_widgets()
        self.populate_preset_dropdown()
    def _recenter_floating_controls(self, event=None):
        """This function is called whenever the main widget resizes."""
        self.update_idletasks()
        if hasattr(self, 'floating_controls_panel') and self.floating_controls_panel and self.floating_controls_panel.winfo_exists() and self.floating_controls_panel.winfo_viewable():
            self.floating_controls_panel.place(in_=self, relx=0.5, rely=1.0, y=-10, anchor="s")
    def _create_widgets(self):
        colors = {'bg': '#222', 'dark': '#343a40'} # ADDED: Using fallback colors
        self.bind("<Configure>", self._recenter_floating_controls)
        preset_bar_frame = ttk.Frame(self)
        preset_bar_frame.pack(side="top", fill='x', padx=5, pady=(0,5))
        preset_action_frame = ttk.Frame(preset_bar_frame)
        preset_action_frame.pack(fill='x', pady=(5,0))
        self.manage_versions_button = ttk.Button(preset_action_frame, text=self.loc.get('manage_versions_button', fallback="Manage Versions"), command=self._open_version_manager, style='info.TButton')
        self.manage_versions_button.pack(side='left', padx=(0, 10))
        ttk.Label(preset_action_frame, text=self.loc.get('load_preset_label', fallback="Load Preset:")).pack(side='left')
        self.preset_combobox = ttk.Combobox(preset_action_frame, state="readonly", width=30)
        self.preset_combobox.pack(side='left', fill='x', expand=True, padx=10)
        self.preset_combobox.bind("<<ComboboxSelected>>", self._on_preset_selected)
        self.delete_preset_button = ttk.Button(preset_action_frame, text=self.loc.get('delete_preset_button', fallback="Delete Preset"), command=self._delete_selected_preset, style='danger.TButton')
        self.delete_preset_button.pack(side='left', padx=(0, 5))
        self.save_preset_button = ttk.Button(preset_action_frame, text=self.loc.get('save_preset_button', fallback="Save as Preset"), command=self._save_as_preset, style='primary.TButton')
        self.save_preset_button.pack(side='left')
        self.webhook_info_frame = ttk.Frame(preset_bar_frame)
        self.webhook_info_frame.pack(fill='x', expand=True, pady=(5,0))
        ttk.Label(self.webhook_info_frame, text="Trigger URL:", style='Webhook.TLabel').pack(side='left', padx=(0, 5)) # English Hardcode
        self.webhook_url_var = ttk.StringVar()
        webhook_url_entry = ttk.Entry(self.webhook_info_frame, textvariable=self.webhook_url_var, state="readonly", width=60, style='Webhook.TEntry')
        webhook_url_entry.pack(side='left', fill='x', expand=True)
        copy_url_button = ttk.Button(self.webhook_info_frame, text="Copy", command=self._copy_webhook_url, style='secondary.TButton') # English Hardcode
        copy_url_button.pack(side='left', padx=5)
        self.canvas_container = ttk.Frame(self)
        self.canvas_container.pack(expand=True, fill='both')
        self.canvas_container.bind("<Button-3>", self._show_canvas_context_menu)
        self.logic_canvas_frame = ttk.Frame(self.canvas_container)
        self.data_canvas_frame = ttk.Frame(self.canvas_container)
        self.canvas = ttk.Canvas(self.logic_canvas_frame, background=colors.get('dark', '#343a40'))
        self.canvas.pack(expand=True, fill='both')
        self.canvas_manager = CanvasManager(self, self.parent_tab, self.canvas, self.kernel)
        self.data_canvas_widget = DataCanvasWidget(self.data_canvas_frame, self.parent_tab, self.kernel, "data_canvas_main")
        self.data_canvas_widget.pack(expand=True, fill='both')
        self.floating_controls_panel = ttk.Frame(self, style='dark.TFrame', padding=5)
        ttk.Separator(self.floating_controls_panel, bootstyle="danger").pack(side="top", fill="x", pady=(0, 5))
        management_group = ttk.LabelFrame(self.floating_controls_panel, text=self.loc.get('workflow_management_title', fallback="Workflow Management"), bootstyle="dark")
        management_group.pack(side='left', padx=(0, 10), fill='y')
        save_button = ttk.Button(management_group, text=self.loc.get('save_workflow_button', fallback="💾 Save"), command=self.parent_tab.action_handler.save_workflow, style='success.TButton')
        save_button.pack(side='left', padx=5, pady=5)
        load_button = ttk.Button(management_group, text=self.loc.get('load_workflow_button', fallback="📂 Load"), command=self.parent_tab.action_handler.load_workflow, style='info.TButton')
        load_button.pack(side='left', padx=5, pady=5)
        clear_button = ttk.Button(management_group, text=self.loc.get('clear_canvas_button', fallback="🧹 Clear"), command=self.parent_tab.action_handler.clear_canvas, style='danger.TButton')
        clear_button.pack(side='left', padx=5, pady=5)
        execution_control_group = ttk.LabelFrame(self.floating_controls_panel, text=self.loc.get('execution_control_title', fallback="Execution Control"), bootstyle="dark")
        execution_control_group.pack(side='left', padx=5, fill='y')
        loop_control_frame = ttk.Frame(execution_control_group, style='dark.TFrame')
        loop_control_frame.pack(fill='x', padx=5, pady=5)
        loop_count_frame = ttk.Frame(loop_control_frame, style='dark.TFrame')
        loop_count_frame.pack(side='left', fill='y')
        ttk.Label(loop_count_frame, text=self.loc.get('loop_run_label', fallback="Repeat:"), style='inverse-dark.TLabel').pack(side='left', padx=(0, 5))
        loop_entry = ttk.Entry(loop_count_frame, textvariable=self.loop_count_var, width=5)
        loop_entry.pack(side='left')
        ttk.Label(loop_count_frame, text=self.loc.get('loop_times_label', fallback="times"), style='inverse-dark.TLabel').pack(side='left', padx=(5, 10))
        ToolTip(loop_entry).update_text("Set how many times the entire workflow should run.")
        delay_options_frame = ttk.Frame(loop_control_frame, style='dark.TFrame')
        delay_options_frame.pack(side='left', fill='y', padx=(10,0))
        ttk.Checkbutton(delay_options_frame, text=self.loc.get('enable_delay_checkbox', fallback="Delay Between Loops"), variable=self.enable_delay_var, style='dark.TCheckbutton').pack(side='left')
        self.static_delay_frame = ttk.Frame(delay_options_frame, style='dark.TFrame')
        self.random_delay_frame = ttk.Frame(delay_options_frame, style='dark.TFrame')
        delay_type_radio_static = ttk.Radiobutton(delay_options_frame, text=self.loc.get('delay_type_static', fallback="Static"), variable=self.delay_type_var, value='static', style='dark.TRadiobutton')
        delay_type_radio_static.pack(side='left', padx=(10, 5))
        ttk.Entry(self.static_delay_frame, textvariable=self.static_delay_var, width=4).pack(side='left')
        ttk.Label(self.static_delay_frame, text="sec", style='inverse-dark.TLabel').pack(side='left', padx=(2,0)) # English Hardcode
        delay_type_radio_random = ttk.Radiobutton(delay_options_frame, text=self.loc.get('delay_type_random', fallback="Random"), variable=self.delay_type_var, value='random', style='dark.TRadiobutton')
        delay_type_radio_random.pack(side='left', padx=(10, 5))
        ttk.Entry(self.random_delay_frame, textvariable=self.random_min_var, width=4).pack(side='left')
        ttk.Label(self.random_delay_frame, text="-", style='inverse-dark.TLabel').pack(side='left', padx=2)
        ttk.Entry(self.random_delay_frame, textvariable=self.random_max_var, width=4).pack(side='left')
        ttk.Label(self.random_delay_frame, text="sec", style='inverse-dark.TLabel').pack(side='left', padx=(2,0)) # English Hardcode
        execution_buttons_frame = ttk.Frame(execution_control_group, style='dark.TFrame')
        execution_buttons_frame.pack(fill='x', pady=(5, 2), padx=5)
        self.simulate_button = ttk.Button(execution_buttons_frame, text=self.loc.get('simulate_workflow_button', fallback="Run Simulation"), command=self.parent_tab.action_handler.simulate_workflow, style='primary.TButton')
        self.simulate_button.pack(side='left', expand=True, fill='x', padx=(0,5))
        self.run_button = ttk.Button(execution_buttons_frame, text=self.loc.get('btn_run_workflow', fallback="Run Workflow"), command=self.parent_tab.action_handler.run_workflow, style='success.TButton')
        self.run_button.pack(side='left', expand=True, fill='x', padx=(0,5))
        self.pause_resume_button = ttk.Button(execution_buttons_frame, text=self.loc.get('btn_pause', fallback="Pause"), command=self.parent_tab.action_handler.pause_workflow, style='info.TButton', state='disabled')
        self.pause_resume_button.pack(side='left', expand=True, fill='x', padx=(0,5))
        self.loop_status_label = ttk.Label(execution_control_group, textvariable=self.loop_status_var, bootstyle="inverse-dark")
        self.loop_status_label.pack(fill='x', pady=(2,5), padx=5)
        view_toggle_frame = ttk.Frame(self.floating_controls_panel, style='dark.TFrame')
        view_toggle_frame.pack(side='left', padx=15, fill='y')
        logic_rb = ttk.Radiobutton(view_toggle_frame, text="Logic", variable=self.view_mode_var, value="logic", command=self._on_view_mode_change, style="light-outline-toolbutton") # English Hardcode
        logic_rb.pack(side='left', pady=10)
        data_rb = ttk.Radiobutton(view_toggle_frame, text="Data", variable=self.view_mode_var, value="data", command=self._on_view_mode_change, style="light-outline-toolbutton") # English Hardcode
        data_rb.pack(side='left', pady=10)
        debugger_toggle_frame = ttk.Frame(self.floating_controls_panel, style='dark.TFrame')
        debugger_toggle_frame.pack(side='left', padx=10, fill='y')
        debugger_switch = ttk.Checkbutton(debugger_toggle_frame, text="Debugger", variable=self.debugger_mode_var, bootstyle="info-round-toggle", command=self._toggle_debugger_mode) # English Hardcode
        debugger_switch.pack(side='left', pady=10)
        self._create_debugger_widgets()
        self._on_view_mode_change()
        self.canvas_container.bind("<Enter>", self._show_floating_controls)
        self.canvas_container.bind("<Leave>", self._schedule_hide_controls)
        self.floating_controls_panel.bind("<Enter>", self._cancel_hide_controls)
        self.floating_controls_panel.bind("<Leave>", self._schedule_hide_controls)
        def _toggle_delay_options(*args):
            if self.delay_type_var.get() == 'static':
                self.random_delay_frame.pack_forget()
                self.static_delay_frame.pack(side='left')
            else:
                self.static_delay_frame.pack_forget()
                self.random_delay_frame.pack(side='left')
        delay_type_radio_static.config(command=_toggle_delay_options)
        delay_type_radio_random.config(command=_toggle_delay_options)
        _toggle_delay_options()
        self.run_button.bind("<Enter>", lambda e: self.run_button.config(bootstyle="danger"))
        self.run_button.bind("<Leave>", lambda e: self.run_button.config(bootstyle="success"))
        self.simulate_button.bind("<Enter>", lambda e: self.simulate_button.config(bootstyle="danger"))
        self.simulate_button.bind("<Leave>", lambda e: self.simulate_button.config(bootstyle="primary"))
        self.save_preset_button.bind("<Enter>", lambda e: self.save_preset_button.config(bootstyle="danger"))
        self.save_preset_button.bind("<Leave>", lambda e: self.save_preset_button.config(bootstyle="primary"))
    def _show_canvas_context_menu(self, event):
        if not self.canvas_manager: return
        self.canvas_manager.interaction_manager._show_canvas_context_menu(event)
    def _show_floating_controls(self, event=None):
        self._cancel_hide_controls()
        if hasattr(self, 'floating_controls_panel') and not self.floating_controls_panel.winfo_viewable():
            self.floating_controls_panel.place(in_=self, relx=0.5, rely=1.0, y=-10, anchor="s")
    def _schedule_hide_controls(self, event=None):
        self.hide_controls_job = self.after(500, self._check_and_hide_controls)
    def _cancel_hide_controls(self, event=None):
        if self.hide_controls_job:
            self.after_cancel(self.hide_controls_job)
            self.hide_controls_job = None
    def _check_and_hide_controls(self):
        if not self.winfo_exists(): return
        cursor_x = self.winfo_pointerx()
        cursor_y = self.winfo_pointery()
        canvas_x1 = self.canvas_container.winfo_rootx()
        canvas_y1 = self.canvas_container.winfo_rooty()
        canvas_x2 = canvas_x1 + self.canvas_container.winfo_width()
        canvas_y2 = canvas_y1 + self.canvas_container.winfo_height()
        panel_x1 = self.floating_controls_panel.winfo_rootx()
        panel_y1 = self.floating_controls_panel.winfo_rooty()
        panel_x2 = panel_x1 + self.floating_controls_panel.winfo_width()
        panel_y2 = panel_y1 + self.floating_controls_panel.winfo_height()
        is_over_canvas = (canvas_x1 <= cursor_x <= canvas_x2) and (canvas_y1 <= cursor_y <= canvas_y2)
        is_over_panel = self.floating_controls_panel.winfo_viewable() and (panel_x1 <= cursor_x <= panel_x2) and (panel_y1 <= cursor_y <= panel_y2)
        if not is_over_canvas and not is_over_panel:
            self.floating_controls_panel.place_forget()
        self.hide_controls_job = None
    def _on_view_mode_change(self):
        if self.view_mode_var.get() == "data":
            if self.canvas_manager:
                self.data_canvas_widget.sync_with_logic_canvas(self.canvas_manager.canvas_nodes)
            self.logic_canvas_frame.pack_forget()
            self.data_canvas_frame.pack(expand=True, fill='both')
        else:
            self.data_canvas_frame.pack_forget()
            self.logic_canvas_frame.pack(expand=True, fill='both')
    def _create_debugger_widgets(self):
        self.debugger_frame = ttk.LabelFrame(self, text=self.loc.get('debugger_title', fallback="Time-Travel Debugger"), padding=5)
    def _toggle_debugger_mode(self):
        if self.debugger_mode_var.get():
            self.show_debugger(self.execution_history or {})
        else:
            self.hide_debugger()
    def show_debugger(self, history_data):
        pass
    def hide_debugger(self):
        pass
    def _on_timeline_scrub(self, value):
        pass
    def populate_preset_dropdown(self):
        def _populate_worker():
            success, presets_data = self.api_client.get_presets()
            if success:
                presets = [p['name'] for p in presets_data]
                self.after(0, _update_combobox, presets)
            else:
                print(f"Failed to load preset list via API: {presets_data}") # English Log
        def _update_combobox(presets):
            self.preset_combobox['values'] = sorted(presets)
            current_selection = self.preset_combobox.get()
            if current_selection not in presets:
                self.preset_combobox.set('')
            self._update_webhook_info()
        threading.Thread(target=_populate_worker, daemon=True).start()
    def _update_webhook_info(self):
        self.webhook_info_frame.pack_forget()
    def _copy_webhook_url(self):
        url_to_copy = self.webhook_url_var.get()
        if url_to_copy:
            self.clipboard_clear()
            self.clipboard_append(url_to_copy)
            print(f"Webhook URL copied to clipboard: {url_to_copy}") # English Log
    def _on_preset_selected(self, event=None):
        if hasattr(self.parent_tab, 'action_handler'):
            self.parent_tab.action_handler.on_preset_selected(event)
    def _save_as_preset(self):
        if hasattr(self.parent_tab, 'action_handler'):
            self.parent_tab.action_handler.save_as_preset()
    def _delete_selected_preset(self):
        if hasattr(self.parent_tab, 'action_handler'):
            self.parent_tab.action_handler._delete_selected_preset()
    def _open_version_manager(self):
        selected_preset = self.preset_combobox.get()
        if not selected_preset:
            messagebox.showwarning(self.loc.get('warning_title', fallback="Warning"), self.loc.get('select_preset_to_delete_warning', fallback="Please select a preset first to manage its versions."))
            return
        VersionManagerPopup(self.parent_tab, self.kernel, selected_preset)
    def update_zoom_label(self):
        if hasattr(self, 'zoom_label') and self.canvas_manager and self.canvas_manager.interaction_manager and self.canvas_manager.interaction_manager.navigation_handler:
            self.zoom_label.config(text=f"{int(self.canvas_manager.interaction_manager.navigation_handler.zoom_level * 100)}%")
    def apply_styles(self, colors):
        pass

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\widgets\dataset_manager_widget\__init__.py
# JUMLAH BARIS : 3
#######################################################################

```py
from flowork_gui.api_client.client import ApiClient
# COMMENT: Old direct kernel import, replaced by refactor script.
# from flowork_kernel.api_client import ApiClient

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\widgets\dataset_manager_widget\dataset_manager_widget.py
# JUMLAH BARIS : 169
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\widgets\dataset_manager_widget\dataset_manager_widget.py
# JUMLAH BARIS : 168
#######################################################################

from flowork_kernel.core import build_security
from flowork_kernel.core import build_security
from flowork_kernel.core import build_security
import ttkbootstrap as ttk
from tkinter import simpledialog, messagebox
from tkinter.scrolledtext import ScrolledText
from flowork_kernel.api_contract import BaseDashboardWidget
import threading
from flowork_gui.api_client.client import ApiClient
class DatasetManagerWidget(BaseDashboardWidget):
    """
    Provides a UI for managing fine-tuning datasets by communicating with the backend API.
    [UPGRADED] Now loads and displays existing data when a dataset is selected.
    """
    TIER = "pro"
    def __init__(self, parent, coordinator_tab, kernel, widget_id: str, refresh_callback=None):
        build_security.perform_runtime_check(__file__)
        build_security.perform_runtime_check(__file__)
        build_security.perform_runtime_check(__file__)
        super().__init__(parent, coordinator_tab, kernel, widget_id)
        self.api_client = ApiClient(kernel=self.kernel)
        self.dataset_var = ttk.StringVar()
        self.refresh_callback = refresh_callback
        self._build_ui()
    def on_widget_load(self):
        """Load datasets when the widget appears."""
        self._load_datasets()
    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        selection_frame = ttk.Frame(self)
        selection_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        selection_frame.columnconfigure(0, weight=1)
        self.dataset_combo = ttk.Combobox(selection_frame, textvariable=self.dataset_var, state="readonly")
        self.dataset_combo.grid(row=0, column=0, sticky="ew")
        self.dataset_combo.bind("<<ComboboxSelected>>", self._on_dataset_selected)
        button_toolbar = ttk.Frame(selection_frame)
        button_toolbar.grid(row=0, column=1, padx=(5,0))
        create_button = ttk.Button(button_toolbar, text="Create", command=self._create_new_dataset, bootstyle="outline-success", width=7)
        create_button.pack(side="left")
        self.delete_button = ttk.Button(button_toolbar, text="Delete", command=self._delete_selected_dataset, bootstyle="outline-danger", width=7)
        self.delete_button.pack(side="left", padx=(5,0))
        self.input_frame = ttk.LabelFrame(self, text="Add or Edit Data (prompt;response per line)")
        self.input_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.input_frame.rowconfigure(0, weight=1)
        self.input_frame.columnconfigure(0, weight=1)
        self.data_input_text = ScrolledText(self.input_frame, wrap="word", height=8)
        self.data_input_text.grid(row=0, column=0, sticky="nsew")
        self.save_button = ttk.Button(self, text="Save Data to Selected Dataset", command=self._save_data_to_dataset, bootstyle="primary")
        self.save_button.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.rowconfigure(1, weight=1)
    def _load_datasets(self):
        self.dataset_combo['values'] = ["Loading..."]
        self.dataset_var.set("Loading...")
        threading.Thread(target=self._load_datasets_worker, daemon=True).start()
    def _load_datasets_worker(self):
        success, response = self.api_client.list_datasets()
        self.after(0, self._populate_dataset_combo, success, response)
    def _populate_dataset_combo(self, success, response):
        if success:
            dataset_names = [ds['name'] for ds in response]
            self.dataset_combo['values'] = sorted(dataset_names)
            if dataset_names:
                self.dataset_var.set(sorted(dataset_names)[0])
                self._on_dataset_selected()
            else:
                self.dataset_var.set("No datasets found. Please create one.")
                self.data_input_text.config(state="normal")
                self.data_input_text.delete("1.0", "end")
                self.data_input_text.config(state="disabled")
        else:
            self.dataset_combo['values'] = ["Error loading datasets"]
            self.dataset_var.set("Error loading datasets")
            self.kernel.write_to_log(f"Failed to load datasets: {response}", "ERROR")
    def _on_dataset_selected(self, event=None):
        selected_dataset = self.dataset_var.get()
        if not selected_dataset or "Loading" in selected_dataset or "Error" in selected_dataset or "No datasets" in selected_dataset:
            return
        self.data_input_text.config(state="normal")
        self.data_input_text.delete("1.0", "end")
        self.data_input_text.insert("1.0", f"Loading data for '{selected_dataset}'...")
        self.data_input_text.config(state="disabled")
        threading.Thread(target=self._load_dataset_content_worker, args=(selected_dataset,), daemon=True).start()
    def _load_dataset_content_worker(self, dataset_name):
        success, data = self.api_client.get_dataset_data(dataset_name)
        self.after(0, self._populate_data_text_area, success, data, dataset_name)
    def _populate_data_text_area(self, success, data, dataset_name):
        self.data_input_text.config(state="normal")
        self.data_input_text.delete("1.0", "end")
        if success:
            formatted_text = ""
            for item in data:
                formatted_text += f"{item.get('prompt', '')};{item.get('response', '')}\n"
            self.data_input_text.insert("1.0", formatted_text)
            self.input_frame.config(text=f"Data for '{dataset_name}' ({len(data)} records)")
        else:
            self.data_input_text.insert("1.0", f"Error loading data for '{dataset_name}'.")
            self.kernel.write_to_log(f"Failed to load content for dataset '{dataset_name}': {data}", "ERROR")
    def _create_new_dataset(self):
        new_name = simpledialog.askstring("Create Dataset", "Enter a name for the new dataset:", parent=self)
        if new_name and new_name.strip():
            success, response = self.api_client.create_dataset(new_name.strip())
            if success:
                self.kernel.write_to_log(f"Successfully created dataset: {new_name}", "SUCCESS")
                if self.refresh_callback:
                    self.refresh_callback()
            else:
                messagebox.showerror("Error", f"Failed to create dataset: {response}", parent=self)
        else:
            self.kernel.write_to_log("Dataset creation cancelled.", "WARN")
    def _delete_selected_dataset(self):
        selected_dataset = self.dataset_var.get()
        if not selected_dataset or "Loading" in selected_dataset or "Error" in selected_dataset or "No datasets" in selected_dataset:
            messagebox.showerror("Error", "Please select a valid dataset to delete.", parent=self)
            return
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete the dataset '{selected_dataset}'?", parent=self):
            self.delete_button.config(state="disabled", text="Deleting...")
            threading.Thread(target=self._delete_dataset_worker, args=(selected_dataset,), daemon=True).start()
    def _delete_dataset_worker(self, dataset_name):
        success, response = self.api_client.delete_dataset(dataset_name)
        self.after(0, self._on_delete_complete, success, response, dataset_name)
    def _on_delete_complete(self, success, response, dataset_name):
        self.delete_button.config(state="normal", text="Delete")
        if success:
            messagebox.showinfo("Success", f"Dataset '{dataset_name}' has been deleted.", parent=self)
            if self.refresh_callback:
                self.refresh_callback()
        else:
            messagebox.showerror("Error", f"Failed to delete dataset: {response}", parent=self)
    def _save_data_to_dataset(self):
        selected_dataset = self.dataset_var.get()
        data_to_add = self.data_input_text.get("1.0", "end-1c").strip()
        if not selected_dataset or "Loading" in selected_dataset or "Error" in selected_dataset or "No datasets" in selected_dataset:
            messagebox.showerror("Error", "Please select or create a valid dataset first.", parent=self)
            return
        if not data_to_add:
            messagebox.showerror("Error", "The data input area is empty.", parent=self)
            return
        parsed_data = []
        for i, line in enumerate(data_to_add.split('\n')):
            if not line.strip(): continue
            if ';' not in line:
                messagebox.showerror("Error", f"Invalid format on line {i+1}: '{line}'. Each line must be 'prompt;response'.", parent=self)
                return
            prompt, response = line.split(';', 1)
            parsed_data.append({"prompt": prompt.strip(), "response": response.strip()})
        self.save_button.config(state="disabled", text="Saving...")
        threading.Thread(target=self._save_data_worker, args=(selected_dataset, parsed_data), daemon=True).start()
    def _save_data_worker(self, dataset_name, data):
        success, response = self.api_client.add_data_to_dataset(dataset_name, data)
        self.after(0, self._on_save_data_complete, success, response, len(data), dataset_name)
    def _on_save_data_complete(self, success, response, count, dataset_name):
        self.save_button.config(state="normal", text="Save Data to Selected Dataset")
        if success:
            messagebox.showinfo("Success", f"{count} records have been successfully saved to dataset '{dataset_name}'.", parent=self)
            if self.refresh_callback:
                self.refresh_callback()
        else:
            messagebox.showerror("Error", f"Failed to save data: {response}", parent=self)
_UNUSED_SIGNATURE = 'B3Ba%m#rDeKa' # Embedded Signature
_UNUSED_SIGNATURE = 'B3Ba%m#rDeKa' # Embedded Signature
_UNUSED_SIGNATURE = 'B3Ba%m#rDeKa' # Embedded Signature

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\widgets\data_canvas_widget\__init__.py
# JUMLAH BARIS : 3
#######################################################################

```py
from flowork_gui.api_client.client import ApiClient
# COMMENT: Old direct kernel import, replaced by refactor script.
# from flowork_kernel.api_client import ApiClient

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\widgets\data_canvas_widget\data_canvas_widget.py
# JUMLAH BARIS : 86
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\widgets\data_canvas_widget\data_canvas_widget.py
# JUMLAH BARIS : 85
#######################################################################

from flowork_kernel.core import build_security
from flowork_kernel.core import build_security
import ttkbootstrap as ttk
from tkinter import ttk as tk_ttk
import json
from flowork_kernel.api_contract import BaseDashboardWidget, IDataPreviewer
from flowork_gui.api_client.client import ApiClient
class DataCanvasWidget(BaseDashboardWidget):
    TIER = "basic"
    """
    The UI for the Data Canvas. It displays a version of the workflow focused
    on previewing the data output of each configured node in real-time.
    """
    def __init__(self, parent, coordinator_tab, kernel, widget_id: str):
        self.api_client = ApiClient(kernel=self.kernel)
        build_security.perform_runtime_check(__file__)
        build_security.perform_runtime_check(__file__)
        super().__init__(parent, coordinator_tab, kernel, widget_id)
        self.parent_tab = coordinator_tab
        self.data_node_widgets = {} # Stores the UI elements for each node on this canvas
        canvas_container = ttk.Frame(self)
        canvas_container.pack(fill='both', expand=True)
        self.canvas = ttk.Canvas(canvas_container)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.kernel.write_to_log("Data Canvas Widget Initialized.", "SUCCESS")
    def sync_with_logic_canvas(self, logic_canvas_nodes):
        """
        Receives the node data from the main logic canvas and rebuilds the
        Data Canvas UI based on it.
        """
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.data_node_widgets.clear()
        if not logic_canvas_nodes:
            ttk.Label(self.scrollable_frame, text="Tambahkan node di Tampilan Logika untuk melihat preview data di sini.").pack(pady=50)
            return
        module_manager = self.kernel.get_service("module_manager_service")
        for node_id, node_data in logic_canvas_nodes.items():
            module_id = node_data.get('module_id')
            node_name = node_data.get('name', 'Unknown')
            node_frame = ttk.LabelFrame(self.scrollable_frame, text=f"{node_name} ({module_id})", padding=10)
            node_frame.pack(fill='x', expand=True, padx=10, pady=5)
            module_instance = module_manager.get_instance(module_id)
            if isinstance(module_instance, IDataPreviewer):
                try:
                    preview_data = module_instance.get_data_preview(node_data.get('config_values', {}))
                    if isinstance(preview_data, list) and preview_data and isinstance(preview_data[0], dict):
                        columns = list(preview_data[0].keys())
                        tree = tk_ttk.Treeview(node_frame, columns=columns, show="headings", height=min(len(preview_data), 5))
                        for col in columns:
                            tree.heading(col, text=col.replace("_", " ").title())
                            tree.column(col, width=120)
                        for item in preview_data:
                            tree.insert("", "end", values=[str(item.get(col, '')) for col in columns])
                        tree.pack(fill='both', expand=True)
                    else:
                        pretty_data = json.dumps(preview_data, indent=2, ensure_ascii=False)
                        text_area = ttk.Text(node_frame, height=5, wrap="word", font=("Consolas", 9))
                        text_area.insert("1.0", pretty_data)
                        text_area.config(state="disabled")
                        text_area.pack(fill='both', expand=True)
                except Exception as e:
                    ttk.Label(node_frame, text=f"Error generating preview: {e}", bootstyle="danger").pack()
            else:
                ttk.Label(node_frame, text=" (Modul ini tidak mendukung data preview) ", bootstyle="secondary").pack()
_UNUSED_SIGNATURE = 'B3Ba%m#rDeKa' # Embedded Signature
_UNUSED_SIGNATURE = 'B3Ba%m#rDeKa' # Embedded Signature

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\widgets\logic_toolbox_widget\__init__.py
# JUMLAH BARIS : 3
#######################################################################

```py
from flowork_gui.api_client.client import ApiClient
# COMMENT: Old direct kernel import, replaced by refactor script.
# from flowork_kernel.api_client import ApiClient

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\widgets\logic_toolbox_widget\logic_toolbox_widget.py
# JUMLAH BARIS : 131
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\widgets\logic_toolbox_widget\logic_toolbox_widget.py
# JUMLAH BARIS : 130
#######################################################################

from flowork_kernel.core import build_security
import ttkbootstrap as ttk
from tkinter import ttk as tk_ttk, StringVar, messagebox
from flowork_kernel.api_contract import BaseDashboardWidget
from flowork_kernel.ui_shell.custom_widgets.tooltip import ToolTip
from flowork_kernel.utils.performance_logger import log_performance
import threading
import time
from flowork_gui.api_client.client import ApiClient
class LogicToolboxWidget(BaseDashboardWidget):
    TIER = "free"
    """
    Widget to display the Logic and Control Flow Modules toolbox.
    """
    def __init__(self, parent, coordinator_tab, kernel, widget_id: str):
        build_security.perform_runtime_check(__file__)
        super().__init__(parent, coordinator_tab, kernel, widget_id)
        self.parent_tab = coordinator_tab
        self.api_client = ApiClient(kernel=self.kernel)
        self.search_var = StringVar()
        self.search_var.trace_add("write", self._on_search)
        self._debounce_job = None
        self._create_widgets()
        self.refresh_content()
    def on_widget_load(self):
        super().on_widget_load()
        event_bus = self.kernel.get_service("event_bus")
        if event_bus:
            event_bus.subscribe("COMPONENT_LIST_CHANGED", f"logic_toolbox_{self.widget_id}", self.refresh_content)
            self.kernel.write_to_log(f"LogicToolboxWidget ({self.widget_id}) is now subscribed to component changes.", "DEBUG")
    def _create_widgets(self):
        search_frame = ttk.Frame(self)
        search_frame.pack(fill='x', padx=5, pady=5)
        search_frame.columnconfigure(1, weight=1)
        search_frame.columnconfigure(2, weight=0)
        search_icon_label = ttk.Label(search_frame, text="", font=("Font Awesome 6 Free Solid", 9))
        search_icon_label.grid(row=0, column=0, padx=(0, 5))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky="ew")
        ToolTip(search_entry).update_text("Type your goal (e.g., 'read a csv file') to search...")
        reload_button = ttk.Button(search_frame, text="⟳", width=3, command=self._force_reload_and_refresh, style="secondary.TButton")
        reload_button.grid(row=0, column=2, padx=(5,0))
        ToolTip(reload_button).update_text("Reload component list")
        ttk.Label(self, text=self.loc.get('logic_modules_title', fallback="Logic Modules")).pack(pady=5, anchor='w', padx=5)
        self.module_tree = tk_ttk.Treeview(self, columns=(), style="Custom.Treeview", selectmode="browse")
        self.module_tree.heading('#0', text=self.loc.get('module_name_column', fallback="Module Name"))
        self.module_tree.pack(expand=True, fill='both', side='top', padx=5, pady=(0,5))
        self.module_tree.bind("<ButtonPress-1>", self.on_drag_start)
        self.module_tree.bind("<B1-Motion>", self.parent_tab.on_drag_motion)
        self.module_tree.bind("<ButtonRelease-1>", self.parent_tab.on_drag_release)
    def _on_search(self, *args):
        if self._debounce_job:
            self.after_cancel(self._debounce_job)
        self._debounce_job = self.after(300, self.populate_module_toolbox)
    def _force_reload_and_refresh(self):
        for i in self.module_tree.get_children():
            self.module_tree.delete(i)
        self.module_tree.insert("", "end", text="  Reloading and Refreshing...", tags=("loading",))
        threading.Thread(target=self._load_data_worker, args=(True,), daemon=True).start()
    @log_performance("Fetching module list for LogicToolbox")
    def _load_data_worker(self, force_reload: bool = False):
        if force_reload:
            self.api_client.trigger_hot_reload()
            time.sleep(1)
        success, all_modules_data = self.api_client.get_components('modules')
        self.after(0, self.populate_module_toolbox, success, all_modules_data)
    def populate_module_toolbox(self, success=True, all_modules_data=None):
        self.kernel.write_to_log(f"[MATA-MATA LOGIKA] Menerima {len(all_modules_data) if all_modules_data is not None else 0} total komponen dari API.", "WARN")
        if all_modules_data:
            for comp in all_modules_data:
                self.kernel.write_to_log(f"  -> Mata-Mata Cek: ID='{comp.get('id')}', Type='{comp.get('manifest', {}).get('type')}'", "DEBUG")
        search_query = self.search_var.get().strip().lower()
        for i in self.module_tree.get_children():
            self.module_tree.delete(i)
        if all_modules_data is None:
            success, all_modules_data = self.api_client.get_components('modules')
        if not success:
            self.module_tree.insert('', 'end', text="  Error: Could not fetch modules...")
            return
        logic_modules_data = [
            mod for mod in all_modules_data
            if mod.get('manifest', {}).get('type') in ['LOGIC', 'CONTROL_FLOW']
        ]
        self.kernel.write_to_log(f"[MATA-MATA LOGIKA] Setelah filter, ditemukan {len(logic_modules_data)} komponen valid untuk ditampilkan.", "WARN")
        modules_to_display = []
        if not search_query:
            for module_data in logic_modules_data:
                 modules_to_display.append((module_data['id'], module_data))
            sorted_modules = sorted(modules_to_display, key=lambda item: item[1].get('name', item[0]).lower())
        else:
            for module_data in logic_modules_data:
                search_haystack = f"{module_data.get('name','')} {module_data.get('description','')}".lower()
                if search_query in search_haystack:
                    modules_to_display.append((module_data['id'], module_data))
            sorted_modules = modules_to_display
        for module_id, module_data in sorted_modules:
            tier = module_data.get('tier', 'free').capitalize()
            display_name = module_data.get('name', 'Unknown')
            label = f" {display_name}"
            if tier.lower() != 'free':
                label += f" [{tier}]"
            is_sufficient = self.kernel.is_tier_sufficient(tier.lower())
            tag = 'sufficient' if is_sufficient else 'insufficient'
            self.module_tree.insert('', 'end', iid=module_id, text=label, tags=(tag, tier.lower()))
        self.module_tree.tag_configure('insufficient', foreground='grey')
        self.update_idletasks()
    def on_drag_start(self, event):
        item_id = self.module_tree.identify_row(event.y)
        if not item_id or 'category' in self.module_tree.item(item_id, "tags"): return
        tags = self.module_tree.item(item_id, "tags")
        if 'insufficient' in tags:
            messagebox.showwarning(
                self.loc.get('license_popup_title'),
                self.loc.get('license_popup_message', module_name=self.module_tree.item(item_id, "text").strip()),
                parent=self.winfo_toplevel()
            )
            tab_manager = self.kernel.get_service("tab_manager_service")
            if tab_manager: tab_manager.open_managed_tab("pricing_page")
            return
        self.parent_tab.on_drag_start(event)
    def refresh_content(self, event_data=None):
        self.kernel.write_to_log("LogicToolboxWidget received signal to refresh from EventBus.", "INFO") # English Log
        threading.Thread(target=self._load_data_worker, args=(False,), daemon=True).start()

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\widgets\log_viewer_widget\__init__.py
# JUMLAH BARIS : 3
#######################################################################

```py
from flowork_gui.api_client.client import ApiClient
# COMMENT: Old direct kernel import, replaced by refactor script.
# from flowork_kernel.api_client import ApiClient

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\widgets\log_viewer_widget\log_viewer_widget.py
# JUMLAH BARIS : 117
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\widgets\log_viewer_widget\log_viewer_widget.py
# JUMLAH BARIS : 116
#######################################################################

from flowork_kernel.core import build_security
from flowork_kernel.core import build_security
from flowork_kernel.core import build_security
import ttkbootstrap as ttk
from tkinter import Text, ttk as tk_ttk
import datetime
from flowork_kernel.api_contract import BaseDashboardWidget
from flowork_gui.api_client.client import ApiClient
class LogViewerWidget(BaseDashboardWidget):
    TIER = "free"  # ADDED BY SCANNER: Default tier
    """Widget mandiri untuk menampilkan, memfilter, dan mengelola log eksekusi."""
    def __init__(self, parent, coordinator_tab, kernel, widget_id: str):
        self.api_client = ApiClient(kernel=self.kernel)
        build_security.perform_runtime_check(__file__)
        build_security.perform_runtime_check(__file__)
        build_security.perform_runtime_check(__file__)
        super().__init__(parent, coordinator_tab, kernel, widget_id)
        self._all_log_entries = []
        self._create_widgets()
        self.on_widget_load()
    def on_widget_load(self):
        """Dipanggil oleh DashboardManager saat widget berhasil dibuat dan ditampilkan."""
        super().on_widget_load()
        if hasattr(self.kernel, 'register_log_viewer'):
            self.kernel.register_log_viewer(self.coordinator_tab.tab_id, self)
    def on_widget_destroy(self):
        """Dipanggil oleh DashboardManager saat widget akan dihancurkan."""
        super().on_widget_destroy()
        if hasattr(self.kernel, 'unregister_log_viewer'):
            self.kernel.unregister_log_viewer(self.coordinator_tab.tab_id)
    def _create_widgets(self):
        ttk.Label(self, text=self.loc.get('execution_log_title'), style='TLabel').pack(pady=5, anchor='w', padx=5)
        log_filter_frame = ttk.Frame(self, style='TFrame')
        log_filter_frame.pack(fill='x', pady=(0, 5), padx=5)
        self.search_entry = ttk.Entry(log_filter_frame, style='Prop.TEntry')
        self.search_entry.pack(side='left', expand=True, fill='x', padx=(0, 5))
        self.search_entry.insert(0, self.loc.get('search_log_placeholder'))
        self.search_entry.bind("<KeyRelease>", self._filter_logs)
        self.filter_combobox = ttk.Combobox(log_filter_frame, values=[self.loc.get(k) for k in ['log_level_all', 'log_level_info', 'log_level_warn', 'log_level_error', 'log_level_success', 'log_level_debug', 'log_level_cmd', 'log_level_detail']], state="readonly")
        self.filter_combobox.set(self.loc.get('log_level_all'))
        self.filter_combobox.pack(side='left')
        self.filter_combobox.bind("<<ComboboxSelected>>", self._filter_logs)
        log_button_frame = ttk.Frame(self, style='TFrame')
        log_button_frame.pack(fill='x', side='bottom', pady=(5,5), padx=5)
        ttk.Button(log_button_frame, text=self.loc.get('copy_log_button'), command=self.copy_log_to_clipboard, style="info.TButton").pack(side='left', expand=True, fill='x', padx=(0, 2))
        ttk.Button(log_button_frame, text=self.loc.get('clear_log_button'), command=self.clear_log, style="success.TButton").pack(side='left', expand=True, fill='x')
        log_text_container = ttk.Frame(self, style='TFrame')
        log_text_container.pack(expand=True, fill='both', side='top', padx=5)
        self.log_text = Text(log_text_container, wrap='word', height=10, state='disabled')
        log_text_scroll = ttk.Scrollbar(log_text_container, command=self.log_text.yview)
        log_text_scroll.pack(side='right', fill='y')
        self.log_text.pack(side='left', expand=True, fill='both')
        self.log_text.config(yscrollcommand=log_text_scroll.set)
        theme_manager = self.kernel.get_service("theme_manager")
        colors = theme_manager.get_colors() if theme_manager else {}
        self.log_text.tag_config("INFO", foreground=colors.get('fg', 'white'))
        self.log_text.tag_config("SUCCESS", foreground=colors.get('success', '#76ff7b'))
        self.log_text.tag_config("WARN", foreground=colors.get('warning', '#ffb627'))
        self.log_text.tag_config("ERROR", foreground=colors.get('danger', '#ff686b'))
        self.log_text.tag_config("DEBUG", foreground=colors.get('info', '#8be9fd'))
        self.log_text.tag_config("CMD", foreground=colors.get('primary', '#007bff'))
        self.log_text.tag_config("DETAIL", foreground=colors.get('secondary', 'grey'))
    def copy_log_to_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append(self.log_text.get('1.0', 'end'))
        self.kernel.write_to_log(self.loc.get('log_copied_to_clipboard'), "SUCCESS")
    def clear_log(self, feedback=True):
        self._all_log_entries = []
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', 'end')
        self.log_text.config(state='disabled')
        if feedback:
            self.kernel.write_to_log(self.loc.get('log_cleared'), "WARN")
    def write_to_log(self, message, level="INFO"):
        try:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            tag = level.upper()
            entry = {"timestamp": timestamp, "message": message, "level": tag}
            self._all_log_entries.append(entry)
            self._filter_logs()
        except Exception as e:
            print(f"CRITICAL LOGGING ERROR: {e} - Message: {message}")
    def _filter_logs(self, event=None):
        search_term = self.search_entry.get().strip().lower()
        if search_term == self.loc.get('search_log_placeholder').lower():
            search_term = ""
        level_map = {
            self.loc.get('log_level_all').upper(): 'ALL',
            self.loc.get('log_level_info').upper(): 'INFO',
            self.loc.get('log_level_warn').upper(): 'WARN',
            self.loc.get('log_level_error').upper(): 'ERROR',
            self.loc.get('log_level_success').upper(): 'SUCCESS',
            self.loc.get('log_level_debug').upper(): 'DEBUG',
            self.loc.get('log_level_cmd').upper(): 'CMD',
            self.loc.get('log_level_detail').upper(): 'DETAIL'
        }
        selected_display_level = self.filter_combobox.get().strip().upper()
        internal_level = level_map.get(selected_display_level, 'ALL')
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', 'end')
        for entry in self._all_log_entries:
            if (not search_term or search_term in entry["message"].lower()) and (internal_level == 'ALL' or entry["level"] == internal_level):
                self.log_text.insert('end', f"[{entry['timestamp']}] ", ("DETAIL",))
                self.log_text.insert('end', f"{entry['message']}\n", (entry['level'],))
        self.log_text.see('end')
        self.log_text.config(state='disabled')
_UNUSED_SIGNATURE = 'B3Ba%m#rDeKa' # Embedded Signature
_UNUSED_SIGNATURE = 'B3Ba%m#rDeKa' # Embedded Signature
_UNUSED_SIGNATURE = 'B3Ba%m#rDeKa' # Embedded Signature

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\widgets\plugin_toolbox_widget\__init__.py
# JUMLAH BARIS : 3
#######################################################################

```py
from flowork_gui.api_client.client import ApiClient
# COMMENT: Old direct kernel import, replaced by refactor script.
# from flowork_kernel.api_client import ApiClient

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\widgets\plugin_toolbox_widget\plugin_toolbox_widget.py
# JUMLAH BARIS : 140
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\widgets\plugin_toolbox_widget\plugin_toolbox_widget.py
# JUMLAH BARIS : 139
#######################################################################

from flowork_kernel.core import build_security
import ttkbootstrap as ttk
from tkinter import ttk as tk_ttk, StringVar, messagebox
from flowork_kernel.api_contract import BaseDashboardWidget
from flowork_kernel.ui_shell.custom_widgets.tooltip import ToolTip
from flowork_kernel.utils.performance_logger import log_performance
import threading
import time
from flowork_gui.api_client.client import ApiClient
class PluginToolboxWidget(BaseDashboardWidget):
    TIER = "free"
    """
    Widget to display the Action and Plugin toolbox.
    (FIXED V2) Correctly fetches and filters both ACTION modules and PLUGIN components.
    """
    def __init__(self, parent, coordinator_tab, kernel, widget_id: str):
        build_security.perform_runtime_check(__file__)
        super().__init__(parent, coordinator_tab, kernel, widget_id)
        self.parent_tab = coordinator_tab
        self.api_client = ApiClient(kernel=self.kernel)
        self.search_var = StringVar()
        self.search_var.trace_add("write", self._on_search)
        self._debounce_job = None
        self._create_widgets()
        self.refresh_content()
    def on_widget_load(self):
        super().on_widget_load()
        event_bus = self.kernel.get_service("event_bus")
        if event_bus:
            event_bus.subscribe("COMPONENT_LIST_CHANGED", f"plugin_toolbox_{self.widget_id}", self.refresh_content)
            self.kernel.write_to_log(f"PluginToolboxWidget ({self.widget_id}) is now subscribed to component changes.", "DEBUG")
    def _create_widgets(self):
        search_frame = ttk.Frame(self)
        search_frame.pack(fill='x', padx=5, pady=5)
        search_frame.columnconfigure(1, weight=1)
        search_frame.columnconfigure(2, weight=0)
        search_icon_label = ttk.Label(search_frame, text="", font=("Font Awesome 6 Free Solid", 9))
        search_icon_label.grid(row=0, column=0, padx=(0, 5))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky="ew")
        ToolTip(search_entry).update_text("Type to search plugins...")
        reload_button = ttk.Button(search_frame, text="⟳", width=3, command=self._force_reload_and_refresh, style="secondary.TButton")
        reload_button.grid(row=0, column=2, padx=(5,0))
        ToolTip(reload_button).update_text("Reload component list")
        ttk.Label(self, text=self.loc.get('action_plugins_title', fallback="Action & Plugin Toolbox"), style='TLabel').pack(pady=5, anchor='w', padx=5)
        self.plugin_tree = tk_ttk.Treeview(self, columns=(), style="Custom.Treeview", selectmode="browse")
        self.plugin_tree.heading('#0', text=self.loc.get('plugin_name_column', fallback="Plugin Name"))
        self.plugin_tree.pack(expand=True, fill='both', side='top', padx=5, pady=(0,5))
        self.plugin_tree.bind("<ButtonPress-1>", self.on_drag_start)
        self.plugin_tree.bind("<B1-Motion>", self.parent_tab.on_drag_motion)
        self.plugin_tree.bind("<ButtonRelease-1>", self.parent_tab.on_drag_release)
    def _on_search(self, *args):
        if self._debounce_job:
            self.after_cancel(self._debounce_job)
        self._debounce_job = self.after(300, self.populate_plugin_panel)
    def _force_reload_and_refresh(self):
        for i in self.plugin_tree.get_children():
            self.plugin_tree.delete(i)
        self.plugin_tree.insert("", "end", text="  Reloading and Refreshing...", tags=("loading",))
        threading.Thread(target=self._load_data_worker, args=(True,), daemon=True).start()
    @log_performance("Fetching data for PluginToolbox")
    def _load_data_worker(self, force_reload: bool = False):
        if force_reload:
            self.api_client.trigger_hot_reload()
            time.sleep(1)
        success_modules, modules_data = self.api_client.get_components('modules')
        success_plugins, plugins_data = self.api_client.get_components('plugins')
        combined_data = []
        if success_modules:
            combined_data.extend(modules_data)
        if success_plugins:
            combined_data.extend(plugins_data)
        self.after(0, self.populate_plugin_panel, True, combined_data)
    def populate_plugin_panel(self, success=True, all_components_data=None):
        self.kernel.write_to_log(f"[MATA-MATA PLUGIN] Menerima {len(all_components_data) if all_components_data is not None else 0} total komponen dari API.", "WARN")
        if all_components_data:
            for comp in all_components_data:
                self.kernel.write_to_log(f"  -> Mata-Mata Cek: ID='{comp.get('id')}', Type='{comp.get('manifest', {}).get('type')}'", "DEBUG")
        search_query = self.search_var.get().strip().lower()
        for i in self.plugin_tree.get_children():
            self.plugin_tree.delete(i)
        if all_components_data is None:
            threading.Thread(target=self._load_data_worker, daemon=True).start()
            return
        if not success:
            self.plugin_tree.insert('', 'end', text="  Error: Could not fetch components...")
            return
        filtered_components = [
            comp for comp in all_components_data
            if comp.get('manifest', {}).get('type') in ['ACTION', 'PLUGIN']
        ]
        self.kernel.write_to_log(f"[MATA-MATA PLUGIN] Setelah filter, ditemukan {len(filtered_components)} komponen valid untuk ditampilkan.", "WARN")
        components_to_display = []
        if not search_query:
            for data in filtered_components:
                 components_to_display.append((data['id'], data))
            sorted_components = sorted(components_to_display, key=lambda item: item[1].get('name', item[0]).lower())
        else:
            for data in filtered_components:
                search_haystack = f"{data.get('name','')} {data.get('description','')}".lower()
                if search_query in search_haystack:
                    components_to_display.append((data['id'], data))
            sorted_components = components_to_display
        for comp_id, comp_data in sorted_components:
            tier = comp_data.get('tier', 'free').capitalize()
            display_name = comp_data.get('name', 'Unknown')
            label = f" {display_name}"
            if tier.lower() != 'free':
                label += f" [{tier}]"
            is_sufficient = self.kernel.is_tier_sufficient(tier.lower())
            tag = 'sufficient' if is_sufficient else 'insufficient'
            self.plugin_tree.insert('', 'end', iid=comp_id, text=label, tags=(tag, tier.lower()))
        self.plugin_tree.tag_configure('insufficient', foreground='grey')
        self.update_idletasks()
    def on_drag_start(self, event):
        item_id = self.plugin_tree.identify_row(event.y)
        if not item_id or 'category' in self.plugin_tree.item(item_id, "tags"): return
        tags = self.plugin_tree.item(item_id, "tags")
        if 'insufficient' in tags:
            messagebox.showwarning(
                self.loc.get('license_popup_title'),
                self.loc.get('license_popup_message', module_name=self.plugin_tree.item(item_id, "text").strip()),
                parent=self.winfo_toplevel()
            )
            tab_manager = self.kernel.get_service("tab_manager_service")
            if tab_manager: tab_manager.open_managed_tab("pricing_page")
            return
        self.parent_tab.on_drag_start(event)
    def refresh_content(self, event_data=None):
        """Called to refresh the widget list if there are changes."""
        self.kernel.write_to_log("PluginToolboxWidget received signal to refresh from EventBus.", "INFO")
        threading.Thread(target=self._load_data_worker, args=(False,), daemon=True).start()

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\widgets\prompt_sender_widget\__init__.py
# JUMLAH BARIS : 3
#######################################################################

```py
from flowork_gui.api_client.client import ApiClient
# COMMENT: Old direct kernel import, replaced by refactor script.
# from flowork_kernel.api_client import ApiClient

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\widgets\prompt_sender_widget\prompt_sender_widget.py
# JUMLAH BARIS : 58
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\widgets\prompt_sender_widget\prompt_sender_widget.py
# JUMLAH BARIS : 57
#######################################################################

from flowork_kernel.core import build_security
import ttkbootstrap as ttk
from tkinter import StringVar, scrolledtext, messagebox
from flowork_kernel.api_contract import BaseDashboardWidget
from flowork_gui.api_client.client import ApiClient
class PromptSenderWidget(BaseDashboardWidget):
    """
    A UI widget to send a text prompt to a specific 'Prompt Receiver' node on the canvas.
    """
    def __init__(self, parent, coordinator_tab, kernel, widget_id: str, **kwargs):
        self.api_client = ApiClient(kernel=self.kernel)
        build_security.perform_runtime_check(__file__)
        super().__init__(parent, coordinator_tab, kernel, widget_id, **kwargs)
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)
        self.target_node_id_var = StringVar(value="receiver-node-1")
        id_frame = ttk.Frame(main_frame)
        id_frame.pack(fill="x", pady=(0, 5))
        ttk.Label(id_frame, text=self.loc.get('prompt_sender_target_id_label', fallback="Target Node ID:")).pack(side="left")
        id_entry = ttk.Entry(id_frame, textvariable=self.target_node_id_var)
        id_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
        self.prompt_text = scrolledtext.ScrolledText(main_frame, height=4, wrap="word", font=("Segoe UI", 10))
        self.prompt_text.pack(fill="both", expand=True, pady=(0, 5))
        send_button = ttk.Button(
            main_frame,
            text=self.loc.get('prompt_sender_send_button', fallback="Send Prompt"),
            command=self._send_prompt,
            bootstyle="primary"
        )
        send_button.pack(fill="x")
    def _send_prompt(self):
        target_node_id = self.target_node_id_var.get().strip()
        prompt_content = self.prompt_text.get("1.0", "end-1c").strip()
        if not target_node_id or not prompt_content:
            messagebox.showwarning(
                self.loc.get('prompt_sender_warning_title', fallback="Input Required"),
                self.loc.get('prompt_sender_warning_message', fallback="Please provide both a target node ID and a prompt.")
            )
            return
        event_bus = self.kernel.get_service("event_bus")
        if event_bus:
            event_name = f"PROMPT_FROM_WIDGET_{target_node_id}"
            event_data = {
                "prompt": prompt_content,
                "sender_widget_id": self.widget_id
            }
            event_bus.publish(event_name, event_data, publisher_id=self.widget_id)
            self.kernel.write_to_log(f"Prompt sent to event '{event_name}'.", "SUCCESS")
            self.prompt_text.delete("1.0", "end")
_UNUSED_SIGNATURE = 'B3Ba%m#rDeKa' # Embedded Signature

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\widgets\widget_toolbox\__init__.py
# JUMLAH BARIS : 3
#######################################################################

```py
from flowork_gui.api_client.client import ApiClient
# COMMENT: Old direct kernel import, replaced by refactor script.
# from flowork_kernel.api_client import ApiClient

```

#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\widgets\widget_toolbox\widget_toolbox_widget.py
# JUMLAH BARIS : 107
#######################################################################

```py
#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\widgets\widget_toolbox\widget_toolbox_widget.py
# JUMLAH BARIS : 106
#######################################################################

from flowork_kernel.core import build_security
import ttkbootstrap as ttk
from tkinter import ttk as tk_ttk
from flowork_kernel.api_contract import BaseDashboardWidget
from flowork_kernel.ui_shell.custom_widgets.tooltip import ToolTip
from tkinter import StringVar
import threading
from flowork_kernel.utils.performance_logger import log_performance
import time # (ADDED) Import time for delay after reload
from flowork_gui.api_client.client import ApiClient
class WidgetToolboxWidget(BaseDashboardWidget):
    TIER = "free"
    """
    Widget to display the toolbox of available widgets.
    (MODIFIED) Refresh button now triggers a full system hot-reload.
    """
    def __init__(self, parent, coordinator_tab, kernel, widget_id: str):
        build_security.perform_runtime_check(__file__)
        super().__init__(parent, coordinator_tab, kernel, widget_id)
        self.coordinator_tab = coordinator_tab
        self.api_client = ApiClient(kernel=self.kernel)
        self.search_var = StringVar()
        self.search_var.trace_add("write", self._on_search)
        self._create_widgets()
        self.refresh_content()
    def on_widget_load(self):
        """Called by DashboardManager when the widget is fully loaded."""
        super().on_widget_load()
        event_bus = self.kernel.get_service("event_bus")
        if event_bus:
            event_bus.subscribe("COMPONENT_LIST_CHANGED", f"widget_toolbox_{self.widget_id}", self.refresh_content)
            self.kernel.write_to_log(f"WidgetToolboxWidget ({self.widget_id}) is now subscribed to component changes.", "DEBUG")
    def _create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        search_frame = ttk.Frame(self)
        search_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        search_frame.columnconfigure(1, weight=1)
        search_frame.columnconfigure(2, weight=0)
        search_icon_label = ttk.Label(search_frame, text="", font=("Font Awesome 6 Free Solid", 9))
        search_icon_label.grid(row=0, column=0, padx=(0, 5))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky="ew")
        ToolTip(search_entry).update_text("Type to search widgets...")
        reload_button = ttk.Button(search_frame, text="⟳", width=3, command=self._force_reload_and_refresh, style="secondary.TButton")
        reload_button.grid(row=0, column=2, padx=(5,0))
        ToolTip(reload_button).update_text("Reload component list")
        ttk.Label(self, text=self.loc.get('available_widgets_header', fallback="Available Widgets")).grid(row=1, column=0, sticky='w', padx=5, pady=(5,0))
        self.widget_tree = tk_ttk.Treeview(self, show="tree", selectmode="browse")
        self.widget_tree.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)
        self.widget_tree.bind("<Double-1>", self._on_widget_select)
    def _on_search(self, *args):
        self.populate_widget_toolbox()
    def _force_reload_and_refresh(self):
        for i in self.widget_tree.get_children():
            self.widget_tree.delete(i)
        self.widget_tree.insert("", "end", text="  Reloading and Refreshing...", tags=("loading",))
        threading.Thread(target=self._load_data_worker, args=(True,), daemon=True).start()
    @log_performance("Fetching widget list for WidgetToolbox")
    def _load_data_worker(self, force_reload: bool = False):
        if force_reload:
            self.api_client.trigger_hot_reload()
            time.sleep(1)
        success, all_widgets_data = self.api_client.get_components('widgets')
        self.after(0, self.populate_widget_toolbox, success, all_widgets_data)
    def populate_widget_toolbox(self, success=True, all_widgets_data=None):
        filter_text = self.search_var.get().lower()
        for item in self.widget_tree.get_children():
            self.widget_tree.delete(item)
        if all_widgets_data is None:
             success, all_widgets_data = self.api_client.get_components('widgets')
        if not success:
            self.widget_tree.insert("", "end", text="  Error: Could not fetch widgets...")
            return
        widgets_to_display = []
        if not filter_text:
            for widget_data in all_widgets_data:
                 widgets_to_display.append((widget_data['id'], widget_data.get('name', widget_data['id'])))
            sorted_widgets = sorted(widgets_to_display, key=lambda item: item[1].lower())
        else:
            for widget_data in all_widgets_data:
                search_haystack = f"{widget_data.get('name','')} {widget_data.get('description','')}".lower()
                if filter_text in search_haystack:
                    widgets_to_display.append((widget_data['id'], widget_data.get('name', widget_data['id'])))
            sorted_widgets = widgets_to_display
        for key, title in sorted_widgets:
            self.widget_tree.insert("", "end", iid=key, text=title)
        self.update_idletasks()
    def _on_widget_select(self, event):
        item_id = self.widget_tree.focus()
        if item_id:
            dashboard_manager = self.coordinator_tab.dashboard_manager
            if dashboard_manager:
                dashboard_manager.add_widget_and_save(item_id, event.x, event.y)
    def refresh_content(self, event_data=None):
        """Called to refresh the widget list if there are changes."""
        self.kernel.write_to_log("WidgetToolboxWidget received signal to refresh from EventBus.", "INFO")
        threading.Thread(target=self._load_data_worker, args=(False,), daemon=True).start()
_UNUSED_SIGNATURE = 'B3Ba%m#rDeKa' # Embedded Signature

```