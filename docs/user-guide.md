# Hướng dẫn sử dụng VNUF Assistant

## Kiến trúc (đơn giản nhất)

Máy có GPU chính là máy mở giao diện — tất cả chạy cùng 1 máy:

```
[Máy GPU]  model_service :8007  ← Qwen3-4B + LoRA
              ↑ localhost
[Máy GPU]  assistant_service :8006  ← gọi model hộ
              ↑ localhost
[Máy GPU]  frontend/index.html  ← mở bằng browser
```

## Cài đặt (1 lần)

### 1. Clone repo + cài Python

```bash
git clone <repo-url> VNUF
cd VNUF/backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install fastapi uvicorn pydantic httpx
```

### 2. Cài model service (chỉ máy GPU)

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu126
pip install transformers peft accelerate "bitsandbytes>=0.46.1"
```

## Chạy mỗi lần dùng

### Terminal 1 — Model service (máy GPU)

Double-click `scripts\host_model_windows.bat` (Windows) hoặc:

```bash
cd VNUF/backend
source .venv/bin/activate
export ADAPTER_PATH=~/VNUF/adapter
export HF_HOME=~/hf_cache
export MODEL_SERVE_PORT=8007
python model_service.py
```

### Terminal 2 — Assistant service

```bash
cd VNUF/backend
source .venv/bin/activate
export MODEL_SERVE_HOST=127.0.0.1
export MODEL_SERVE_PORT=8007
python assistant_service.py
```

### Terminal 3 — Mở giao diện

Double-click `frontend/index.html`.

## Kiểm tra

```bash
curl http://localhost:8006/assistant \
  -H "Content-Type: application/json" \
  -d '{"user_message":"hom nay toi buon"}'
```

- Câu dài, tự nhiên → **OK**
- Câu ngắn "Cảm xúc trung tính — một không gian yên bình..." → model chưa kết nối

## Lỗi thường gặp

| Lỗi | Fix |
|-----|-----|
| `Lỗi kết nối với server` | `:8006` chưa chạy |
| Trả về template cũ | `:8007` chưa chạy hoặc sai port |
| `No space left on device` | Set `TMP`/`TEMP` sang ổ D: trước khi pip install |
| `bitsandbytes` thiếu GPU | `pip install -U "bitsandbytes>=0.46.1"` |
