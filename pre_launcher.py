#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\pre_launcher.py
# (DIUBAH) Final fix untuk memaksa log error dari main.py muncul
#######################################################################

import tkinter as tk
from tkinter import ttk
import threading
import subprocess
import os
import sys
import time
import traceback

# --- Constants ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PID_FILE = os.path.join(PROJECT_ROOT, "pre_launcher.pid")
FIRST_RUN_LOCK_FILE = os.path.join(PROJECT_ROOT, "data", ".first_run_complete")
GIF_PATH = os.path.join(PROJECT_ROOT, "teetah.gif")
MAIN_APP_READY_SIGNAL = os.path.join(PROJECT_ROOT, "data", ".main_app_ready")


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

        self.status_label = ttk.Label(self, text="Starting Flowork...", style="Preload.TLabel")
        self.status_label.pack(pady=(5, 20), fill="x", padx=10)

    def update_status(self, text):
        self.status_label.config(text=text)
        self.update_idletasks()

def run_background_processes(window_instance):
    try:
        is_first_run = not os.path.exists(FIRST_RUN_LOCK_FILE)

        if is_first_run:
            # (BAGIAN INI TETAP SILENT KARENA SUDAH BERHASIL)
            window_instance.update_status("Performing first-time setup...\nThis may take a few minutes.")
            bootstrap_script_path = os.path.join(PROJECT_ROOT, "scripts", "bootstrap.py")
            python_exe = os.path.join(PROJECT_ROOT, "python", "python.exe")
            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = subprocess.CREATE_NO_WINDOW
            result = subprocess.run([python_exe, bootstrap_script_path], cwd=PROJECT_ROOT, capture_output=True, text=True, creationflags=creation_flags)
            if result.returncode != 0:
                 raise Exception(f"Bootstrap script failed:\n{result.stderr}")

        window_instance.update_status("Loading FLOWORK...\nWaiting for application to be ready...")

        if os.path.exists(MAIN_APP_READY_SIGNAL):
            os.remove(MAIN_APP_READY_SIGNAL)

        launcher_script_path = os.path.join(PROJECT_ROOT, "launcher.py")

        # (DIUBAH) Kita pastikan menggunakan python.exe (versi konsol) untuk debugging
        python_exe_for_main_app = os.path.join(PROJECT_ROOT, "python", "python.exe")

        # (DIUBAH TOTAL) Ini adalah perbaikan utamanya.
        # Kita tidak lagi menggunakan 'creation_flags' saat memanggil aplikasi utama.
        # Ini akan memaksa jendela konsol baru untuk muncul.
        window_instance.update_status("Launching main application...")
        subprocess.Popen([python_exe_for_main_app, launcher_script_path], cwd=PROJECT_ROOT)

        # Loop pendeteksian sinyal tetap sama
        timeout = 90
        start_time = time.time()
        signal_received = False
        while time.time() - start_time < timeout:
            if os.path.exists(MAIN_APP_READY_SIGNAL):
                window_instance.update_status("Application is ready! Finishing up...")
                signal_received = True
                break
            time.sleep(0.5)

        if not signal_received:
            raise TimeoutError(f"Main application did not start within {timeout} seconds.")

        if os.path.exists(MAIN_APP_READY_SIGNAL):
            os.remove(MAIN_APP_READY_SIGNAL)

        time.sleep(1)
        if window_instance.winfo_exists():
            window_instance.destroy()

    except Exception as e:
        error_full_traceback = traceback.format_exc()
        final_error_message = f"A fatal error occurred in Pre-Launcher:\n{e}"
        window_instance.update_status(final_error_message)
        with open(os.path.join(PROJECT_ROOT, "pre_launcher_error.log"), "w", encoding='utf-8') as f:
            f.write(str(e))
            f.write("\n\n")
            f.write(error_full_traceback)
        time.sleep(15)
        if window_instance.winfo_exists():
            window_instance.destroy()

if __name__ == "__main__":
    try:
        os.makedirs(os.path.join(PROJECT_ROOT, "data"), exist_ok=True)
        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))
        app = PreloaderWindow()
        threading.Thread(target=run_background_processes, args=(app,), daemon=True).start()
        app.mainloop()
    finally:
        if os.path.exists(PID_FILE):
            try: os.remove(PID_FILE)
            except OSError: pass