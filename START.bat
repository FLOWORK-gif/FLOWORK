@echo off
TITLE FLOWORK Server - Live Log

:: ==================================================================
:: == KONFIGURASI: Sesuaikan waktu tunggu jika server lambat.
::    Untuk komputer kebanyakan, 10 detik sudah lebih dari cukup.
set WAIT_SECONDS=25
:: ==================================================================

ECHO ==================================================================
ECHO ==            FLOWORK Unified Server Launcher (v.Ultimate)        ==
ECHO ==================================================================
ECHO.

ECHO [INFO] Preparing the environment...
ECHO [INFO] Project Root: %~dp0
ECHO [INFO] Checking Python version used by Poetry:
poetry run python --version
ECHO.

REM --- Beri jeda waktu yang bisa dikonfigurasi agar server punya waktu untuk siap ---
ECHO [INFO] Waiting for %WAIT_SECONDS% seconds to allow the server to initialize...
timeout /t %WAIT_SECONDS% /nobreak >nul

REM --- Buka browser setelah menunggu ---
ECHO [INFO] Opening Server Control Panel in browser...
ECHO [INFO] If you see an error, increase WAIT_SECONDS at the top of this script.
start http://127.0.0.1:8989/

ECHO.
ECHO ==================================================================
ECHO ==                 LIVE SERVER LOG STARTED                      ==
ECHO ==   (Log ini juga disimpan secara lengkap di server.log)       ==
ECHO ==================================================================
ECHO.

REM --- Jalankan server dengan perintah PowerShell yang canggih untuk menambahkan timestamp di setiap baris ---
powershell -Command "& {poetry run python main.py 2>&1 | ForEach-Object { '[{0}] {1}' -f (Get-Date -Format 'HH:mm:ss'), $_ } | Tee-Object -FilePath 'server.log' -Append}"

ECHO.
ECHO ==================================================================
ECHO ==                  SERVER PROCESS TERMINATED                   ==
ECHO ==================================================================
pause