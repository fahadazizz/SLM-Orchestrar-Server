import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = FastAPI()

MODEL_REPO_ID = os.getenv("MODEL_REPO_ID")
if not MODEL_REPO_ID:
    raise ValueError("MODEL_REPO_ID environment variable not set")

print(f"Loading model: {MODEL_REPO_ID}...")
# Load model and tokenizer
# Use float16 if GPU is available, else float32
device = "cuda" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if device == "cuda" else torch.float32

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_REPO_ID)

    # Optimize loading
    load_kwargs = {
        "low_cpu_mem_usage": True,
    }

    if device == "cuda":
        load_kwargs["device_map"] = "auto"
        load_kwargs["dtype"] = torch.float16
    else:
        # On CPU, use float32 as float16 might not be supported or slower, 
        # but if memory is tight, we might want to try float16 if supported.
        # For now, stick to float32 for compatibility, but warn user.
        load_kwargs["dtype"] = torch.float32
        # device_map="auto" with accelerate can help with OOM by offloading
        load_kwargs["device_map"] = "auto"
        load_kwargs["offload_folder"] = "offload"

    print(f"Loading model with kwargs: {load_kwargs}")

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_REPO_ID,
        **load_kwargs
    )
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
        inputs = tokenizer(request.prompt, return_tensors="pt").to(model.device)
        outputs = model.generate(
            **inputs, 
            max_length=request.max_length, 
            do_sample=True,
            top_k=50,
            top_p=0.95
        )
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return {"response": generated_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_REPO_ID}
