"""Model serving endpoint — chạy trên máy có GPU (Colab T4/A10).

POST /generate → {"messages": [{"role":"user","content":"..."}], ...params} → {"response": "..."}
- Load base Qwen3-4B (HF) + adapter LoRA (vừa train xong)
- Serve bằng vLLM (tối ưu VRAM + speed inference)
- Chạy ở cổng 8007 → assistant_service gọi tới đây

Cách chạy trên Colab:
    !pip install vllm peft
    !python /content/model_service.py &
    !cloudflared tunnel --url http://localhost:8007  → lấy URL public
Sau đó cập nhật MODEL_SERVE_HOST trong config.py thành URL tunnel.
"""
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from vllm import LLM, SamplingParams

# ── Config ───────────────────────────────────────────────────────────────────
MODEL_NAME = os.getenv("BASE_MODEL", "Qwen/Qwen3-4B-Instruct")
ADAPTER_PATH = os.getenv("ADAPTER_PATH", "/content/lora_adapter")
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
llm: LLM | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global llm
    logger.info("Loading %s + adapter %s", MODEL_NAME, ADAPTER_PATH)
    llm = LLM(
        model=MODEL_NAME,
        enable_lora=True,       # bật chế độ load adapter
        max_model_len=2048,
        tensor_parallel_size=1, # dùng 1 GPU (T4/V100)
    )

    # Load adapter LoRA (phải được mount tại ADAPTER_PATH)
    if os.path.isdir(ADAPTER_PATH):
        llm.llm_engine.lora_manager.add_lora(
            lora_id="vnuf_lora",
            lora_path=ADAPTER_PATH,
            max_lora_rank=16,
        )
        logger.info("Adapter loaded: %s", ADAPTER_PATH)
    else:
        logger.warning("Adapter path not found: %s — will run base model only", ADAPTER_PATH)
    yield
    logger.info("Model service shutting down")

app = FastAPI(
    title="VNUF Model Service",
    description="Fine-tuned Qwen3-4B adapter endpoint",
    version="1.0.0",
    lifespan=lifespan,
)

@app.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    if llm is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    params = SamplingParams(
        max_tokens=req.max_new_tokens,
        temperature=req.temperature,
        top_p=req.top_p,
        stop=["<|im_start|>"],
    )

    outputs = llm.generate(
        prompts=[req.messages],
        sampling_params=params,
        lora_request={"vnuf_lora": 1} if os.path.isdir(ADAPTER_PATH) else None,
    )

    text = outputs[0].outputs[0].text.strip()
    logger.info("Generated %d chars", len(text))
    return GenerateResponse(response=text)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SERVE_PORT)