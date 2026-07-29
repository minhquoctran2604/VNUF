"""Centralized config for VNUF backend services."""
import os

# ── Ports ────────────────────────────────────────────────────────────────────
EMOTION_PORT = int(os.getenv("EMOTION_PORT", "8005"))
ASSISTANT_PORT = int(os.getenv("ASSISTANT_PORT", "8006"))

# ── CORS — allow file:// access (frontend/index.html opened directly) ─────────
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# ── Service URLs (used by FE and any internal FE→BE plumbing) ───────────────
EMOTION_URL = f"http://localhost:{EMOTION_PORT}/predict_emotion"
ASSISTANT_URL = f"http://localhost:{ASSISTANT_PORT}/assistant"
