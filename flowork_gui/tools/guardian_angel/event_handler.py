# dev: awenk audico
# EMAIL: SAHIDINAOLA@GMAIL.COM
# WEBSITE: WWW.TEETAH.ART
# File NAME: tools/guardian_angel/event_handler.py

import os
import time
import logging
from watchdog.events import FileSystemEventHandler

class BackupEventHandler(FileSystemEventHandler):
    """
    A specialized event handler that detects file system changes
    and triggers the backup cycle via the archiver.
    Its single responsibility is to handle watchdog events.
    """
    def __init__(self, archiver):
        """
        Initializes the event handler.
        Args:
            archiver: An instance of the Archiver class to run backups.
        """
        self.archiver = archiver
        self.last_triggered = 0
        self.debounce_period = 5  # seconds

    def on_any_event(self, event):
        """
        This method is called by the watchdog observer when any file event occurs.
        Args:
            event: The event object representing the file system change.
        """
        # Note: Do not trigger a backup for changes to the backup file itself.
        if os.path.abspath(event.src_path) == os.path.abspath(self.archiver.backup_file_path):
            return

        # Note: Check if the path is in one of the fully excluded directories.
        path_str_for_dir_check = event.src_path.replace(os.sep, '/')
        if any(f"/{excluded_dir}/" in f"/{path_str_for_dir_check}/" or path_str_for_dir_check.endswith(f"/{excluded_dir}") for excluded_dir in self.archiver.excluded_dirs_entirely):
             return

        # Note: Exclude specific file names.
        if os.path.basename(event.src_path) in self.archiver.excluded_files:
            return

        # Note: Ignore events for directories.
        if event.is_directory:
            return

        # Note: Debounce to prevent rapid firing for a single save action.
        current_time = time.time()
        if current_time - self.last_triggered > self.debounce_period:
            logging.info(f"CHANGE DETECTED in: {event.src_path}. Rerunning backup cycle...")
            self.last_triggered = current_time
            # Note: The handler's only job is to delegate the action to the archiver.
            self.archiver.run_backup_cycle()