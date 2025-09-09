#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\kernel.py
# JUMLAH BARIS : 14
#######################################################################

try:
    from .kernel_logic import *
except ImportError as e:
    print("FATAL KERNEL ERROR: Could not load the compiled kernel logic (kernel_logic.kernel).") # English log
    print(f"Ensure you have run the build_engine.py script. Details: {e}") # English log
    import sys
    sys.exit(1)
