import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llama_cpp import Llama
from huggingface_hub import hf_hub_download

app = FastAPI()

MODEL_REPO_ID = os.getenv("MODEL_REPO_ID")
MODEL_FILENAME = os.getenv("MODEL_FILENAME")

if not MODEL_REPO_ID:
    raise ValueError("MODEL_REPO_ID environment variable not set")

print(f"Initializing model from {MODEL_REPO_ID}...")

try:
    # Download model if not present
    model_path = hf_hub_download(
        repo_id=MODEL_REPO_ID,
        filename=MODEL_FILENAME if MODEL_FILENAME else "*Q4_K_M.gguf" # Fallback pattern
    )
    print(f"Model path: {model_path}")

    # Load model
    # n_ctx=2048 is default context window, adjust if needed
    llm = Llama(model_path=model_path, n_ctx=2048, verbose=True)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    raise e

class InferenceRequest(BaseModel):
    prompt: str
    max_length: int = 100

@app.post("/inference")
async def inference(request: InferenceRequest):
    try:
        output = llm(
            request.prompt,
            max_tokens=request.max_length,
            stop=["User:", "\n"], # Stop tokens
            echo=False
        )
        return {"response": output["choices"][0]["text"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_REPO_ID}
