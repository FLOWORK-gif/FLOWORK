#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\pre_launcher.py
# (FINAL) Shows live dependency check logs in the UI.
#######################################################################
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import subprocess
import os
import sys
import time
import traceback
import queue

# --- Constants ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PID_FILE = os.path.join(PROJECT_ROOT, "pre_launcher.pid")
GIF_PATH = os.path.join(PROJECT_ROOT, "teetah.gif")
MAIN_APP_READY_SIGNAL = os.path.join(PROJECT_ROOT, "data", ".main_app_ready")
# (ADDED) Path to the log file we will be monitoring
DEP_LOG_FILE = os.path.join(PROJECT_ROOT, "data", "dependency_check.log")

class PreloaderWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.attributes('-topmost', True)

        width, height = 300, 250 # (MODIFIED) Increased height for the log box
        screen_width, screen_height = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = (screen_width // 2) - (width // 2), (screen_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        self.config(bg="#2c3e50")

        self.logo_label = ttk.Label(self, background="#2c3e50")
        self.logo_label.pack(pady=(20, 10))

        try:
            self.logo_photo = tk.PhotoImage(file=GIF_PATH)
            self.logo_label.config(image=self.logo_photo)
        except tk.TclError:
            self.logo_label.config(text="Teetah", foreground="#ecf0f1", font=("Helvetica", 12, "bold"))

        self.status_label = ttk.Label(self, text="Starting Flowork...", background="#2c3e50", foreground="#ecf0f1", font=("Helvetica", 10))
        self.status_label.pack(pady=(5, 5), fill="x", padx=10)

        # (ADDED) ScrolledText widget for displaying logs
        self.log_widget = scrolledtext.ScrolledText(self, height=5, bg="#1a2530", fg="#bdc3c7", font=("Consolas", 8), relief="flat", borderwidth=0)
        self.log_widget.pack(pady=(0, 10), padx=10, fill="x")
        self.log_widget.insert(tk.END, "Initializing...")
        self.log_widget.config(state="disabled")

        # (ADDED) Queue for thread-safe UI updates
        self.log_queue = queue.Queue()
        self.process_log_queue()

    def update_status(self, text):
        self.status_label.config(text=text)

    def process_log_queue(self):
        """Processes messages from the log queue to update the UI safely."""
        try:
            while True:
                line = self.log_queue.get_nowait()
                self.log_widget.config(state="normal")
                # (MODIFIED) Check for a special signal to clear the box
                if line == "__CLEAR__":
                    self.log_widget.delete(1.0, tk.END)
                else:
                    self.log_widget.insert(tk.END, line)
                    self.log_widget.see(tk.END) # Auto-scroll
                self.log_widget.config(state="disabled")
        except queue.Empty:
            pass # No new messages
        self.after(200, self.process_log_queue) # Poll every 200ms

def tail_log_file(log_queue):
    """A function to 'tail -f' a log file and put new lines into a queue."""
    # Clear the queue and send a signal to clear the text box
    while not log_queue.empty():
        log_queue.get_nowait()
    log_queue.put("__CLEAR__")

    try:
        with open(DEP_LOG_FILE, 'r', encoding='utf-8') as f:
            f.seek(0, 2) # Go to the end of the file
            while not os.path.exists(MAIN_APP_READY_SIGNAL):
                line = f.readline()
                if not line:
                    time.sleep(0.1) # Wait for new content
                    continue
                log_queue.put(line)
    except FileNotFoundError:
        log_queue.put("Waiting for dependency check to start...\n")
        # Keep checking if the file gets created
        while not os.path.exists(DEP_LOG_FILE) and not os.path.exists(MAIN_APP_READY_SIGNAL):
            time.sleep(0.5)
        if os.path.exists(DEP_LOG_FILE):
            tail_log_file(log_queue) # Retry tailing the file
    except Exception as e:
        log_queue.put(f"Error reading log: {e}\n")

def run_background_processes(window_instance):
    try:
        # Clear the signal file if it exists from a previous run
        if os.path.exists(MAIN_APP_READY_SIGNAL):
            os.remove(MAIN_APP_READY_SIGNAL)

        # (ADDED) Start the log tailing in a separate thread
        log_tail_thread = threading.Thread(target=tail_log_file, args=(window_instance.log_queue,), daemon=True)
        log_tail_thread.start()

        window_instance.update_status("Loading FLOWORK...")

        launcher_script_path = os.path.join(PROJECT_ROOT, "launcher.py")
        pythonw_exe = os.path.join(PROJECT_ROOT, "python", "pythonw.exe")

        creation_flags = 0
        if sys.platform == "win32":
            creation_flags = subprocess.CREATE_NO_WINDOW

        subprocess.Popen([pythonw_exe, launcher_script_path], cwd=PROJECT_ROOT, creationflags=creation_flags)

        timeout = 90
        start_time = time.time()
        while time.time() - start_time < timeout:
            if os.path.exists(MAIN_APP_READY_SIGNAL):
                break
            time.sleep(0.5)
        else: # This else belongs to the while loop, runs if loop finishes without break
            raise TimeoutError(f"Main application did not start within {timeout} seconds.")

        window_instance.update_status("Application is ready!")
        time.sleep(1)
        if window_instance.winfo_exists():
            window_instance.destroy()

    except Exception as e:
        error_full_traceback = traceback.format_exc()
        window_instance.log_queue.put(f"\nA FATAL ERROR OCCURRED:\n{e}")
        with open(os.path.join(PROJECT_ROOT, "pre_launcher_error.log"), "w", encoding='utf-8') as f:
            f.write(str(e) + "\n\n" + error_full_traceback)
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