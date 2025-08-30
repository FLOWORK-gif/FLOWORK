#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\scripts\bootstrap.py
# (File baru untuk instalasi otomatis bagi pengguna)
#######################################################################

import subprocess
import sys
import os
import time

def main():
    """
    (MODIFIED) This script is now fully silent for integration with the preloader.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    python_exe = os.path.join(project_root, "python", "python.exe")
    requirements_file = os.path.join(project_root, "requirements.txt")
    first_run_lock_file = os.path.join(project_root, "data", ".first_run_complete")

    # (COMMENTED) All print statements are silenced.
    # print("--- Flowork First-Time Setup ---")

    if not os.path.exists(python_exe) or not os.path.exists(requirements_file):
        sys.exit(1) # Exit with an error code if critical files are missing

    # print(f"[INFO] Installing dependencies from {os.path.basename(requirements_file)}...")
    # print("[INFO] This may take several minutes depending on your internet speed. Please be patient.")

    try:
        command = [
            python_exe, "-m", "pip", "install",
            "--no-cache-dir",
            "--no-warn-script-location",
            "-r", requirements_file
        ]

        # (MODIFIED) Run the subprocess silently, redirecting all output to DEVNULL.
        # This is crucial for preventing any console flashes.
        creation_flags = 0
        if sys.platform == "win32":
            creation_flags = subprocess.CREATE_NO_WINDOW

        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creation_flags
        )

        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, command)

        # print("\n[SUCCESS] All libraries installed successfully!")

        os.makedirs(os.path.dirname(first_run_lock_file), exist_ok=True)
        with open(first_run_lock_file, 'w') as f:
            f.write(str(time.time()))

        # print("[SUCCESS] First-time setup is complete.")

    except Exception as e:
        # print(f"\n[FATAL ERROR] An error occurred during library installation: {e}")
        # print("Please check your internet connection and try running the launcher again.")
        if os.path.exists(first_run_lock_file):
            os.remove(first_run_lock_file)
        sys.exit(1) # Exit with an error code on failure

if __name__ == "__main__":
    main()