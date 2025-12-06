from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import models
from database import SessionLocal
from config import settings

# Configuración de bcrypt para hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema de seguridad Bearer Token
security = HTTPBearer()

def get_db():
    """Dependency para obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    """
    Hash de contraseña usando bcrypt
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        Hash de la contraseña
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica que la contraseña coincida con el hash
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash de la contraseña almacenada
        
    Returns:
        True si coinciden, False en caso contrario
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un JWT access token
    
    Args:
        data: Datos a incluir en el token (ej: {"sub": user_id})
        expires_delta: Tiempo de expiración opcional
        
    Returns:
        Token JWT firmado
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """
    Crea un JWT refresh token con mayor duración
    
    Args:
        data: Datos a incluir en el token
        
    Returns:
        Refresh token JWT firmado
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    """
    Decodifica y valida un JWT token
    
    Args:
        token: JWT token a decodificar
        
    Returns:
        Payload del token
        
    Raises:
        HTTPException: Si el token es inválido o ha expirado
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> models.Usuario:
    """
    Dependency para obtener el usuario actual desde el token JWT
    
    Args:
        credentials: Credenciales del header Authorization
        db: Sesión de base de datos
        
    Returns:
        Usuario autenticado
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    token = credentials.credentials
    
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(models.Usuario).filter(models.Usuario.id == int(user_id)).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def get_current_active_user(
    current_user: models.Usuario = Depends(get_current_user)
) -> models.Usuario:
    """
    Dependency para verificar que el usuario esté activo
    
    Args:
        current_user: Usuario obtenido del token
        
    Returns:
        Usuario activo
        
    Raises:
        HTTPException: Si el usuario está inactivo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    # Verificar que el usuario no esté baneado
    if current_user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario baneado"
        )
    
    return current_user

def authenticate_user(db: Session, email: str, password: str) -> Optional[models.Usuario]:
    """
    Autentica un usuario con email y contraseña
    
    Args:
        db: Sesión de base de datos
        email: Email del usuario
        password: Contraseña en texto plano
        
    Returns:
        Usuario si las credenciales son correctas, None en caso contrario
    """
    user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    
    if not user:
        return None
    
    if not verify_password(password, user.password):
        return None
    
    return user

def get_current_promotor(
    current_user: models.Usuario = Depends(get_current_active_user)
) -> models.Usuario:
    """
    Dependency para verificar que el usuario sea promotor
    
    Args:
        current_user: Usuario obtenido del token
        
    Returns:
        Usuario promotor
        
    Raises:
        HTTPException: Si el usuario no es promotor
    """
    if current_user.role not in ['promotor', 'owner', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los promotores, owners y admins pueden realizar esta acción"
        )
    return current_user

def get_current_admin(
    current_user: models.Usuario = Depends(get_current_active_user)
) -> models.Usuario:
    """
    Dependency para verificar que el usuario sea administrador
    
    Args:
        current_user: Usuario obtenido del token
        
    Returns:
        Usuario admin
        
    Raises:
        HTTPException: Si el usuario no es admin
    """
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden realizar esta acción"
        )
    return current_user

def get_current_owner_or_admin(
    current_user: models.Usuario = Depends(get_current_active_user)
) -> models.Usuario:
    """
    Dependency para verificar que el usuario sea owner o admin
    
    Args:
        current_user: Usuario obtenido del token
        
    Returns:
        Usuario owner o admin
        
    Raises:
        HTTPException: Si el usuario no es owner ni admin
    """
    if current_user.role not in ['owner', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los owners y administradores pueden realizar esta acción"
        )
    return current_user

def get_current_scanner(
    current_user: models.Usuario = Depends(get_current_active_user)
) -> models.Usuario:
    """
    Dependency para verificar que el usuario tenga permisos de scanner
    Scanner role puede escanear tickets pero no crear/editar eventos
    
    Args:
        current_user: Usuario obtenido del token
        
    Returns:
        Usuario scanner, promotor, owner o admin
        
    Raises:
        HTTPException: Si el usuario no tiene permisos de scanner
    """
    if current_user.role not in ['scanner', 'promotor', 'owner', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para escanear tickets"
        )
    return current_user
