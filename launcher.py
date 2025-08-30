#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\launcher.py
# JUMLAH BARIS : 124 (Bertambah karena ada perbaikan)
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
LIBS_ZIP_NAME = "libs.zip"
LIBS_DIR_NAME = "libs"
MAIN_SCRIPT_BASE_NAME = "main"
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
        print(f"\n[FATAL ERROR] {zip_name} not found. Cannot run the application.")
        return False
    print(f"Extracting '{zip_name}'... Please wait, this might take a moment.")
    try:
        os.makedirs(target_path, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            total_files = len(zip_ref.infolist())
            for i, file_info in enumerate(zip_ref.infolist()):
                zip_ref.extract(file_info, target_path)
                progress_percentage = (i + 1) / total_files * 100
                show_progress(f"Unpacking '{zip_name}': file {i+1}/{total_files} ({progress_percentage:.1f}%)")
        print(f"\nExtraction of '{zip_name}' complete.")
        return True
    except Exception as e:
        print(f"\n[FATAL ERROR] Failed to extract {zip_name}: {e}")
        shutil.rmtree(target_path, ignore_errors=True)
        return False

def find_main_script(project_root):
    """
    (ADDED) Intelligently finds the main script to run.
    It prioritizes the compiled .pyd file for production/release,
    and falls back to the .py file for development.
    """
    compiled_ext = ".pyd" if platform.system() == "Windows" else ".so"
    for filename in os.listdir(project_root):
        if filename.startswith(MAIN_SCRIPT_BASE_NAME) and filename.endswith(compiled_ext):
            print(f"  -> Found compiled main script: {filename}")
            return filename
    source_file = MAIN_SCRIPT_BASE_NAME + ".py"
    if os.path.exists(os.path.join(project_root, source_file)):
        print(f"  -> Found source code main script: {source_file}")
        return source_file
    return None

def signal_handler(sig, frame):
    """
    (FIXED) Handles termination signals more robustly to ensure the child process is also killed,
    especially when the console window is closed on Windows.
    """
    print("\n[INFO] Termination signal received. Shutting down Flowork application...") # English Log
    if child_process and child_process.poll() is None: # (MODIFIED) Check if the child process is still running
        try:
            # (FIXED) Use a more robust termination method for Windows process groups
            if platform.system() == "Windows":
                print("[INFO] Sending CTRL_BREAK_EVENT to process group...") # English Log
                # This signal is sent to the entire process group started by the child
                os.kill(child_process.pid, signal.CTRL_BREAK_EVENT)
            else:
                # For Unix-like systems, kill the entire process group
                print("[INFO] Sending SIGTERM to process group...") # English Log
                os.killpg(os.getpgid(child_process.pid), signal.SIGTERM)
        except Exception as e:
            # Fallback if the primary method fails for any reason
            print(f"[WARN] Could not terminate process group cleanly, attempting fallback kill: {e}") # English Log
            child_process.kill()
    sys.exit(0)

def main():
    global child_process # (DITAMBAHKAN) Menggunakan variabel global
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    project_root = os.path.dirname(os.path.abspath(__file__))
    print("--- Flowork Portable Launcher ---")
    if not extract_archive(PYTHON_ZIP_NAME, PYTHON_DIR_NAME, project_root):
        time.sleep(5)
        sys.exit(1)
    if not extract_archive(LIBS_ZIP_NAME, LIBS_DIR_NAME, project_root):
        time.sleep(5)
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
        print(f"\n[FATAL ERROR] Could not find 'python.exe' or 'pythonw.exe' in the extracted '{PYTHON_DIR_NAME}' folder.")
        time.sleep(5)
        sys.exit(1)
    main_script_to_run = find_main_script(project_root)
    if not main_script_to_run:
        print(f"\n[FATAL ERROR] Main script '{MAIN_SCRIPT_BASE_NAME}.py' or its compiled version not found.")
        time.sleep(5)
        sys.exit(1)
    main_script_path = os.path.join(project_root, main_script_to_run)
    print(f"\nStarting Flowork with '{os.path.basename(final_python_executable)}' on '{main_script_to_run}'...")
    try:
        command_to_run = [final_python_executable, main_script_path]
        creationflags = 0
        if platform.system() == "Windows":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
        child_process = subprocess.Popen(command_to_run, cwd=project_root, creationflags=creationflags)
        child_process.wait()
    except subprocess.CalledProcessError as e:
        print(f"\n[APP ERROR] The application exited with an error (code: {e.returncode}).")
    except Exception as e:
        print(f"\n[LAUNCHER ERROR] Failed to start the main application: {e}")
        time.sleep(10)

if __name__ == "__main__":
    main()