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

# ── Model LLM service (vLLM + LoRA, runs on GPU machine) ───────────────────
MODEL_SERVE_HOST = os.getenv("MODEL_SERVE_HOST", "localhost")
MODEL_SERVE_PORT = int(os.getenv("MODEL_SERVE_PORT", "8007"))
MODEL_SERVE_URL = f"http://{MODEL_SERVE_HOST}:{MODEL_SERVE_PORT}/generate"
