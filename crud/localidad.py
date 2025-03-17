from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import models
import schemas
from typing import List

def create_localidad(db: Session, localidad: schemas.LocalidadCreate):
    """
    Create a new location
    """
    try:
        # Check if location already exists
        existing_localidad = db.query(models.Localidad).filter(
            models.Localidad.ciudad.ilike(localidad.ciudad)
        ).first()
        
        if existing_localidad:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Location already exists"
            )
        
        # Create localidad model instance
        db_localidad = models.Localidad(
            ciudad=localidad.ciudad
        )
        
        db.add(db_localidad)
        db.commit()
        db.refresh(db_localidad)
        return db_localidad
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create location"
        )

def get_localidad(db: Session, localidad_id: int):
    """
    Retrieve a location by its ID
    """
    localidad = db.query(models.Localidad).filter(models.Localidad.id == localidad_id).first()
    if not localidad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    return localidad

def get_localidades(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    ciudad: str = None
):
    """
    Retrieve multiple locations with optional filtering
    """
    query = db.query(models.Localidad)
    
    if ciudad:
        query = query.filter(models.Localidad.ciudad.ilike(f"%{ciudad}%"))
    
    return query.offset(skip).limit(limit).all()

def update_localidad(db: Session, localidad_id: int, localidad: schemas.LocalidadCreate):
    """
    Update an existing location
    """
    db_localidad = get_localidad(db, localidad_id)
    
    try:
        # Check if new city name already exists
        existing_localidad = db.query(models.Localidad).filter(
            models.Localidad.ciudad.ilike(localidad.ciudad),
            models.Localidad.id != localidad_id
        ).first()
        
        if existing_localidad:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Location with this name already exists"
            )
        
        # Update fields
        db_localidad.ciudad = localidad.ciudad
        
        db.commit()
        db.refresh(db_localidad)
        return db_localidad
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update location"
        )

def delete_localidad(db: Session, localidad_id: int):
    """
    Delete a location by its ID
    """
    db_localidad = get_localidad(db, localidad_id)
    
    try:
        # Check if location is used in any events
        eventos_count = db.query(models.Evento).filter(models.Evento.localidad_id == localidad_id).count()
        
        if eventos_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete location. {eventos_count} events are associated with this location."
            )
        
        db.delete(db_localidad)
        db.commit()
        return {"detail": "Location deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not delete location: {str(e)}"
        )