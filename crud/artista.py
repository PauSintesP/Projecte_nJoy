from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import models
import schemas
from typing import List, Optional

def create_artista(db: Session, artista: schemas.ArtistaCreate):
    """
    Create a new artist
    """
    try:
        # Create artist model instance
        db_artista = models.Artista(
            nartistico=artista.nartistico,
            nreal=artista.nreal
        )
        
        db.add(db_artista)
        db.commit()
        db.refresh(db_artista)
        return db_artista
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create artist. Check input data."
        )

def get_artista(db: Session, artista_id: int):
    """
    Retrieve an artist by their ID
    """
    artista = db.query(models.Artista).filter(models.Artista.id == artista_id).first()
    if not artista:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artist not found"
        )
    return artista

def get_artistas(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    nartistico: str = None
):
    """
    Retrieve multiple artists with optional filtering
    """
    query = db.query(models.Artista)
    
    if nartistico:
        query = query.filter(models.Artista.nartistico.ilike(f"%{nartistico}%"))
    
    return query.offset(skip).limit(limit).all()

def update_artista(db: Session, artista_id: int, artista: schemas.ArtistaCreate):
    """
    Update an existing artist
    """
    db_artista = get_artista(db, artista_id)
    
    try:
        # Update fields
        db_artista.nartistico = artista.nartistico
        db_artista.nreal = artista.nreal
        
        db.commit()
        db.refresh(db_artista)
        return db_artista
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update artist. Check input data."
        )

def delete_artista(db: Session, artista_id: int):
    """
    Delete an artist by their ID
    """
    db_artista = get_artista(db, artista_id)
    
    try:
        db.delete(db_artista)
        db.commit()
        return {"detail": "Artist deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not delete artist: {str(e)}"
        )