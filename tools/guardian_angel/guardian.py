# dev: awenk audico
# EMAIL: SAHIDINAOLA@GMAIL.COM
# WEBSITE: WWW.TEETAH.ART
# File NAME: tools/guardian_angel/guardian.py

import time
import logging
from watchdog.observers import Observer
from .event_handler import BackupEventHandler

class GuardianAngel:
    """
    The main orchestrator for the backup system.
    Its single responsibility is to set up and run the file system observer.
    """
    def __init__(self, project_root: str, archiver_instance):
        """
        Initializes the Guardian Angel.
        Args:
            project_root (str): The root directory of the project to watch.
            archiver_instance: An instance of the Archiver to perform backups.
        """
        self.project_root = project_root
        self.archiver = archiver_instance
        self.observer = Observer()

    def start(self):
        """
        Starts the Guardian Angel's watch.
        It runs the initial backup and then monitors for changes indefinitely.
        """
        # Note: Run one backup cycle on startup.
        self.archiver.run_backup_cycle()

        # Note: Create the specialized event handler.
        event_handler = BackupEventHandler(archiver=self.archiver)

        # Note: Schedule the observer to watch the project root recursively.
        self.observer.schedule(event_handler, self.project_root, recursive=True)
        self.observer.start()

        logging.info(f"Guardian Angel is active. Watching for changes in: {self.project_root}")
        logging.info("Press Ctrl+C to stop watching.")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
            logging.info("Guardian Angel stopped by user.")

        self.observer.join()