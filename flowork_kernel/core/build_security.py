#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\core\build_security.py
# (This is a new file to be created)
# NOTE: This file holds our security signature and runtime checks.
#######################################################################
import os
import sys

# (ADDED) This is the official, hardcoded signature that will be embedded
# into every compiled .aola_flowork file. This is our "secret keyword".
OFFICIAL_BUILD_SIGNATURE = "B3Ba%m#rDeKa"

def perform_runtime_check(module_file_path):
    """
    This function is injected into the __init__ of every compiled module.
    It performs critical security checks at the moment the module is loaded.
    """
    # --- RULE 1: Check for the existence of the build fingerprint ---
    # This ensures the module was not just copied without its validation file.
    module_dir = os.path.dirname(os.path.abspath(module_file_path))
    fingerprint_path = os.path.join(module_dir, "build_fingerprint.json")

    if not os.path.exists(fingerprint_path):
        # COMMENT: If the fingerprint is missing, the module is considered invalid.
        # We raise a specific error that the kernel can catch.
        # This helps prevent simple copy-paste cracking.
        raise RuntimeError(f"Security Alert: Module at '{module_dir}' is missing its 'build_fingerprint.json' and cannot be loaded.")

    # (COMMENT) The second rule (checking for the signature key) is handled by the
    # ModuleManagerService before this code is even executed, as a primary line of defense.
    # It opens the .aola_flowork file in binary mode and searches for the signature bytes.