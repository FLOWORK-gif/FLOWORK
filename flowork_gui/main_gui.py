#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_gui\main_gui.py
# JUMLAH BARIS : 242
#######################################################################

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
def ensure_required_files_exist():
    """
    Checks for and creates necessary __init__.py files AND other critical files like exceptions.py.
    This makes the GUI package truly self-healing and robust against missing files.
    """
    print("[INFO] Verifying project structure and required files...") # English Log
    try:
        project_root = os.path.dirname(os.path.abspath(__file__))
        required_package_dirs = [
            ".", "api_client", "core", "utils", # Root level packages
            "views", "views/canvas_components", "views/canvas_components/interactions",
            "views/components", "views/custom_widgets", "views/lifecycle", "views/popups",
            "views/ui_components", "views/ui_components/controllers",
            "plugins", "plugins/flowork_core_ui", "plugins/flowork_core_ui/components",
            "plugins/flowork_core_ui/generator_components", "plugins/flowork_core_ui/settings_components",
            "plugins/metrics_dashboard", "plugins/metrics_logger_plugin",
            "plugins/system_diagnostics_plugin", # <-- INI YANG KURANG KEMARIN
            "widgets", "widgets/canvas_area", "widgets/data_canvas_widget",
            "widgets/dataset_manager_widget", "widgets/logic_toolbox_widget", "widgets/log_viewer_widget",
            "widgets/plugin_toolbox_widget", "widgets/prompt_sender_widget", "widgets/widget_toolbox"
        ]
        for rel_dir in required_package_dirs:
            dir_path = os.path.join(project_root, rel_dir.replace('/', os.sep)) # Handle path separators
            init_path = os.path.join(dir_path, "__init__.py")
            if not os.path.exists(init_path):
                os.makedirs(dir_path, exist_ok=True)
                with open(init_path, 'w') as f: pass
                print(f"  -> [AUTO-FIX] Created missing package file: {os.path.join(os.path.basename(project_root), rel_dir, '__init__.py')}") # English Log
        exceptions_file_path = os.path.join(project_root, "exceptions.py")
        if not os.path.exists(exceptions_file_path):
            print(f"  -> [AUTO-FIX] Critical file 'exceptions.py' not found. Creating it now...") # English Log
            exceptions_content = '''"""
Central repository for all custom Flowork exceptions for the GUI Client.
"""
class FloworkException(Exception): pass
class PermissionDeniedError(FloworkException): pass
'''
            with open(exceptions_file_path, 'w', encoding='utf-8') as f:
                f.write(exceptions_content)
    except Exception as e:
        print(f"  -> [ERROR] Could not perform self-healing setup: {e}") # English Log
ensure_required_files_exist()
project_root_for_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root_for_path not in sys.path:
    sys.path.insert(0, project_root_for_path)
from flowork_gui.api_client.client import ApiClient
from flowork_gui.views.ui_components.menubar_manager import MenubarManager
from flowork_gui.views.ui_components.tab_manager import UITabManager
from flowork_gui.views.custom_widgets.draggable_notebook import DraggableNotebook
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
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
            def __init__(self):
                self.language_map = {"en": "English", "id": "Bahasa Indonesia"}
            def get(self, key, fallback=None, **kwargs):
                if fallback is None:
                    return f"[{key}]"
                return fallback.format(**kwargs)
            def get_available_languages_display(self):
                return list(self.language_map.values())
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
