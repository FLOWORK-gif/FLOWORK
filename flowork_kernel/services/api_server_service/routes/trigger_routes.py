#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\trigger_routes.py
# JUMLAH BARIS : 102
#######################################################################

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
class TriggerRule(BaseModel):
    name: str
    trigger_id: str
    preset_to_run: str
    is_enabled: bool = True
    config: Dict[str, Any] = {}
router = APIRouter(
    tags=["Triggers"]
)
@router.get("/triggers/definitions", response_model=List[dict])
async def handle_get_trigger_definitions(request: Request):
    trigger_manager = request.app.service_instance.trigger_manager
    if not trigger_manager:
        raise HTTPException(status_code=503, detail="TriggerManager service is unavailable.")
    definitions = [tdata['manifest'] for tid, tdata in trigger_manager.loaded_triggers.items()]
    return sorted(definitions, key=lambda x: x.get('name', ''))
@router.get("/triggers/rules", response_model=List[dict])
async def handle_get_trigger_rules(request: Request):
    state_manager = request.app.service_instance.state_manager
    if not state_manager:
        raise HTTPException(status_code=503, detail="StateManager service is unavailable.")
    all_rules = state_manager.get("trigger_rules", {})
    trigger_manager = request.app.service_instance.trigger_manager
    scheduler_manager = request.app.service_instance.scheduler_manager
    enriched_rules = []
    for rid, rdata in all_rules.items():
        enriched_data = rdata.copy()
        enriched_data['id'] = rid
        trigger_id = rdata.get('trigger_id')
        enriched_data['trigger_name'] = trigger_manager.loaded_triggers.get(trigger_id, {}).get('manifest', {}).get('name', trigger_id) if trigger_manager else trigger_id
        next_run = None
        if scheduler_manager and trigger_id == 'cron_trigger' and rdata.get('is_enabled'):
            try:
                next_run_time = scheduler_manager.get_next_run_time(rid)
                if next_run_time:
                    next_run = next_run_time.isoformat()
            except Exception as e:
                request.app.service_instance.kernel.write_to_log(f"A non-critical error occurred while fetching next_run_time for job '{rid}'. The UI will show '-'. Error: {e}", "WARN") # English Log
                next_run = None
        enriched_data['next_run_time'] = next_run
        enriched_rules.append(enriched_data)
    return enriched_rules
@router.get("/triggers/rules/{rule_id}", response_model=Dict[str, Any])
async def handle_get_trigger_rule_by_id(rule_id: str, request: Request):
    state_manager = request.app.service_instance.state_manager
    if not state_manager:
        raise HTTPException(status_code=503, detail="StateManager service is unavailable.")
    all_rules = state_manager.get("trigger_rules", {})
    rule_data = all_rules.get(rule_id)
    if rule_data:
        return rule_data
    raise HTTPException(status_code=404, detail=f"Rule with ID '{rule_id}' not found.")
@router.post("/triggers/rules", status_code=201)
async def handle_post_trigger_rule(request: Request, body: TriggerRule):
    state_manager = request.app.service_instance.state_manager
    if not state_manager:
        raise HTTPException(status_code=503, detail="StateManager service is unavailable.")
    new_rule_id = str(uuid.uuid4())
    all_rules = state_manager.get("trigger_rules", {})
    all_rules[new_rule_id] = body.model_dump()
    state_manager.set("trigger_rules", all_rules)
    return {"status": "success", "id": new_rule_id}
@router.put("/triggers/rules/{rule_id}")
async def handle_put_trigger_rule(rule_id: str, request: Request, body: TriggerRule):
    state_manager = request.app.service_instance.state_manager
    if not state_manager:
        raise HTTPException(status_code=503, detail="StateManager service is unavailable.")
    all_rules = state_manager.get("trigger_rules", {})
    if rule_id not in all_rules:
        raise HTTPException(status_code=404, detail=f"Rule with ID '{rule_id}' not found.")
    all_rules[rule_id] = body.model_dump()
    state_manager.set("trigger_rules", all_rules)
    return {"status": "success", "id": rule_id}
@router.delete("/triggers/rules/{rule_id}", status_code=204)
async def handle_delete_trigger_rule(rule_id: str, request: Request):
    state_manager = request.app.service_instance.state_manager
    if not state_manager:
        raise HTTPException(status_code=503, detail="StateManager service is unavailable.")
    all_rules = state_manager.get("trigger_rules", {})
    if rule_id in all_rules:
        del all_rules[rule_id]
        state_manager.set("trigger_rules", all_rules)
        return None
    else:
        raise HTTPException(status_code=404, detail=f"Rule with ID '{rule_id}' not found.")
@router.post("/triggers/actions/reload")
async def handle_reload_triggers(request: Request):
    trigger_manager = request.app.service_instance.trigger_manager
    if not trigger_manager:
        raise HTTPException(status_code=503, detail="TriggerManager service is unavailable.")
    trigger_manager.start_all_listeners()
    return {"status": "success", "message": "Trigger reload process initiated."}
