"""Main FastAPI application for Hospital Chatbot."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from datetime import datetime
import os

from backend.config import settings
from backend.services.chatbot_service import ChatbotService
from backend.models.chat_models import ChatMessage, ChatResponse

# Initialize FastAPI app
app = FastAPI(
    title="Hospital Chatbot API",
    description="API cho chatbot hỗ trợ bệnh nhân",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Chatbot Service
chatbot_service = ChatbotService(api_key=settings.GEMINI_API_KEY)


@app.get("/")
async def root():
    """Root endpoint - serve HTML interface."""
    html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {
        "message": "Hospital Chatbot API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "frontend": "Open frontend/index.html in your browser"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """
    Endpoint để gửi tin nhắn đến chatbot.
    
    Args:
        message: ChatMessage chứa nội dung tin nhắn và patient_id (optional)
    
    Returns:
        ChatResponse với phản hồi từ chatbot
    """
    try:
        response = await chatbot_service.get_response(
            user_message=message.message,
            patient_id=message.patient_id,
            conversation_history=message.conversation_history or []
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi xử lý tin nhắn: {str(e)}"
        )


@app.post("/api/chat/stream")
async def chat_stream(message: ChatMessage):
    """
    Endpoint để stream phản hồi từ chatbot (real-time).
    
    Args:
        message: ChatMessage chứa nội dung tin nhắn
    
    Returns:
        Streaming response từ chatbot
    """
    try:
        async def generate():
            async for chunk in chatbot_service.get_stream_response(
                user_message=message.message,
                patient_id=message.patient_id,
                conversation_history=message.conversation_history or []
            ):
                yield f"data: {chunk}\n\n"
        
        from fastapi.responses import StreamingResponse
        return StreamingResponse(generate(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi stream phản hồi: {str(e)}"
        )


@app.get("/api/chat/history/{patient_id}")
async def get_chat_history(patient_id: str, limit: int = 50):
    """
    Lấy lịch sử chat của bệnh nhân.
    
    Args:
        patient_id: ID của bệnh nhân
        limit: Số lượng tin nhắn tối đa
    
    Returns:
        Danh sách lịch sử chat
    """
    try:
        history = await chatbot_service.get_chat_history(patient_id, limit)
        return {"patient_id": patient_id, "history": history}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi lấy lịch sử chat: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )

