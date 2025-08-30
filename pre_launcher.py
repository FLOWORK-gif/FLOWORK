#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\pre_launcher.py
# (DIUBAH) Versi dengan deteksi sinyal otomatis dari aplikasi utama
#######################################################################

import tkinter as tk
from tkinter import ttk
import threading
import subprocess
import os
import sys
import time
import traceback # (DITAMBAHKAN) Import traceback untuk logging error

# --- Constants ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PID_FILE = os.path.join(PROJECT_ROOT, "pre_launcher.pid")
FIRST_RUN_LOCK_FILE = os.path.join(PROJECT_ROOT, "data", ".first_run_complete")
GIF_PATH = os.path.join(PROJECT_ROOT, "teetah.gif")
# (DITAMBAHKAN) Path untuk file sinyal dari aplikasi utama
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
            print(f"Warning: Could not load {GIF_PATH}. It might be missing or in an unsupported GIF format for Tkinter.")
        except Exception as e:
            self.logo_label.config(text="Teetah")
            print(f"An error occurred while loading teetah.gif: {e}")

        self.status_label = ttk.Label(self, text="Starting Flowork...", style="Preload.TLabel")
        self.status_label.pack(pady=(5, 20), fill="x", padx=10)

    def update_status(self, text):
        self.status_label.config(text=text)
        self.update_idletasks() # Force update

def run_background_processes(window_instance):
    """
    (DIUBAH) Logika startup sekarang menunggu sinyal, bukan sleep.
    """
    try:
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

        window_instance.update_status("Loading FLOWORK...\nWaiting for application to be ready...")

        # (DITAMBAHKAN) Hapus file sinyal lama jika ada untuk memastikan proses bersih
        if os.path.exists(MAIN_APP_READY_SIGNAL):
            os.remove(MAIN_APP_READY_SIGNAL)

        launcher_script_path = os.path.join(PROJECT_ROOT, "launcher.py")
        pythonw_exe = os.path.join(PROJECT_ROOT, "python", "pythonw.exe")

        creation_flags = 0
        if sys.platform == "win32":
            creation_flags = subprocess.CREATE_NO_WINDOW

        subprocess.Popen([pythonw_exe, launcher_script_path], cwd=PROJECT_ROOT, creationflags=creation_flags)

        # (DIUBAH) Ganti time.sleep dengan loop pendeteksian sinyal
        timeout = 90  # Timeout dalam detik (misal: 1.5 menit)
        start_time = time.time()
        signal_received = False
        while time.time() - start_time < timeout:
            if os.path.exists(MAIN_APP_READY_SIGNAL):
                window_instance.update_status("Application is ready! Finishing up...")
                signal_received = True
                break
            time.sleep(0.5) # Cek setiap setengah detik

        if not signal_received:
            raise TimeoutError(f"Main application did not start within {timeout} seconds.")
        
        # (DITAMBAHKAN) Cleanup file sinyal setelah diterima
        if os.path.exists(MAIN_APP_READY_SIGNAL):
            os.remove(MAIN_APP_READY_SIGNAL)
        
        # time.sleep(20) # (DIKOMENTARI) Logika lama yang tidak andal
        time.sleep(1) # Kasih jeda sesaat sebelum close
        if window_instance.winfo_exists():
            window_instance.destroy()

    except Exception as e:
        # (DIUBAH) Penanganan error yang lebih baik
        error_full_traceback = traceback.format_exc()
        final_error_message = f"A fatal error occurred:\n{e}"
        window_instance.update_status(final_error_message)
        # Tulis log yang lebih detail untuk debugging
        with open(os.path.join(PROJECT_ROOT, "pre_launcher_error.log"), "w", encoding='utf-8') as f:
            f.write(str(e))
            f.write("\n\n")
            f.write(error_full_traceback)
        time.sleep(15) # Beri waktu pengguna untuk membaca error
        if window_instance.winfo_exists():
            window_instance.destroy()

if __name__ == "__main__":
    try:
        # Pastikan folder data ada
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