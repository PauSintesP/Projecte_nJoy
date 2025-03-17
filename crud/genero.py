from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import models
import schemas
from typing import List, Optional

def create_genero(db: Session, genero: schemas.GeneroCreate):
    """
    Create a new genre
    """
    try:
        # Create genre model instance
        db_genero = models.Genero(
            nombre=genero.nombre
        )
        
        db.add(db_genero)
        db.commit()
        db.refresh(db_genero)
        return db_genero
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create genre. Check input data."
        )

def get_genero(db: Session, genero_id: int):
    """
    Retrieve a genre by its ID
    """
    genero = db.query(models.Genero).filter(models.Genero.id == genero_id).first()
    if not genero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Genre not found"
        )
    return genero

def get_generos(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    nombre: str = None
):
    """
    Retrieve multiple genres with optional filtering
    """
    query = db.query(models.Genero)
    
    if nombre:
        query = query.filter(models.Genero.nombre.ilike(f"%{nombre}%"))
    
    return query.offset(skip).limit(limit).all()

def update_genero(db: Session, genero_id: int, genero: schemas.GeneroCreate):
    """
    Update an existing genre
    """
    db_genero = get_genero(db, genero_id)
    
    try:
        # Update fields
        db_genero.nombre = genero.nombre
        
        db.commit()
        db.refresh(db_genero)
        return db_genero
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update genre. Check input data."
        )

def delete_genero(db: Session, genero_id: int):
    """
    Delete a genre by its ID
    """
    db_genero = get_genero(db, genero_id)
    
    try:
        db.delete(db_genero)
        db.commit()
        return {"detail": "Genre deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not delete genre: {str(e)}"
        )