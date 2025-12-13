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
    if not _db_url:
        # Si no hay DATABASE_URL en las variables de entorno
        if os.getenv("ENV", "production") == "local":
            _db_url = "sqlite:///./njoy_local.db"
        else:
            _db_url = "mysql+pymysql://root:123@127.0.0.1/BBDDJoy"
    DATABASE_URL: str = _db_url
    
    # CORS - Dominios permitidos
    ALLOWED_ORIGINS: List[str] = [
        origin.strip() 
        for origin in os.getenv(
            "ALLOWED_ORIGINS", 
            "http://localhost:3000,http://localhost:5173,http://localhost:8080,https://web-njoy.vercel.app,https://web-njoy-kdt4bjgbo-pausintesps-projects.vercel.app"
        ).split(",")
    ]
    
    # Configuración de la aplicación
    APP_NAME: str = "nJoy API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

settings = Settings()
