#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\kernel.py
# (This is a stable, uncompiled loader stub)
#######################################################################

# This file acts as a stable, uncompiled loader.
# It allows the main kernel logic to be secured in a compiled .kernel file
# while keeping the initial entry point simple and debuggable.

try:
    # Import everything from the compiled kernel logic.
    # The custom importer in main.py will find 'kernel_logic.kernel'
    from .kernel_logic import *
except ImportError as e:
    # This provides a crucial fallback error message if the compiled file is missing or corrupt.
    # This message will be visible even if the main logger hasn't started.
    print("FATAL KERNEL ERROR: Could not load the compiled kernel logic (kernel_logic.kernel).") # English log
    print(f"Ensure you have run the build_engine.py script. Details: {e}") # English log
    # In a real app, you might show a GUI messagebox here before exiting.
    import sys
    sys.exit(1)