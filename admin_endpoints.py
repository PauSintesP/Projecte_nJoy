from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
from auth import get_db, get_current_active_user as get_current_user, hash_password

router = APIRouter()

@router.post("/admin/users", tags=["Admin"], response_model=schemas.Usuario)
def create_user_admin(
    user_data: schemas.AdminUserCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Crear un nuevo usuario (Solo Admin)
    
    Permite al administrador crear usuarios con cualquier rol directamente.
    """
    # Verificar que el usuario actual sea admin
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden crear usuarios"
        )
    
    # Verificar si el email ya existe
    db_user = db.query(models.Usuario).filter(models.Usuario.email == user_data.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Hashear la contraseña
    hashed_password = hash_password(user_data.password)
    
    # Crear el usuario con los datos proporcionados
    new_user = models.Usuario(
        nombre=user_data.nombre,
        apellidos=user_data.apellidos,
        email=user_data.email,
        password=hashed_password,
        fecha_nacimiento=user_data.fecha_nacimiento,
        pais=user_data.pais,
        role=user_data.role if user_data.role else 'user',
        is_active=user_data.is_active, # Now safe to access
        is_banned=user_data.is_banned  # Now safe to access
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user
