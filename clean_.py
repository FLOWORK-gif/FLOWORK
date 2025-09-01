#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\clean.py
# (MODIFIED: Aggressive build artifact cleaner for redevelopment)
#######################################################################

import os
import shutil

def clean_project_artifacts():
    """
    Function to find and AGGRESSIVELY delete specific build artifacts from
    within module, widget, and plugin folders to force a complete rebuild.
    TARGETS: build_fingerprint.json, *.aola_flowork, vendor/, *.py.tmp.build, *.pyi
    """
    project_folder = os.getcwd()
    print("--- Flowork Build Artifact Cleaner (Aggressive Mode) ---")
    print(f"This script will clean build artifacts to force recompilation inside: {project_folder}")
    confirm = input("Are you sure you want to continue? (y/n): ")
    if confirm.lower() != 'y':
        print("Cleaning process cancelled by user.")
        return

    # Define component directories to scan
    component_base_dirs = ['modules', 'plugins', 'widgets', 'triggers', 'ai_providers', 'formatters']

    # Define artifact patterns to delete
    files_to_delete_exact = ['build_fingerprint.json']
    files_to_delete_endswith = ['.aola_flowork', '.pyi', '.pyd','.vendor_hash']
    folders_to_delete = ['vendor']
    folders_to_delete_endswith = ['.py.tmp.build', '.build',]

    deleted_files = 0
    deleted_folders = 0

    print("\nScanning component directories for artifacts to clean...")
    for base_dir in component_base_dirs:
        full_base_path = os.path.join(project_folder, base_dir)
        if not os.path.isdir(full_base_path):
            continue

        for component_name in os.listdir(full_base_path):
            component_path = os.path.join(full_base_path, component_name)
            if not os.path.isdir(component_path):
                continue

            # Walk through each component's directory to find and delete artifacts
            for root, dirs, files in os.walk(component_path, topdown=False):
                # Delete targeted folders
                for dir_name in list(dirs): # Use a copy to allow modification
                    path_to_delete = os.path.join(root, dir_name)
                    if dir_name in folders_to_delete or any(dir_name.endswith(pattern) for pattern in folders_to_delete_endswith):
                        try:
                            shutil.rmtree(path_to_delete)
                            deleted_folders += 1
                            print(f"[DELETED] Folder: {os.path.relpath(path_to_delete, project_folder)}")
                        except OSError as e:
                            print(f"[ERROR] Failed to delete folder {path_to_delete}: {e}")

                # Delete targeted files
                for file_name in files:
                    if file_name in files_to_delete_exact or any(file_name.endswith(pattern) for pattern in files_to_delete_endswith):
                        # Add a safeguard to not delete essential __init__.pyi if it exists
                        if file_name == '__init__.pyi':
                            continue
                        path_to_delete = os.path.join(root, file_name)
                        try:
                            os.remove(path_to_delete)
                            deleted_files += 1
                            print(f"[DELETED] File: {os.path.relpath(path_to_delete, project_folder)}")
                        except OSError as e:
                            print(f"[ERROR] Failed to delete file {path_to_delete}: {e}")

    # Also clean up general Python cache
    deleted_pycache_folders = 0
    print("\nCleaning up general Python cache (__pycache__)...")
    for root, dirs, files in os.walk(project_folder, topdown=False):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                deleted_pycache_folders += 1
                # print(f"[DELETED] Cache folder: {pycache_path}") # Optional: uncomment for more noise
            except OSError as e:
                print(f"[ERROR] Failed to delete folder {pycache_path}: {e}")

    print("\n--- CLEANUP PROCESS FINISHED ---")
    print(f"Total artifact folders deleted: {deleted_folders}")
    print(f"Total artifact files deleted: {deleted_files}")
    print(f"Total __pycache__ folders deleted: {deleted_pycache_folders}")
    print("Your components are now clean and ready for a fresh build!")

if __name__ == "__main__":
    clean_project_artifacts()

