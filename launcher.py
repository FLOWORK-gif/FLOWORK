#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\launcher.py
# JUMLAH BARIS : 103
#######################################################################

import sys
import os
import zipfile
import subprocess
import time
import shutil
import platform
import signal
PYTHON_ZIP_NAME = "python.zip"
PYTHON_DIR_NAME = "python"
MAIN_SCRIPT_BASE_NAME = "main"
PRELOADER_PID_FILE = "pre_launcher.pid"
child_process = None
def show_progress(message):
    """Simple progress display for the console."""
    sys.stdout.write(f"\r> {message}")
    sys.stdout.flush()
def extract_archive(zip_name, target_dir, project_root):
    """Generic function to extract a zip file with progress."""
    zip_path = os.path.join(project_root, zip_name)
    target_path = os.path.join(project_root, target_dir)
    if os.path.exists(target_path):
        print(f"'{target_dir}' directory already exists. Skipping extraction.")
        return True
    if not os.path.exists(zip_path):
        return False
    try:
        os.makedirs(target_path, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            total_files = len(zip_ref.infolist())
            for i, file_info in enumerate(zip_ref.infolist()):
                zip_ref.extract(file_info, target_path)
    except Exception as e:
        shutil.rmtree(target_path, ignore_errors=True)
        return False
    return True
def find_main_script(project_root):
    """
    Intelligently finds the main script to run.
    """
    compiled_ext = ".pyd" if platform.system() == "Windows" else ".so"
    for filename in os.listdir(project_root):
        if filename.startswith(MAIN_SCRIPT_BASE_NAME) and filename.endswith(compiled_ext):
            return filename
    source_file = MAIN_SCRIPT_BASE_NAME + ".py"
    if os.path.exists(os.path.join(project_root, source_file)):
        return source_file
    return None
def signal_handler(sig, frame):
    """
    Handles termination signals more robustly.
    """
    if child_process and child_process.poll() is None:
        try:
            if platform.system() == "Windows":
                os.kill(child_process.pid, signal.CTRL_BREAK_EVENT)
            else:
                os.killpg(os.getpgid(child_process.pid), signal.SIGTERM)
        except Exception:
            child_process.kill()
    sys.exit(0)
def main():
    global child_process
    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        project_root = os.path.dirname(os.path.abspath(__file__))
        if not extract_archive(PYTHON_ZIP_NAME, PYTHON_DIR_NAME, project_root):
            sys.exit(1)
        python_dir_path = os.path.join(project_root, PYTHON_DIR_NAME)
        python_exe_path = os.path.join(python_dir_path, "python.exe")
        pythonw_exe_path = os.path.join(python_dir_path, "pythonw.exe")
        final_python_executable = None
        if os.path.exists(pythonw_exe_path):
            final_python_executable = pythonw_exe_path
        elif os.path.exists(python_exe_path):
            final_python_executable = python_exe_path
        else:
            sys.exit(1)
        main_script_to_run = find_main_script(project_root)
        if not main_script_to_run:
            sys.exit(1)
        main_script_path = os.path.join(project_root, main_script_to_run)
        try:
            command_to_run = [final_python_executable, main_script_path]
            creationflags = 0
            if platform.system() == "Windows":
                creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
            child_process = subprocess.Popen(command_to_run, cwd=project_root, creationflags=creationflags)
            child_process.wait()
        except Exception:
            time.sleep(10) # Wait in case of error so the user might see something if run manually
    finally:
        pass
if __name__ == "__main__":
    main()
