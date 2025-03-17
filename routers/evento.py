from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

import crud
import models
import schemas
from database import get_db
from routers.usuario import get_current_user

# Router configuration
router = APIRouter()

# Event Creation Endpoint
@router.post("/", response_model=schemas.EventoResponse)
def create_evento(
    evento: schemas.EventoCreate, 
    db: Session = Depends(get_db),
   
):
    """
    Create a new event (Authenticated users only)
    """
    return crud.create_evento(db=db, evento=evento)

# Get Event by ID
@router.get("/{evento_id}", response_model=schemas.EventoResponse)
def read_evento(
    evento_id: int, 
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific event by ID
    """
    return crud.get_evento(db, evento_id)

# List Events with Optional Filtering
@router.get("/", response_model=List[schemas.EventoResponse])
def read_eventos(
    skip: int = 0, 
    limit: int = 100,
    nombre: Optional[str] = None,
    tipo: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List events with optional filtering by name and type
    """
    return crud.get_eventos(db, skip=skip, limit=limit, nombre=nombre, tipo=tipo)

# Update Event
@router.put("/{evento_id}", response_model=schemas.EventoResponse)
def update_evento(
    evento_id: int, 
    evento: schemas.EventoCreate, 
    db: Session = Depends(get_db),
   
):
    """
    Update an existing event (Authenticated users only)
    """
    return crud.update_evento(db=db, evento_id=evento_id, evento=evento)

# Delete Event
@router.delete("/{evento_id}")
def delete_evento(
    evento_id: int, 
    db: Session = Depends(get_db),
   
):
    """
    Delete an event (Authenticated users only)
    """
    return crud.delete_evento(db=db, evento_id=evento_id)

# Get Events by Organizer
@router.get("/organizador/{organizador_dni}", response_model=List[schemas.EventoResponse])
def read_eventos_by_organizador(
    organizador_dni: str, 
    db: Session = Depends(get_db)
):
    """
    Retrieve events by a specific organizer
    """
    return crud.get_eventos_by_organizador(db, organizador_dni)

# Get Events by Location
@router.get("/localidad/{localidad_id}", response_model=List[schemas.EventoResponse])
def read_eventos_by_localidad(
    localidad_id: int, 
    db: Session = Depends(get_db)
):
    """
    Retrieve events in a specific location
    """
    return crud.get_eventos_by_localidad(db, localidad_id)