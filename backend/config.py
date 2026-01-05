"""Configuration settings for the application."""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Gemini API Configuration
    GEMINI_API_KEY: str  # Required - must be set in .env file
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./hospital_chatbot.db"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS Configuration - read as string, will be parsed
    CORS_ORIGINS: str = "*"
    
    def get_cors_origins(self) -> list[str]:
        """Parse CORS_ORIGINS from string to list."""
        cors_value = os.getenv("CORS_ORIGINS", self.CORS_ORIGINS)
        if cors_value == "*":
            return ["*"]
        # Split by comma and strip whitespace
        return [origin.strip() for origin in cors_value.split(",") if origin.strip()]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
try:
    settings = Settings()
except Exception as e:
    import sys
    print("ERROR: Không thể load cấu hình từ .env file!")
    print("Vui lòng tạo file .env từ .env.example và thêm GEMINI_API_KEY")
    print(f"Chi tiết lỗi: {str(e)}")
    sys.exit(1)

