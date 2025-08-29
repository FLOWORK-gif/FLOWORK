#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\component_routes.py
# JUMLAH BARIS : 193
#######################################################################

from .base_api_route import BaseApiRoute
import os
import cgi
import zipfile
import tempfile
import shutil
class ComponentRoutes(BaseApiRoute):
    """
    Manages API routes for component (modules, plugins, widgets, etc.) lifecycle.
    """
    def register_routes(self):
        return {
            "GET /api/v1/modules": self.handle_get_modules,
            "GET /api/v1/modules/{item_id}": self.handle_get_modules,
            "POST /api/v1/modules/install": self.handle_install_modules,
            "PATCH /api/v1/modules/{item_id}/state": self.handle_patch_modules_state,
            "DELETE /api/v1/modules/{item_id}": self.handle_delete_modules,
            "GET /api/v1/plugins": self.handle_get_plugins,
            "GET /api/v1/plugins/{item_id}": self.handle_get_plugins,
            "POST /api/v1/plugins/install": self.handle_install_plugins,
            "PATCH /api/v1/plugins/{item_id}/state": self.handle_patch_plugins_state,
            "DELETE /api/v1/plugins/{item_id}": self.handle_delete_plugins,
            "GET /api/v1/widgets": self.handle_get_widgets,
            "GET /api/v1/widgets/{item_id}": self.handle_get_widgets,
            "POST /api/v1/widgets/install": self.handle_install_widgets,
            "PATCH /api/v1/widgets/{item_id}/state": self.handle_patch_widgets_state,
            "DELETE /api/v1/widgets/{item_id}": self.handle_delete_widgets,
            "GET /api/v1/triggers": self.handle_get_triggers,
            "GET /api/v1/triggers/{item_id}": self.handle_get_triggers,
            "POST /api/v1/triggers/install": self.handle_install_triggers,
            "PATCH /api/v1/triggers/{item_id}/state": self.handle_patch_triggers_state,
            "DELETE /api/v1/triggers/{item_id}": self.handle_delete_triggers,
            "GET /api/v1/ai_providers": self.handle_get_ai_providers,
            "GET /api/v1/ai_providers/{item_id}": self.handle_get_ai_providers,
            "POST /api/v1/ai_providers/install": self.handle_install_ai_providers,
            "PATCH /api/v1/ai_providers/{item_id}/state": self.handle_patch_ai_providers_state,
            "DELETE /api/v1/ai_providers/{item_id}": self.handle_delete_ai_providers,
        }
    def _get_manager_for_type(self, resource_type):
        """Helper method to get the correct manager service based on resource type."""
        manager_map = {
            "modules": "module_manager_service",
            "plugins": "module_manager_service",
            "widgets": "widget_manager_service",
            "triggers": "trigger_manager_service",
            "ai_providers": "ai_provider_manager_service"
        }
        manager_name = manager_map.get(resource_type)
        if not manager_name:
            return None, f"Resource type '{resource_type}' is invalid."
        if manager_name == "module_manager_service":
            manager = self.service_instance.module_manager_service
        elif manager_name == "widget_manager_service":
            manager = self.service_instance.widget_manager_service
        elif manager_name == "trigger_manager_service":
            manager = self.service_instance.trigger_manager_service
        elif manager_name == "ai_provider_manager_service":
            manager = self.service_instance.ai_provider_manager_service
        else:
            manager = None
        if not manager:
            return None, f"{manager_name} service is unavailable, possibly due to license restrictions."
        return manager, None
    def _get_components(self, handler, resource_type, item_id=None):
        manager, error = self._get_manager_for_type(resource_type)
        if error: return handler._send_response(503, {"error": error})
        core_files = self.service_instance.core_component_ids
        items_attr_map = {
            "module_manager_service": "loaded_modules", "widget_manager_service": "loaded_widgets",
            "trigger_manager_service": "loaded_triggers", "ai_provider_manager_service": "loaded_providers"
        }
        items_attr_name = items_attr_map.get(manager.service_id)
        if not items_attr_name:
            return handler._send_response(500, {"error": f"Unknown items attribute for service '{manager.service_id}'"})
        items = getattr(manager, items_attr_name, {})
        if item_id:
            if item_id in items:
                item_data = items[item_id]
                manifest = item_data.get('manifest', {}) if isinstance(item_data, dict) else (item_data.get_manifest() if hasattr(item_data, 'get_manifest') else {})
                response_data = { "id": item_id, "name": manifest.get('name', item_id), "version": manifest.get('version', 'N/A'), "is_paused": isinstance(item_data, dict) and item_data.get('is_paused', False), "description": manifest.get('description', ''), "manifest": manifest }
                handler._send_response(200, response_data)
            else:
                handler._send_response(404, {"error": f"Component '{item_id}' not found in '{resource_type}'."})
            return
        response_data = []
        for item_id_loop, item_data in items.items():
            is_paused = False
            manifest = {}
            tier = 'N/A'
            if manager.service_id == "ai_provider_manager_service":
                if hasattr(item_data, 'get_manifest'):
                    manifest = item_data.get_manifest()
                is_paused = False
                if hasattr(item_data, 'TIER'):
                    tier = getattr(item_data, 'TIER', 'free').lower()
            else:
                manifest = item_data.get('manifest', {})
                is_paused = item_data.get('is_paused', False)
                tier = manifest.get('tier', 'free')
            if resource_type == 'modules' and manifest.get('type') not in ['LOGIC', 'ACTION', 'CONTROL_FLOW']: continue
            if resource_type == 'plugins' and manifest.get('type') not in ['PLUGIN', 'SERVICE']: continue
            is_core = item_id_loop in core_files
            response_data.append({
                "id": item_id_loop, "name": manifest.get('name', item_id_loop),
                "version": manifest.get('version', 'N/A'), "is_paused": is_paused,
                "description": manifest.get('description', ''), "is_core": is_core,
                "tier": tier
            })
        handler._send_response(200, response_data)
    def _install_component(self, handler, resource_type):
        try:
            form = cgi.FieldStorage(fp=handler.rfile, headers=handler.headers, environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': handler.headers['Content-Type']})
            if 'file' not in form: return handler._send_response(400, {"error": "File upload is missing. Use 'file' as the form field name."})
            file_item = form['file']
            if not file_item.filename: return handler._send_response(400, {"error": "Filename is missing."})
            manager, error = self._get_manager_for_type(resource_type)
            if error: return handler._send_response(503, {"error": error})
            success, message = manager.install_component(file_item.file)
            if success:
                handler._send_response(201, {"status": "success", "message": message})
            else:
                handler._send_response(400, {"error": message})
        except Exception as e:
            self.logger(f"Error processing component install for {resource_type}: {e}", "CRITICAL")
            handler._send_response(500, {"error": f"Failed to process file upload: {e}"})
    def _delete_component(self, handler, resource_type, item_id):
        sanitized_id = os.path.basename(item_id)
        if sanitized_id != item_id:
            self.logger(f"Path traversal attempt blocked. Original ID: '{item_id}', Sanitized: '{sanitized_id}'", "CRITICAL")
            handler._send_response(400, {"error": "Invalid component ID format."})
            return
        if item_id in self.service_instance.core_component_ids:
            error_msg = self.service_instance.loc.get('api_core_component_delete_error', fallback="Core components cannot be deleted.")
            return handler._send_response(403, {"error": error_msg})
        manager, error = self._get_manager_for_type(resource_type)
        if error: return handler._send_response(503, {"error": error})
        success, message = manager.uninstall_component(item_id)
        if success:
            handler._send_response(200, {"status": "success", "message": message})
        else:
            handler._send_response(404, {"error": message})
    def _patch_component_state(self, handler, resource_type, item_id):
        if item_id in self.service_instance.core_component_ids:
            error_msg = self.service_instance.loc.get('api_core_component_disable_error', fallback="Core components cannot be disabled.")
            return handler._send_response(403, {"error": error_msg})
        body = handler._get_json_body()
        if body is None or 'paused' not in body or not isinstance(body['paused'], bool):
            return handler._send_response(400, {"error": "Request body must contain a boolean 'paused' key."})
        is_paused = body['paused']
        manager, error = self._get_manager_for_type(resource_type)
        if error: return handler._send_response(503, {"error": error})
        pause_method = None
        if resource_type in ['modules', 'plugins']:
            pause_method = getattr(manager, 'set_module_paused', None)
        elif resource_type == 'widgets':
            pause_method = getattr(manager, 'set_widget_paused', None)
        elif resource_type == 'triggers':
            pause_method = getattr(manager, 'set_trigger_paused', None)
        if not pause_method:
            return handler._send_response(500, {"error": f"State management method not found on {type(manager).__name__} for '{resource_type}'."})
        success = pause_method(item_id, is_paused)
        if success:
            action = "paused" if is_paused else "resumed"
            handler._send_response(200, {"status": "success", "message": f"{resource_type.capitalize()[:-1]} '{item_id}' has been {action}."})
        else:
            handler._send_response(404, {"error": f"{resource_type.capitalize()[:-1]} '{item_id}' not found."})
    def handle_get_modules(self, handler, item_id=None): self._get_components(handler, 'modules', item_id)
    def handle_install_modules(self, handler): self._install_component(handler, 'modules')
    def handle_delete_modules(self, handler, item_id=None): self._delete_component(handler, 'modules', item_id)
    def handle_patch_modules_state(self, handler, item_id=None): self._patch_component_state(handler, 'modules', item_id)
    def handle_get_plugins(self, handler, item_id=None): self._get_components(handler, 'plugins', item_id)
    def handle_install_plugins(self, handler): self._install_component(handler, 'plugins')
    def handle_delete_plugins(self, handler, item_id=None): self._delete_component(handler, 'plugins', item_id)
    def handle_patch_plugins_state(self, handler, item_id=None): self._patch_component_state(handler, 'plugins', item_id)
    def handle_get_widgets(self, handler, item_id=None): self._get_components(handler, 'widgets', item_id)
    def handle_install_widgets(self, handler): self._install_component(handler, 'widgets')
    def handle_delete_widgets(self, handler, item_id=None): self._delete_component(handler, 'widgets', item_id)
    def handle_patch_widgets_state(self, handler, item_id=None): self._patch_component_state(handler, 'widgets', item_id)
    def handle_get_triggers(self, handler, item_id=None): self._get_components(handler, 'triggers', item_id)
    def handle_install_triggers(self, handler): self._install_component(handler, 'triggers')
    def handle_delete_triggers(self, handler, item_id=None): self._delete_component(handler, 'triggers', item_id)
    def handle_patch_triggers_state(self, handler, item_id=None): self._patch_component_state(handler, 'triggers', item_id)
    def handle_get_ai_providers(self, handler, item_id=None): self._get_components(handler, 'ai_providers', item_id)
    def handle_install_ai_providers(self, handler): self._install_component(handler, 'ai_providers')
    def handle_delete_ai_providers(self, handler, item_id=None): self._delete_component(handler, 'ai_providers', item_id)
    def handle_patch_ai_providers_state(self, handler, item_id=None): self._patch_component_state(handler, 'ai_providers', item_id)
