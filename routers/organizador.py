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

# Organizador Creation Endpoint
@router.post("/", response_model=schemas.OrganizadorResponse)
def create_organizador(
    organizador: schemas.OrganizadorCreate, 
    db: Session = Depends(get_db),
   
):
    """
    Create a new organizador (Authenticated users only)
    """
    return crud.create_organizador(db=db, organizador=organizador)

# Get Organizador by DNI
@router.get("/{dni}", response_model=schemas.OrganizadorResponse)
def read_organizador(
    dni: str, 
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific organizador by DNI
    """
    return crud.get_organizador(db, dni)

# List Organizadores with Optional Filtering
@router.get("/", response_model=List[schemas.OrganizadorResponse])
def read_organizadores(
    skip: int = 0, 
    limit: int = 100,
    ncompleto: Optional[str] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List organizadores with optional filtering by name or email
    """
    return crud.get_organizadores(db, skip=skip, limit=limit, ncompleto=ncompleto, email=email)

# Update Organizador
@router.put("/{dni}", response_model=schemas.OrganizadorResponse)
def update_organizador(
    dni: str, 
    organizador: schemas.OrganizadorCreate, 
    db: Session = Depends(get_db),
   
):
    """
    Update an existing organizador (Authenticated users only)
    """
    return crud.update_organizador(db=db, dni=dni, organizador=organizador)

# Delete Organizador
@router.delete("/{dni}")
def delete_organizador(
    dni: str, 
    db: Session = Depends(get_db),
   
):
    """
    Delete an organizador (Authenticated users only)
    """
    return crud.delete_organizador(db=db, dni=dni)