# Remote Model Setup — GPU host + Client UI (via Tailscale)

Architecture:

```
[GPU machine]  model_service.py :8007 (0.0.0.0)
      ^ tailscale IP, e.g. http://100.x.y.z:8007/generate
      |
[Client] emotion_service.py :8005 (localhost) ─┐
[Client] assistant_service.py :8006 (localhost) ─┼─> frontend/index.html
                                                 │   (hardcodes localhost:8005/8006)
```

Key constraint: `frontend/index.html:210,219` calls `http://localhost:8005` and
`http://localhost:8006` directly. So every client MUST run emotion + assistant
locally. Only the Qwen LoRA call (`assistant -> model`, `backend/config.py:16-18`)
goes remote via Tailscale.

## 1. GPU host (Windows, RTX 3050 4GB) — one time

```powershell
cd D:\VNUF\VNUF
.\..\.venv\Scripts\Activate.ps1   # or use .venv python directly
pip install fastapi uvicorn pydantic httpx
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install transformers peft accelerate "bitsandbytes>=0.46.1"

$env:ADAPTER_PATH = "D:\VNUF\VNUF\adapter"   # must contain adapter_model.safetensors + tokenizer files
$env:HF_HOME = "D:\hf_cache"                 # C: is full, keep base model on D:
$env:MODEL_SERVE_PORT = "8007"
python D:\VNUF\VNUF\backend\model_service.py
```

Verify on host: `curl http://localhost:8007/health` → `{"status":"ok"}`.

Firewall (admin CMD, one time):

```cmd
netsh advfirewall firewall add rule name="VNUF model 8007" dir=in action=allow protocol=TCP localport=8007
```

Tailscale on host: install, login to same tailnet, note its IP
(`tailscale ip -4` → e.g. `100.93.26.96`). Model already binds `0.0.0.0:8007`
(`model_service.py:107`), so no extra flag needed.

## 2. Client (any OS, same tailnet) — per member

Prerequisites: git, Python 3.12, Tailscale logged into the SAME tailnet.

```bash
git clone <repo-url> VNUF
cd VNUF/backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install fastapi uvicorn pydantic httpx

# Terminal 1 — emotion (local only)
python emotion_service.py        # :8005

# Terminal 2 — assistant (points to remote GPU)
export MODEL_SERVE_HOST=100.93.26.96   # <-- replace with real GPU tailscale IP
export MODEL_SERVE_PORT=8007
python assistant_service.py      # :8006
```

Windows (PowerShell) equivalent:

```powershell
$env:MODEL_SERVE_HOST = "100.93.26.96"
$env:MODEL_SERVE_PORT = "8007"
python backend\assistant_service.py
```

Open UI: double-click `frontend/index.html` in a browser.
No build step; no server needed for the HTML file.

Verify remote reachability BEFORE opening UI:

```bash
curl http://100.93.26.96:8007/health
curl -X POST http://localhost:8006/assistant \
  -H "Content-Type: application/json" \
  -d '{"user_message":"hom nay toi buon","emotion":"buon"}'
```

First call returns model text; if GPU is down it falls back to template
responses (`assistant_service.py:151-157`) — UI still works, just without LoRA.

## 3. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `curl` to `100.x:8007` timeout | Host firewall blocking; host `model_service` not running; different tailnet / ACL. Check `tailscale status` on both ends. |
| `CUDA out of memory` on host | 4GB VRAM borderline for Qwen3-4B 4-bit. Close browsers/games, retry. Persistent → switch host to GGUF + llama.cpp or a bigger GPU. Code is already 4-bit (`model_service.py:56`), no further quant flag to flip. |
| `Adapter path not found — base model only` | `ADAPTER_PATH` wrong. Must be folder with `adapter_model.safetensors`. |
| C: disk full during first load | `HF_HOME` not set to D:. Base model ~8GB downloads on first run. |
| Frontend `Lỗi kết nối với server` | `:8005`/`:8006` not running locally. Frontend cannot point to remote — always localhost. |
