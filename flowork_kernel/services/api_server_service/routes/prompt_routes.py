#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\prompt_routes.py
# JUMLAH BARIS : 70
#######################################################################

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
class PromptData(BaseModel):
    name: str
    content: str
    id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
router = APIRouter(
    tags=["Prompts"]
)
@router.get('/prompts', response_model=List[Dict[str, Any]])
async def get_all_prompts(request: Request):
    prompt_manager = request.app.service_instance.prompt_manager_service
    if not prompt_manager:
        raise HTTPException(status_code=503, detail="PromptManagerService is not available.")
    result = prompt_manager.get_all_prompts()
    if result is not None:
        return result
    raise HTTPException(status_code=500, detail="Service call to get all prompts failed.")
@router.post('/prompts', status_code=201)
async def create_prompt(request: Request, prompt_data: PromptData):
    prompt_manager = request.app.service_instance.prompt_manager_service
    if not prompt_manager:
        raise HTTPException(status_code=503, detail="PromptManagerService is not available.")
    result = prompt_manager.create_prompt(prompt_data.model_dump())
    if result and 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    if result:
        return result
    raise HTTPException(status_code=500, detail="Service call to create prompt failed.")
@router.get('/prompts/{prompt_id}')
async def get_prompt_by_id(prompt_id: str, request: Request):
    prompt_manager = request.app.service_instance.prompt_manager_service
    if not prompt_manager:
        raise HTTPException(status_code=503, detail="PromptManagerService is not available.")
    result = prompt_manager.get_prompt(prompt_id)
    if result:
        return result
    raise HTTPException(status_code=404, detail="Prompt not found or service call failed.")
@router.put('/prompts/{prompt_id}')
async def update_prompt(prompt_id: str, request: Request, prompt_data: PromptData):
    prompt_manager = request.app.service_instance.prompt_manager_service
    if not prompt_manager:
        raise HTTPException(status_code=503, detail="PromptManagerService is not available.")
    result = prompt_manager.update_prompt(prompt_id, prompt_data.model_dump())
    if result and 'error' in result:
        raise HTTPException(status_code=400, detail=result['error'])
    if result:
        return result
    raise HTTPException(status_code=500, detail="Service call to update prompt failed.")
@router.delete('/prompts/{prompt_id}')
async def delete_prompt(prompt_id: str, request: Request):
    prompt_manager = request.app.service_instance.prompt_manager_service
    if not prompt_manager:
        raise HTTPException(status_code=503, detail="PromptManagerService is not available.")
    result = prompt_manager.delete_prompt(prompt_id)
    if result and 'error' in result:
        raise HTTPException(status_code=404, detail=result['error'])
    if result:
        return result
    raise HTTPException(status_code=500, detail="Service call to delete prompt failed.")
