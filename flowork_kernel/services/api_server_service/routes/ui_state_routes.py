#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\ui_state_routes.py
# JUMLAH BARIS : 61
#######################################################################

from .base_api_route import BaseApiRoute
class UiStateRoutes(BaseApiRoute):
    """
    Manages API routes for dashboard layouts and tab sessions.
    """
    def register_routes(self):
        return {
            "GET /api/v1/uistate/dashboards/{tab_id}": self.handle_get_dashboard_layout,
            "POST /api/v1/uistate/dashboards/{tab_id}": self.handle_post_dashboard_layout,
            "GET /api/v1/uistate/session/tabs": self.handle_get_session_tabs,
            "POST /api/v1/uistate/session/tabs": self.handle_post_session_tabs,
            "POST /api/v1/ui/actions/open_tab": self.handle_ui_action_open_tab,
        }
    def handle_get_dashboard_layout(self, handler, tab_id=None):
        state_manager = self.service_instance.state_manager
        if not state_manager:
            return handler._send_response(503, {"error": "StateManager service is unavailable."})
        layout_key = f"dashboard_layout_{tab_id}"
        layout_data = state_manager.get(layout_key, {})
        handler._send_response(200, layout_data)
    def handle_post_dashboard_layout(self, handler, tab_id=None):
        state_manager = self.service_instance.state_manager
        if not state_manager:
            return handler._send_response(503, {"error": "StateManager service is unavailable."})
        body = handler._get_json_body()
        if body is None: return
        layout_key = f"dashboard_layout_{tab_id}"
        state_manager.set(layout_key, body)
        handler._send_response(200, {"status": "success", "message": f"Layout for dashboard '{tab_id}' saved."})
    def handle_get_session_tabs(self, handler):
        state_manager = self.service_instance.state_manager
        if not state_manager:
            return handler._send_response(503, {"error": "StateManager service is unavailable."})
        open_tabs = state_manager.get("open_tabs", [])
        handler._send_response(200, open_tabs)
    def handle_post_session_tabs(self, handler):
        state_manager = self.service_instance.state_manager
        if not state_manager:
            return handler._send_response(503, {"error": "StateManager service is unavailable."})
        body = handler._get_json_body()
        if body is None: return
        state_manager.set("open_tabs", body)
        handler._send_response(200, {"status": "success", "message": "Tab session saved."})
    def handle_ui_action_open_tab(self, handler):
        body = handler._get_json_body()
        if body is None: return
        tab_key = body.get("tab_key")
        if not tab_key:
            return handler._send_response(400, {"error": "Request body must contain 'tab_key'."})
        tab_manager = self.kernel.get_service("tab_manager_service")
        if not tab_manager:
            return handler._send_response(503, {"error": "UI Tab Manager service is not available."})
        self.kernel.root.after(0, tab_manager.open_managed_tab, tab_key)
        handler._send_response(200, {"status": "success", "message": f"Request to open tab '{tab_key}' sent to UI."})
