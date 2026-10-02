# Hướng dẫn sử dụng VNUF Assistant (cho thành viên mới)

## Kiến trúc

```
[Máy GPU - Windows]  model_service :8007  ← chạy bởi 1 người duy nhất
        ↑ Tailscale
[Máy bạn - bất kỳ OS]  assistant_service :8006  ← mỗi người tự chạy
        ↑ localhost
[Máy bạn]  frontend/index.html  ← mở bằng browser
```

## Cài đặt (1 lần)

### 1. Tailscale

- Tải: https://tailscale.com/download
- Đăng nhập bằng **tài khoản đã được mời vào tailnet** (hỏi người setup)
- Kiểm tra: `tailscale status` → thấy máy GPU với IP `100.x.x.x`

### 2. Clone repo + cài Python

```bash
git clone <repo-url> VNUF
cd VNUF/backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install fastapi uvicorn pydantic httpx
```

## Chạy mỗi lần dùng

### Terminal 1 — Assistant service

```bash
cd VNUF/backend
source .venv/bin/activate

# Đặt IP Tailscale của máy GPU (hỏi người setup nếu không biết)
export MODEL_SERVE_HOST=100.x.x.x
export MODEL_SERVE_PORT=8007

python assistant_service.py
```

Windows PowerShell:
```powershell
$env:MODEL_SERVE_HOST = "100.x.x.x"
$env:MODEL_SERVE_PORT = "8007"
python assistant_service.py
```

### Terminal 2 — Mở giao diện

Double-click `frontend/index.html` trong file explorer.

Hoặc serve qua HTTP (nếu muốn truy cập từ máy khác trong LAN):
```bash
cd VNUF/frontend
python3 -m http.server 8080
# Rồi mở browser vào http://localhost:8080/index.html
```

## Kiểm tra

```bash
# Test assistant có gọi được model không
curl http://localhost:8006/assistant \
  -H "Content-Type: application/json" \
  -d '{"user_message":"hom nay toi buon"}'
```

- Trả về câu dài, tự nhiên → **OK**, model đang hoạt động
- Trả về câu ngắn kiểu "Cảm xúc trung tính — một không gian yên bình..." → model GPU chưa kết nối (kiểm tra IP, Tailscale, máy GPU có đang chạy không)

## Lỗi thường gặp

| Lỗi | Nguyên nhân | Fix |
|-----|-------------|-----|
| `Lỗi kết nối với server` | `:8006` chưa chạy | Chạy assistant_service |
| Trả về template cũ | Sai IP Tailscale hoặc máy GPU tắt | Kiểm tra `tailscale status` + IP |
| `tailscale status` không thấy máy GPU | Chưa cùng tailnet | Đăng nhập lại Tailscale |
| Port 8006 bị chiếm | Có người khác chạy trên máy | Đổi port: `export ASSISTANT_PORT=8007` + sửa HTML |

## Lưu ý

- **Máy GPU phải bật và chạy `scripts\host_model_windows.bat`** thì mọi người mới dùng được
- Mỗi người tự chạy `:8006` trên máy mình — không chia sẻ port
- Frontend gọi `localhost:8006` nên **phải mở HTML trên cùng máy đang chạy `:8006`**
