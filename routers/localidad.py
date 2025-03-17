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

# Location Creation Endpoint
@router.post("/", response_model=schemas.LocalidadResponse)
def create_localidad(
    localidad: schemas.LocalidadCreate, 
    db: Session = Depends(get_db),
   
):
    """
    Create a new location (Authenticated users only)
    """
    return crud.create_localidad(db=db, localidad=localidad)

# Get Location by ID
@router.get("/{localidad_id}", response_model=schemas.LocalidadResponse)
def read_localidad(
    localidad_id: int, 
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific location by ID
    """
    return crud.get_localidad(db, localidad_id)

# List Locations with Optional Filtering
@router.get("/", response_model=List[schemas.LocalidadResponse])
def read_localidades(
    skip: int = 0, 
    limit: int = 100,
    ciudad: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List locations with optional filtering by city name
    """
    return crud.get_localidades(db, skip=skip, limit=limit, ciudad=ciudad)

# Update Location
@router.put("/{localidad_id}", response_model=schemas.LocalidadResponse)
def update_localidad(
    localidad_id: int, 
    localidad: schemas.LocalidadCreate, 
    db: Session = Depends(get_db),
   
):
    """
    Update an existing location (Authenticated users only)
    """
    return crud.update_localidad(db=db, localidad_id=localidad_id, localidad=localidad)

# Delete Location
@router.delete("/{localidad_id}")
def delete_localidad(
    localidad_id: int, 
    db: Session = Depends(get_db),
   
):
    """
    Delete a location (Authenticated users only)
    """
    return crud.delete_localidad(db=db, localidad_id=localidad_id)