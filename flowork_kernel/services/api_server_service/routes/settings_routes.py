#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\settings_routes.py
# JUMLAH BARIS : 32
#######################################################################

from .base_api_route import BaseApiRoute
class SettingsRoutes(BaseApiRoute):
    """
    Manages API routes for application settings.
    """
    def register_routes(self):
        return {
            "GET /api/v1/settings": self.handle_get_settings,
            "PATCH /api/v1/settings": self.handle_patch_settings,
        }
    def handle_get_settings(self, handler):
        loc = self.service_instance.loc
        if not loc:
            return handler._send_response(503, {"error": "LocalizationManager service is unavailable."})
        handler._send_response(200, loc._settings_cache)
    def handle_patch_settings(self, handler):
        loc = self.service_instance.loc
        if not loc:
            return handler._send_response(503, {"error": "LocalizationManager service is unavailable."})
        body = handler._get_json_body()
        if body is None: return
        current_settings = loc._settings_cache.copy()
        current_settings.update(body)
        loc._save_settings(current_settings)
        handler._send_response(200, {"status": "success", "message": "Settings updated."})
