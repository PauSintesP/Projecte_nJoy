import os
from dotenv import load_dotenv
from typing import List

# Cargar variables de entorno desde .env
load_dotenv()

class Settings:
    """Configuración centralizada de la aplicación"""
    
    # Seguridad JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production-min-32-chars")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))  # 1 hora
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))  # 30 días
    
    # Base de datos
    # Determinar la DATABASE_URL según el entorno
    _db_url = os.getenv("DATABASE_URL", "")
    
    # Soporte automático para Vercel Postgres / Neon
    if not _db_url:
        _db_url = os.getenv("POSTGRES_URL", "")
        if _db_url and _db_url.startswith("postgres://"):
            _db_url = _db_url.replace("postgres://", "postgresql://", 1)

    # Soporte para MySQL o fallbacks
    if not _db_url:
        # Si no hay DATABASE_URL en las variables de entorno
        if os.getenv("ENV", "production") == "local":
            _db_url = "sqlite:///./njoy_local.db"
        else:
            # Fallback peligroso para prod, pero mantenemos por compatibilidad si no se configura nada
             _db_url = "mysql+pymysql://root:123@127.0.0.1/BBDDJoy"
    
    DATABASE_URL: str = _db_url
    
    # CORS - Dominios permitidos
    # CORS - Dominios permitidos
    ALLOWED_ORIGINS: List[str] = [
        origin.strip() 
        for origin in os.getenv(
            "ALLOWED_ORIGINS", 
            "http://localhost:3000,http://localhost:5173,http://localhost:8080,https://web-njoy.vercel.app,https://projecte-n-joy.vercel.app"
        ).split(",")
    ]
    
    
    # Configuración de la aplicación
    APP_NAME: str = "nJoy API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Email Configuration (Resend)
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "onboarding@resend.dev")
    EMAIL_FROM_NAME: str = os.getenv("EMAIL_FROM_NAME", "nJoy")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    VERIFICATION_TOKEN_EXPIRY_HOURS: int = int(os.getenv("VERIFICATION_TOKEN_EXPIRY_HOURS", "24"))

settings = Settings()
