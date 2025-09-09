#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\Users\User\Desktop\flowork_gui\run_gui.bat
# JUMLAH BARIS : 53
#######################################################################

@echo off
REM =================================================================
REM  File: run_gui.bat
REM  Description: Installs dependencies and starts the STANDALONE FLOWORK GUI.
REM  Version: 7.0 (Self-installing)
REM =================================================================

REM COMMENT: The current directory IS the GUI project directory.
SET "GUI_PROJECT_DIR=%~dp0"
SET "LOG_FILE=%GUI_PROJECT_DIR%gui.log"

REM --- (DIHAPUS SEMENTARA) Pembuatan header log akan dihandle oleh Python ---
REM (
REM     echo =================================================================
REM     echo  LOG SESSION STARTED AT: %DATE% %TIME%
REM     echo =================================================================
REM     echo.
REM ) > "%LOG_FILE%"

ECHO [INFO] Preparing FLOWORK GUI Environment...
ECHO [INFO] Syncing dependencies from pyproject.toml. This may take a moment on first run...

REM ADDED: The crucial step to install GUI-specific dependencies.
poetry install --no-root
IF %ERRORLEVEL% NEQ 0 (
    ECHO [FATAL] Failed to install GUI dependencies using Poetry.
    pause
    exit /b
)

ECHO [INFO] Starting FLOWORK GUI (Standalone)...
ECHO [INFO] Environment is ready.
ECHO [INFO] A complete log is being saved to %LOG_FILE%
ECHO -----------------------------------------------------------------
ECHO.

REM --- (PERBAIKAN) Menjalankan Python secara langsung, tanpa Tee-Object ---
REM --- Python script will now handle its own logging. ---
REM powershell -Command "& {poetry run python main_gui.py 2>&1 | Tee-Object -FilePath '%LOG_FILE%' -Append}"
poetry run python main_gui.py

ECHO.
ECHO -----------------------------------------------------------------
ECHO [INFO] GUI process has been terminated.
(
    echo.
    echo -----------------------------------------------------------------
    echo [INFO] GUI process terminated.
    echo =================================================================
    echo  LOG SESSION ENDED AT: %DATE% %TIME%
    echo =================================================================
) >> "%LOG_FILE%"

pause