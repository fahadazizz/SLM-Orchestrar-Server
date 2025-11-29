import requests
import time
import sys

BASE_URL = "http://localhost:8000"

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
    for _ in range(30):
        time.sleep(2)
        res = requests.get(f"{BASE_URL}/status")
        statuses = res.json()
        for s in statuses:
            if s["model_id"] == model_id and s["status"] == "running":
                print("Model is running!")
                return
    raise Exception("Model failed to start within timeout")

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

if __name__ == "__main__":
    try:
        model_id = test_list_models()
        test_run_model(model_id)
        test_inference(model_id)
        test_stop_model(model_id)
        print("\nAll tests passed!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        sys.exit(1)
