#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\ui_state_routes.py
# JUMLAH BARIS : 56
#######################################################################

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Any
class OpenTabRequest(BaseModel):
    tab_key: str
router = APIRouter(
    tags=["UI State"]
)
@router.get("/uistate/dashboards/{tab_id}", response_model=Dict[str, Any])
async def handle_get_dashboard_layout(tab_id: str, request: Request):
    state_manager = request.app.service_instance.state_manager
    if not state_manager:
        raise HTTPException(status_code=503, detail="StateManager service is unavailable.")
    layout_key = f"dashboard_layout_{tab_id}"
    layout_data = state_manager.get(layout_key, {})
    return layout_data
@router.post("/uistate/dashboards/{tab_id}")
async def handle_post_dashboard_layout(tab_id: str, request: Request, layout_data: Dict[str, Any]):
    state_manager = request.app.service_instance.state_manager
    if not state_manager:
        raise HTTPException(status_code=503, detail="StateManager service is unavailable.")
    layout_key = f"dashboard_layout_{tab_id}"
    state_manager.set(layout_key, layout_data)
    return {"status": "success", "message": f"Layout for dashboard '{tab_id}' saved."}
@router.get("/uistate/session/tabs", response_model=List[dict])
async def handle_get_session_tabs(request: Request):
    state_manager = request.app.service_instance.state_manager
    if not state_manager:
        raise HTTPException(status_code=503, detail="StateManager service is unavailable.")
    open_tabs = state_manager.get("open_tabs", [])
    return open_tabs
@router.post("/uistate/session/tabs")
async def handle_post_session_tabs(request: Request, tabs_data: List[Dict[str, Any]]):
    state_manager = request.app.service_instance.state_manager
    if not state_manager:
        raise HTTPException(status_code=503, detail="StateManager service is unavailable.")
    state_manager.set("open_tabs", tabs_data)
    return {"status": "success", "message": "Tab session saved."}
@router.post("/ui/actions/open_tab")
async def handle_ui_action_open_tab(request: Request, body: OpenTabRequest):
    kernel = request.app.service_instance.kernel
    tab_manager = kernel.get_service("tab_manager_service")
    if not tab_manager:
        raise HTTPException(status_code=503, detail="UI Tab Manager service is not available.")
    if hasattr(kernel, 'root') and kernel.root:
        kernel.root.after(0, tab_manager.open_managed_tab, body.tab_key)
        return {"status": "success", "message": f"Request to open tab '{body.tab_key}' sent to UI."}
    else:
        raise HTTPException(status_code=503, detail="UI is not ready to handle tab actions.")
