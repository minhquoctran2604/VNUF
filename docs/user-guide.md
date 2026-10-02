# Hướng dẫn sử dụng VNUF Assistant

## Mỗi lần dùng

```powershell
cd D:\VNUF\VNUF
git pull origin master
.\scripts\host_model_windows.bat
```

Terminal 2:
```powershell
$env:MODEL_SERVE_HOST = "127.0.0.1"; $env:MODEL_SERVE_PORT = "8007"
python D:\VNUF\VNUF\backend\assistant_service.py
```

Double-click `frontend/index.html` → chat.

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

Cài đặt lần đầu → xem [setup-guide.md](setup-guide.md)
