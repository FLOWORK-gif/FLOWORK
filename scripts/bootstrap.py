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
    This script is the user-facing dependency installer.
    It reads the requirements.txt file and uses the bundled python's pip
    to install all necessary libraries.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    python_exe = os.path.join(project_root, "python", "python.exe")
    requirements_file = os.path.join(project_root, "requirements.txt")
    first_run_lock_file = os.path.join(project_root, "data", ".first_run_complete")

    print("--- Flowork First-Time Setup ---")

    if not os.path.exists(python_exe):
        print(f"[FATAL] Bundled Python not found at: {python_exe}")
        return

    if not os.path.exists(requirements_file):
        print(f"[FATAL] requirements.txt not found at: {requirements_file}")
        return

    print(f"[INFO] Installing dependencies from {os.path.basename(requirements_file)}...")
    print("[INFO] This may take several minutes depending on your internet speed. Please be patient.")

    try:
        # Command to install dependencies using the bundled pip
        command = [
            python_exe, "-m", "pip", "install",
            "--no-cache-dir", # Ensures fresh downloads
            "--no-warn-script-location",
            "-r", requirements_file
        ]

        # Run the command and print output in real-time
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"  {output.strip()}")

        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command)

        print("\n[SUCCESS] All libraries installed successfully!")

        # Create the lock file to indicate setup is complete
        os.makedirs(os.path.dirname(first_run_lock_file), exist_ok=True)
        with open(first_run_lock_file, 'w') as f:
            f.write(str(time.time()))

        print("[SUCCESS] First-time setup is complete.")

    except Exception as e:
        print(f"\n[FATAL ERROR] An error occurred during library installation: {e}")
        print("Please check your internet connection and try running the launcher again.")
        # Optional: Clean up a potentially corrupted state
        if os.path.exists(first_run_lock_file):
            os.remove(first_run_lock_file)
        # Keep the console open for the user to see the error
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()