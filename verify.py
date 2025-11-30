import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_list_models():
    print("Testing GET /models...")
    res = requests.get(f"{BASE_URL}/models")
    assert res.status_code == 200
    models = res.json()["models"]
    print(f"Models found: {len(models)}")
    assert len(models) > 0
    return models[0]["id"]

def test_run_model(model_id):
    print(f"Testing POST /run for {model_id}...")
    res = requests.post(f"{BASE_URL}/run", json={"model_id": model_id})
    assert res.status_code == 200
    print("Model start request sent.")
    
    # Wait for container to be ready
    print("Waiting for container to be ready...")
    model_port = None
    for _ in range(30):
        time.sleep(2)
        res = requests.get(f"{BASE_URL}/status")
        statuses = res.json()
        for s in statuses:
            if s["model_id"] == model_id and s["status"] == "running":
                print("Container is running!")
                model_port = s["port"]
                break
        if model_port:
            break
    
    if not model_port:
        raise Exception("Model container failed to start within timeout")

    # Wait for Model Server to be ready (Application Startup)
    print(f"Waiting for Model Server on port {model_port} to be ready...")
    server_ready = False
    for _ in range(30): # Wait up to 60s for model load
        try:
            health_res = requests.get(f"http://127.0.0.1:{model_port}/health")
            if health_res.status_code == 200:
                print("Model Server is ready!")
                server_ready = True
                break
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(2)
    
    if not server_ready:
        raise Exception("Model Server failed to become ready (Health check failed)")

def test_inference(model_id):
    print(f"Testing POST /inference for {model_id}...")
    # Give it a few more seconds for the internal server to actually bind port
    time.sleep(5) 
    prompt = "Hello, how are you?"
    res = requests.post(f"{BASE_URL}/inference", json={"model_id": model_id, "prompt": prompt, "max_length": 50})
    if res.status_code != 200:
        print(f"Inference failed: {res.text}")
    assert res.status_code == 200
    print(f"Response: {res.json()['response']}")

def test_stop_model(model_id):
    print(f"Testing POST /stop for {model_id}...")
    res = requests.post(f"{BASE_URL}/stop", json={"model_id": model_id})
    assert res.status_code == 200
    print("Model stopped.")


def test_add_model():
    print("Testing POST /models...")
    new_model = {
        "id": "test-model",
        "name": "Test Model",
        "source": "huggingface",
        "repo_id": "Test/Model",
        "container_config": {
            "image": "orchestrar-runner:latest",
            "port": 8003,
            "gpu": False
        }
    }
    res = requests.post(f"{BASE_URL}/models", json=new_model)
    if res.status_code != 200:
        print(f"Failed to add model: {res.text}")
    assert res.status_code == 200
    print("Model added successfully.")
    
    # Verify it's in the list
    res = requests.get(f"{BASE_URL}/models")
    models = res.json()["models"]
    found = False
    for m in models:
        if m["id"] == "test-model":
            found = True
            break
    assert found
    print("Model found in list.")

def test_delete_model():
    print("Testing DELETE /models/test-model...")
    res = requests.delete(f"{BASE_URL}/models/test-model")
    if res.status_code != 200:
        print(f"Failed to delete model: {res.text}")
    assert res.status_code == 200
    print("Model deleted successfully.")

    # Verify it's gone
    res = requests.get(f"{BASE_URL}/models")
    models = res.json()["models"]
    found = False
    for m in models:
        if m["id"] == "test-model":
            found = True
            break
    assert not found
    print("Model gone from list.")


if __name__ == "__main__":
    try:
        model_id = test_list_models()
        test_add_model()
        test_run_model(model_id)
        print("modle is running")
        test_inference(model_id)
        print("test successful inference")
        test_stop_model(model_id)
        print("model stoped")
        test_delete_model()
        print("\nAll tests passed!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        sys.exit(1)
