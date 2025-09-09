#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\system_routes.py
# JUMLAH BARIS : 100
#######################################################################

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import time
import os
class AddonUploadRequest(BaseModel):
    comp_type: str
    component_id: str
    description: str
    tier: str
router = APIRouter()
public_router = APIRouter()
@public_router.get("/status", tags=["System"])
async def handle_get_status(request: Request):
    """
    Handles the public status check endpoint. This route does not require authentication.
    """
    kernel = request.app.service_instance.kernel
    api_key = None
    if kernel and hasattr(kernel, 'get_service'):
        variable_manager = kernel.get_service("variable_manager_service")
        if variable_manager:
            api_key = variable_manager.get_variable("FLOWORK_API_KEY")
    status_info = {
        "status": "ok",
        "version": kernel.APP_VERSION,
        "timestamp": time.time(),
        "api_key": api_key
    }
    return status_info
@public_router.get("/system/connections", tags=["System"])
async def get_connection_count(request: Request):
    """
    New public endpoint to get the number of active WebSocket connections.
    """
    connection_manager = request.app.service_instance.connection_manager
    return {"active_connections": connection_manager.connection_count}
@public_router.get("/system/log", tags=["System"])
async def get_server_log(request: Request):
    """
    ADDED: New public endpoint to get the latest content of the server log file.
    """
    log_file_path = os.path.join(request.app.service_instance.kernel.logs_path, "server.log")
    try:
        if os.path.exists(log_file_path):
            with open(log_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                return {"log_content": "".join(lines[-100:])}
        return {"log_content": "Log file not found."}
    except Exception as e:
        return {"log_content": f"Error reading log file: {str(e)}"}
@router.post("/addons/upload", tags=["System"])
async def handle_addon_upload(request: Request, body: AddonUploadRequest):
    addon_service = request.app.service_instance.addon_service
    if not addon_service:
        raise HTTPException(status_code=503, detail="CommunityAddonService is not available.")
    try:
        success, result_message = addon_service.upload_component(
            body.comp_type,
            body.component_id,
            body.description,
            body.tier
        )
        if success:
            return {"status": "success", "message": result_message}
        else:
            raise HTTPException(status_code=500, detail=result_message)
    except Exception as e:
        request.app.service_instance.kernel.write_to_log(f"API Addon Upload Error: {e}", "ERROR")
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/system/actions/hot_reload", tags=["System"])
async def handle_hot_reload(request: Request):
    try:
        request.app.service_instance.kernel.hot_reload_components()
        return {"status": "success", "message": "Hot reload process initiated."}
    except Exception as e:
        request.app.service_instance.kernel.write_to_log(f"Hot reload via API failed: {e}", "CRITICAL")
        raise HTTPException(status_code=500, detail=f"Internal server error during hot reload: {e}")
@router.post("/system/actions/restart", tags=["System"])
async def handle_restart(request: Request):
    """
    Handles the API request to trigger a restart event.
    """
    try:
        kernel = request.app.service_instance.kernel
        event_bus = kernel.get_service("event_bus")
        if event_bus and hasattr(kernel, 'root') and kernel.root:
            kernel.root.after(100, lambda: event_bus.publish("RESTART_APP", {}))
            return {"status": "accepted", "message": "Restart signal sent to the application."}
        else:
            raise HTTPException(status_code=503, detail="EventBus service or UI root is not available to process the restart signal.")
    except Exception as e:
        request.app.service_instance.kernel.write_to_log(f"Restart via API failed: {e}", "CRITICAL")
        raise HTTPException(status_code=500, detail=f"Internal server error during restart signal: {e}")
