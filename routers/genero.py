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

# Genre Creation Endpoint
@router.post("/", response_model=schemas.GeneroResponse)
def create_genero(
    genero: schemas.GeneroCreate, 
    db: Session = Depends(get_db),
   
):
    """
    Create a new genre (Authenticated users only)
    """
    return crud.create_genero(db=db, genero=genero)

# Get Genre by ID
@router.get("/{genero_id}", response_model=schemas.GeneroResponse)
def read_genero(
    genero_id: int, 
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific genre by ID
    """
    return crud.get_genero(db, genero_id)

# List Genres with Optional Filtering
@router.get("/", response_model=List[schemas.GeneroResponse])
def read_generos(
    skip: int = 0, 
    limit: int = 100,
    nombre: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List genres with optional filtering by name
    """
    return crud.get_generos(db, skip=skip, limit=limit, nombre=nombre)

# Update Genre
@router.put("/{genero_id}", response_model=schemas.GeneroResponse)
def update_genero(
    genero_id: int, 
    genero: schemas.GeneroCreate, 
    db: Session = Depends(get_db),
   
):
    """
    Update an existing genre (Authenticated users only)
    """
    return crud.update_genero(db=db, genero_id=genero_id, genero=genero)

# Delete Genre
@router.delete("/{genero_id}")
def delete_genero(
    genero_id: int, 
    db: Session = Depends(get_db),
   
):
    """
    Delete a genre (Authenticated users only)
    """
    return crud.delete_genero(db=db, genero_id=genero_id)