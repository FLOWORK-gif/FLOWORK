#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\settings_routes.py
# JUMLAH BARIS : 27
#######################################################################

from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any
router = APIRouter(
    tags=["Settings"]
)
@router.get("/settings", response_model=Dict[str, Any])
async def handle_get_settings(request: Request):
    loc = request.app.service_instance.loc
    if not loc:
        raise HTTPException(status_code=503, detail="LocalizationManager service is unavailable.")
    return loc._settings_cache
@router.patch("/settings")
async def handle_patch_settings(request: Request, settings_data: Dict[str, Any]):
    loc = request.app.service_instance.loc
    if not loc:
        raise HTTPException(status_code=503, detail="LocalizationManager service is unavailable.")
    current_settings = loc._settings_cache.copy()
    current_settings.update(settings_data)
    loc._save_settings(current_settings)
    return {"status": "success", "message": "Settings updated."}
