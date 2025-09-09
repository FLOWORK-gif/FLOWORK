@echo off
REM =================================================================
REM  File: run_server.bat
REM  Description: Starts FLOWORK server with LIVE console logging
REM               AND complete file logging using PowerShell.
REM  Version: 3.0 (FINAL)
REM =================================================================

SET "LOG_FILE=server.log"

REM --- Membuat file log baru dengan header timestamp ---
(
    echo =================================================================
    echo  LOG SESSION STARTED AT: %DATE% %TIME%
    echo =================================================================
    echo.
) > %LOG_FILE%

ECHO [INFO] Starting FLOWORK Server...
ECHO [INFO] Live output is shown below. A complete log is also being saved to %LOG_FILE%
ECHO -----------------------------------------------------------------
ECHO.

REM --- Menjalankan perintah utama dan 'membelah' outputnya ---
REM Output akan tampil di CMD ini DAN ditambahkan ke file log.
powershell -Command "& {poetry run python main.py 2>&1 | Tee-Object -FilePath '%LOG_FILE%' -Append}"

ECHO.
ECHO -----------------------------------------------------------------
ECHO [INFO] Server process has been terminated.
(
    echo.
    echo -----------------------------------------------------------------
    echo [INFO] Server process terminated.
    echo =================================================================
    echo  LOG SESSION ENDED AT: %DATE% %TIME%
    echo =================================================================
) >> %LOG_FILE%

pause