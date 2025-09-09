#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\preset_routes.py
# JUMLAH BARIS : 86
#######################################################################

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Any
class PresetSaveRequest(BaseModel):
    name: str
    workflow_data: Dict[str, Any]
router = APIRouter(
    tags=["Presets"]
)
@router.get("/presets", response_model=List[dict])
async def handle_get_presets(request: Request):
    preset_manager = request.app.service_instance.preset_manager
    if not preset_manager:
        raise HTTPException(status_code=503, detail="PresetManager service is unavailable.")
    preset_list = preset_manager.get_preset_list()
    loc = request.app.service_instance.loc
    core_files = request.app.service_instance.core_component_ids
    response_data = []
    for name in preset_list:
        response_data.append({
            "id": name, "name": name, "version": "N/A", "is_paused": False,
            "description": loc.get('marketplace_preset_desc') if loc else 'Workflow Preset File',
            "is_core": name in core_files, "tier": "N/A"
        })
    return response_data
@router.get("/presets/{preset_name}", response_model=Dict[str, Any])
async def handle_get_preset_data(preset_name: str, request: Request):
    preset_manager = request.app.service_instance.preset_manager
    if not preset_manager:
        raise HTTPException(status_code=503, detail="PresetManager service is unavailable.")
    preset_data = preset_manager.get_preset_data(preset_name)
    if preset_data:
        return preset_data
    else:
        raise HTTPException(status_code=404, detail=f"Preset '{preset_name}' not found.")
@router.post("/presets", status_code=201)
async def handle_post_presets(request: Request, body: PresetSaveRequest):
    preset_manager = request.app.service_instance.preset_manager
    if not preset_manager:
        raise HTTPException(status_code=503, detail="PresetManager service is unavailable.")
    if preset_manager.save_preset(body.name, body.workflow_data):
        return {"status": "success", "message": f"Preset '{body.name}' created/updated."}
    else:
        raise HTTPException(status_code=500, detail=f"Failed to save preset '{body.name}'.")
@router.delete("/presets/{preset_name}", status_code=204)
async def handle_delete_preset(preset_name: str, request: Request):
    preset_manager = request.app.service_instance.preset_manager
    if not preset_manager:
        raise HTTPException(status_code=503, detail="PresetManager service is unavailable.")
    success = preset_manager.delete_preset(preset_name)
    if not success:
        raise HTTPException(status_code=404, detail=f"Preset '{preset_name}' not found or could not be deleted.")
    return None
@router.get("/presets/{preset_name}/versions", response_model=List[dict])
async def handle_get_preset_versions(preset_name: str, request: Request):
    preset_manager = request.app.service_instance.preset_manager
    if not preset_manager:
        raise HTTPException(status_code=503, detail="PresetManager service is unavailable.")
    return preset_manager.get_preset_versions(preset_name)
@router.get("/presets/{preset_name}/versions/{version_filename}", response_model=Dict[str, Any])
async def handle_get_preset_version_data(preset_name: str, version_filename: str, request: Request):
    preset_manager = request.app.service_instance.preset_manager
    if not preset_manager:
        raise HTTPException(status_code=503, detail="PresetManager service is unavailable.")
    version_data = preset_manager.load_preset_version(preset_name, version_filename)
    if version_data:
        return version_data
    else:
        raise HTTPException(status_code=404, detail=f"Version '{version_filename}' for preset '{preset_name}' not found.")
@router.delete("/presets/{preset_name}/versions/{version_filename}")
async def handle_delete_preset_version(preset_name: str, version_filename: str, request: Request):
    preset_manager = request.app.service_instance.preset_manager
    if not preset_manager:
        raise HTTPException(status_code=503, detail="PresetManager service is unavailable.")
    success = preset_manager.delete_preset_version(preset_name, version_filename)
    if success:
        return {"status": "success", "message": f"Version '{version_filename}' deleted."}
    else:
        raise HTTPException(status_code=404, detail=f"Could not delete version '{version_filename}'.")
