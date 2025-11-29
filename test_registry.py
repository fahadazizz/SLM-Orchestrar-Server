from app.services.model_registry import ModelRegistry

def test_registry():
    registry = ModelRegistry()
    models = registry.get_all_models()
    print(f"Models loaded: {len(models)}")
    for m in models:
        print(f"- {m.name} ({m.id}) -> {m.repo_id}")
    
    assert len(models) > 0
    assert models[0].id == "tiny-llama"
    print("Registry test passed!")

if __name__ == "__main__":
    test_registry()
