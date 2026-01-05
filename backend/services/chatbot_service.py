"""Service xử lý chatbot với Google Gemini API."""
import google.generativeai as genai
from typing import List, Optional, AsyncGenerator
from datetime import datetime
import json

from backend.models.chat_models import ChatResponse, ChatHistoryItem


class ChatbotService:
    """Service để tương tác với Google Gemini API cho chatbot bệnh viện."""
    
    def __init__(self, api_key: str):
        """
        Khởi tạo ChatbotService.
        
        Args:
            api_key: Google Gemini API key
        """
        genai.configure(api_key=api_key)
        # Sử dụng model gemini-2.5-flash (nhanh và hiệu quả)
        # Có thể thay bằng 'models/gemini-2.5-pro' nếu cần độ chính xác cao hơn
        try:
            self.model = genai.GenerativeModel('models/gemini-2.5-flash')
        except Exception:
            # Fallback to latest models
            try:
                self.model = genai.GenerativeModel('models/gemini-flash-latest')
            except Exception:
                self.model = genai.GenerativeModel('models/gemini-pro-latest')
        
        # System prompt cho chatbot bệnh viện
        self.system_prompt = """Bạn là chatbot hỗ trợ bệnh nhân tại bệnh viện. 

QUY TẮC TRẢ LỜI:
1. TRẢ LỜI TRỰC TIẾP vào câu hỏi trước, không lan man
2. Trả lời NGẮN GỌN (2-4 câu), cụ thể và đúng trọng tâm
3. Nếu không biết, nói thẳng "Tôi không có thông tin về..." thay vì giải thích dài
4. Trả lời bằng tiếng Việt, thân thiện nhưng chuyên nghiệp

THÔNG TIN BỆNH VIỆN MẪU:
- Giờ làm việc: Thứ 2 - Thứ 6: 7h00 - 17h00, Thứ 7 - Chủ nhật: 7h00 - 12h00
- Các khoa chính: Nội khoa, Ngoại khoa, Sản phụ khoa, Nhi khoa, Thần kinh, Tim mạch, Tai mũi họng, Mắt, Da liễu
- Đặt lịch: Gọi hotline 1900-xxxx hoặc đăng ký online qua website
- Quy trình khám: Đăng ký → Lấy số thứ tự → Khám bệnh → Thanh toán → Lấy thuốc (nếu có)

VỀ TRIỆU CHỨNG VÀ BỆNH:
Khi bệnh nhân hỏi "triệu chứng này là bệnh gì" hoặc "dấu hiệu của bệnh gì":
1. PHẢI trả lời cụ thể về các khả năng bệnh có thể gây ra triệu chứng đó (2-4 khả năng phổ biến)
2. Giải thích ngắn gọn tại sao các triệu chứng đó có thể liên quan đến các bệnh đó
3. Gợi ý khoa cần khám
4. Nhấn mạnh cần khám bác sĩ để chẩn đoán chính xác

VÍ DỤ CÁCH TRẢ LỜI ĐÚNG:
Người dùng: "Tôi đau lưng, mệt mỏi, chán ăn, hay quên - đây là dấu hiệu bệnh gì?"
Chatbot: "Các triệu chứng đau lưng, mệt mỏi, chán ăn và hay quên có thể liên quan đến một số khả năng:
- Suy nhược cơ thể do thiếu dinh dưỡng hoặc căng thẳng kéo dài
- Các vấn đề về cột sống (thoái hóa, thoát vị đĩa đệm)
- Rối loạn chuyển hóa hoặc thiếu máu
- Các vấn đề về thần kinh hoặc tuần hoàn máu não

Bạn nên đến khám tại khoa Nội khoa tổng quát hoặc Thần kinh để được bác sĩ thăm khám, làm xét nghiệm và chẩn đoán chính xác. Bạn có muốn tôi hướng dẫn đặt lịch khám không?"

LƯU Ý: KHÔNG chỉ lặp lại triệu chứng, PHẢI giải thích các khả năng bệnh và hướng dẫn cụ thể.

NHIỆM VỤ:
- Trả lời câu hỏi về dịch vụ, giờ làm việc, quy trình khám bệnh
- Hướng dẫn về các khoa phù hợp với triệu chứng
- Cung cấp thông tin đặt lịch hẹn"""
        
        # Lưu trữ lịch sử chat (trong production nên dùng database)
        self.chat_history: dict[str, List[dict]] = {}
    
    def _format_conversation(self, user_message: str, history: List[dict]) -> str:
        """
        Format cuộc trò chuyện để gửi đến Gemini.
        
        Args:
            user_message: Tin nhắn hiện tại của người dùng
            history: Lịch sử cuộc trò chuyện
        
        Returns:
            Chuỗi đã format để gửi đến model
        """
        # Tạo prompt rõ ràng hơn với instruction cụ thể
        conversation = self.system_prompt + "\n\n"
        conversation += "=== CUỘC TRÒ CHUYỆN ===\n\n"
        
        # Thêm lịch sử cuộc trò chuyện (chỉ lấy 5 tin nhắn gần nhất để tập trung)
        if history:
            for item in history[-5:]:  # Giảm xuống 5 để tập trung hơn
                if isinstance(item, dict):
                    user_msg = item.get("user", item.get("message", ""))
                    bot_msg = item.get("bot", item.get("response", ""))
                    conversation += f"Bệnh nhân: {user_msg}\n"
                    conversation += f"Chatbot: {bot_msg}\n\n"
        
        # Thêm instruction rõ ràng trước câu hỏi cuối
        conversation += f"Bệnh nhân: {user_message}\n\n"
        
        # Kiểm tra nếu câu hỏi về triệu chứng/bệnh
        symptom_keywords = ['triệu chứng', 'dấu hiệu', 'bệnh gì', 'bệnh gì', 'nguy cơ', 'có thể', 'là gì']
        if any(keyword in user_message.lower() for keyword in symptom_keywords):
            conversation += "QUAN TRỌNG: Bệnh nhân đang hỏi về triệu chứng/bệnh. Bạn PHẢI:\n"
            conversation += "1. Liệt kê 2-4 khả năng bệnh có thể gây ra các triệu chứng đó\n"
            conversation += "2. Giải thích ngắn gọn tại sao\n"
            conversation += "3. Gợi ý khoa cần khám\n"
            conversation += "4. Nhấn mạnh cần khám bác sĩ\n"
            conversation += "KHÔNG chỉ lặp lại triệu chứng!\n\n"
        
        conversation += "Chatbot: "
        
        return conversation
    
    async def get_response(
        self, 
        user_message: str, 
        patient_id: Optional[str] = None,
        conversation_history: Optional[List[dict]] = None
    ) -> ChatResponse:
        """
        Lấy phản hồi từ chatbot.
        
        Args:
            user_message: Tin nhắn của người dùng
            patient_id: ID của bệnh nhân (optional)
            conversation_history: Lịch sử cuộc trò chuyện (optional)
        
        Returns:
            ChatResponse với phản hồi từ chatbot
        """
        try:
            # Format conversation
            prompt = self._format_conversation(
                user_message, 
                conversation_history or []
            )
            
            # Cấu hình generation để trả lời đầy đủ và cụ thể
            generation_config = {
                "temperature": 0.8,  # Tăng một chút để có câu trả lời tự nhiên hơn
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 2000,  # Tăng cao để đảm bảo trả lời đầy đủ, không bị cắt
            }
            
            # Gọi Gemini API với config
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Xử lý response từ Gemini - đảm bảo lấy đầy đủ
            if hasattr(response, 'text') and response.text:
                bot_response = response.text.strip()
            elif hasattr(response, 'candidates') and response.candidates:
                # Xử lý khi response có candidates
                candidate = response.candidates[0]
                
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    # Lấy tất cả các parts để đảm bảo đầy đủ
                    parts_text = []
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            parts_text.append(part.text)
                    bot_response = ''.join(parts_text).strip()
                else:
                    bot_response = str(candidate)
            else:
                bot_response = str(response)
            
            if not bot_response:
                bot_response = "Xin lỗi, tôi không thể tạo phản hồi. Vui lòng thử lại."
            
            # Lưu vào lịch sử
            if patient_id:
                if patient_id not in self.chat_history:
                    self.chat_history[patient_id] = []
                
                self.chat_history[patient_id].append({
                    "user": user_message,
                    "bot": bot_response,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Tạo gợi ý câu hỏi tiếp theo
            suggestions = self._generate_suggestions(user_message, bot_response)
            
            return ChatResponse(
                response=bot_response,
                patient_id=patient_id,
                timestamp=datetime.now(),
                suggestions=suggestions
            )
            
        except Exception as e:
            raise Exception(f"Lỗi khi gọi Gemini API: {str(e)}")
    
    async def get_stream_response(
        self,
        user_message: str,
        patient_id: Optional[str] = None,
        conversation_history: Optional[List[dict]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Lấy phản hồi stream từ chatbot (real-time).
        
        Args:
            user_message: Tin nhắn của người dùng
            patient_id: ID của bệnh nhân (optional)
            conversation_history: Lịch sử cuộc trò chuyện (optional)
        
        Yields:
            Các chunk của phản hồi từ chatbot
        """
        try:
            prompt = self._format_conversation(
                user_message,
                conversation_history or []
            )
            
            # Cấu hình generation cho streaming
            generation_config = {
                "temperature": 0.8,
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": 2000,  # Tăng cao để đảm bảo trả lời đầy đủ
            }
            
            # Stream response từ Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                stream=True
            )
            
            full_response = ""
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    yield json.dumps({
                        "chunk": chunk.text,
                        "done": False
                    }, ensure_ascii=False)
            
            # Lưu vào lịch sử
            if patient_id:
                if patient_id not in self.chat_history:
                    self.chat_history[patient_id] = []
                
                self.chat_history[patient_id].append({
                    "user": user_message,
                    "bot": full_response,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Gửi signal hoàn thành
            yield json.dumps({
                "chunk": "",
                "done": True,
                "full_response": full_response
            }, ensure_ascii=False)
            
        except Exception as e:
            yield json.dumps({
                "error": f"Lỗi khi stream phản hồi: {str(e)}",
                "done": True
            }, ensure_ascii=False)
    
    def _generate_suggestions(
        self, 
        user_message: str, 
        bot_response: str
    ) -> List[str]:
        """
        Tạo gợi ý câu hỏi tiếp theo dựa trên ngữ cảnh.
        
        Args:
            user_message: Tin nhắn của người dùng
            bot_response: Phản hồi từ chatbot
        
        Returns:
            Danh sách các gợi ý câu hỏi
        """
        # Gợi ý mặc định
        default_suggestions = [
            "Giờ làm việc của bệnh viện là gì?",
            "Tôi cần đặt lịch hẹn khám như thế nào?",
            "Các khoa nào đang hoạt động?",
            "Tôi cần mang theo gì khi đến khám?"
        ]
        
        return default_suggestions[:3]
    
    async def get_chat_history(
        self, 
        patient_id: str, 
        limit: int = 50
    ) -> List[ChatHistoryItem]:
        """
        Lấy lịch sử chat của bệnh nhân.
        
        Args:
            patient_id: ID của bệnh nhân
            limit: Số lượng tin nhắn tối đa
        
        Returns:
            Danh sách lịch sử chat
        """
        if patient_id not in self.chat_history:
            return []
        
        history = self.chat_history[patient_id][-limit:]
        
        return [
            ChatHistoryItem(
                message=item["user"],
                response=item["bot"],
                timestamp=datetime.fromisoformat(item["timestamp"]),
                patient_id=patient_id
            )
            for item in history
        ]

