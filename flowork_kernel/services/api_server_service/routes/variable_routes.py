#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\variable_routes.py
# JUMLAH BARIS : 55
#######################################################################

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
class VariableUpdateRequest(BaseModel):
    value: Any
    is_secret: bool
    is_enabled: bool = True
    mode: Optional[str] = None
class VariableStatePatch(BaseModel):
    enabled: bool
router = APIRouter(
    tags=["Variables"]
)
@router.get("/variables", response_model=List[dict])
async def handle_get_variables(request: Request):
    variable_manager = request.app.service_instance.variable_manager
    if not variable_manager:
        raise HTTPException(status_code=503, detail="VariableManager service is unavailable.")
    return variable_manager.get_all_variables_for_api()
@router.put("/variables/{variable_name}")
async def handle_put_variables(variable_name: str, request: Request, body: VariableUpdateRequest):
    variable_manager = request.app.service_instance.variable_manager
    if not variable_manager:
        raise HTTPException(status_code=503, detail="VariableManager service is unavailable.")
    try:
        variable_manager.set_variable(variable_name, body.value, body.is_secret, body.is_enabled, mode=body.mode)
        return {"status": "success", "message": f"Variable '{variable_name}' saved."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.patch("/variables/{variable_name}/state")
async def handle_patch_variable_state(variable_name: str, request: Request, body: VariableStatePatch):
    variable_manager = request.app.service_instance.variable_manager
    if not variable_manager:
        raise HTTPException(status_code=503, detail="VariableManager service is unavailable.")
    success = variable_manager.set_variable_enabled_state(variable_name, body.enabled)
    if success:
        action = "enabled" if body.enabled else "disabled"
        return {"status": "success", "message": f"Variable '{variable_name}' has been {action}."}
    else:
        raise HTTPException(status_code=404, detail=f"Variable '{variable_name}' not found.")
@router.delete("/variables/{variable_name}", status_code=204)
async def handle_delete_variables(variable_name: str, request: Request):
    variable_manager = request.app.service_instance.variable_manager
    if not variable_manager:
        raise HTTPException(status_code=503, detail="VariableManager service is unavailable.")
    if not variable_manager.delete_variable(variable_name):
        raise HTTPException(status_code=404, detail=f"Variable '{variable_name}' not found.")
    return None
