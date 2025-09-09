#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\cleaner_tool.py
# JUMLAH BARIS : 90
#######################################################################

import os
import shutil
class ArtifactCleaner:
    """
    Handles the logic for aggressively cleaning specific build artifacts
    from component folders to force a complete rebuild.
    """
    def __init__(self, project_folder, report_callback=print):
        self.project_folder = project_folder
        self.report = report_callback
        self.component_base_dirs = ['modules', 'plugins', 'widgets', 'triggers', 'ai_providers', 'formatters']
        self.files_to_delete_exact = ['.vendor_hash', 'build_fingerprint.json']
        self.files_to_delete_endswith = ['.pyi', '.pyd', '.original','.service', '.kernel', '.aola', '.ai', '.flow', '.teetah','.aola_flowork','.module.flowork','.plugin.flowork','.widget.flowork','.trigger.flowork','.scanner.flowork']
        self.folders_to_delete = ['vendor', 'vendor']
        self.folders_to_delete_endswith = ['.py.tmp.build', '.build']
        self.deleted_files = 0
        self.deleted_folders = 0
        self.deleted_pycache_folders = 0
    def run_cleanup(self):
        """Executes the entire aggressive cleanup process."""
        self.report("Scanning component directories for artifacts to clean...", "INFO") # English Log
        self._clean_component_artifacts()
        self.report("\nCleaning up general Python cache (__pycache__)...", "INFO") # English Log
        self._clean_pycache()
        self._report_summary()
    def _clean_component_artifacts(self):
        for base_dir in self.component_base_dirs:
            full_base_path = os.path.join(self.project_folder, base_dir)
            if not os.path.isdir(full_base_path):
                continue
            for component_name in os.listdir(full_base_path):
                component_path = os.path.join(full_base_path, component_name)
                if not os.path.isdir(component_path):
                    continue
                for root, dirs, files in os.walk(component_path, topdown=False):
                    for dir_name in list(dirs):
                        path_to_delete = os.path.join(root, dir_name)
                        if dir_name in self.folders_to_delete or any(dir_name.endswith(p) for p in self.folders_to_delete_endswith):
                            self._delete_folder(path_to_delete)
                    for file_name in files:
                        if file_name in self.files_to_delete_exact or any(file_name.endswith(p) for p in self.files_to_delete_endswith):
                            if file_name == '__init__.pyi': continue
                            self._delete_file(os.path.join(root, file_name))
    def _clean_pycache(self):
        for root, dirs, files in os.walk(self.project_folder, topdown=False):
            if '__pycache__' in dirs:
                self._delete_folder(os.path.join(root, '__pycache__'), is_pycache=True)
    def _delete_folder(self, path, is_pycache=False):
        try:
            shutil.rmtree(path)
            if is_pycache: self.deleted_pycache_folders += 1
            else: self.deleted_folders += 1
            self.report(f"[DELETED] Folder: {os.path.relpath(path, self.project_folder)}", "SUCCESS") # English Log
        except OSError as e:
            self.report(f"[ERROR] Failed to delete folder {path}: {e}", "ERROR") # English Log
    def _delete_file(self, path):
        try:
            os.remove(path)
            self.deleted_files += 1
            self.report(f"[DELETED] File: {os.path.relpath(path, self.project_folder)}", "SUCCESS") # English Log
        except OSError as e:
            self.report(f"[ERROR] Failed to delete file {path}: {e}", "ERROR") # English Log
    def _report_summary(self):
        self.report("\n--- CLEANUP PROCESS FINISHED ---", "INFO") # English Hardcode
        self.report(f"Total artifact folders deleted: {self.deleted_folders}", "INFO") # English Hardcode
        self.report(f"Total artifact files deleted: {self.deleted_files}", "INFO") # English Hardcode
        self.report(f"Total __pycache__ folders deleted: {self.deleted_pycache_folders}", "INFO") # English Hardcode
        self.report("Your components are now clean and ready for a fresh build!", "SUCCESS") # English Hardcode
def main():
    """Main execution block for when this script is run directly from the console."""
    project_folder = os.getcwd()
    print("--- Flowork Build Artifact Cleaner (Aggressive Mode) ---") # English Hardcode
    print(f"This script will clean build artifacts to force recompilation inside: {project_folder}") # English Hardcode
    confirm = input("Are you sure you want to continue? (y/n): ") # English Hardcode
    if confirm.lower() != 'y':
        print("Cleaning process cancelled by user.") # English Hardcode
        return
    def console_reporter(message, level="INFO"):
        print(message)
    cleaner = ArtifactCleaner(project_folder, console_reporter)
    cleaner.run_cleanup()
if __name__ == "__main__":
    main()
