# API Contract: Vietnamese Empathetic Assistant

## Services

Two independent FastAPI services, each runnable separately:

| Service | Port | Endpoint | Purpose |
|---------|------|----------|---------|
| Emotion Service | 8005 | POST `/predict_emotion` | Classify emotion from Vietnamese text |
| Assistant Service | 8006 | POST `/assistant` | Generate empathetic response |

## 1. Emotion Service

### POST /predict_emotion

**Request:**
```json
{
  "text": "Hôm nay mình thật sự rất vui vì đã đạt được mục tiêu!"
}
```

**Response (200):**
```json
{
  "emotion": "vui",
  "confidence": 0.85
}
```

**Emotion Labels:**
- `vui` — joy/happiness
- `buon` — sadness
- `lo_au` — anxiety
- `gian_du` — anger
- `trung_tinh` — neutral
- `hy_vong` — hope
- `that_vong` — disappointment

**Error Handling:**
- If the model fails, the service falls back to `trung_tinh` (neutral) with confidence `0.5`.
- Invalid input (empty text, text too long) returns `422 Unprocessable Entity`.

## 2. Assistant Service

### POST /assistant

**Request:**
```json
{
  "user_message": "Tôi cảm thấy rất lo âu trước kỳ thi.",
  "emotion": "lo_au"
}
```

**Response (200):**
```json
{
  "response": "Lo âu là dấu hiệu của sự quan tâm. Hãy hít sâu, đếm đến 5, và nhớ rằng bạn đã vượt qua nhiều khó khăn rồi."
}
```

**Error Handling:**
- Invalid emotion label returns `422 Unprocessable Entity`.
- Internal errors return `500 Internal Server Error`.

## 3. Health Checks

Both services expose:

```
GET /health → {"status": "ok", "service": "<service_name>"}
```

## 4. Logging

Each request is logged with:
- Timestamp
- Service name
- Request input (truncated to 100 chars)
- Response output (truncated to 100 chars)
- Errors with full stack trace

## 5. Run Instructions

### Prerequisites
```bash
pip install -r requirements.txt
```

### Run Emotion Service (port 8005)
```bash
python emotion_service.py
# or
uvicorn emotion_service:app --host 0.0.0.0 --port 8005
```

### Run Assistant Service (port 8006)
```bash
python assistant_service.py
# or
uvicorn assistant_service:app --host 0.0.0.0 --port 8006
```

### Run Both
```bash
# Terminal 1
uvicorn emotion_service:app --host 0.0.0.0 --port 8005

# Terminal 2
uvicorn assistant_service:app --host 0.0.0.0 --port 8006
```

### Docker (optional)
Each service can be containerized independently:
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY emotion_service.py .
CMD ["uvicorn", "emotion_service:app", "--host", "0.0.0.0", "--port", "8005"]
```

## 6. Data Flow

```
Frontend → [Emotion Service] → emotion label
            ↓
            → [Assistant Service] → empathetic response
            ↓
           Frontend
```

The frontend (or a gateway service) calls `/predict_emotion` first, then passes the emotion to `/assistant`.
