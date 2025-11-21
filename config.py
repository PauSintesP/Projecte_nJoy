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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "43200"))  # 30 días
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))  # 7 días
    
    # Base de datos
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+pymysql://root:123@127.0.0.1/BBDDJoy")
    
    # CORS - Dominios permitidos
    ALLOWED_ORIGINS: List[str] = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost:3000,http://localhost:5173,http://localhost:8080"
    ).split(",")
    
    # Configuración de la aplicación
    APP_NAME: str = "nJoy API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

settings = Settings()
