#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE https://github.com/FLOWORK-gif/FLOWORK
# File NAME : C:\FLOWORK\flowork_kernel\services\api_server_service\routes\dataset_routes.py
# JUMLAH BARIS : 58
#######################################################################

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Any
class DatasetCreateRequest(BaseModel):
    name: str
class DatasetAddDataRequest(BaseModel):
    data: List[Dict[str, Any]]
router = APIRouter(
    tags=["Datasets"]
)
@router.get("/datasets", response_model=List[dict])
async def handle_get_datasets(request: Request):
    dataset_manager = request.app.service_instance.dataset_manager_service
    if not dataset_manager:
        raise HTTPException(status_code=503, detail="DatasetManagerService is not available.")
    return dataset_manager.list_datasets()
@router.post("/datasets", status_code=201)
async def handle_post_datasets(request: Request, body: DatasetCreateRequest):
    dataset_manager = request.app.service_instance.dataset_manager_service
    if not dataset_manager:
        raise HTTPException(status_code=503, detail="DatasetManagerService is not available.")
    success = dataset_manager.create_dataset(body.name)
    if success:
        return {"status": "success", "message": f"Dataset '{body.name}' created."}
    else:
        raise HTTPException(status_code=409, detail=f"Dataset '{body.name}' already exists or could not be created.")
@router.get("/datasets/{dataset_name}/data", response_model=List[dict])
async def handle_get_dataset_data(dataset_name: str, request: Request):
    dataset_manager = request.app.service_instance.dataset_manager_service
    if not dataset_manager:
        raise HTTPException(status_code=503, detail="DatasetManagerService is not available.")
    return dataset_manager.get_dataset_data(dataset_name)
@router.post("/datasets/{dataset_name}/data")
async def handle_post_dataset_data(dataset_name: str, request: Request, body: DatasetAddDataRequest):
    dataset_manager = request.app.service_instance.dataset_manager_service
    if not dataset_manager:
        raise HTTPException(status_code=503, detail="DatasetManagerService is not available.")
    success = dataset_manager.add_data_to_dataset(dataset_name, body.data)
    if success:
        return {"status": "success", "message": f"Added {len(body.data)} records to dataset '{dataset_name}'."}
    else:
        raise HTTPException(status_code=500, detail=f"Failed to add data to dataset '{dataset_name}'.")
@router.delete("/datasets/{dataset_name}", status_code=204)
async def handle_delete_dataset(dataset_name: str, request: Request):
    dataset_manager = request.app.service_instance.dataset_manager_service
    if not dataset_manager:
        raise HTTPException(status_code=503, detail="DatasetManagerService is not available.")
    success = dataset_manager.delete_dataset(dataset_name)
    if not success:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_name}' not found.")
    return None # Return None for 204 No Content
