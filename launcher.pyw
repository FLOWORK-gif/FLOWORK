#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\launcher.pyw
# (DIUBAH) Logika pengecekan libs.zip dinonaktifkan
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

# All print statements in this file are commented out for silent operation.
def show_progress(message):
    pass

def extract_archive(zip_name, target_dir, project_root):
    zip_path = os.path.join(project_root, zip_name)
    target_path = os.path.join(project_root, target_dir)
    if os.path.exists(target_path):
        return True
    if not os.path.exists(zip_path):
        return False
    try:
        os.makedirs(target_path, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_path)
        return True
    except Exception as e:
        shutil.rmtree(target_path, ignore_errors=True)
        return False

def find_main_script(project_root):
    compiled_ext = ".pyd" if platform.system() == "Windows" else ".so"
    for filename in os.listdir(project_root):
        if filename.startswith(MAIN_SCRIPT_BASE_NAME) and filename.endswith(compiled_ext):
            return filename
    source_file = MAIN_SCRIPT_BASE_NAME + ".py"
    if os.path.exists(os.path.join(project_root, source_file)):
        return source_file
    return None

def signal_handler(sig, frame):
    if child_process and child_process.poll() is None:
        try:
            if platform.system() == "Windows":
                os.kill(child_process.pid, signal.CTRL_BREAK_EVENT)
            else:
                os.killpg(os.getpgid(child_process.pid), signal.SIGTERM)
        except Exception as e:
            child_process.kill()
    sys.exit(0)

def cleanup_preloader():
    pid_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), PRELOADER_PID_FILE)
    if os.path.exists(pid_file_path):
        try:
            time.sleep(2)
            with open(pid_file_path, "r") as f:
                pid = int(f.read().strip())
            if platform.system() == "Windows":
                subprocess.run(['taskkill', '/F', '/PID', str(pid)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                os.kill(pid, signal.SIGKILL)
        except (ValueError, OSError, subprocess.CalledProcessError) as e:
            pass
        finally:
            try:
                os.remove(pid_file_path)
            except OSError as e:
                pass

def main():
    global child_process

    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        project_root = os.path.dirname(os.path.abspath(__file__))

        if not extract_archive(PYTHON_ZIP_NAME, PYTHON_DIR_NAME, project_root):
            sys.exit(1)

        python_dir_path = os.path.join(project_root, PYTHON_DIR_NAME)
        pythonw_exe_path = os.path.join(python_dir_path, "pythonw.exe")

        final_python_executable = None
        if os.path.exists(pythonw_exe_path):
            final_python_executable = pythonw_exe_path
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

            # (ULTIMATE FIX) Redirect stdout and stderr to DEVNULL.
            # This forcibly silences any and all console output from the main script,
            # preventing Windows from creating a console window for it.
            child_process = subprocess.Popen(
                command_to_run,
                cwd=project_root,
                creationflags=creationflags,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            child_process.wait()

        except Exception as e:
            pass # Fail silently in case of launcher error

    finally:
        pass

if __name__ == "__main__":
    main()