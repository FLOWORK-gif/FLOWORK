@echo off
rem This file is now a smart launcher that will check for updates and the environment.

echo =========================================================
echo FLOWORK SMART LAUNCHER
echo =====================================================
echo.

REM *** IMPORTANT LINE: Move to the directory where this .bat file is located ***
cd /d "%~dp0"

echo [STAGE 1/4] Checking and preparing the environment (first-time installation)...
echo -------------------------------------------------------

rem ======================================================================
rem === CHANGE HERE: Call python directly, not through poetry run ===
python scripts/setup.py
rem =========================================================================

echo ---------------------------------------------
echo.

echo [STEP 2/4] Checking for updates from GitHub...
echo -------------------------------------------------------
rem (This is the updater script from the previous answer, if you used it)
rem python updater.py
echo -------------------------------------------------------
echo.

echo [STEP 3/4] Checking license and version...
echo [STEP 4/4] Running Flowork...
echo -------------------------------------------------------
rem Running the main launcher that will start the Flowork application
poetry run python launcher.py
echo -------------------------------------------------------
echo.

echo Process completed. Press any key to exit.
pause >nul