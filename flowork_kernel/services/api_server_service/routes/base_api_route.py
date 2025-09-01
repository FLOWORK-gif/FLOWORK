#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\base_api_route.py
# JUMLAH BARIS : 32
#######################################################################

from abc import ABC, abstractmethod
class BaseApiRoute(ABC):
    """
    Abstract base class for all API route handlers.
    Each route module must inherit from this class and implement its methods.
    """
    def __init__(self, service_instance):
        self.service_instance = service_instance
        self.kernel = service_instance.kernel
        self.logger = self.kernel.write_to_log
    @abstractmethod
    def register_routes(self) -> dict:
        """
        This method must return a dictionary that maps URL patterns to handler methods.
        Example:
        return {
            "GET /agents": self.handle_get_all,
            "POST /agents": self.handle_create,
            "GET /agents/{agent_id}": self.handle_get_one,
            "DELETE /agents/{agent_id}": self.handle_delete
        }
        The key is "METHOD /path/pattern".
        The value is the handler method from this class.
        """
        pass
