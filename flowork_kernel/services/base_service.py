#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\services\base_service.py
# JUMLAH BARIS : 38
#######################################################################

class BaseService:
    """
    The base class for all services in the Flowork ecosystem.
    Each service inherits from this class to ensure it has a consistent
    initialization method and can be managed by the Kernel's lifecycle.
    """
    def __init__(self, kernel, service_id: str):
        """
        Initializes the service.
        Args:
            kernel: The main Kernel instance, providing access to other services and core functions.
            service_id (str): The unique identifier for this service, as defined in services.json.
        """
        self.kernel = kernel
        self.service_id = service_id
        self.logger = self.kernel.write_to_log # (ADDED) Logger is now fundamental for all services
        self.loc = None # Will be available after localization_manager is loaded
        if 'localization_manager' in self.kernel.services:
            self.loc = self.kernel.get_service('localization_manager')
    def start(self):
        """
        Optional method to start any background tasks or long-running processes.
        Called by the Kernel during the startup sequence.
        """
        pass
    def stop(self):
        """
        Optional method to gracefully stop any background tasks before the application closes.
        Called by the Kernel during the shutdown sequence.
        """
        pass
