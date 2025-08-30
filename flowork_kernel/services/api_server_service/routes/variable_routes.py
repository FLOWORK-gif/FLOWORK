#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\variable_routes.py
# JUMLAH BARIS : 64
#######################################################################

from .base_api_route import BaseApiRoute
class VariableRoutes(BaseApiRoute):
    """
    Manages API routes for variable CRUD operations.
    """
    def register_routes(self):
        return {
            "GET /api/v1/variables": self.handle_get_variables,
            "PUT /api/v1/variables/{variable_name}": self.handle_put_variables,
            "PATCH /api/v1/variables/{variable_name}/state": self.handle_patch_variable_state,
            "DELETE /api/v1/variables/{variable_name}": self.handle_delete_variables,
        }
    def handle_get_variables(self, handler):
        variable_manager = self.service_instance.variable_manager
        if not variable_manager:
            return handler._send_response(503, {"error": "VariableManager service is unavailable."})
        all_vars = variable_manager.get_all_variables_for_api()
        handler._send_response(200, all_vars)
    def handle_put_variables(self, handler, variable_name=None):
        variable_manager = self.service_instance.variable_manager
        if not variable_manager:
            return handler._send_response(503, {"error": "VariableManager service is unavailable."})
        body = handler._get_json_body()
        if body is None: return
        value = body.get("value")
        is_secret = body.get("is_secret", False)
        is_enabled = body.get("is_enabled", True)
        mode = body.get("mode", "single")
        if value is None:
            return handler._send_response(400, {"error": "Request body must contain 'value'."})
        try:
            variable_manager.set_variable(variable_name, value, is_secret, is_enabled, mode=mode)
            handler._send_response(200, {"status": "success", "message": f"Variable '{variable_name}' saved."})
        except ValueError as e:
            handler._send_response(400, {"error": str(e)})
    def handle_patch_variable_state(self, handler, variable_name=None):
        variable_manager = self.service_instance.variable_manager
        if not variable_manager:
            return handler._send_response(503, {"error": "VariableManager service is unavailable."})
        body = handler._get_json_body()
        if body is None or 'enabled' not in body or not isinstance(body['enabled'], bool):
            return handler._send_response(400, {"error": "Request body must contain a boolean 'enabled' key."})
        is_enabled = body['enabled']
        success = variable_manager.set_variable_enabled_state(variable_name, is_enabled)
        if success:
            action = "enabled" if is_enabled else "disabled"
            handler._send_response(200, {"status": "success", "message": f"Variable '{variable_name}' has been {action}."})
        else:
            handler._send_response(404, {"error": f"Variable '{variable_name}' not found."})
    def handle_delete_variables(self, handler, variable_name=None):
        variable_manager = self.service_instance.variable_manager
        if not variable_manager:
            return handler._send_response(503, {"error": "VariableManager service is unavailable."})
        if variable_manager.delete_variable(variable_name):
            handler._send_response(204, None)
        else:
            handler._send_response(404, {"error": f"Variable '{variable_name}' not found."})
