"""Emotion classification service for Vietnamese empathetic assistant.

POST /predict_emotion → {"text": "..."} → {"emotion": "...", "confidence": float}
"""
import logging
import random
import re
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import CORS_ORIGINS, EMOTION_PORT

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [emotion] %(levelname)s %(message)s",
)
logger = logging.getLogger("emotion_service")

# ── Constants ────────────────────────────────────────────────────────────────
EMOTION_LABELS = [
    "vui",       # joy
    "buon",      # sadness
    "lo_au",     # anxiety
    "gian_du",   # anger
    "trung_tinh",# neutral
    "hy_vong",   # hope
    "that_vong", # disappointment
]
FALLBACK_EMOTION = "trung_tinh"

# ── Models ───────────────────────────────────────────────────────────────────
class EmotionRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)

class EmotionResponse(BaseModel):
    emotion: str
    confidence: float

# ── Keyword-based classifier ─────────────────────────────────────────────────
# ponytail: simple keyword matching, replace with trained model when available
# Keywords are ordered by specificity — longer/more specific keywords first.
# Emotion-specific keywords are checked in priority order to avoid overlap.
EMOTION_KEYWORDS: dict[str, list[str]] = {
    "vui": ["vui vẻ", "vui sướng", "hạnh phúc", "tuyệt vời", "tuyệt hảo", "hoàn hảo",
            "phấn khởi", "mừng", "vui lên", "siêu", "vui", "thích", "yêu", "đẹp", "tốt"],
    "buon": ["buồn bã", "buồn", "đau đớn", "tổn thương", "cô đơn", "đơn độc",
             "chán nản", "chán", "mệt mỏi", "mệt", "thất bại", "khóc", "đau"],
    "lo_au": ["lo âu", "lo lắng", "lo ngại", "bất an", "hồ nghi", "e dè",
              "bối rối", "hồi hộp", "sợ sệt", "run", "lo lắng", "lo âu", "lo"],
    "gian_du": ["phẫn nộ", "tức giận", "giận dữ", "thù hận", "phản bội",
                "bất công", "nổi giận", "cơn giận", "giận", "tức", "thù", "phẫn"],
    "hy_vong": ["hy vọng", "mong đợi", "mong muốn", "tin tốt", "phấn đấu",
                "kiên trì", "cơ hội", "tiến bộ", "phát triển", "tương lai",
                "mong", "hy vọng"],
    "that_vong": ["thất vọng", "thất bại", "hối tiếc", "hối hận", "tồi tệ",
                  "thất bực", "thất vọng", "kém", "tệ", "sai"],
    "trung_tinh": ["thường", "bình thường", "không rõ", "không chắc",
                   "cũng được", "tương đối", "ổn", "không sao"],
}

def _classify_emotion(text: str) -> tuple[str, float]:
    """Classify emotion from Vietnamese text using keyword matching.

    Returns (emotion, confidence) where confidence is in [0.0, 1.0].
    """
    text_lower = text.lower()
    scores: dict[str, float] = {label: 0.0 for label in EMOTION_LABELS}

    for emotion, keywords in EMOTION_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                # Weight by keyword length (longer = more specific)
                scores[emotion] += len(kw) / 10.0

    # Normalize scores
    total = sum(scores.values())
    if total > 0:
        for k in scores:
            scores[k] = scores[k] / total

    best_emotion = max(scores, key=scores.get)
    best_score = scores[best_emotion]

    # If no clear signal, fall back to neutral
    if best_score < 0.15:
        return FALLBACK_EMOTION, 0.5

    return best_emotion, round(best_score, 4)

# ── App ──────────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Emotion service starting up")
    yield
    logger.info("Emotion service shutting down")

app = FastAPI(
    title="VNUF Emotion Service",
    description="Vietnamese emotion classification endpoint",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict_emotion", response_model=EmotionResponse)
async def predict_emotion(req: EmotionRequest):
    """Predict emotion from Vietnamese text."""
    logger.info("predict_emotion called: text=%r", req.text[:100])

    try:
        emotion, confidence = _classify_emotion(req.text)
        logger.info("predict_emotion result: emotion=%s confidence=%.4f", emotion, confidence)
        return EmotionResponse(emotion=emotion, confidence=confidence)
    except Exception as e:
        logger.error("predict_emotion error: %s", e, exc_info=True)
        # Fallback: return neutral emotion on any failure
        logger.warning("Falling back to neutral emotion due to error")
        return EmotionResponse(emotion=FALLBACK_EMOTION, confidence=0.5)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "emotion_service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=EMOTION_PORT)
