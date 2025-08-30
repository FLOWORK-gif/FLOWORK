#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\scripts\setup.py
# (Full code for the modified file with silent subprocess)
#######################################################################

import os
import sys
import subprocess
import shutil
import hashlib
import json
import stat
import time

LIBS_FOLDER = "libs"
VENV_FOLDER = ".venv"
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LOCK_FILE_PATH = os.path.join(PROJECT_ROOT, "poetry.lock")
STATE_FILE_PATH = os.path.join(PROJECT_ROOT, "data", "dependency_state.json")

def verbose_rmtree(path):
    """
    (MODIFIED) rmtree version that is more informative and resilient.
    It now returns True on success and False on failure.
    """
    path = os.path.abspath(path)
    if not os.path.exists(path):
        # print(f"  -> Path '{os.path.basename(path)}' not found, no need to delete.")
        return True # Considered a success if it doesn't exist
    # print(f"  -> Deleting folder '{os.path.basename(path)}' recursively...")
    time.sleep(0.5)
    had_error = False
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            filepath = os.path.join(root, name)
            try:
                os.chmod(filepath, stat.S_IWRITE)
                os.unlink(filepath)
            except OSError:
                had_error = True
        for name in dirs:
            dirpath = os.path.join(root, name)
            try:
                shutil.rmtree(dirpath)
            except OSError:
                had_error = True
    try:
        shutil.rmtree(path)
    except OSError:
         had_error = True
    return not had_error

def run_command(command, message):
    """
    (MODIFIED) Runs a command and now ensures it's completely silent when run from the main app.
    """
    # (ADDED) This is the key fix. We add the CREATE_NO_WINDOW flag to all subprocesses
    # called by THIS script, ensuring they don't flash a console window.
    creation_flags = 0
    if sys.platform == "win32":
        creation_flags = subprocess.CREATE_NO_WINDOW

    # (COMMENT) We don't need to print the status messages if we are running silently.
    # The preloader popup is handling user feedback.
    # print(f"\n> {message}")

    try:
        process = subprocess.Popen(
            command,
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, # (MODIFIED) Capture stderr as well
            text=True,
            encoding='utf-8',
            errors='replace',
            shell=True,
            creationflags=creation_flags # (ADDED) Apply the silent flag
        )
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            # (COMMENT) Even in case of error, we don't print directly
            # because this script can be run from a silent context.
            # Logging should happen in the main app if necessary.
            return False
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def get_lock_hash():
    if not os.path.exists(LOCK_FILE_PATH): return None
    return hashlib.md5(open(LOCK_FILE_PATH,'rb').read()).hexdigest()

def get_last_install_hash():
    if not os.path.exists(STATE_FILE_PATH): return None
    try:
        with open(STATE_FILE_PATH, 'r') as f:
            return json.load(f).get('lock_hash')
    except (IOError, json.JSONDecodeError):
        return None

def save_current_install_hash(lock_hash):
    os.makedirs(os.path.dirname(STATE_FILE_PATH), exist_ok=True)
    with open(STATE_FILE_PATH, 'w') as f:
        json.dump({'lock_hash': lock_hash}, f)

def main():
    os.chdir(PROJECT_ROOT)
    current_hash = get_lock_hash()
    last_hash = get_last_install_hash()

    if current_hash == last_hash and os.path.isdir(LIBS_FOLDER):
        # (COMMENT) No need to print in a potentially silent script
        return

    verbose_rmtree(os.path.join(PROJECT_ROOT, LIBS_FOLDER))
    venv_path = os.path.join(PROJECT_ROOT, VENV_FOLDER)
    if os.path.exists(venv_path):
        success = verbose_rmtree(venv_path)
        if not success:
            # (COMMENT) Cannot show messagebox here, exit silently.
            # The preloader will eventually time out or the launcher will fail.
            sys.exit(1)

    if not run_command(['poetry', 'config', 'virtualenvs.in-project', 'true'], "Setting up Poetry..."):
        return
    if not run_command(['poetry', 'install'], f"Installing dependencies..."):
        return

    temp_req_file = "temp_requirements.txt"
    if not run_command(['poetry', 'export', '-f', 'requirements.txt', '--output', temp_req_file, '--without-hashes'], "Exporting dependencies..."):
        return

    pip_install_cmd = ['poetry', 'run', 'pip', 'install', '--target', LIBS_FOLDER, '-r', temp_req_file]
    if not run_command(pip_install_cmd, f"Populating '{LIBS_FOLDER}'..."):
        if os.path.exists(temp_req_file): os.remove(temp_req_file)
        return

    if os.path.exists(temp_req_file):
        os.remove(temp_req_file)

    new_hash = get_lock_hash()
    if new_hash:
        save_current_install_hash(new_hash)

if __name__ == "__main__":
    main()