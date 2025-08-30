#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\scripts\setup.py
# (Full code for the modified file)
#######################################################################
import subprocess
import sys
import os

def install_packages():
    # Arahkan ke path pip yang ada di dalam folder python portabel
    pip_executable = os.path.join(os.path.dirname(sys.executable), 'Scripts', 'pip.exe')
    requirements_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'requirements.txt')

    if not os.path.exists(pip_executable):
        print("ERROR: pip.exe not found. Cannot install dependencies.")
        return

    if not os.path.exists(requirements_path):
        print("INFO: requirements.txt not found. No dependencies to install.")
        return

    print("INFO: Checking and installing dependencies from requirements.txt...")
    
    # Perintah untuk instalasi, dengan flag -q (quiet) agar tidak terlalu berisik
    command = [
        pip_executable,
        "install",
        "-r",
        requirements_path,
        "--quiet",
        "--no-warn-script-location"
    ]

    try:
        # Jalankan perintah dan cetak outputnya secara real-time
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                # Kita tidak perlu mencetak setiap baris progres pip
                # Cukup biarkan proses berjalan
                pass
        
        if process.returncode == 0:
            print("SUCCESS: All dependencies are up to date.")
        else:
            print(f"ERROR: pip process finished with exit code {process.returncode}.")
            
    except Exception as e:
        print(f"FATAL ERROR: An exception occurred during dependency installation: {e}")

if __name__ == "__main__":
    install_packages()