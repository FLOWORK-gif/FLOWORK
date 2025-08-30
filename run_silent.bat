@echo off
REM File ini akan menjadi jembatan antara VBS dan Poetry
REM untuk memastikan environment yang benar digunakan tanpa menampilkan konsol.

REM Pindah ke direktori di mana script ini berada
cd /d "%~dp0"

REM Jalankan pre_launcher.py menggunakan poetry dengan pythonw (windowless)
poetry run pythonw pre_launcher.py