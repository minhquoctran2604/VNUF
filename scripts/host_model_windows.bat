@echo off
REM VNUF model host — double-click de serve Qwen3-4B LoRA tren :8007. GIU CUA SO NAY MO.
REM Neu repo/venv khong nam o D:\VNUF, sua 2 duong dan duoi cho khop may ban.
set ADAPTER_PATH=D:\VNUF\VNUF\adapter
set HF_HOME=D:\hf_cache
set MODEL_SERVE_PORT=8007
set HF_HUB_DISABLE_SYMLINKS_WARNING=1
D:\VNUF\.venv\Scripts\python.exe D:\VNUF\VNUF\backend\model_service.py
echo.
echo [host] service da dung (xem loi phia tren). Nhan phim bat ky de dong.
pause >nul
