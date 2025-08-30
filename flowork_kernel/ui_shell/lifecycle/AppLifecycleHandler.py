#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\ui_shell\lifecycle\AppLifecycleHandler.py
# (Full code for the modified file)
#######################################################################

from tkinter import messagebox
import logging
import threading
from PIL import Image
import pystray
import sys
import os
import shutil

class AppLifecycleHandler:
    """
    Handles application lifecycle events like closing, restarting, etc.
    This keeps the closing/saving logic separate from the main window.
    """
    def __init__(self, main_window, kernel):
        """
        Initializes the lifecycle handler.

        Args:
            main_window: A reference to the main Tkinter window.
            kernel: The application kernel.
        """
        self.main_window = main_window
        self.kernel = kernel
        self.loc = self.kernel.get_service("localization_manager")
        self.tray_icon = None
        self.tray_thread = None

        event_bus = self.kernel.get_service("event_bus")
        if event_bus:
            event_bus.subscribe("RESTART_APP", "lifecycle_handler_restart", self._on_restart_request)
            event_bus.subscribe("RESTART_APP_AFTER_UPDATE", "lifecycle_handler_update_restart", self._on_restart_request)
            event_bus.subscribe("REQUEST_CLEANUP_AND_EXIT", "lifecycle_handler_deactivation", self._on_cleanup_and_exit_request)
            self.kernel.write_to_log("LifecycleHandler is now listening for RESTART and EXIT events.", "INFO")

    def on_closing_app(self, is_restarting=False):
        """
        (MODIFIED) Handles the application closing sequence.
        It now intelligently decides whether to minimize to tray or perform a full exit.

        Args:
            is_restarting (bool): If True, the app will perform a full, clean shutdown
                                  without confirmation, bypassing the system tray.
        """
        if is_restarting:
            # A forced restart (e.g., after an update) needs a full, clean exit.
            # We call the existing _exit_app method but tell it not to ask for confirmation.
            self.kernel.write_to_log("Forced restart detected. Performing full application shutdown.", "WARN")
            self._exit_app(ask_confirmation=False)
        else:
            # Standard close behavior (e.g., user clicks the 'X' button)
            # is to minimize to the system tray.
            self.main_window.withdraw()
            self._create_or_show_tray_icon()

    def _on_restart_request(self, event_data=None):
        """Handles the application restart logic triggered by an event."""
        self.kernel.write_to_log("Restart request received via EventBus. Initiating shutdown...", "WARN")
        self.kernel.stop_all_services()
        self.main_window.destroy()
        try:
            os.execl(sys.executable, sys.executable, *sys.argv)
        except Exception as e:
            self.kernel.write_to_log(f"Failed to perform self-restart: {e}", "CRITICAL")
            sys.exit(1)

    def _on_cleanup_and_exit_request(self, event_data=None):
        """Handles the full cleanup and exit process after a license deactivation."""
        self.kernel.write_to_log("Cleanup and Exit request received. Starting process...", "WARN")
        self.main_window.after(100, self._perform_safe_cleanup_and_exit)

    def _perform_safe_cleanup_and_exit(self):
        """Contains the actual logic for clearing cache and then exiting."""
        self.kernel.write_to_log("Performing cache cleanup...", "INFO")
        deleted_folders, deleted_files = 0, 0
        current_log_file = None

        # Safely get the current log file path
        if hasattr(self.kernel, 'file_logger') and self.kernel.file_logger.handlers:
            current_log_file = self.kernel.file_logger.handlers[0].baseFilename

        for root, dirs, files in os.walk(self.kernel.project_root_path, topdown=False):
            if '__pycache__' in dirs:
                pycache_path = os.path.join(root, '__pycache__')
                try:
                    shutil.rmtree(pycache_path)
                    deleted_folders += 1
                except (OSError, PermissionError):
                    self.kernel.write_to_log(f"Could not delete cache folder (in use): {os.path.basename(pycache_path)}", "WARN")

            for name in files:
                if name.endswith(".pyc") or name.endswith(".log"):
                    file_path = os.path.join(root, name)
                    if file_path == current_log_file:
                        continue # Don't delete the log file we are currently writing to
                    try:
                        os.remove(file_path)
                        deleted_files += 1
                    except (OSError, PermissionError):
                        pass # Ignore if file is locked

        self.kernel.write_to_log(f"Cache cleanup finished. Deleted {deleted_folders} folders and {deleted_files} files.", "SUCCESS")
        self._exit_app(ask_confirmation=False) # Exit without asking again

    def _create_or_show_tray_icon(self):
        """Creates and runs the system tray icon in a separate thread if it's not already running."""
        if self.tray_thread and self.tray_thread.is_alive():
            return

        try:
            # Use an absolute path to be more robust
            icon_path = os.path.join(self.kernel.project_root_path, "flowork-icon.ico")
            image = Image.open(icon_path)
        except FileNotFoundError:
            self.kernel.write_to_log("System tray icon.ico not found, using placeholder.", "ERROR")
            image = Image.new('RGB', (64, 64), color='blue')

        menu = (
            pystray.MenuItem(
                self.loc.get('tray_menu_show', fallback='Show Flowork'),
                self._show_window,
                default=True
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                self.loc.get('tray_menu_exit', fallback='Exit Flowork'),
                lambda: self._exit_app(ask_confirmation=True)
            )
        )

        self.tray_icon = pystray.Icon("flowork", image, "Flowork", menu)
        self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        self.tray_thread.start()
        self.kernel.write_to_log("Application minimized to system tray.", "INFO")

    def _show_window(self):
        """Shows the main window when the tray icon option is clicked."""
        if self.tray_icon:
            self.tray_icon.stop()
        self.main_window.after(0, self.main_window.deiconify)

    def _perform_safe_exit(self, ask_confirmation=True):
        """This method contains the actual shutdown logic and is designed to be called on the main UI thread."""
        should_proceed = True

        if ask_confirmation:
            title = self.loc.get('confirm_exit_title', fallback="Exit Application")
            message = self.loc.get('confirm_exit_message', fallback="Are you sure you want to exit?")
            should_proceed = messagebox.askyesno(title, message, parent=self.main_window)

        if not should_proceed:
            self.kernel.write_to_log("Exit process cancelled by user.", "INFO")
            return

        # Save session state before exiting
        try:
            if hasattr(self.main_window, 'save_layout_and_session'):
                self.main_window.save_layout_and_session()
        except Exception as e:
            self.kernel.write_to_log(f"Error saving session on exit: {e}", "WARN")

        self.kernel.write_to_log("Application exit initiated.", "INFO")
        self.kernel.stop_all_services()
        self.main_window.destroy()
        sys.exit(0) # Ensure the process terminates

    def _exit_app(self, ask_confirmation=True):
        """The real exit logic for the application, ensuring the tray icon is handled."""
        if self.tray_icon:
            self.tray_icon.stop()
        # Schedule the safe exit on the main UI thread
        self.main_window.after(0, self._perform_safe_exit, ask_confirmation)