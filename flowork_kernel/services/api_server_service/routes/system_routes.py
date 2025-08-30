#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\system_routes.py
# JUMLAH BARIS : 72
#######################################################################

from .base_api_route import BaseApiRoute
import time
class SystemRoutes(BaseApiRoute):
    """
    Manages API routes for system actions like hot-reloading, addon uploads, and status checks.
    """
    def register_routes(self) -> dict:
        return {
            "POST /api/v1/addons/upload": self.handle_addon_upload,
            "POST /api/v1/system/actions/hot_reload": self.handle_hot_reload,
            "GET /api/v1/status": self.handle_get_status,
            "POST /api/v1/system/actions/restart": self.handle_restart, # <<< MODIFIKASI: Tambahkan rute baru
        }
    def handle_get_status(self, handler):
        """
        Handles the public status check endpoint. This route does not require authentication.
        """
        status_info = {
            "status": "ok",
            "version": self.kernel.APP_VERSION,
            "timestamp": time.time()
        }
        handler._send_response(200, status_info)
    def handle_addon_upload(self, handler):
        addon_service = self.service_instance.addon_service
        if not addon_service:
            return handler._send_response(503, {"error": "CommunityAddonService is not available."})
        body = handler._get_json_body()
        if body is None: return
        comp_type = body.get("comp_type")
        component_id = body.get("component_id")
        description = body.get("description")
        tier = body.get("tier")
        if not all([comp_type, component_id, description, tier]):
            return handler._send_response(400, {"error": "Request body must contain 'comp_type', 'component_id', 'description', and 'tier'."})
        try:
            success, result_message = addon_service.upload_component(comp_type, component_id, description, tier)
            if success:
                handler._send_response(200, {"status": "success", "message": result_message})
            else:
                handler._send_response(500, {"error": result_message})
        except Exception as e:
            self.logger(f"API Addon Upload Error: {e}", "ERROR")
            handler._send_response(500, {"error": str(e)})
    def handle_hot_reload(self, handler):
        try:
            self.kernel.hot_reload_components()
            handler._send_response(200, {"status": "success", "message": "Hot reload process initiated."})
        except Exception as e:
            self.logger(f"Hot reload via API failed: {e}", "CRITICAL")
            handler._send_response(500, {"error": f"Internal server error during hot reload: {e}"})
    def handle_restart(self, handler):
        """
        Handles the API request to trigger a restart event.
        """
        try:
            event_bus = self.kernel.get_service("event_bus")
            if event_bus:
                self.kernel.root.after(100, lambda: event_bus.publish("RESTART_APP", {}))
                handler._send_response(202, {"status": "accepted", "message": "Restart signal sent to the application."})
            else:
                handler._send_response(503, {"error": "EventBus service is not available to process the restart signal."})
        except Exception as e:
            self.logger(f"Restart via API failed: {e}", "CRITICAL")
            handler._send_response(500, {"error": f"Internal server error during restart signal: {e}"})
