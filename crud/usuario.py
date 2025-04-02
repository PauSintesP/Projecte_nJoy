from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import models
import schemas

def get_user_by_username(db: Session, username: str):
    """
    Retrieve a user by their username
    """
    return db.query(models.Usuario).filter(models.Usuario.user == username).first()

def create_user(db: Session, user: schemas.UsuarioCreate):
    """
    Create a new user without password hashing.
    """
    # Check if username already exists
    existing_user = get_user_by_username(db, user.user)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create user model instance with plain text password
    db_user = models.Usuario(
        user=user.user,
        ncompleto=user.ncompleto,
        fnacimiento=user.fnacimiento,
        email=user.email,
        contrasena=user.contrasena
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create user"
        )

def get_user(db: Session, user_id: int):
    """
    Retrieve a user by their ID
    """
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve multiple users with pagination
    """
    return db.query(models.Usuario).offset(skip).limit(limit).all()

def update_user(db: Session, user_id: int, user: schemas.UsuarioCreate):
    """
    Update an existing user without password hashing.
    """
    db_user = get_user(db, user_id)
    
    # Update fields
    db_user.user = user.user
    db_user.ncompleto = user.ncompleto
    db_user.email = user.email
    db_user.fnacimiento = user.fnacimiento
    
    # Update password directly if provided
    if user.contrasena:
        db_user.contrasena = user.contrasena
    
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update user"
        )

def delete_user(db: Session, user_id: int):
    """
    Delete a user by their ID
    """
    db_user = get_user(db, user_id)
    
    try:
        db.delete(db_user)
        db.commit()
        return {"detail": "User deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not delete user: {str(e)}"
        )

def authenticate_user(db: Session, email: str, password: str):
    """
    Authenticate a user by comparing plain text passwords.
    """
    user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not user:
        return False
    if user.contrasena != password:
        return False
    return user