from fastapi import APIRouter, HTTPException, Depends
from typing import List
import requests
from app.schemas import (
    ModelListResponse, RunModelRequest, StopModelRequest, 
    InferenceRequest, InferenceResponse, ContainerStatus, AddModelRequest
)
from app.services.model_registry import ModelRegistry
from app.services.docker_service import DockerService

router = APIRouter()
model_registry = ModelRegistry()
docker_service = DockerService()

@router.get("/health")
def health_check():
    return {"status": "ok", "service": "orchestrator"}

@router.get("/models", response_model=ModelListResponse)
def list_models():
    return {"models": model_registry.get_all_models()}

@router.post("/models", response_model=AddModelRequest)
def add_model(request: AddModelRequest):
    try:
        model_registry.add_model(request)
        return request
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/models/{model_id}")
def delete_model(model_id: str):
    try:
        # 1. Remove container
        docker_service.remove_container(model_id)
        # 2. Remove from registry
        model_registry.delete_model(model_id)
        return {"status": "deleted", "model_id": model_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/run", response_model=ContainerStatus)
def run_model(request: RunModelRequest):
    model_config = model_registry.get_model(request.model_id)
    if not model_config:
        raise HTTPException(status_code=404, detail="Model not found")
    
    status = docker_service.start_container(model_config)
    if "error" in status.status:
        raise HTTPException(status_code=500, detail=status.status)
    return status

@router.post("/stop", response_model=ContainerStatus)
def stop_model(request: StopModelRequest):
    status = docker_service.stop_container(request.model_id)
    if status.status == "not_found":
        raise HTTPException(status_code=404, detail="Container not found")
    return status

@router.get("/status", response_model=List[ContainerStatus])
def get_status():
    return docker_service.list_running_models()

@router.post("/inference", response_model=InferenceResponse)
def inference(request: InferenceRequest):
    # 1. Check if model is running
    container = docker_service.get_container_by_model_id(request.model_id)
    if not container or container.status != "running":
        raise HTTPException(status_code=400, detail="Model is not running. Please start it first.")
    
    # 2. Get port
    model_config = model_registry.get_model(request.model_id)
    if not model_config:
         raise HTTPException(status_code=404, detail="Model config not found")
    
    port = model_config.container_config.port
    
    # 3. Proxy request
    try:
        url = f"http://127.0.0.1:{port}/inference"
        response = requests.post(url, json={"prompt": request.prompt, "max_length": request.max_length})
        response.raise_for_status()
        return InferenceResponse(model_id=request.model_id, response=response.json()["response"])
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=502, detail="Model server not reachable. It might be starting up.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
