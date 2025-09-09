#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\execution_routes.py
# JUMLAH BARIS : 63
#######################################################################

from fastapi import APIRouter, HTTPException, Request
from typing import Optional, Dict, Any
import time
router = APIRouter(
    tags=["Execution"]
)
@router.post("/workflow/execute/{preset_name}", status_code=202)
async def handle_workflow_execution(preset_name: str, request: Request, payload: Optional[Dict[str, Any]] = None):
    kernel = request.app.service_instance.kernel
    if not kernel.is_tier_sufficient('basic'):
        COOLDOWN_SECONDS = 300 # 5 minutes
        state_manager = request.app.service_instance.state_manager
        if state_manager:
            last_call_timestamp = state_manager.get("api_last_call_timestamp_free_tier", 0)
            current_time = time.time()
            if (current_time - last_call_timestamp) < COOLDOWN_SECONDS:
                remaining_time = int(COOLDOWN_SECONDS - (current_time - last_call_timestamp))
                error_message = f"API call limit for Free tier. Please wait {remaining_time} seconds."
                raise HTTPException(status_code=429, detail=error_message)
    try:
        initial_payload = payload if payload is not None else {"triggered_by": "api"}
        kernel.write_to_log(f"API call received to execute preset '{preset_name}'.", "INFO") # English Log
        if not kernel.is_tier_sufficient('basic'):
            state_manager = request.app.service_instance.state_manager
            if state_manager:
                state_manager.set("api_last_call_timestamp_free_tier", time.time())
        job_id = request.app.service_instance.trigger_workflow_by_api(preset_name, initial_payload)
        if job_id:
            return {"status": "accepted", "message": f"Workflow for preset '{preset_name}' has been queued.", "job_id": job_id}
        else:
            raise HTTPException(status_code=404, detail=f"Preset '{preset_name}' not found.")
    except Exception as e:
        kernel.write_to_log(f"Error handling API execution for '{preset_name}': {e}", "ERROR") # English Log
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
@router.post("/diagnostics/execute/{scanner_id}", status_code=202)
@router.post("/diagnostics/execute", status_code=202)
async def handle_scan_execution(request: Request, scanner_id: Optional[str] = None):
    try:
        log_target = 'ALL' if not scanner_id else scanner_id
        request.app.service_instance.kernel.write_to_log(f"API call received to execute diagnostics scan for: {log_target}.", "INFO") # English Log
        job_id = request.app.service_instance.trigger_scan_by_api(scanner_id)
        if job_id:
            return {"status": "accepted", "message": f"System diagnostics scan for '{log_target}' has been queued.", "job_id": job_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to start diagnostics scan.")
    except Exception as e:
        request.app.service_instance.kernel.write_to_log(f"Error handling API scan execution: {e}", "ERROR") # English Log
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
@router.get("/workflow/status/{job_id}")
@router.get("/diagnostics/status/{job_id}")
async def handle_get_job_status(job_id: str, request: Request):
    status_data = request.app.service_instance.get_job_status(job_id)
    if status_data:
        return status_data
    else:
        raise HTTPException(status_code=404, detail=f"Job with ID '{job_id}' not found.")
