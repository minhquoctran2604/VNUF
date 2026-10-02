"""LLM assistant service for Vietnamese empathetic assistant.

POST /assistant → {"user_message": "...", "emotion": "..."} → {"response": "..."}
"""
import logging
import os
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from config import CORS_ORIGINS, ASSISTANT_PORT, MODEL_SERVE_URL

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [assistant] %(levelname)s %(message)s",
)
logger = logging.getLogger("assistant_service")

# ── Constants ────────────────────────────────────────────────────────────────
VALID_EMOTIONS = {
    "vui", "buon", "lo_au", "gian_du", "trung_tinh", "hy_vong", "that_vong",
}
FALLBACK_EMOTION = "trung_tinh"

# ── Emotion-specific response templates ──────────────────────────────────────
# ponytail: template-based responses, replace with LLM when available
EMOTION_RESPONSES: dict[str, list[str]] = {
    "vui": [
        "Tuyệt vời! Niềm vui của bạn thật sự lan tỏa. Hãy giữ nụ cười ấy nhé!",
        "Mình rất vui khi bạn cảm thấy tốt! Hãy tận hưởng khoảnh khắc này.",
        "Niềm vui cháy lên như ngọn lửa — đừng để nó tắt. Cứ tiếp tục thế này!",
    ],
    "buon": [
        "Mình hiểu cảm giác buồn của bạn. Đôi khi chỉ cần được lắng nghe là đủ. Hãy kể cho mình nghe.",
        "Buồn là cảm xúc tự nhiên. Đừng ép mình phải vui ngay. Hãy cho phép cảm xúc lưu trữ vào lòng.",
        "Nỗi đau sẽ qua. Bạn không cô đơn đây — mình ở đây lắng nghe.",
    ],
    "lo_au": [
        "Lo âu là dấu hiệu của sự quan tâm. Hãy hít sâu, đếm đến 5, và nhớ rằng bạn đã vượt qua nhiều khó khăn rồi.",
        "Cảm xúc lo âu sẽ qua. Hãy tập trung vào hơi thở và điều bạn có thể kiểm soát ngay bây giờ.",
        "Lo âu không phải kẻ thù — nó là cơ chế bảo vệ. Hãy để nó qua mà không để nó chi phối.",
    ],
    "gian_du": [
        "Tức giận là năng lượng. Hãy kêu lên một cách lành mạnh — viết ra, chạy bộ, hoặc nói với người tin cậy.",
        "Cơn giận sẽ qua. Đừng để nó khiến bạn mất đi bình yên. Hãy thở sâu và chọn cách ứng xử khôn ngoan.",
        "Giận dữ là con người. Nhưng bạn là người chọn cách phản hồi. Hãy để hơi thở dẫn lối.",
    ],
    "trung_tinh": [
        "Cảm xúc trung tính — một không gian yên bình để suy ngẫm. Điều gì đang nằm trong tâm hồn bạn?",
        "Trung tính là sự cân bằng. Hãy để nó dẫn bạn đến những suy nghĩ mới.",
        "Bạn đang ở không gian trung tính — một thời điểm để lắng nghe chính mình.",
    ],
    "hy_vong": [
        "Hy vọng là ánh sáng ở chân trời. Hãy tiếp tục bước đi — mỗi bước là một phần của hành trình.",
        "Niềm tin vào tương lai là sức mạnh lớn nhất. Hãy giữ nó cháy lên!",
        "Hy vọng không bao giờ chết. Nó là động lực để bạn vượt qua mọi thử thách.",
    ],
    "that_vong": [
        "Thất vọng là phần không thể thiếu của hành trình. Nhưng từ đây, bạn có thể chọn hướng đi mới.",
        "Mỗi lần thất vọng là một bài học. Hãy học hỏi và tiếp tục — bạn mạnh hơn bạn nghĩ.",
        "Thất vọng tạm thời, nhưng sự kiên cường của bạn là vĩnh cửu. Hãy tiếp tục.",
    ],
}

def _generate_response(user_message: str, emotion: str) -> str:
    """Generate empathetic response based on user message and detected emotion."""
    import random

    if emotion not in VALID_EMOTIONS:
        emotion = FALLBACK_EMOTION

    templates = EMOTION_RESPONSES.get(emotion, EMOTION_RESPONSES[FALLBACK_EMOTION])
    base_response = random.choice(templates)

    # Append acknowledgment of the user's message
    return f"{base_response}"

# ── Models ───────────────────────────────────────────────────────────────────
class AssistantRequest(BaseModel):
    user_message: str = Field(..., min_length=1, max_length=2000)
    # Optional — frontend calls assistant directly (keyword emotion service
    # bypassed: too weak vs LLM semantics). Defaults to neutral.
    emotion: str = Field(default="trung_tinh", min_length=1)

    @field_validator("emotion")
    @classmethod
    def validate_emotion(cls, v: str) -> str:
        v_lower = v.lower().strip()
        if v_lower not in VALID_EMOTIONS:
            raise ValueError(
                f"Invalid emotion '{v}'. Must be one of: {', '.join(sorted(VALID_EMOTIONS))}"
            )
        return v_lower

class AssistantResponse(BaseModel):
    response: str

# ── App ──────────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Assistant service starting up")
    yield
    logger.info("Assistant service shutting down")

app = FastAPI(
    title="VNUF Assistant Service",
    description="Vietnamese empathetic LLM assistant endpoint",
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

@app.post("/assistant", response_model=AssistantResponse)
async def assistant(req: AssistantRequest):
    """Generate empathetic response using model service if available, else template fallback."""
    logger.info(
        "assistant called: user_message=%r emotion=%s",
        req.user_message[:100], req.emotion,
    )

    # 1. Try calling fine-tuned Model Service (GPU vLLM + LoRA)
    use_model = os.getenv("USE_MODEL_SERVICE", "true").lower() == "true"
    if use_model:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    MODEL_SERVE_URL,
                    json={
                        "messages": [{"role": "user", "content": req.user_message}],
                        "max_new_tokens": 256,
                        "temperature": 0.7,
                        "top_p": 0.9,
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    model_response = data.get("response", "")
                    if model_response:
                        logger.info("assistant (model) response: %r", model_response[:100])
                        return AssistantResponse(response=model_response)
        except Exception as e:
            logger.warning("Model service unavailable (%s), falling back to templates", e)

    # 2. Standby / Fallback: Template-based empathetic generator
    try:
        response = _generate_response(req.user_message, req.emotion)
        logger.info("assistant (template) response: %r", response[:100])
        return AssistantResponse(response=response)
    except Exception as e:
        logger.error("assistant error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "assistant_service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=ASSISTANT_PORT)
