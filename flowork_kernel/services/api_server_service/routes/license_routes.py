#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\license_routes.py
# JUMLAH BARIS : 48
#######################################################################

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any
class LicenseActivateRequest(BaseModel):
    license_content: Dict[str, Any]
class LicenseValidateRequest(BaseModel):
    license_key: str
    machine_id: str
router = APIRouter(
    tags=["License"]
)
@router.post("/license/activate")
async def handle_activate_license(request: Request, body: LicenseActivateRequest):
    license_manager = request.app.service_instance.kernel.get_service("license_manager_service")
    if not license_manager:
        raise HTTPException(status_code=503, detail="LicenseManager service is not available.")
    success, message = license_manager.activate_license_on_server(body.license_content)
    if success:
        return {"status": "success", "message": message}
    else:
        raise HTTPException(status_code=400, detail=message)
@router.post("/license/deactivate")
async def handle_deactivate_license(request: Request):
    license_manager = request.app.service_instance.kernel.get_service("license_manager_service")
    if not license_manager:
        raise HTTPException(status_code=503, detail="LicenseManager service is not available.")
    success, message = license_manager.deactivate_license_on_server()
    if success:
        return {"status": "success", "message": message}
    else:
        raise HTTPException(status_code=400, detail=message)
@router.post("/license/validate")
async def handle_validate_license(request: Request, body: LicenseValidateRequest):
    license_manager = request.app.service_instance.kernel.get_service("license_manager_service")
    if not license_manager:
        raise HTTPException(status_code=503, detail="LicenseManager service is not available.")
    success, message = license_manager.validate_local_license_online(body.license_key, body.machine_id)
    if success:
        return {"status": "success", "message": message}
    else:
        raise HTTPException(status_code=403, detail=message) # 403 Forbidden is more appropriate
