#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\clean.py
# JUMLAH BARIS : 77
#######################################################################

import os
import shutil
class ProjectCleaner:
    """
    Handles the logic for cleaning up general project cache files and folders.
    """
    def __init__(self, project_folder, report_callback=print):
        self.project_folder = project_folder
        self.report = report_callback
        self.top_level_folders_deleted = 0
        self.cache_folders_deleted = 0
        self.files_deleted = 0
    def run_cleanup(self):
        """Executes the entire cleanup process."""
        self._delete_top_level_folders()
        self._walk_and_clean()
        self._report_summary()
    def _delete_top_level_folders(self):
        folders_to_delete = ['build', 'dist']
        for folder_name in folders_to_delete:
            folder_path = os.path.join(self.project_folder, folder_name)
            if os.path.isdir(folder_path):
                try:
                    shutil.rmtree(folder_path)
                    self.top_level_folders_deleted += 1
                    self.report(f"[DELETED] Top-level folder: {folder_path}", "SUCCESS") # English Log
                except OSError as e:
                    self.report(f"[ERROR] Failed to delete folder {folder_path}: {e}", "ERROR") # English Log
    def _walk_and_clean(self):
        for root, dirs, files in os.walk(self.project_folder, topdown=False):
            dirs[:] = [d for d in dirs if d not in ['build', 'dist']]
            if '__pycache__' in dirs:
                pycache_folder_path = os.path.join(root, '__pycache__')
                try:
                    shutil.rmtree(pycache_folder_path)
                    self.cache_folders_deleted += 1
                    self.report(f"[DELETED] Cache folder: {pycache_folder_path}", "SUCCESS") # English Log
                except OSError as e:
                    self.report(f"[ERROR] Failed to delete folder {pycache_folder_path}: {e}", "ERROR") # English Log
            for file_name in files:
                if file_name.endswith(('.pyc', '.log')):
                    file_path = os.path.join(root, file_name)
                    try:
                        os.remove(file_path)
                        self.files_deleted += 1
                        self.report(f"[DELETED] File: {file_path}", "SUCCESS") # English Log
                    except OSError as e:
                        self.report(f"[ERROR] Failed to delete file {file_path}: {e}", "ERROR") # English Log
    def _report_summary(self):
        self.report("\n--- CLEANUP PROCESS FINISHED ---", "INFO") # English Hardcode
        self.report(f"Total build/dist folders deleted: {self.top_level_folders_deleted}", "INFO") # English Hardcode
        self.report(f"Total __pycache__ folders deleted: {self.cache_folders_deleted}", "INFO") # English Hardcode
        self.report(f"Total .pyc and .log files deleted: {self.files_deleted}", "INFO") # English Hardcode
        self.report("Your project is now cleaner and ready for a new build!", "SUCCESS") # English Hardcode
def main():
    """
    Main execution block for when this script is run directly from the console.
    """
    project_folder = os.getcwd()
    print(f"This will clean up cache, logs, and build folders inside: {project_folder}") # English Hardcode
    confirmation = input("Are you sure you want to continue? (y/n): ") # English Hardcode
    if confirmation.lower() != 'y':
        print("Cleanup cancelled by user.") # English Hardcode
        return
    def console_reporter(message, level="INFO"):
        print(message)
    cleaner = ProjectCleaner(project_folder, console_reporter)
    cleaner.run_cleanup()
if __name__ == "__main__":
    main()
