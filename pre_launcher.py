#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\pre_launcher.py
# (Full code for the STABLE version with static GIF)
#######################################################################

import tkinter as tk
from tkinter import ttk
import threading
import subprocess
import os
import sys
import time

# --- Constants ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PID_FILE = os.path.join(PROJECT_ROOT, "pre_launcher.pid")
FIRST_RUN_LOCK_FILE = os.path.join(PROJECT_ROOT, "data", ".first_run_complete")
GIF_PATH = os.path.join(PROJECT_ROOT, "teetah.gif") # (PENTING) Pastikan teetah.gif ada di sini

class PreloaderWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.attributes('-topmost', True)

        width, height = 300, 180 # Sedikit lebih tinggi untuk logo dan teks
        screen_width, screen_height = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = (screen_width // 2) - (width // 2), (screen_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        self.config(bg="#2c3e50")
        style = ttk.Style()
        style.configure("Preload.TLabel", background="#2c3e50", foreground="#ecf0f1", font=("Helvetica", 11))

        # (MODIFIED) Logic to display static GIF without Pillow
        self.logo_label = ttk.Label(self, style="Preload.TLabel")
        self.logo_label.pack(pady=(20, 10))

        try:
            self.logo_photo = tk.PhotoImage(file=GIF_PATH)
            self.logo_label.config(image=self.logo_photo)
        except tk.TclError:
            # This happens if the GIF format is complex or the file is missing
            self.logo_label.config(text="Teetah")
            print(f"Warning: Could not load {GIF_PATH}. It might be missing or in an unsupported GIF format for Tkinter.")
        except Exception as e:
            self.logo_label.config(text="Teetah")
            print(f"An error occurred while loading teetah.gif: {e}")

        self.status_label = ttk.Label(self, text="Starting Flowork...", style="Preload.TLabel")
        self.status_label.pack(pady=(5, 20), fill="x", padx=10)

    def update_status(self, text):
        self.status_label.config(text=text)

def run_background_processes(window_instance):
    """
    The smart startup logic. Checks for first run before launching.
    """
    try:
        is_first_run = not os.path.exists(FIRST_RUN_LOCK_FILE)

        if is_first_run:
            window_instance.update_status("Performing first-time setup...\nThis may take a few minutes.")

            bootstrap_script_path = os.path.join(PROJECT_ROOT, "scripts", "bootstrap.py")
            python_exe = os.path.join(PROJECT_ROOT, "python", "python.exe")

            # Run bootstrap silently for the user
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

        time.sleep(20)
        if window_instance.winfo_exists():
            window_instance.destroy()

    except Exception as e:
        window_instance.update_status(f"A fatal error occurred:\n{e}")
        # In case of error, we create a log file for the user to check
        with open(os.path.join(PROJECT_ROOT, "pre_launcher_error.log"), "w") as f:
            f.write(str(e))
            f.write("\n\n")
            f.write(traceback.format_exc())
        time.sleep(15) # Give the user time to read the error
        if window_instance.winfo_exists():
            window_instance.destroy()

if __name__ == "__main__":
    # This block remains the same
    try:
        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))
        app = PreloaderWindow()
        threading.Thread(target=run_background_processes, args=(app,), daemon=True).start()
        app.mainloop()
    finally:
        if os.path.exists(PID_FILE):
            try: os.remove(PID_FILE)
            except OSError: pass