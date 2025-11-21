from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import models, schemas
from auth import hash_password, verify_password

def get_user_by_email(db: Session, email: str):
    """Obtener usuario por email"""
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()

def login_user(db: Session, email: str, contrasena: str):
    """
    Login de usuario con verificación de contraseña hasheada
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    
    # Verificar contraseña hasheada
    if not verify_password(contrasena, user.contrasena):
        return None
    
    return user

def create_item(db: Session, model, schema):
    """
    Crear un nuevo item en la base de datos
    Si es un Usuario, hashear la contraseña
    """
    item_dict = schema.dict()
    
    # Si es un usuario, hashear la contraseña antes de guardar
    if model == models.Usuario and 'contrasena' in item_dict:
        item_dict['contrasena'] = hash_password(item_dict['contrasena'])
    
    # Verificar si ya existe (para evitar duplicados)
    if model == models.Usuario:
        if get_user_by_email(db, item_dict['email']):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        existing_user = db.query(models.Usuario).filter(
            models.Usuario.user == item_dict['user']
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya existe"
            )
    
    db_item = model(**item_dict)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_items(db: Session, model, skip: int = 0, limit: int = 100):
    """Obtener lista de items con paginación"""
    return db.query(model).offset(skip).limit(limit).all()

def get_item(db: Session, model, item_id: int):
    """Obtener un item por ID"""
    item = db.query(model).filter_by(id=item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} no encontrado"
        )
    return item

def update_item(db: Session, model, item_id: int, schema):
    """
    Actualizar un item existente
    Si es un Usuario y se actualiza la contraseña, hashearla
    """
    db_item = db.query(model).filter_by(id=item_id).first()
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} no encontrado"
        )
    
    update_data = schema.dict(exclude_unset=True)
    
    # Si es un usuario y se actualiza la contraseña, hashearla
    if model == models.Usuario and 'contrasena' in update_data:
        update_data['contrasena'] = hash_password(update_data['contrasena'])
    
    for key, value in update_data.items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_item(db: Session, model, item_id: int):
    """Eliminar un item por ID"""
    db_item = db.query(model).filter_by(id=item_id).first()
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} no encontrado"
        )
    
    db.delete(db_item)
    db.commit()
    return {"detail": f"{model.__name__} eliminado correctamente"}
