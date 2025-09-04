#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\Users\User\Desktop\FLOWORK\clean.py
# JUMLAH BARIS : 60
#######################################################################

import os
import shutil
def bersihkan_sampah():
    """
    Fungsi untuk mencari dan menghapus folder __pycache__, build, dist
    dan file dengan ekstensi .pyc dan .log di dalam direktori
    tempat skrip ini dijalankan dan semua subfolder-nya.
    """
    folder_proyek = os.getcwd()
    print(f"Akan membersihkan cache, log, dan folder build di dalam: {folder_proyek}")
    konfirmasi = input("Apakah Anda yakin ingin melanjutkan? (y/n): ")
    if konfirmasi.lower() != 'y':
        print("Pembersihan dibatalkan oleh pengguna.")
        return
    folders_to_delete_top_level = ['build', 'dist']
    folder_dihapus_utama = 0
    for folder_name in folders_to_delete_top_level:
        path_folder = os.path.join(folder_proyek, folder_name)
        if os.path.isdir(path_folder):
            try:
                shutil.rmtree(path_folder)
                folder_dihapus_utama += 1
                print(f"[DIHAPUS] Folder utama: {path_folder}")
            except OSError as e:
                print(f"[ERROR] Gagal menghapus folder {path_folder}: {e}")
    folder_dihapus = 0
    file_dihapus = 0
    for root, dirs, files in os.walk(folder_proyek, topdown=False):
        dirs[:] = [d for d in dirs if d not in folders_to_delete_top_level]
        if '__pycache__' in dirs:
            path_folder_cache = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(path_folder_cache)
                folder_dihapus += 1
                print(f"[DIHAPUS] Folder cache: {path_folder_cache}")
            except OSError as e:
                print(f"[ERROR] Gagal menghapus folder {path_folder_cache}: {e}")
        for nama_file in files:
            if nama_file.endswith(('.pyc', '.log')):
                path_file = os.path.join(root, nama_file)
                try:
                    os.remove(path_file)
                    file_dihapus += 1
                    print(f"[DIHAPUS] File: {path_file}")
                except OSError as e:
                    print(f"[ERROR] Gagal menghapus file {path_file}: {e}")
    print("\n--- PROSES PEMBERSIHAN SELESAI ---")
    print(f"Total folder build/dist yang dihapus: {folder_dihapus_utama}")
    print(f"Total folder __pycache__ yang dihapus: {folder_dihapus}")
    print(f"Total file .pyc dan .log yang dihapus: {file_dihapus}")
    print("Proyek Anda sekarang lebih bersih dan siap untuk build baru!")
if __name__ == "__main__":
    bersihkan_sampah()
