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

# Artist Creation Endpoint
@router.post("/", response_model=schemas.ArtistaResponse)
def create_artista(
    artista: schemas.ArtistaCreate, 
    db: Session = Depends(get_db),
):
    """
    Create a new artist (Authenticated users only)
    """
    return crud.create_artista(db=db, artista=artista)

# Get Artist by ID
@router.get("/{artista_id}", response_model=schemas.ArtistaResponse)
def read_artista(
    artista_id: int, 
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific artist by ID
    """
    return crud.get_artista(db, artista_id)

# List Artists with Optional Filtering
@router.get("/", response_model=List[schemas.ArtistaResponse])
def read_artistas(
    skip: int = 0, 
    limit: int = 100,
    nartistico: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List artists with optional filtering by name
    """
    return crud.get_artistas(db, skip=skip, limit=limit, nartistico=nartistico)

# Update Artist
@router.put("/{artista_id}", response_model=schemas.ArtistaResponse)
def update_artista(
    artista_id: int, 
    artista: schemas.ArtistaCreate, 
    db: Session = Depends(get_db),
):
    """
    Update an existing artist (Authenticated users only)
    """
    return crud.update_artista(db=db, artista_id=artista_id, artista=artista)

# Delete Artist
@router.delete("/{artista_id}")
def delete_artista(
    artista_id: int, 
    db: Session = Depends(get_db),
):
    """
    Delete an artist (Authenticated users only)
    """
    return crud.delete_artista(db=db, artista_id=artista_id)
