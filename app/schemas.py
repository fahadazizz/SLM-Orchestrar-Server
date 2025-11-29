from pydantic import BaseModel
from typing import Optional, List

class ContainerConfig(BaseModel):
    image: str
    port: int
    gpu: bool = False

class ModelConfig(BaseModel):
    id: str
    name: str
    source: str
    repo_id: str
    container_config: ContainerConfig

class ModelListResponse(BaseModel):
    models: List[ModelConfig]

class RunModelRequest(BaseModel):
    model_id: str

class StopModelRequest(BaseModel):
    model_id: str

class InferenceRequest(BaseModel):
    model_id: str
    prompt: str
    max_length: Optional[int] = 100

class InferenceResponse(BaseModel):
    model_id: str
    response: str

class ContainerStatus(BaseModel):
    model_id: str
    status: str
    container_id: Optional[str] = None
    port: Optional[int] = None
