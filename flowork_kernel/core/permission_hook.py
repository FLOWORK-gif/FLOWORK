#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\core\permission_hook.py
# JUMLAH BARIS : 61
#######################################################################

import sys
from flowork_kernel.kernel import Kernel
from flowork_kernel.exceptions import PermissionDeniedError
_kernel_instance = None
def get_kernel():
    global _kernel_instance
    if _kernel_instance is None:
        _kernel_instance = Kernel.instance
    return _kernel_instance
class PermissionHook:
    """
    A Python Import Hook that acts as a gatekeeper for premium libraries.
    """
    PROTECTED_MODULES = {
        "selenium": "web_scraping_advanced",
        "webdriver_manager": "web_scraping_advanced",
        "torch": "ai_local_models",
        "diffusers": "ai_local_models",
        "transformers": "ai_local_models",
        "llama_cpp": "ai_local_models",
        "moviepy": "video_processing",
        "nuitka": "core_compilation"
    }
    def __init__(self):
        self._active = False
        kernel = get_kernel()
        if kernel:
            event_bus = kernel.get_service("event_bus", is_system_call=True)
            if event_bus:
                event_bus.subscribe("event_all_services_started", "PermissionHookActivator", self.activate)
    def activate(self, event_data=None):
        """Activates the hook to start enforcing permissions."""
        kernel = get_kernel()
        if kernel:
            kernel.write_to_log("PermissionHook: Activating import-level security.", "SUCCESS")
        self._active = True
    def find_spec(self, fullname, path, target=None):
        """
        The core method of the import hook.
        """
        if not self._active:
            return None
        module_root = fullname.split('.')[0]
        if module_root in self.PROTECTED_MODULES:
            kernel = get_kernel()
            if kernel:
                permission_manager = kernel.get_service("permission_manager_service", is_system_call=True)
                capability = self.PROTECTED_MODULES[module_root]
                if permission_manager:
                    try:
                        permission_manager.check_permission(capability)
                    except PermissionDeniedError as e:
                        raise e
        return None
