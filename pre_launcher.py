#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\pre_launcher.py
# JUMLAH BARIS : 130
#######################################################################

import tkinter as tk
from tkinter import ttk
import threading
import subprocess
import os
import sys
import time
import traceback # [ADDED] To log errors properly
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PID_FILE = os.path.join(PROJECT_ROOT, "pre_launcher.pid")
FIRST_RUN_LOCK_FILE = os.path.join(PROJECT_ROOT, "data", ".first_run_complete")
GIF_PATH = os.path.join(PROJECT_ROOT, "teetah.gif")
DEV_MODE_FILE = os.path.join(PROJECT_ROOT, "devmode.on") # [ADDED] Path to devmode file
MAIN_APP_READY_SIGNAL = os.path.join(PROJECT_ROOT, "data", ".main_app_ready") # [ADDED] Signal file path
DEV_MODE_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAysqZG2+F82W0TgLHmF3Y
0GRPEZvXvmndTY84N/wA1ljt+JxMBVsmcVTkv8f1TrmFRD19IDzl2Yzb2lgqEbEy
GFxHhudC28leDsVEIp8B+oYWVm8Mh242YKYK8r5DAvr9CPQivnIjZ4BWgKKddMTd
harVxLF2CoSoTs00xWKd6VlXfoW9wdBvoDVifL+hCMepgLLdQQE4HbamPDJ3bpra
pCgcAD5urmVoJEUJdjd+Iic27RBK7jD1dWDO2MASMh/0IyXyM8i7RDymQ88gZier
U0OdWzeCWGyl4EquvR8lj5GNz4vg2f+oEY7h9AIC1f4ARtoihc+apSntqz7nAqa/
sQIDAQAB
-----END PUBLIC KEY-----"""
class PreloaderWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        width, height = 300, 180
        screen_width, screen_height = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = (screen_width // 2) - (width // 2), (screen_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        self.config(bg="#2c3e50")
        style = ttk.Style()
        style.configure("Preload.TLabel", background="#2c3e50", foreground="#ecf0f1", font=("Helvetica", 11))
        self.logo_label = ttk.Label(self, style="Preload.TLabel")
        self.logo_label.pack(pady=(20, 10))
        try:
            self.logo_photo = tk.PhotoImage(file=GIF_PATH)
            self.logo_label.config(image=self.logo_photo)
        except tk.TclError:
            self.logo_label.config(text="Teetah")
        except Exception as e:
            self.logo_label.config(text="Teetah")
        self.status_label = ttk.Label(self, text="Starting Flowork...", style="Preload.TLabel") # English Hardcode
        self.status_label.pack(pady=(5, 20), fill="x", padx=10)
    def update_status(self, text):
        self.status_label.config(text=text)
def _validate_dev_mode():
    if not os.path.exists(DEV_MODE_FILE):
        return False
    try:
        with open(DEV_MODE_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        if content == DEV_MODE_PUBLIC_KEY.strip():
            return True
        else:
            return False
    except Exception:
        return False
def run_background_processes(window_instance):
    """
    [MODIFIED] The smart startup logic. Now detects dev mode and runs the appropriate script.
    It now also waits for a signal file from the main app instead of a fixed time.
    """
    try:
        is_dev_mode_active = _validate_dev_mode()
        if os.path.exists(MAIN_APP_READY_SIGNAL):
            os.remove(MAIN_APP_READY_SIGNAL)
        if is_dev_mode_active:
            window_instance.update_status("DEVELOPMENT MODE ACTIVE\nLaunching main application...") # English Hardcode
            command = ['poetry', 'run', 'pythonw', 'main.py'] # Use pythonw to keep it silent
            subprocess.Popen(command, cwd=PROJECT_ROOT, shell=True)
        else:
            is_first_run = not os.path.exists(FIRST_RUN_LOCK_FILE)
            if is_first_run:
                window_instance.update_status("Performing first-time setup...\nThis may take a few minutes.")
                bootstrap_script_path = os.path.join(PROJECT_ROOT, "scripts", "bootstrap.py")
                python_exe = os.path.join(PROJECT_ROOT, "python", "python.exe")
                creation_flags = 0
                if sys.platform == "win32":
                    creation_flags = subprocess.CREATE_NO_WINDOW
                result = subprocess.run([python_exe, bootstrap_script_path], cwd=PROJECT_ROOT, capture_output=True, text=True, creationflags=creation_flags)
                if result.returncode != 0:
                     raise Exception(f"Bootstrap script failed:\n{result.stderr}")
            window_instance.update_status("Loading FLOWORK...")
            launcher_script_path = os.path.join(PROJECT_ROOT, "launcher.py")
            pythonw_exe = os.path.join(PROJECT_ROOT, "python", "pythonw.exe")
            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = subprocess.CREATE_NO_WINDOW
            subprocess.Popen([pythonw_exe, launcher_script_path], cwd=PROJECT_ROOT, creationflags=creation_flags)
        timeout_seconds = 60 # Wait for up to 60 seconds
        start_time = time.time()
        window_instance.update_status("Waiting for application to initialize...") # English hardcode
        while not os.path.exists(MAIN_APP_READY_SIGNAL):
            if time.time() - start_time > timeout_seconds:
                raise TimeoutError("Main application failed to send the ready signal within the time limit.")
            time.sleep(0.5)
        if window_instance.winfo_exists():
            window_instance.destroy()
    except Exception as e:
        window_instance.update_status(f"A fatal error occurred:\n{e}")
        with open(os.path.join(PROJECT_ROOT, "pre_launcher_error.log"), "w") as f:
            f.write(str(e))
            f.write("\n\n")
            f.write(traceback.format_exc())
        time.sleep(15)
        if window_instance.winfo_exists():
            window_instance.destroy()
if __name__ == "__main__":
    try:
        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))
        app = PreloaderWindow()
        threading.Thread(target=run_background_processes, args=(app,), daemon=True).start()
        app.mainloop()
    finally:
        if os.path.exists(PID_FILE):
            try:
                os.remove(PID_FILE)
            except OSError:
                pass
