# Hospital Project 2025 - AI

Dự án bệnh viện năm 2025 với tích hợp AI - Chatbot hỗ trợ bệnh nhân sử dụng Google Gemini.

## Mô tả

Dự án quản lý bệnh viện với chatbot AI sử dụng Google Gemini API để hỗ trợ bệnh nhân:
- Trả lời câu hỏi về dịch vụ bệnh viện
- Hướng dẫn quy trình khám bệnh
- Cung cấp thông tin về các khoa, phòng ban
- Hỗ trợ đặt lịch hẹn khám
- Lưu trữ lịch sử chat

## Cấu trúc dự án

```
Hospital_Prj_2025-1_AI/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── models/
│   │   ├── __init__.py
│   │   └── chat_models.py  # Pydantic models
│   └── services/
│       ├── __init__.py
│       └── chatbot_service.py  # Gemini AI service
├── requirements.txt         # Python dependencies
├── run.py                  # Script để chạy server
└── README.md
```

## Cài đặt

### 1. Cài đặt Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Cấu hình môi trường

Tạo file `.env` trong thư mục gốc (hoặc copy từ `.env.example`):

```env
GEMINI_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./hospital_chatbot.db
HOST=0.0.0.0
PORT=8000
```

**Lưu ý:** API key phải được set trong file `.env`. Copy file `.env.example` thành `.env` và điền API key của bạn.

## Sử dụng

### Chạy server

```bash
python run.py
```

Hoặc:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Server sẽ chạy tại: `http://localhost:8000`

### API Documentation

Sau khi chạy server, truy cập:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### API Endpoints

#### 1. Health Check
```
GET /health
```

#### 2. Chat với chatbot
```
POST /api/chat
Content-Type: application/json

{
  "message": "Xin chào, tôi muốn biết giờ làm việc của bệnh viện",
  "patient_id": "P001",  // optional
  "conversation_history": []  // optional
}
```

**Response:**
```json
{
  "response": "Xin chào! Bệnh viện làm việc từ 7h sáng đến 5h chiều...",
  "patient_id": "P001",
  "timestamp": "2025-01-XX...",
  "suggestions": [
    "Giờ làm việc của bệnh viện là gì?",
    "Tôi cần đặt lịch hẹn khám như thế nào?",
    "Các khoa nào đang hoạt động?"
  ]
}
```

#### 3. Chat với streaming (real-time)
```
POST /api/chat/stream
Content-Type: application/json

{
  "message": "Tôi cần đặt lịch khám",
  "patient_id": "P001"
}
```

#### 4. Lấy lịch sử chat
```
GET /api/chat/history/{patient_id}?limit=50
```

### Ví dụ sử dụng với cURL

```bash
# Chat với chatbot
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Xin chào, tôi muốn biết giờ làm việc",
    "patient_id": "P001"
  }'

# Lấy lịch sử chat
curl "http://localhost:8000/api/chat/history/P001?limit=10"
```

### Ví dụ sử dụng với Python

```python
import requests

# Chat với chatbot
response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "message": "Xin chào, tôi muốn đặt lịch khám",
        "patient_id": "P001"
    }
)
print(response.json())
```

## Tính năng

- ✅ Chatbot AI với Google Gemini
- ✅ API RESTful với FastAPI
- ✅ Streaming response (real-time)
- ✅ Lưu trữ lịch sử chat
- ✅ Hỗ trợ CORS
- ✅ API documentation tự động (Swagger/ReDoc)
- ✅ Error handling

## Công nghệ sử dụng

- **Backend Framework:** FastAPI
- **AI Model:** Google Gemini 2.5 Flash
- **Language:** Python 3.8+
- **API Documentation:** Swagger UI, ReDoc

## Deployment

Backend đã được chuẩn bị sẵn để deploy. Xem file `DEPLOY.md` để biết chi tiết các cách deploy:

- **Docker**: Sử dụng `docker-compose up -d`
- **VPS/Cloud**: Deploy với systemd hoặc PM2
- **Cloud Platforms**: Railway, Render, Fly.io

### Quick Start với Docker

```bash
# 1. Tạo file .env từ .env.example
cp .env.example .env
# Chỉnh sửa .env và thêm GEMINI_API_KEY

# 2. Build và chạy
docker-compose up -d

# 3. Kiểm tra
curl http://localhost:8000/health
```

Xem `DEPLOY.md` để biết thêm chi tiết.

## Giấy phép

[Thêm thông tin giấy phép]

