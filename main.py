#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\main.py
# (DIUBAH) Dependency checker now writes to a log file for the preloader.
#######################################################################

import sys
import os
import subprocess
import importlib.util

# --- NEW: Define project root early for the logger path ---
PROJECT_ROOT_FOR_LOGGER = os.path.dirname(os.path.abspath(__file__))
LOG_FILE_PATH = os.path.join(PROJECT_ROOT_FOR_LOGGER, "data", "dependency_check.log")

def check_and_install_dependencies():
    """
    Checks for required libraries, installs them if missing, and logs the
    process to a file that the preloader can read.
    """
    required_libs = {
        "pystray": "pystray",
        "pyaudio": "PyAudio"
    }

    # Ensure the 'data' directory exists and clear the old log file
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
    with open(LOG_FILE_PATH, "w", encoding='utf-8') as f:
        f.write("--- Running Dependency Check ---\n")

    def log_message(message):
        """Helper function to print to console AND write to the log file."""
        print(message) # Still useful for direct debugging
        with open(LOG_FILE_PATH, "a", encoding='utf-8') as f:
            f.write(message + "\n")

    all_good = True

    for lib_import_name, lib_pip_name in required_libs.items():
        spec = importlib.util.find_spec(lib_import_name)
        if spec is None:
            all_good = False
            log_message(f"[WARN] Required library '{lib_import_name}' not found. Installing...")
            try:
                command = [sys.executable, "-m", "pip", "install", lib_pip_name, "--quiet", "--disable-pip-version-check"]
                # Redirect stdout/stderr to DEVNULL to keep the process clean, log our own messages.
                subprocess.check_call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                log_message(f"[SUCCESS] Library '{lib_pip_name}' installed successfully.")
            except subprocess.CalledProcessError:
                log_message(f"[FATAL] Failed to install '{lib_pip_name}'. Please check internet connection.")
                sys.exit(1)
        else:
            log_message(f"[INFO] Library '{lib_import_name}' is already installed.")

    if all_good:
        log_message("[SUCCESS] All required dependencies are present.")

    log_message("--- Dependency Check Finished ---")


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
# importlib.util is already imported at the top
from importlib.machinery import SourcelessFileLoader
# subprocess is already imported at the top
import importlib.metadata
from tkinter import messagebox
import webbrowser
if project_root_for_path not in sys.path:
    sys.path.insert(0, project_root_for_path)
try:
    from importlib.abc import MetaPathFinder
except ImportError:
    MetaPathFinder = object

def signal_preloader_app_is_ready():
    """Creates a signal file to notify the preloader that the main app is ready."""
    try:
        project_root = project_root_for_path
        signal_file_path = os.path.join(project_root, "data", ".main_app_ready")
        os.makedirs(os.path.dirname(signal_file_path), exist_ok=True)
        with open(signal_file_path, "w") as f:
            pass
        print("[INFO] Signal sent to preloader: Application is ready.")
    except Exception as e:
        print(f"[ERROR] Could not create preloader signal file: {e}")

class TeetahFinder(MetaPathFinder):
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
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def write(self, s):
        if s and s.strip():
            self.log_queue.put(s)
        if sys.__stdout__ is not None:
            try:
                sys.__stdout__.write(s)
            except Exception:
                pass

    def flush(self):
        if sys.__stdout__ is not None:
            try:
                sys.__stdout__.flush()
            except Exception:
                pass

log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"flowork_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

def run_gui_mode(kernel_instance):
    from flowork_kernel.ui_shell.main_window import MainWindow
    kernel_instance.write_to_log("Starting application in GUI mode...", "INFO")
    root = MainWindow(kernel_instance)
    kernel_instance.set_root(root)
    root.after(100, signal_preloader_app_is_ready)
    root.mainloop()

def run_headless_mode(kernel_instance, preset_to_run):
    kernel_instance.write_to_log(f"Starting application in HEADLESS mode for preset: '{preset_to_run}'", "INFO")
    api_service = kernel_instance.get_service("api_server_service")
    if api_service:
        api_service.trigger_workflow_by_api(preset_to_run)
    else:
        kernel_instance.write_to_log("API service not found for headless execution.", "ERROR")
    kernel_instance.write_to_log("Headless execution finished. Application will be closed.", "INFO")
    kernel_instance.stop_all_services()

if __name__ == "__main__":
    check_and_install_dependencies()

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