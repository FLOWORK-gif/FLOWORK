#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\component_routes.py
# JUMLAH BARIS : 150
#######################################################################

import os
from fastapi import APIRouter, HTTPException, Request, Body, UploadFile, File
from pydantic import BaseModel
from typing import List
import shutil
import tempfile
class ComponentStateUpdate(BaseModel):
    paused: bool
router = APIRouter(
    tags=["Components"]
)
def _get_manager_for_type(request: Request, resource_type: str):
    manager_map = {
        "modules": "module_manager_service",
        "plugins": "plugin_manager_service",
        "widgets": "widget_manager_service",
        "triggers": "trigger_manager_service",
        "ai_providers": "ai_provider_manager_service"
    }
    manager_name = manager_map.get(resource_type)
    if not manager_name:
        raise HTTPException(status_code=400, detail=f"Resource type '{resource_type}' is invalid.")
    service_instance = request.app.service_instance
    manager = getattr(service_instance, manager_name, None)
    if not manager:
        raise HTTPException(status_code=503, detail=f"{manager_name} service is unavailable.")
    return manager # MODIFIED: Simply return the manager instance.
@router.get("/{resource_type}", response_model=List[dict])
async def get_components(resource_type: str, request: Request):
    manager = _get_manager_for_type(request, resource_type)
    core_files = request.app.service_instance.core_component_ids
    items_attr_map = {
        "module_manager_service": "loaded_modules",
        "plugin_manager_service": "loaded_plugins",
        "widget_manager_service": "loaded_widgets",
        "trigger_manager_service": "loaded_triggers",
        "ai_provider_manager_service": "loaded_providers"
    }
    items_attr_name = items_attr_map.get(manager.service_id)
    if not items_attr_name:
        raise HTTPException(status_code=500, detail=f"Unknown items attribute for service '{manager.service_id}'")
    items = getattr(manager, items_attr_name, {})
    response_data = []
    for item_id_loop, item_data in items.items():
        is_paused = False
        manifest = {}
        tier = 'N/A'
        if manager.service_id == "ai_provider_manager_service":
            if hasattr(item_data, 'get_manifest'):
                manifest = item_data.get_manifest()
            is_paused = False
            if hasattr(item_data, 'TIER'):
                tier = getattr(item_data, 'TIER', 'free').lower()
        else:
            manifest = item_data.get('manifest', {})
            is_paused = item_data.get('is_paused', False)
            tier = manifest.get('tier', 'free')
        is_core = item_id_loop in core_files
        response_data.append({
            "id": item_id_loop,
            "name": manifest.get('name', item_id_loop),
            "version": manifest.get('version', 'N/A'),
            "is_paused": is_paused,
            "description": manifest.get('description', ''),
            "is_core": is_core,
            "tier": tier,
            "manifest": manifest
        })
    return response_data
@router.get("/{resource_type}/{item_id}", response_model=dict)
async def get_component_by_id(resource_type: str, item_id: str, request: Request):
    manager = _get_manager_for_type(request, resource_type)
    items_attr_map = {
        "module_manager_service": "loaded_modules",
        "plugin_manager_service": "loaded_plugins",
        "widget_manager_service": "loaded_widgets",
        "trigger_manager_service": "loaded_triggers",
        "ai_provider_manager_service": "loaded_providers"
    }
    items_attr_name = items_attr_map.get(manager.service_id)
    if not items_attr_name:
         raise HTTPException(status_code=500, detail=f"Unknown items attribute for service '{manager.service_id}'")
    items = getattr(manager, items_attr_name, {})
    if item_id in items:
        item_data = items[item_id]
        manifest = item_data.get('manifest', {}) if isinstance(item_data, dict) else (item_data.get_manifest() if hasattr(item_data, 'get_manifest') else {})
        response_data = {
            "id": item_id,
            "name": manifest.get('name', item_id),
            "version": manifest.get('version', 'N/A'),
            "is_paused": isinstance(item_data, dict) and item_data.get('is_paused', False),
            "description": manifest.get('description', ''),
            "manifest": manifest
        }
        return response_data
    else:
        raise HTTPException(status_code=404, detail=f"Component '{item_id}' not found in '{resource_type}'.")
@router.post("/{resource_type}/install", status_code=201)
async def install_component(resource_type: str, request: Request, file: UploadFile = File(...)):
    manager = _get_manager_for_type(request, resource_type)
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .zip files are allowed.")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        success, message = manager.install_component(tmp_path)
        os.remove(tmp_path) # Clean up the temporary file
        if success:
            return {"status": "success", "message": message}
        else:
            raise HTTPException(status_code=400, detail=message)
    except Exception as e:
        request.app.service_instance.kernel.write_to_log(f"Error processing component install for {resource_type}: {e}", "CRITICAL") # English Log
        raise HTTPException(status_code=500, detail=f"Failed to process file upload: {e}")
@router.patch("/{resource_type}/{item_id}/state")
async def patch_component_state(resource_type: str, item_id: str, request: Request, body: ComponentStateUpdate):
    if item_id in request.app.service_instance.core_component_ids:
        raise HTTPException(status_code=403, detail="Core components cannot be disabled.")
    manager = _get_manager_for_type(request, resource_type)
    pause_method_name = f"set_{resource_type.rstrip('s')}_paused"
    pause_method = getattr(manager, pause_method_name, None)
    if not pause_method or not callable(pause_method):
        raise HTTPException(status_code=500, detail=f"State management method not found on {type(manager).__name__} for '{resource_type}'.")
    success = pause_method(item_id, body.paused)
    if success:
        action = "paused" if body.paused else "resumed"
        return {"status": "success", "message": f"{resource_type.capitalize()[:-1]} '{item_id}' has been {action}."}
    else:
        raise HTTPException(status_code=404, detail=f"{resource_type.capitalize()[:-1]} '{item_id}' not found.")
@router.delete("/{resource_type}/{item_id}", status_code=200)
async def delete_component(resource_type: str, item_id: str, request: Request):
    sanitized_id = os.path.basename(item_id)
    if sanitized_id != item_id:
        raise HTTPException(status_code=400, detail="Invalid component ID format.")
    if item_id in request.app.service_instance.core_component_ids:
        raise HTTPException(status_code=403, detail="Core components cannot be deleted.")
    manager = _get_manager_for_type(request, resource_type)
    success, message = manager.uninstall_component(item_id)
    if success:
        return {"status": "success", "message": message}
    else:
        raise HTTPException(status_code=404, detail=message)
