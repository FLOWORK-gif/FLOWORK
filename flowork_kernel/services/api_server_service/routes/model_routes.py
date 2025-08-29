#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\model_routes.py
# JUMLAH BARIS : 122
#######################################################################

from .base_api_route import BaseApiRoute
import os
import cgi
import tempfile
import shutil
class ModelRoutes(BaseApiRoute):
    """
    Manages API routes for model conversion, uploading, and listing.
    """
    def register_routes(self):
        return {
            "POST /api/v1/models/convert": self.handle_post_model_conversion,
            "GET /api/v1/models/convert/status/{job_id}": self.handle_get_conversion_status,
            "POST /api/v1/models/upload": self.handle_model_upload,
            "GET /api/v1/ai_models": self.handle_get_local_ai_models,
            "POST /api/v1/models/requantize": self.handle_post_model_requantize,
        }
    def handle_post_model_requantize(self, handler):
        converter_service = self.service_instance.converter_service
        if not converter_service:
            return handler._send_response(503, {"error": "ModelConverterService is not available due to license restrictions."}) # English Hardcode
        body = handler._get_json_body()
        if not body: return
        required_keys = ['source_gguf_path', 'output_gguf_name']
        if not all(key in body for key in required_keys):
            return handler._send_response(400, {"error": f"Request body must contain: {', '.join(required_keys)}"}) # English Hardcode
        result = converter_service.start_requantize_job(
            body['source_gguf_path'],
            body['output_gguf_name'],
            body.get('quantize_method', 'Q4_K_M')
        )
        if "error" in result:
            handler._send_response(409, result)
        else:
            handler._send_response(202, result)
    def handle_post_model_conversion(self, handler):
        converter_service = self.service_instance.converter_service
        if not converter_service:
            return handler._send_response(503, {"error": "ModelConverterService is not available due to license restrictions."})
        body = handler._get_json_body()
        if not body: return
        required_keys = ['source_model_folder', 'output_gguf_name']
        if not all(key in body for key in required_keys):
            return handler._send_response(400, {"error": f"Request body must contain: {', '.join(required_keys)}"})
        result = converter_service.start_conversion_job(
            body['source_model_folder'],
            body['output_gguf_name'],
            body.get('quantize_method', 'Q4_K_M')
        )
        if "error" in result:
            handler._send_response(409, result)
        else:
            handler._send_response(202, result)
    def handle_get_conversion_status(self, handler, job_id=None):
        converter_service = self.service_instance.converter_service
        if not converter_service:
            return handler._send_response(503, {"error": "ModelConverterService is not available due to license restrictions."})
        status = converter_service.get_job_status(job_id)
        if "error" in status:
            handler._send_response(404, status)
        else:
            handler._send_response(200, status)
    def handle_model_upload(self, handler):
        addon_service = self.service_instance.addon_service
        if not addon_service:
            return handler._send_response(503, {"error": "CommunityAddonService is not available."})
        try:
            form = cgi.FieldStorage(
                fp=handler.rfile,
                headers=handler.headers,
                environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': handler.headers['Content-Type']}
            )
            if 'file' not in form:
                return handler._send_response(400, {"error": "File upload is missing. Use 'file' as the form field name."})
            file_item = form['file']
            description = form.getvalue("description", "")
            tier = form.getvalue("tier", "pro")
            model_id = form.getvalue("model_id", "unknown_model")
            if not file_item.filename:
                return handler._send_response(400, {"error": "Filename is missing from upload."})
            with tempfile.NamedTemporaryFile(delete=False, suffix=".gguf") as tmp_file:
                shutil.copyfileobj(file_item.file, tmp_file)
                temp_model_path = tmp_file.name
            success, message = addon_service.upload_model(temp_model_path, model_id, description, tier)
            os.remove(temp_model_path)
            if success:
                handler._send_response(200, {"status": "success", "message": message})
            else:
                handler._send_response(500, {"error": message})
        except Exception as e:
            self.logger(f"API Model Upload Error: {e}", "CRITICAL")
            handler._send_response(500, {"error": f"Failed to process model upload: {e}"})
    def handle_get_local_ai_models(self, handler):
        models_path = os.path.join(self.kernel.project_root_path, "ai_models")
        try:
            if not os.path.isdir(models_path):
                os.makedirs(models_path)
                return handler._send_response(200, [])
            gguf_files = [f for f in os.listdir(models_path) if f.endswith(".gguf")]
            response_data = []
            for filename in gguf_files:
                model_id = filename.replace('.gguf', '')
                response_data.append({
                    "id": model_id,
                    "name": model_id,
                    "version": "N/A",
                    "is_paused": False,
                    "description": f"Local GGUF model file: {filename}",
                    "is_core": False,
                    "tier": "pro"
                })
            handler._send_response(200, response_data)
        except Exception as e:
            self.logger(f"Error listing local AI models: {e}", "ERROR")
            handler._send_response(500, {"error": f"Could not list local AI models: {e}"})
