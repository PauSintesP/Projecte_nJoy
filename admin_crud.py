"""
CRUD operations específicas para administración
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional, Dict
import models


def get_all_users_admin(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    role_filter: Optional[str] = None,
    is_active_filter: Optional[bool] = None,
    is_banned_filter: Optional[bool] = None,
    search: Optional[str] = None
) -> List[models.Usuario]:
    """
    Obtener todos los usuarios con filtros opcionales (solo para admin)
    
    Args:
        db: Session de base de datos
        skip: Número de registros a saltar (paginación)
        limit: Número de registros a retornar
        role_filter: Filtrar por rol específico
        is_active_filter: Filtrar por estado activo
        is_banned_filter: Filtrar por estado baneado
        search: Buscar por nombre, apellidos o email
    
    Returns:
        Lista de usuarios que coinciden con los filtros
    """
    query = db.query(models.Usuario)
    
    # Aplicar filtros
    if role_filter:
        query = query.filter(models.Usuario.role == role_filter)
    
    if is_active_filter is not None:
        query = query.filter(models.Usuario.is_active == is_active_filter)
    
    if is_banned_filter is not None:
        query = query.filter(models.Usuario.is_banned == is_banned_filter)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (models.Usuario.nombre.ilike(search_pattern)) |
            (models.Usuario.apellidos.ilike(search_pattern)) |
            (models.Usuario.email.ilike(search_pattern))
        )
    
    return query.offset(skip).limit(limit).all()


def update_user_role(db: Session, user_id: int, new_role: str) -> models.Usuario:
    """
    Cambiar el rol de un usuario
    
    Args:
        db: Session de base de datos
        user_id: ID del usuario
        new_role: Nuevo rol (user, promotor, owner, admin)
    
    Returns:
        Usuario actualizado
    
    Raises:
        HTTPException: Si el usuario no existe o el rol es inválido
    """
    valid_roles = ['user', 'promotor', 'owner', 'admin']
    if new_role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rol inválido. Debe ser uno de: {', '.join(valid_roles)}"
        )
    
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    user.role = new_role
    db.commit()
    db.refresh(user)
    return user


def ban_user(db: Session, user_id: int) -> models.Usuario:
    """
    Banear un usuario
    
    Args:
        db: Session de base de datos
        user_id: ID del usuario a banear
    
    Returns:
        Usuario actualizado
    
    Raises:
        HTTPException: Si el usuario no existe o ya está baneado
    """
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya está baneado"
        )
    
    user.is_banned = True
    user.is_active = False  # También desactivar
    db.commit()
    db.refresh(user)
    return user


def unban_user(db: Session, user_id: int) -> models.Usuario:
    """
    Desbanear un usuario
    
    Args:
        db: Session de base de datos
        user_id: ID del usuario a desbanear
    
    Returns:
        Usuario actualizado
    
    Raises:
        HTTPException: Si el usuario no existe o no está baneado
    """
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    if not user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario no está baneado"
        )
    
    user.is_banned = False
    user.is_active = True  # Reactivar
    db.commit()
    db.refresh(user)
    return user


def delete_user_admin(db: Session, user_id: int) -> Dict[str, str]:
    """
    Eliminar un usuario (solo admin)
    
    Args:
        db: Session de base de datos
        user_id: ID del usuario a eliminar
    
    Returns:
        Mensaje de confirmación
    
    Raises:
        HTTPException: Si el usuario no existe
    """
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # TODO: Considerar si eliminar en cascada tickets, pagos, etc.
    # Por ahora solo eliminamos el usuario
    db.delete(user)
    db.commit()
    return {"detail": f"Usuario {user.email} eliminado correctamente"}


def get_user_statistics(db: Session) -> Dict[str, int]:
    """
    Obtener estadísticas de usuarios
    
    Args:
        db: Session de base de datos
    
    Returns:
        Diccionario con estadísticas
    """
    total_users = db.query(models.Usuario).count()
    active_users = db.query(models.Usuario).filter(models.Usuario.is_active == True).count()
    banned_users = db.query(models.Usuario).filter(models.Usuario.is_banned == True).count()
    
    # Contar por roles
    users_by_role = {}
    for role in ['user', 'promotor', 'owner', 'admin']:
        count = db.query(models.Usuario).filter(models.Usuario.role == role).count()
        users_by_role[role] = count
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "banned_users": banned_users,
        "inactive_users": total_users - active_users,
        **{f"{role}_count": count for role, count in users_by_role.items()}
    }
