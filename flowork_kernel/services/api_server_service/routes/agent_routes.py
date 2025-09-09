#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\agent_routes.py
# JUMLAH BARIS : 83
#######################################################################

from fastapi import APIRouter, HTTPException, Body, Request
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
class AgentRunRequest(BaseModel):
    objective: str
class AgentCreateOrUpdateRequest(BaseModel):
    id: Optional[UUID] = None
    name: str
    description: Optional[str] = ""
    brain_model_id: str
    tool_ids: List[str] = Field(default_factory=list)
    prompt_template: Optional[str] = ""
router = APIRouter(
    tags=["Agents"]
)
@router.get("/agents", response_model=List[dict])
async def handle_get_agents(request: Request):
    agent_manager = request.app.service_instance.agent_manager
    if not agent_manager:
        raise HTTPException(status_code=503, detail="AgentManagerService is not available.")
    return agent_manager.get_all_agents()
@router.get("/agents/{agent_id}", response_model=dict)
async def handle_get_agent_by_id(agent_id: str, request: Request):
    agent_manager = request.app.service_instance.agent_manager
    if not agent_manager:
        raise HTTPException(status_code=503, detail="AgentManagerService is not available.")
    agent = agent_manager.get_agent(agent_id)
    if agent:
        return agent
    else:
        raise HTTPException(status_code=404, detail=f"Agent with ID '{agent_id}' not found.")
@router.post("/agents", status_code=201, response_model=dict)
async def handle_post_agents(request: Request, agent_data: AgentCreateOrUpdateRequest):
    agent_manager = request.app.service_instance.agent_manager
    if not agent_manager:
        raise HTTPException(status_code=503, detail="AgentManagerService is not available.")
    result = agent_manager.save_agent(agent_data.model_dump())
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
@router.delete("/agents/{agent_id}", status_code=204)
async def handle_delete_agent(agent_id: str, request: Request):
    agent_manager = request.app.service_instance.agent_manager
    if not agent_manager:
        raise HTTPException(status_code=503, detail="AgentManagerService is not available.")
    if not agent_manager.delete_agent(agent_id):
        raise HTTPException(status_code=404, detail="Agent not found.")
    return None # Return None for 204 No Content
@router.post("/agents/{agent_id}/run", status_code=202)
async def handle_run_agent(agent_id: str, request: Request, body: AgentRunRequest):
    agent_executor = request.app.service_instance.agent_executor
    if not agent_executor:
        raise HTTPException(status_code=503, detail="AgentExecutorService is not available.")
    result = agent_executor.run_agent(agent_id, body.objective)
    if "error" in result:
        raise HTTPException(status_code=409, detail=result["error"]) # 409 Conflict is suitable here
    return result
@router.get("/agents/run/{run_id}")
async def handle_get_agent_run_status(run_id: str, request: Request):
    agent_executor = request.app.service_instance.agent_executor
    if not agent_executor:
        raise HTTPException(status_code=503, detail="AgentExecutorService is not available.")
    status = agent_executor.get_run_status(run_id)
    if "error" in status:
        raise HTTPException(status_code=404, detail=status["error"])
    return status
@router.post("/agents/run/{run_id}/stop")
async def handle_stop_agent_run(run_id: str, request: Request):
    agent_executor = request.app.service_instance.agent_executor
    if not agent_executor:
        raise HTTPException(status_code=503, detail="AgentExecutorService is not available.")
    result = agent_executor.stop_agent_run(run_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
