#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\pre_launcher.py
# (VERSI FINAL) Peluncuran senyap (silent) dengan animasi loading
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

        # (DITAMBAHKAN) Atribut untuk kontrol animasi
        self._animation_job = None
        self._animation_running = False

    def update_status(self, text):
        self.status_label.config(text=text)
        self.update_idletasks()

    # (DITAMBAHKAN) Fungsi untuk memulai animasi loading
    def start_loading_animation(self, base_text="Loading"):
        if self._animation_running:
            return
        self._animation_running = True
        self._animation_base_text = base_text
        self._animation_dots = 0
        self._update_animation_frame()

    # (DITAMBAHKAN) Fungsi untuk menghentikan animasi loading
    def stop_loading_animation(self):
        self._animation_running = False
        if self._animation_job:
            self.after_cancel(self._animation_job)
            self._animation_job = None

    # (DITAMBAHKAN) Fungsi internal yang akan dipanggil berulang untuk update frame animasi
    def _update_animation_frame(self):
        if not self._animation_running:
            return
        self._animation_dots = (self._animation_dots + 1) % 4
        dots = "." * self._animation_dots
        self.status_label.config(text=f"{self._animation_base_text}{dots}")
        self._animation_job = self.after(500, self._update_animation_frame)


def run_background_processes(window_instance):
    try:
        is_first_run = not os.path.exists(FIRST_RUN_LOCK_FILE)

        if is_first_run:
            window_instance.start_loading_animation("Performing first-time setup")
            bootstrap_script_path = os.path.join(PROJECT_ROOT, "scripts", "bootstrap.py")
            python_exe = os.path.join(PROJECT_ROOT, "python", "python.exe")

            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = subprocess.CREATE_NO_WINDOW

            result = subprocess.run([python_exe, bootstrap_script_path], cwd=PROJECT_ROOT, capture_output=True, text=True, creationflags=creation_flags)

            if result.returncode != 0:
                 raise Exception(f"Bootstrap script failed:\n{result.stderr}")
            window_instance.stop_loading_animation()

        window_instance.start_loading_animation("Loading FLOWORK")

        if os.path.exists(MAIN_APP_READY_SIGNAL):
            os.remove(MAIN_APP_READY_SIGNAL)

        launcher_script_path = os.path.join(PROJECT_ROOT, "launcher.py")

        # (DIUBAH) Kembalikan ke pythonw.exe untuk mode silent/profesional
        pythonw_exe = os.path.join(PROJECT_ROOT, "python", "pythonw.exe")

        # (DIUBAH) Kembalikan creation_flags untuk memastikan tidak ada jendela konsol muncul
        creation_flags = 0
        if sys.platform == "win32":
            creation_flags = subprocess.CREATE_NO_WINDOW

        subprocess.Popen([pythonw_exe, launcher_script_path], cwd=PROJECT_ROOT, creationflags=creation_flags)

        timeout = 90
        start_time = time.time()
        signal_received = False
        while time.time() - start_time < timeout:
            if os.path.exists(MAIN_APP_READY_SIGNAL):
                signal_received = True
                break
            time.sleep(0.5)

        window_instance.stop_loading_animation()

        if not signal_received:
            raise TimeoutError(f"Main application did not start within {timeout} seconds.")

        if os.path.exists(MAIN_APP_READY_SIGNAL):
            os.remove(MAIN_APP_READY_SIGNAL)

        window_instance.update_status("Application is ready!")
        time.sleep(1)
        if window_instance.winfo_exists():
            window_instance.destroy()

    except Exception as e:
        window_instance.stop_loading_animation()
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