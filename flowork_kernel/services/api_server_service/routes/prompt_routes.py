#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\prompt_routes.py
# JUMLAH BARIS : 77
#######################################################################

from .base_api_route import BaseApiRoute
class PromptRoutes(BaseApiRoute):
    """
    (REFACTORED) Manages API routes for Prompt Templates.
    This class is now a thin layer that delegates all logic to the PromptManagerService.
    (HARDENED) Added checks to handle cases where the service might fail to load and return None.
    """
    def register_routes(self):
        return {
            'GET /api/v1/prompts': self.get_all_prompts,
            'POST /api/v1/prompts': self.create_prompt,
            'GET /api/v1/prompts/{prompt_id}': self.get_prompt_by_id,
            'PUT /api/v1/prompts/{prompt_id}': self.update_prompt,
            'DELETE /api/v1/prompts/{prompt_id}': self.delete_prompt
        }
    def get_all_prompts(self, handler, **kwargs):
        prompt_manager = self.service_instance.prompt_manager_service
        if not prompt_manager:
            return handler._send_response(503, {"error": "PromptManagerService is not available."})
        result = prompt_manager.get_all_prompts()
        if result is not None:
            handler._send_response(200, result)
        else:
            handler._send_response(500, {"error": "Service call to get all prompts failed."})
    def get_prompt_by_id(self, handler, prompt_id):
        prompt_manager = self.service_instance.prompt_manager_service
        if not prompt_manager:
            return handler._send_response(503, {"error": "PromptManagerService is not available."})
        result = prompt_manager.get_prompt(prompt_id)
        if result:
            handler._send_response(200, result)
        else:
            handler._send_response(404, {"error": "Prompt not found or service call failed."})
    def create_prompt(self, handler):
        prompt_manager = self.service_instance.prompt_manager_service
        if not prompt_manager:
            return handler._send_response(503, {"error": "PromptManagerService is not available."})
        body = handler._get_json_body()
        if not body: return
        result = prompt_manager.create_prompt(body)
        if result and 'error' in result:
            handler._send_response(400, result)
        elif result:
            handler._send_response(201, result)
        else:
            handler._send_response(500, {"error": "Service call to create prompt failed."})
    def update_prompt(self, handler, prompt_id):
        prompt_manager = self.service_instance.prompt_manager_service
        if not prompt_manager:
            return handler._send_response(503, {"error": "PromptManagerService is not available."})
        body = handler._get_json_body()
        if not body: return
        result = prompt_manager.update_prompt(prompt_id, body)
        if result and 'error' in result:
            handler._send_response(400, result)
        elif result:
            handler._send_response(200, result)
        else:
            handler._send_response(500, {"error": "Service call to update prompt failed."})
    def delete_prompt(self, handler, prompt_id):
        prompt_manager = self.service_instance.prompt_manager_service
        if not prompt_manager:
            return handler._send_response(503, {"error": "PromptManagerService is not available."})
        result = prompt_manager.delete_prompt(prompt_id)
        if result and 'error' in result:
            handler._send_response(404, result)
        elif result:
            handler._send_response(200, result)
        else:
            handler._send_response(500, {"error": "Service call to delete prompt failed."})
