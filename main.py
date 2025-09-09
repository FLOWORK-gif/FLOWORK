#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\main.py
# JUMLAH BARIS : 67
#######################################################################

import sys
import os
PROJECT_ROOT_FOR_LOGGER = os.path.dirname(os.path.abspath(__file__))
project_root_for_path = os.path.dirname(os.path.abspath(__file__))
libs_path = os.path.join(project_root_for_path, 'libs')
if project_root_for_path not in sys.path:
    sys.path.insert(0, project_root_for_path)
if libs_path not in sys.path:
    sys.path.insert(0, libs_path)
import logging
import datetime
import queue
import time
from importlib.machinery import SourcelessFileLoader, ExtensionFileLoader
import importlib.metadata
if project_root_for_path not in sys.path:
    sys.path.insert(0, project_root_for_path)
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"flowork_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
if __name__ == "__main__":
    project_root_path = os.path.dirname(os.path.abspath(__file__))
    PID_FILE = os.path.join(project_root_path, "server.pid")
    from flowork_kernel.core.permission_hook import PermissionHook
    sys.meta_path.insert(1, PermissionHook())
    kernel = None
    try:
        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))
        from flowork_kernel.kernel import Kernel
        kernel = Kernel(project_root_path)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
            ]
        )
        logging.info("Starting Flowork application...") # English Log
        kernel.start_all_services()
        kernel.write_to_log("Flowork Server is now running. Press Ctrl+C to stop.", "SUCCESS") # English Log
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            kernel.write_to_log("Server shutdown requested by user (Ctrl+C).", "INFO") # English Log
    except Exception as e:
        print(f"FATAL SERVER ERROR: {e}") # English Log
        logging.critical(f"A fatal error occurred during server startup: {e}", exc_info=True) # English Log
        sys.exit(1)
    finally:
        if kernel:
            kernel.write_to_log("Initiating graceful shutdown of all services.", "INFO") # English Log
            kernel.stop_all_services()
        if os.path.exists(PID_FILE):
            try:
                os.remove(PID_FILE)
            except OSError as e:
                print(f"Could not remove PID file: {e}")
        print("Flowork Server has been shut down.") # English Log
