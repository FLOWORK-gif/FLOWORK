#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\preset_routes.py
# JUMLAH BARIS : 89
#######################################################################

from .base_api_route import BaseApiRoute
class PresetRoutes(BaseApiRoute):
    """
    Manages API routes for preset CRUD and versioning.
    """
    def register_routes(self):
        return {
            "GET /api/v1/presets": self.handle_get_presets,
            "GET /api/v1/presets/{preset_name}": self.handle_get_presets,
            "POST /api/v1/presets": self.handle_post_presets,
            "DELETE /api/v1/presets/{preset_name}": self.handle_delete_preset,
            "GET /api/v1/presets/{preset_name}/versions": self.handle_get_preset_versions,
            "GET /api/v1/presets/{preset_name}/versions/{version_filename}": self.handle_get_preset_versions,
            "DELETE /api/v1/presets/{preset_name}/versions/{version_filename}": self.handle_delete_preset_version,
        }
    def handle_get_presets(self, handler, preset_name=None):
        preset_manager = self.service_instance.preset_manager
        if not preset_manager:
            return handler._send_response(503, {"error": "PresetManager service is unavailable."})
        if preset_name:
            preset_data = preset_manager.get_preset_data(preset_name)
            if preset_data:
                handler._send_response(200, preset_data)
            else:
                handler._send_response(404, {"error": f"Preset '{preset_name}' not found."})
        else:
            preset_list = preset_manager.get_preset_list()
            loc = self.service_instance.loc
            core_files = self.service_instance.core_component_ids
            response_data = []
            for name in preset_list:
                response_data.append({
                    "id": name, "name": name, "version": "N/A", "is_paused": False,
                    "description": loc.get('marketplace_preset_desc', fallback='Workflow Preset File') if loc else 'Workflow Preset File',
                    "is_core": name in core_files, "tier": "N/A"
                })
            handler._send_response(200, response_data)
    def handle_post_presets(self, handler):
        preset_manager = self.service_instance.preset_manager
        if not preset_manager:
            return handler._send_response(503, {"error": "PresetManager service is unavailable."})
        body = handler._get_json_body()
        if body is None: return
        preset_name = body.get("name")
        workflow_data = body.get("workflow_data")
        if not preset_name or not workflow_data:
            return handler._send_response(400, {"error": "Request body must contain 'name' and 'workflow_data'."})
        if preset_manager.save_preset(preset_name, workflow_data):
            handler._send_response(201, {"status": "success", "message": f"Preset '{preset_name}' created/updated."})
        else:
            handler._send_response(500, {"error": f"Failed to save preset '{preset_name}'."})
    def handle_delete_preset(self, handler, preset_name=None):
        preset_manager = self.service_instance.preset_manager
        if not preset_manager:
            return handler._send_response(503, {"error": "PresetManager service is unavailable."})
        success = preset_manager.delete_preset(preset_name)
        if success:
            handler._send_response(204, None)
        else:
            handler._send_response(404, {"error": f"Preset '{preset_name}' not found or could not be deleted."})
    def handle_get_preset_versions(self, handler, preset_name=None, version_filename=None):
        preset_manager = self.service_instance.preset_manager
        if not preset_manager:
            return handler._send_response(503, {"error": "PresetManager service is unavailable."})
        if version_filename:
            version_data = preset_manager.load_preset_version(preset_name, version_filename)
            if version_data:
                handler._send_response(200, version_data)
            else:
                handler._send_response(404, {"error": f"Version '{version_filename}' for preset '{preset_name}' not found."})
        else:
            versions_list = preset_manager.get_preset_versions(preset_name)
            handler._send_response(200, versions_list)
    def handle_delete_preset_version(self, handler, preset_name=None, version_filename=None):
        preset_manager = self.service_instance.preset_manager
        if not preset_manager:
            return handler._send_response(503, {"error": "PresetManager service is unavailable."})
        success = preset_manager.delete_preset_version(preset_name, version_filename)
        if success:
            handler._send_response(200, {"status": "success", "message": f"Version '{version_filename}' deleted."})
        else:
            handler._send_response(404, {"error": f"Could not delete version '{version_filename}'."})
