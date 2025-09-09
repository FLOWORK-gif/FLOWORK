#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\training_routes.py
# JUMLAH BARIS : 41
#######################################################################

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any
class TrainingStartRequest(BaseModel):
    base_model_id: str
    dataset_name: str
    new_model_name: str
    training_args: Dict[str, Any]
router = APIRouter(
    tags=["AI Training"]
)
@router.post("/training/start", status_code=202)
async def handle_start_training_job(request: Request, body: TrainingStartRequest):
    training_service = request.app.service_instance.training_service
    if not training_service:
        raise HTTPException(status_code=503, detail="AITrainingService is not available.")
    result = training_service.start_fine_tuning_job(
        body.base_model_id,
        body.dataset_name,
        body.new_model_name,
        body.training_args
    )
    if "error" in result:
        raise HTTPException(status_code=409, detail=result["error"])
    return result
@router.get("/training/status/{job_id}")
async def handle_get_training_job_status(job_id: str, request: Request):
    training_service = request.app.service_instance.training_service
    if not training_service:
        raise HTTPException(status_code=503, detail="AITrainingService is not available.")
    status = training_service.get_job_status(job_id)
    if "error" in status:
        raise HTTPException(status_code=404, detail=status["error"])
    return status
