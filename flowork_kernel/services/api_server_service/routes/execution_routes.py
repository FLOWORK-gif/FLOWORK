#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\execution_routes.py
# JUMLAH BARIS : 70
#######################################################################

from .base_api_route import BaseApiRoute
import time
class ExecutionRoutes(BaseApiRoute):
    """
    Manages API routes for starting workflows/scans and checking job statuses.
    """
    def register_routes(self):
        return {
            "POST /api/v1/workflow/execute/{preset_name}": self.handle_workflow_execution,
            "POST /api/v1/diagnostics/execute": self.handle_scan_execution,
            "POST /api/v1/diagnostics/execute/{scanner_id}": self.handle_scan_execution,
            "GET /api/v1/workflow/status/{job_id}": self.handle_get_job_status,
            "GET /api/v1/diagnostics/status/{job_id}": self.handle_get_job_status,
        }
    def handle_workflow_execution(self, handler, preset_name=None):
        if not preset_name:
            return handler._send_response(400, {"error": "Preset name is required for execution."})
        if not self.kernel.is_tier_sufficient('basic'):
            COOLDOWN_SECONDS = 300 # 5 minutes
            state_manager = self.service_instance.state_manager
            if state_manager:
                last_call_timestamp = state_manager.get("api_last_call_timestamp_free_tier", 0)
                current_time = time.time()
                if (current_time - last_call_timestamp) < COOLDOWN_SECONDS:
                    remaining_time = int(COOLDOWN_SECONDS - (current_time - last_call_timestamp))
                    error_message = f"API call limit for Free tier. Please wait {remaining_time} seconds."
                    self.logger(error_message, "WARN")
                    return handler._send_response(429, {"status": "error", "message": error_message}) # HTTP 429 Too Many Requests
        try:
            body = handler._get_json_body()
            initial_payload = body if body is not None else {"triggered_by": "api"}
            self.logger(f"API call received to execute preset '{preset_name}'.", "INFO")
            if not self.kernel.is_tier_sufficient('basic'):
                if state_manager:
                    state_manager.set("api_last_call_timestamp_free_tier", time.time())
            job_id = self.service_instance.trigger_workflow_by_api(preset_name, initial_payload)
            if job_id:
                handler._send_response(202, {"status": "accepted", "message": f"Workflow for preset '{preset_name}' has been queued.", "job_id": job_id})
            else:
                handler._send_response(404, {"status": "error", "message": f"Preset '{preset_name}' not found."})
        except Exception as e:
            self.logger(f"Error handling API execution for '{preset_name}': {e}", "ERROR")
            handler._send_response(500, {"error": f"Internal Server Error: {e}"})
    def handle_scan_execution(self, handler, scanner_id=None):
        try:
            log_target = 'ALL' if not scanner_id else scanner_id
            self.logger(f"API call received to execute diagnostics scan for: {log_target}.", "INFO")
            job_id = self.service_instance.trigger_scan_by_api(scanner_id)
            if job_id:
                handler._send_response(202, {"status": "accepted", "message": f"System diagnostics scan for '{log_target}' has been queued.", "job_id": job_id})
            else:
                handler._send_response(500, {"status": "error", "message": "Failed to start diagnostics scan."})
        except Exception as e:
            self.logger(f"Error handling API scan execution: {e}", "ERROR")
            handler._send_response(500, {"error": f"Internal Server Error: {e}"})
    def handle_get_job_status(self, handler, job_id=None):
        if not job_id:
            return handler._send_response(400, {"error": "Job ID is required."})
        status_data = self.service_instance.get_job_status(job_id)
        if status_data:
            handler._send_response(200, status_data)
        else:
            handler._send_response(404, {"error": f"Job with ID '{job_id}' not found."})
