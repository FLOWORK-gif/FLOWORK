#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\launcher.py
# (Full code for the NEW file)
#######################################################################
import ttkbootstrap as ttk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import subprocess
import threading
import os
import sys
import time

# --- Konfigurasi ---
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
SETUP_SCRIPT_PATH = os.path.join(APP_ROOT, "scripts", "setup.py")
MAIN_APP_PATH = os.path.join(APP_ROOT, "main.py")
PYTHON_EXEC = os.path.join(APP_ROOT, "python", "pythonw.exe")
FLAG_FILE = os.path.join(APP_ROOT, "data", "setup_complete.flag")

class ElegantLauncher(ttk.Window):
    def __init__(self, is_first_run):
        super().__init__(themename="darkly")
        self.is_first_run = is_first_run
        
        if self.is_first_run:
            self.title("Flowork Setup")
            self.geometry("500x350")
        else:
            self.title("Flowork")
            self.geometry("300x150")

        self.resizable(False, False)
        # Pusatkan jendela
        self.eval('tk::PlaceWindow . center')

        if self.is_first_run:
            self._build_setup_ui()
            self.after(500, self._start_setup_thread)
        else:
            self._build_loading_ui()
            self.after(500, self._start_main_app_thread)
            
    def _build_setup_ui(self):
        ttk.Label(self, text="First Time Setup", font=("-size 14 -weight bold")).pack(pady=10)
        ttk.Label(self, text="Installing required libraries. Please wait...", bootstyle="secondary").pack(pady=5, padx=10)
        
        log_frame = ttk.LabelFrame(self, text="Log", padding=5)
        log_frame.pack(pady=10, padx=10, fill="both", expand=True)
        self.log_area = ScrolledText(log_frame, wrap="word", state="disabled", height=8, font=("Consolas", 8))
        self.log_area.pack(fill="both", expand=True)
        
        self.progress_bar = ttk.Progressbar(self, mode='indeterminate')
        self.progress_bar.pack(pady=10, padx=10, fill="x")
        self.progress_bar.start()

    def _build_loading_ui(self):
        ttk.Label(self, text="Flowork", font=("-size 16 -weight bold")).pack(pady=10)
        ttk.Label(self, text="Loading application...", bootstyle="secondary").pack(pady=5, padx=10)
        
        self.progress_bar = ttk.Progressbar(self, mode='indeterminate')
        self.progress_bar.pack(pady=10, padx=10, fill="x")
        self.progress_bar.start()

    def _add_to_log(self, message):
        self.log_area.config(state="normal")
        self.log_area.insert("end", message)
        self.log_area.see("end")
        self.log_area.config(state="disabled")

    def _start_setup_thread(self):
        threading.Thread(target=self._run_setup_script, daemon=True).start()

    def _run_setup_script(self):
        try:
            process = subprocess.Popen(
                [PYTHON_EXEC.replace("pythonw.exe", "python.exe"), SETUP_SCRIPT_PATH],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.after(0, self._add_to_log, output)
            
            # Buat file penanda bahwa setup selesai
            with open(FLAG_FILE, 'w') as f:
                f.write('done')
            
            self.after(0, self._on_setup_complete)
        except Exception as e:
            self.after(0, self._on_setup_error, str(e))

    def _on_setup_complete(self):
        self.progress_bar.stop()
        messagebox.showinfo("Setup Complete", "Flowork is ready. The application will now restart.", parent=self)
        self._restart_app()

    def _on_setup_error(self, error_message):
        self.progress_bar.stop()
        messagebox.showerror("Setup Failed", f"An error occurred:\n\n{error_message}", parent=self)
        self.destroy()

    def _start_main_app_thread(self):
        threading.Thread(target=self._launch_main_app, daemon=True).start()

    def _launch_main_app(self):
        # Beri jeda loading palsu agar terasa mulus
        time.sleep(3) 
        try:
            subprocess.Popen([PYTHON_EXEC, MAIN_APP_PATH], cwd=APP_ROOT)
        except Exception:
            # Jika gagal, mungkin karena proses sebelumnya belum mati
            # Cukup tutup jendela loading ini
            pass
        finally:
            self.after(1000, self.destroy) # Tunggu 1 detik sebelum menutup

    def _restart_app(self):
        # Jalankan kembali launcher via file .bat
        subprocess.Popen([os.path.join(APP_ROOT, "Flowork.bat")], cwd=APP_ROOT, shell=True)
        self.destroy()

if __name__ == "__main__":
    # Cek apakah setup sudah pernah dijalankan
    first_run = not os.path.exists(FLAG_FILE)
    app = ElegantLauncher(is_first_run=first_run)
    app.mainloop()