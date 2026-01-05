"""Pydantic models for chat API."""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ChatMessage(BaseModel):
    """Model cho tin nhắn từ người dùng."""
    message: str = Field(..., description="Nội dung tin nhắn")
    patient_id: Optional[str] = Field(None, description="ID của bệnh nhân (nếu có)")
    conversation_history: Optional[List[dict]] = Field(
        None, 
        description="Lịch sử cuộc trò chuyện trước đó"
    )


class ChatResponse(BaseModel):
    """Model cho phản hồi từ chatbot."""
    response: str = Field(..., description="Phản hồi từ chatbot")
    patient_id: Optional[str] = Field(None, description="ID của bệnh nhân")
    timestamp: datetime = Field(default_factory=datetime.now, description="Thời gian phản hồi")
    suggestions: Optional[List[str]] = Field(
        None, 
        description="Gợi ý câu hỏi tiếp theo"
    )


class ChatHistoryItem(BaseModel):
    """Model cho một mục trong lịch sử chat."""
    message: str
    response: str
    timestamp: datetime
    patient_id: Optional[str] = None

