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

    def save_models(self):
        data = {"models": [model.dict() for model in self.models]}
        with open(self.config_path, "w") as f:
            yaml.dump(data, f, sort_keys=False)

    def add_model(self, model_config: ModelConfig):
        # Check if exists
        if self.get_model(model_config.id):
            raise ValueError(f"Model with id {model_config.id} already exists")
        
        self.models.append(model_config)
        self.save_models()

    def delete_model(self, model_id: str):
        model = self.get_model(model_id)
        if not model:
            raise ValueError(f"Model with id {model_id} not found")
        
        self.models = [m for m in self.models if m.id != model_id]
        self.save_models()
