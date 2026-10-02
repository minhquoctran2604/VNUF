# Setup Guide — VNUF Assistant (cài đặt lần đầu)

## Kiến trúc

Máy có GPU chính là máy mở giao diện — tất cả chạy cùng 1 máy:

```
[Máy GPU]  model_service :8007  ← Qwen3-4B + LoRA
              ↑ localhost
[Máy GPU]  assistant_service :8006  ← gọi model hộ
              ↑ localhost
[Máy GPU]  frontend/index.html  ← mở bằng browser
```

## 1. Clone repo + cài Python

```bash
git clone <repo-url> VNUF
cd VNUF/backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install fastapi uvicorn pydantic httpx
```

## 2. Cài model service (chỉ máy GPU)

```bash
# Windows: set temp sang ổ D: trước khi pip install (tránh đầy C:)
setx TMP D:\pip_tmp
setx TEMP D:\pip_tmp
# Mở terminal mới sau khi setx

pip install torch --index-url https://download.pytorch.org/whl/cu126
pip install transformers peft accelerate "bitsandbytes>=0.46.1"
```

## 3. Chuẩn bị adapter

Copy folder `adapter/` (chứa `adapter_model.safetensors` + tokenizer) vào `VNUF/adapter/`.

## 4. Chạy thử

```powershell
# Terminal 1 — model
.\scripts\host_model_windows.bat

# Terminal 2 — assistant
$env:MODEL_SERVE_HOST = "127.0.0.1"; $env:MODEL_SERVE_PORT = "8007"
python assistant_service.py

# Terminal 3 — UI
# Double-click frontend/index.html
```

## Lỗi thường gặp

| Lỗi | Fix |
|-----|-----|
| `No space left on device` | Set `TMP`/`TEMP` sang ổ D: trước khi pip install |
| `bitsandbytes` thiếu GPU | `pip install -U "bitsandbytes>=0.46.1"` |
| `torch.cuda.is_available()` = False | Cài lại torch cu126, kiểm tra driver |
| `CUDA out of memory` | Đóng browser/game nặng, restart service |
| `Adapter path not found` | Copy adapter vào `VNUF/adapter/` |
