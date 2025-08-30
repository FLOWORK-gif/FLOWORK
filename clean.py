#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\clean.py
# JUMLAH BARIS : 60
#######################################################################

import os
import shutil
def clean_project_artifacts():
    """
    Function to find and delete __pycache__, build, dist folders
    and files with .pyc and .log extensions within the script's
    execution directory and all its subfolders.
    """
    project_folder = os.getcwd()
    print(f"This script will clean cache, logs, and build folders inside: {project_folder}")
    confirm = input("Are you sure you want to continue? (y/n): ")
    if confirm.lower() != 'y':
        print("Cleaning process cancelled by user.")
        return
    folders_to_delete_top_level = ['build', 'dist']
    deleted_top_level_folders = 0
    for folder_name in folders_to_delete_top_level:
        folder_path = os.path.join(project_folder, folder_name)
        if os.path.isdir(folder_path):
            try:
                shutil.rmtree(folder_path)
                deleted_top_level_folders += 1
                print(f"[DELETED] Top-level folder: {folder_path}")
            except OSError as e:
                print(f"[ERROR] Failed to delete folder {folder_path}: {e}")
    deleted_folders = 0
    deleted_files = 0
    for root, dirs, files in os.walk(project_folder, topdown=False):
        dirs[:] = [d for d in dirs if d not in folders_to_delete_top_level]
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                deleted_folders += 1
                print(f"[DELETED] Cache folder: {pycache_path}")
            except OSError as e:
                print(f"[ERROR] Failed to delete folder {pycache_path}: {e}")
        for file_name in files:
            if file_name.endswith(('.pyc', '.log')):
                file_path = os.path.join(root, file_name)
                try:
                    os.remove(file_path)
                    deleted_files += 1
                    print(f"[DELETED] File: {file_path}")
                except OSError as e:
                    print(f"[ERROR] Failed to delete file {file_path}: {e}")
    print("\n--- CLEANUP PROCESS FINISHED ---")
    print(f"Total build/dist folders deleted: {deleted_top_level_folders}")
    print(f"Total __pycache__ folders deleted: {deleted_folders}")
    print(f"Total .pyc and .log files deleted: {deleted_files}")
    print("Your project is now cleaner and ready for a new build!")
if __name__ == "__main__":
    clean_project_artifacts()
