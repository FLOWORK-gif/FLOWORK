#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\training_routes.py
# JUMLAH BARIS : 45
#######################################################################

from .base_api_route import BaseApiRoute
class TrainingRoutes(BaseApiRoute):
    """
    Manages API routes for starting and monitoring AI fine-tuning jobs.
    """
    def register_routes(self):
        return {
            "POST /api/v1/training/start": self.handle_start_training_job,
            "GET /api/v1/training/status/{job_id}": self.handle_get_training_job_status,
        }
    def handle_start_training_job(self, handler):
        training_service = self.service_instance.training_service
        if not training_service:
            return handler._send_response(503, {"error": "AITrainingService is not available due to license restrictions."})
        body = handler._get_json_body()
        if not body: return
        required_keys = ['base_model_id', 'dataset_name', 'new_model_name', 'training_args']
        if not all(key in body for key in required_keys):
            return handler._send_response(400, {"error": f"Request body must contain: {', '.join(required_keys)}"})
        result = training_service.start_fine_tuning_job(
            body['base_model_id'],
            body['dataset_name'],
            body['new_model_name'],
            body['training_args']
        )
        if "error" in result:
            handler._send_response(409, result)
        else:
            handler._send_response(202, result)
    def handle_get_training_job_status(self, handler, job_id=None):
        training_service = self.service_instance.training_service
        if not training_service:
            return handler._send_response(503, {"error": "AITrainingService is not available due to license restrictions."})
        status = training_service.get_job_status(job_id)
        if "error" in status:
            handler._send_response(404, status)
        else:
            handler._send_response(200, status)
