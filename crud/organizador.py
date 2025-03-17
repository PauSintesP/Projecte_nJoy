from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import models
import schemas
from typing import List
import re

def validate_email(email: str):
    """
    Basic email validation
    """
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )

def validate_phone(phone: str):
    """
    Basic phone number validation
    """
    phone_regex = r'^\+?1?\d{9,15}$'
    if not re.match(phone_regex, phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid phone number format"
        )

def create_organizador(db: Session, organizador: schemas.OrganizadorCreate):
    """
    Create a new organizer
    """
    try:
        # Validate email and phone
        validate_email(organizador.email)
        validate_phone(organizador.telefono)
        
        # Check if organizador already exists
        existing_organizador = db.query(models.Organizador).filter(
            (models.Organizador.dni == organizador.dni) | 
            (models.Organizador.email == organizador.email)
        ).first()
        
        if existing_organizador:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organizador with this DNI or email already exists"
            )
        
        # Create organizador model instance
        db_organizador = models.Organizador(
            dni=organizador.dni,
            ncompleto=organizador.ncompleto,
            email=organizador.email,
            telefono=organizador.telefono,
            web=organizador.web
        )
        
        db.add(db_organizador)
        db.commit()
        db.refresh(db_organizador)
        return db_organizador
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create organizador"
        )

def get_organizador(db: Session, dni: str):
    """
    Retrieve an organizer by their DNI
    """
    organizador = db.query(models.Organizador).filter(models.Organizador.dni == dni).first()
    if not organizador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organizador not found"
        )
    return organizador

def get_organizadores(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    ncompleto: str = None,
    email: str = None
):
    """
    Retrieve multiple organizers with optional filtering
    """
    query = db.query(models.Organizador)
    
    if ncompleto:
        query = query.filter(models.Organizador.ncompleto.ilike(f"%{ncompleto}%"))
    
    if email:
        query = query.filter(models.Organizador.email.ilike(f"%{email}%"))
    
    return query.offset(skip).limit(limit).all()

def update_organizador(db: Session, dni: str, organizador: schemas.OrganizadorCreate):
    """
    Update an existing organizer
    """
    db_organizador = get_organizador(db, dni)
    
    try:
        # Validate email and phone
        validate_email(organizador.email)
        validate_phone(organizador.telefono)
        
        # Check if new email is already in use by another organizador
        existing_organizador = db.query(models.Organizador).filter(
            models.Organizador.email == organizador.email,
            models.Organizador.dni != dni
        ).first()
        
        if existing_organizador:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use by another organizador"
            )
        
        # Update fields
        db_organizador.ncompleto = organizador.ncompleto
        db_organizador.email = organizador.email
        db_organizador.telefono = organizador.telefono
        db_organizador.web = organizador.web
        
        db.commit()
        db.refresh(db_organizador)
        return db_organizador
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update organizador"
        )

def delete_organizador(db: Session, dni: str):
    """
    Delete an organizer by their DNI
    """
    db_organizador = get_organizador(db, dni)
    
    try:
        # Check if organizador has any events
        eventos_count = db.query(models.Evento).filter(models.Evento.organizador_dni == dni).count()
        
        if eventos_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete organizador. {eventos_count} events are associated with this organizador."
            )
        
        db.delete(db_organizador)
        db.commit()
        return {"detail": "Organizador deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not delete organizador: {str(e)}"
        )