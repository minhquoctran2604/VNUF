"""Model serving endpoint — chạy trên máy có GPU.

POST /generate → {"messages": [{"role":"user","content":"..."}]} → {"response": "..."}
- Load base Qwen3-4B (HF) 4-bit + adapter LoRA vừa train
- ponytail: transformers+peft thay vì vLLM — vLLM cần ~8GB VRAM cho base fp16,
  máy target 4GB; đổi sang vLLM khi có GPU >=8GB hoặc cần throughput.

Chạy:
    source .venv/bin/activate
    export ADAPTER_PATH=~/VNUF/adapter
    python3 model_service.py
"""
import os
import logging
from contextlib import asynccontextmanager

import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# ── Config ───────────────────────────────────────────────────────────────────
MODEL_NAME = os.getenv("BASE_MODEL", "unsloth/Qwen3-4B-Instruct-2507")
ADAPTER_PATH = os.path.expanduser(os.getenv("ADAPTER_PATH", "~/VNUF/adapter"))
SERVE_PORT = int(os.getenv("MODEL_SERVE_PORT", "8007"))

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [model] %(levelname)s %(message)s",
)
logger = logging.getLogger("model_service")

# ── Models ───────────────────────────────────────────────────────────────────
class GenerateRequest(BaseModel):
    messages: list[dict] = Field(..., min_length=1)
    max_new_tokens: int = 256
    temperature: float = 0.7
    top_p: float = 0.9

class GenerateResponse(BaseModel):
    response: str

# ── App ──────────────────────────────────────────────────────────────────────
model = None
tokenizer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, tokenizer
    logger.info("Loading %s (4-bit) + adapter %s", MODEL_NAME, ADAPTER_PATH)
    tokenizer_src = ADAPTER_PATH if os.path.isdir(ADAPTER_PATH) else MODEL_NAME
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_src)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        load_in_4bit=True,
        device_map="auto",
    )
    if os.path.isdir(ADAPTER_PATH):
        model = PeftModel.from_pretrained(model, ADAPTER_PATH)
        logger.info("Adapter loaded: %s", ADAPTER_PATH)
    else:
        logger.warning("Adapter path not found: %s — base model only", ADAPTER_PATH)
    model.eval()
    yield
    logger.info("Model service shutting down")

app = FastAPI(
    title="VNUF Model Service",
    description="Fine-tuned Qwen3-4B adapter endpoint",
    version="1.1.0",
    lifespan=lifespan,
)

@app.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    inputs = tokenizer.apply_chat_template(
        req.messages, add_generation_prompt=True,
        return_tensors="pt", return_dict=True,
    ).to(model.device)

    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=req.max_new_tokens,
            temperature=req.temperature,
            top_p=req.top_p,
            do_sample=True,
        )

    text = tokenizer.decode(
        out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True
    ).strip()
    logger.info("Generated %d chars", len(text))
    return GenerateResponse(response=text)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "model_service", "model": MODEL_NAME}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SERVE_PORT)
