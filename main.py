#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\main.py
# (Full code for the modified file)
#######################################################################

import sys
import os
project_root_for_path = os.path.dirname(os.path.abspath(__file__))
libs_path = os.path.join(project_root_for_path, 'libs')
if project_root_for_path not in sys.path:
    sys.path.insert(0, project_root_for_path)
if libs_path not in sys.path:
    sys.path.insert(0, libs_path)
from flowork_kernel.core.permission_hook import PermissionHook
from flowork_kernel.exceptions import MandatoryUpdateRequiredError, PermissionDeniedError
sys.meta_path.insert(0, PermissionHook())
import logging
import datetime
import argparse
import queue
import time
from io import StringIO
import importlib.util
from importlib.machinery import SourcelessFileLoader
import subprocess
import importlib.metadata
from tkinter import messagebox
import webbrowser
if project_root_for_path not in sys.path:
    sys.path.insert(0, project_root_for_path)
try:
    from importlib.abc import MetaPathFinder
except ImportError:
    # from _frozen_importlib_external import MetaPathFinder
    # (COMMENT) Using a simple object as a fallback for compatibility
    MetaPathFinder = object

# (DITAMBAHKAN) Fungsi baru untuk memberi sinyal ke pre_launcher.py
def signal_preloader_app_is_ready():
    """Creates a signal file to notify the preloader that the main app is ready."""
    try:
        # Note: Uses the global project_root_for_path defined at the top of the script
        project_root = project_root_for_path
        signal_file_path = os.path.join(project_root, "data", ".main_app_ready")

        # Ensure the 'data' directory exists
        os.makedirs(os.path.dirname(signal_file_path), exist_ok=True)

        # Create the empty signal file
        with open(signal_file_path, "w") as f:
            pass

        # Use print because the kernel logger might not be fully configured yet
        # or might not output to a visible console.
        print("[INFO] Signal sent to preloader: Application is ready.")
    except Exception as e:
        print(f"[ERROR] Could not create preloader signal file: {e}")

class TeetahFinder(MetaPathFinder):
    """
    Custom finder that will be inserted into Python's import system.
    Its job is to find our .teetah files.
    """
    def __init__(self, root_path):
        self.root_path = root_path
        self._failed_imports = set()
    def find_spec(self, fullname, path, target=None):
        if not fullname.startswith('flowork_kernel'):
            return None
        if fullname in self._failed_imports:
            return None
        module_path_part = fullname.replace('.', os.sep)
        potential_path = os.path.join(self.root_path, f"{module_path_part}.teetah")
        if os.path.exists(potential_path):
            loader = SourcelessFileLoader(fullname, potential_path)
            return importlib.util.spec_from_loader(fullname, loader)
        else:
            self._failed_imports.add(fullname)
            return None

class ConsoleOutputInterceptor(StringIO):
    """
    A file-like object that will capture everything written to it
    and put it into a queue.
    (MODIFIED) Now robustly handles environments with no standard output (like pythonw.exe).
    """
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def write(self, s):
        # (MODIFIED) This is the core fix.
        # It ALWAYS sends the output to the UI queue.
        if s and s.strip():
            self.log_queue.put(s)

        # It ONLY attempts to write to the console if a console (sys.__stdout__) actually exists.
        # This makes it work in both normal (pythonw.exe) and debug (python.exe) modes.
        if sys.__stdout__ is not None:
            try:
                sys.__stdout__.write(s)
            except Exception:
                # Failsafe in case the stream is closed or invalid
                pass

    def flush(self):
        # (MODIFIED) Also check if stdout exists before flushing.
        if sys.__stdout__ is not None:
            try:
                sys.__stdout__.flush()
            except Exception:
                pass


log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"flowork_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

def run_gui_mode(kernel_instance):
    """This function contains all the logic for running the application with a graphical interface."""
    from flowork_kernel.ui_shell.main_window import MainWindow
    kernel_instance.write_to_log("Starting application in GUI mode...", "INFO")
    root = MainWindow(kernel_instance)
    kernel_instance.set_root(root)

    # (DITAMBAHKAN) Kirim sinyal bahwa aplikasi sudah siap SEBELUM masuk ke mainloop.
    # Ini akan memberitahu pre_launcher.py untuk menutup dirinya.
    signal_preloader_app_is_ready()

    root.mainloop()

def run_headless_mode(kernel_instance, preset_to_run):
    """Function to run a workflow from the command line without a GUI."""
    kernel_instance.write_to_log(f"Starting application in HEADLESS mode for preset: '{preset_to_run}'", "INFO")
    api_service = kernel_instance.get_service("api_server_service")
    if api_service:
        api_service.trigger_workflow_by_api(preset_to_run)
    else:
        kernel_instance.write_to_log("API service not found for headless execution.", "ERROR")
    kernel_instance.write_to_log("Headless execution finished. Application will be closed.", "INFO")
    kernel_instance.stop_all_services()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flowork - Universal Workflow Orchestrator.")
    parser.add_argument(
        '--run-preset',
        type=str,
        help='Runs a specific preset in headless mode (no GUI) and then exits.'
    )
    parser.add_argument(
        '--start-server',
        action='store_true',
        help='Forces the API server to start, overriding the setting in settings.json. The app will run in the background.'
    )
    args = parser.parse_args()
    project_root_path = os.path.dirname(os.path.abspath(__file__))
    sys.meta_path.insert(1, TeetahFinder(project_root_path))

    try:
        from flowork_kernel.kernel import Kernel
        kernel = Kernel(project_root_path)

        # This interceptor will now work correctly in both GUI and Debug modes.
        console_interceptor = ConsoleOutputInterceptor(kernel.cmd_log_queue)
        sys.stdout = console_interceptor
        sys.stderr = console_interceptor

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
            ]
        )
        logging.info("Starting Flowork application...")

        if args.start_server:
            loc = kernel.get_service("localization_manager")
            if loc:
                loc.save_setting("webhook_enabled", True)
                kernel.write_to_log("API server has been force-enabled via command line argument.", "WARN")

        kernel.start_all_services()

    except MandatoryUpdateRequiredError as e:
        info = e.update_info
        loc = None
        if 'kernel' in locals() and hasattr(kernel, 'get_service'):
            loc = kernel.get_service("localization_manager")

        def get_text(key, fallback, **kwargs):
            if loc:
                return loc.get(key, fallback=fallback, **kwargs)
            return fallback.format(**kwargs)

        update_message = (
            get_text('update_popup_header', "Update to Version {version} Required", version=info.get('version', 'N/A')) + "\n\n" +
            get_text('update_popup_changelog_label', "Changes in this version:") + "\n" +
            "\n".join(f"- {item}" for item in info.get('changelog', ["No details available."])) + "\n\n" +
            get_text('update_popup_exit_message', "The application will now close. Please download the new version.")
        )
        title = get_text('update_popup_title', "Mandatory Update Available")
        prompt = get_text('update_popup_open_browser_prompt', "Open the download page now?")
        if messagebox.askyesno(title, update_message + f"\n\n{prompt}"):
            webbrowser.open(info.get('download_url', 'https://www.teetah.art'))
        sys.exit(0)

    except (Exception, PermissionDeniedError) as e:
        messagebox.showerror("Fatal Startup Error", f"An unrecoverable error occurred during startup:\n\n{e}")
        sys.exit(1)

    if args.run_preset:
        run_headless_mode(kernel, args.run_preset)
    elif args.start_server:
        kernel.write_to_log("Flowork is now running in server-only mode. Press Ctrl+C to stop.", "SUCCESS")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            kernel.write_to_log("Server-only mode stopped by user.", "INFO")
            kernel.stop_all_services()
    else:
        run_gui_mode(kernel)