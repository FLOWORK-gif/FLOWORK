#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\pre_launcher.py
#######################################################################

import tkinter as tk
from tkinter import ttk
import threading
import subprocess
import os
import sys
import time
import traceback # (DITAMBAHKAN) Import traceback untuk logging error yang lebih baik

# --- Constants ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PID_FILE = os.path.join(PROJECT_ROOT, "pre_launcher.pid")
FIRST_RUN_LOCK_FILE = os.path.join(PROJECT_ROOT, "data", ".first_run_complete")
GIF_PATH = os.path.join(PROJECT_ROOT, "teetah.gif")

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
        style.configure("Preload.TLabel", background="#2c3e50", foreground="#ecf0f1", font=("Helvetica", 9)) # (DIUBAH) Ukuran font dikecilkan agar muat untuk pesan error panjang

        self.logo_label = ttk.Label(self, style="Preload.TLabel")
        self.logo_label.pack(pady=(20, 10))

        try:
            self.logo_photo = tk.PhotoImage(file=GIF_PATH)
            self.logo_label.config(image=self.logo_photo)
        except tk.TclError:
            self.logo_label.config(text="Teetah")
            print(f"Warning: Could not load {GIF_PATH}.")
        except Exception as e:
            self.logo_label.config(text="Teetah")
            print(f"An error occurred while loading teetah.gif: {e}")

        self.status_label = ttk.Label(self, text="Starting Flowork...", style="Preload.TLabel", wraplength=280, justify="center") # (DITAMBAHKAN) wraplength agar teks error tidak kepotong
        self.status_label.pack(pady=(5, 20), fill="x", padx=10)

    def update_status(self, text):
        self.status_label.config(text=text)
        self.update_idletasks() # (DITAMBAHKAN) Paksa window untuk update teksnya segera

def run_background_processes(window_instance):
    try:
        is_first_run = not os.path.exists(FIRST_RUN_LOCK_FILE)

        if is_first_run:
            window_instance.update_status("Performing first-time setup...\nThis may take a few minutes.")

            bootstrap_script_path = os.path.join(PROJECT_ROOT, "scripts", "bootstrap.py")
            python_exe = os.path.join(PROJECT_ROOT, "python", "python.exe")

            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = subprocess.CREATE_NO_WINDOW

            result = subprocess.run([python_exe, bootstrap_script_path], cwd=PROJECT_ROOT, capture_output=True, text=True, creationflags=creation_flags, encoding='utf-8')

            # (DIUBAH TOTAL) Logika penanganan error dibuat lebih informatif
            if result.returncode != 0:
                error_message = f"First-time setup failed (pip install error).\n\nError details:\n{result.stderr}"
                # Tulis log yang lebih detail
                with open(os.path.join(PROJECT_ROOT, "pre_launcher_error.log"), "w", encoding='utf-8') as f:
                    f.write(error_message)
                # Tampilkan error di GUI dan berhenti
                window_instance.update_status(error_message)
                time.sleep(15) # Beri waktu untuk membaca error
                window_instance.destroy()
                return # Hentikan eksekusi

        # Jika setup berhasil, buat lock file agar tidak diulang lagi
        os.makedirs(os.path.dirname(FIRST_RUN_LOCK_FILE), exist_ok=True)
        with open(FIRST_RUN_LOCK_FILE, "w") as f:
            f.write("completed")

        window_instance.update_status("Loading FLOWORK...")

        launcher_script_path = os.path.join(PROJECT_ROOT, "launcher.py")
        pythonw_exe = os.path.join(PROJECT_ROOT, "python", "pythonw.exe")

        creation_flags = 0
        if sys.platform == "win32":
            creation_flags = subprocess.CREATE_NO_WINDOW

        subprocess.Popen([pythonw_exe, launcher_script_path], cwd=PROJECT_ROOT, creationflags=creation_flags)

        time.sleep(5) # (DIUBAH) Waktu tunggu dikurangi
        if window_instance.winfo_exists():
            window_instance.destroy()

    except Exception as e:
        error_full_traceback = traceback.format_exc()
        final_error_message = f"A fatal error occurred:\n{e}"
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
        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))
        app = PreloaderWindow()
        threading.Thread(target=run_background_processes, args=(app,), daemon=True).start()
        app.mainloop()
    finally:
        if os.path.exists(PID_FILE):
            try: os.remove(PID_FILE)
            except OSError: pass