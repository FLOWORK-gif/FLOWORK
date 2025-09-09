#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\model_routes.py
# JUMLAH BARIS : 103
#######################################################################

from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
from pydantic import BaseModel
from typing import List
import os
import shutil
import tempfile
class ModelConvertRequest(BaseModel):
    source_model_folder: str
    output_gguf_name: str
    quantize_method: str = "Q4_K_M"
class ModelRequantizeRequest(BaseModel):
    source_gguf_path: str
    output_gguf_name: str
    quantize_method: str = "Q4_K_M"
router = APIRouter(
    tags=["AI Models"]
)
@router.post("/models/convert", status_code=202)
async def handle_post_model_conversion(request: Request, body: ModelConvertRequest):
    converter_service = request.app.service_instance.converter_service
    if not converter_service:
        raise HTTPException(status_code=503, detail="ModelConverterService is not available.")
    result = converter_service.start_conversion_job(
        body.source_model_folder,
        body.output_gguf_name,
        body.quantize_method
    )
    if "error" in result:
        raise HTTPException(status_code=409, detail=result["error"])
    return result
@router.post("/models/requantize", status_code=202)
async def handle_post_model_requantize(request: Request, body: ModelRequantizeRequest):
    converter_service = request.app.service_instance.converter_service
    if not converter_service:
        raise HTTPException(status_code=503, detail="ModelConverterService is not available.")
    result = converter_service.start_requantize_job(
        body.source_gguf_path,
        body.output_gguf_name,
        body.quantize_method
    )
    if "error" in result:
        raise HTTPException(status_code=409, detail=result["error"])
    return result
@router.get("/models/convert/status/{job_id}")
async def handle_get_conversion_status(job_id: str, request: Request):
    converter_service = request.app.service_instance.converter_service
    if not converter_service:
        raise HTTPException(status_code=503, detail="ModelConverterService is not available.")
    status = converter_service.get_job_status(job_id)
    if "error" in status:
        raise HTTPException(status_code=404, detail=status["error"])
    return status
@router.post("/models/upload")
async def handle_model_upload(
    request: Request,
    description: str = Form(...),
    tier: str = Form(...),
    model_id: str = Form(...),
    file: UploadFile = File(...)
):
    addon_service = request.app.service_instance.addon_service
    if not addon_service:
        raise HTTPException(status_code=503, detail="CommunityAddonService is not available.")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".gguf") as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            temp_model_path = tmp_file.name
        success, message = addon_service.upload_model(temp_model_path, model_id, description, tier)
        os.remove(temp_model_path)
        if success:
            return {"status": "success", "message": message}
        else:
            raise HTTPException(status_code=500, detail=message)
    except Exception as e:
        request.app.service_instance.kernel.write_to_log(f"API Model Upload Error: {e}", "CRITICAL")
        raise HTTPException(status_code=500, detail=f"Failed to process model upload: {e}")
@router.get("/ai_models", response_model=List[dict])
async def handle_get_local_ai_models(request: Request):
    kernel = request.app.service_instance.kernel
    models_path = os.path.join(kernel.project_root_path, "ai_models")
    try:
        if not os.path.isdir(models_path):
            os.makedirs(models_path)
            return []
        gguf_files = [f for f in os.listdir(models_path) if f.endswith(".gguf")]
        response_data = []
        for filename in gguf_files:
            model_id = filename.replace('.gguf', '')
            response_data.append({
                "id": model_id, "name": model_id, "version": "N/A", "is_paused": False,
                "description": f"Local GGUF model file: {filename}", "is_core": False, "tier": "pro"
            })
        return response_data
    except Exception as e:
        kernel.write_to_log(f"Error listing local AI models: {e}", "ERROR")
        raise HTTPException(status_code=500, detail=f"Could not list local AI models: {e}")
