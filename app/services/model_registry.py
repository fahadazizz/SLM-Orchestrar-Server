import yaml
from typing import List, Optional
from app.schemas import ModelConfig

class ModelRegistry:
    def __init__(self, config_path: str = "config/models.yaml"):
        self.config_path = config_path
        self.models: List[ModelConfig] = []
        self.load_models()

    def load_models(self):
        with open(self.config_path, "r") as f:
            data = yaml.safe_load(f)
            for model_data in data.get("models", []):
                self.models.append(ModelConfig(**model_data))

    def get_all_models(self) -> List[ModelConfig]:
        return self.models

    def get_model(self, model_id: str) -> Optional[ModelConfig]:
        for model in self.models:
            if model.id == model_id:
                return model
        return None
