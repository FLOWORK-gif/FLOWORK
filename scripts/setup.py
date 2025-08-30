#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\scripts\setup.py
# JUMLAH BARIS : 144
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
        print(f"  -> Path '{os.path.basename(path)}' not found, no need to delete.")
        return True # (MODIFIED) Considered a success if it doesn't exist
    print(f"  -> Deleting folder '{os.path.basename(path)}' recursively...")
    time.sleep(0.5)
    had_error = False
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            filepath = os.path.join(root, name)
            try:
                os.chmod(filepath, stat.S_IWRITE) # Attempt to unlock
                os.unlink(filepath)
            except OSError as e:
                print(f"    [WARN] Failed to delete file {filepath}: {e}")
                had_error = True
        for name in dirs:
            dirpath = os.path.join(root, name)
            try:
                shutil.rmtree(dirpath)
            except OSError as e:
                print(f"    [WARN] Failed to delete folder {dirpath}: {e}")
                had_error = True
    try:
        shutil.rmtree(path)
        print(f"  [SUCCESS] Folder '{os.path.basename(path)}' successfully deleted.")
    except OSError as e:
         print(f"  [WARN] Failed to delete root folder {path}: {e}")
         had_error = True
    return not had_error # (MODIFIED) Return the success status
def run_command(command, message):
    """Fungsi untuk menjalankan perintah dan menampilkan output-nya secara real-time."""
    print(f"\n> {message}")
    try:
        process = subprocess.Popen(
            command,
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            shell=True
        )
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"  {output.strip()}")
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command)
        print(f"  [SUCCESS] {message} selesai.")
        return True
    except FileNotFoundError:
        print(f"  [ERROR] Perintah '{command[0]}' tidak ditemukan. Pastikan Poetry sudah terinstall.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Gagal menjalankan: {' '.join(command)}")
        print(f"  -> Proses selesai dengan kode error: {e.returncode}")
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
        print("[INFO] Dependensi sudah sinkron. Melewatkan instalasi.")
        return
    print("\n[SETUP] Dependensi tidak sinkron atau belum terinstall. Memulai proses...")
    print("        Proses ini mungkin memakan waktu beberapa menit, tergantung kecepatan internet.")
    verbose_rmtree(os.path.join(PROJECT_ROOT, LIBS_FOLDER))
    venv_path = os.path.join(PROJECT_ROOT, VENV_FOLDER)
    if os.path.exists(venv_path):
        success = verbose_rmtree(venv_path)
        if not success:
            print("\n================================= GAGAL ===================================")
            print("[FATAL ERROR] Gagal menghapus folder .venv sebelumnya.")
            print("Ini biasanya terjadi karena ada terminal atau proses Flowork yang masih berjalan.")
            print("\nSOLUSI:")
            print("1. Tutup SEMUA terminal atau command prompt yang terbuka di folder FLOWORK.")
            print("2. Pastikan tidak ada proses 'python.exe' dari Flowork yang berjalan di Task Manager.")
            print("3. Coba jalankan kembali launcher ini.")
            print("===========================================================================")
            sys.exit(1) # (ADDED) Stop the script here to prevent further errors
    if not run_command(['poetry', 'config', 'virtualenvs.in-project', 'true'], "Mengatur Poetry untuk membuat .venv lokal..."):
        return
    if not run_command(['poetry', 'install'], f"Membuat virtual environment & menginstall dependensi..."):
        return
    temp_req_file = "temp_requirements.txt"
    if not run_command(['poetry', 'export', '-f', 'requirements.txt', '--output', temp_req_file, '--without-hashes'], "Mengekspor daftar dependensi..."):
        return
    pip_install_cmd = ['poetry', 'run', 'pip', 'install', '--target', LIBS_FOLDER, '-r', temp_req_file]
    if not run_command(pip_install_cmd, f"Menginstall semua paket ke dalam folder '{LIBS_FOLDER}'..."):
        if os.path.exists(temp_req_file): os.remove(temp_req_file)
        return
    if os.path.exists(temp_req_file):
        os.remove(temp_req_file)
        print(f"  -> File sementara '{temp_req_file}' dibersihkan.")
    new_hash = get_lock_hash()
    if new_hash:
        save_current_install_hash(new_hash)
        print("  [SUCCESS] Status dependensi baru berhasil disimpan.")
    print("\n[SUCCESS] Proses setup & sinkronisasi dependensi selesai!")
if __name__ == "__main__":
    main()
