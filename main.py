#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\main.py
# JUMLAH BARIS : 161 (PLUS PERBAIKAN)
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
    from _frozen_importlib_external import MetaPathFinder
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
    """
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue
    def write(self, s):
        if s.strip():
            self.log_queue.put(s)
        sys.__stdout__.write(s)
    def flush(self):
        sys.__stdout__.flush()
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"flowork_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
def run_gui_mode(kernel_instance):
    """This function contains all the logic for running the application with a graphical interface."""
    from flowork_kernel.ui_shell.main_window import MainWindow
    kernel_instance.write_to_log("Starting application in GUI mode...", "INFO")
    root = MainWindow(kernel_instance)
    kernel_instance.set_root(root)
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
    # --- [FIX] START: Initialize a hidden root window for early popups ---
    # This ensures that any messagebox call during startup has a valid parent.
    try:
        import ttkbootstrap as ttk
        hidden_root = ttk.Window()
        hidden_root.withdraw()
    except Exception:
        # Fallback if ttkbootstrap fails for some reason
        import tkinter
        hidden_root = tkinter.Tk()
        hidden_root.withdraw()
    # --- [FIX] END ---

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
    
    # --- [FIX] Make sure to destroy the hidden root if we are not entering GUI mode ---
    if args.run_preset or args.start_server:
        hidden_root.destroy()

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
        # If we enter GUI mode, we don't need the hidden_root anymore because MainWindow will take over.
        # It's good practice to destroy it before starting the main loop of the new window,
        # but since MainWindow creates a new Toplevel, it's generally safe.
        # For cleanliness, we can destroy it.
        hidden_root.destroy()
        run_gui_mode(kernel)