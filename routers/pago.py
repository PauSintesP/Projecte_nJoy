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

# Payment Creation Endpoint
@router.post("/", response_model=schemas.PagoResponse)
def create_pago(
    pago: schemas.PagoCreate, 
    db: Session = Depends(get_db),
   
):
    """
    Create a new payment (Authenticated users only)
    Ensures user can only create payment for themselves
    """
    if pago.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create payment for another user"
        )
    return crud.create_pago(db=db, pago=pago)

# Get Payment by ID
@router.get("/{pago_id}", response_model=schemas.PagoResponse)
def read_pago(
    pago_id: int, 
    db: Session = Depends(get_db),
   
):
    """
    Retrieve a specific payment by ID (Authenticated users only)
    """
    return crud.get_pago(db, pago_id)

# List Payments with Optional Filtering
@router.get("/", response_model=List[schemas.PagoResponse])
def read_pagos(
    skip: int = 0, 
    limit: int = 100,
    usuario_id: Optional[int] = None,
    metodo_pago: Optional[str] = None,
    db: Session = Depends(get_db),
   
):
    """
    List payments with optional filtering (Authenticated users only)
    """
    return crud.get_pagos(db, skip=skip, limit=limit, usuario_id=usuario_id, metodo_pago=metodo_pago)

# Get Payments by User
@router.get("/usuario/{usuario_id}", response_model=List[schemas.PagoResponse])
def read_pagos_by_usuario(
    usuario_id: int, 
    db: Session = Depends(get_db),
   
):
    """
    Retrieve payments for a specific user (Authenticated users only)
    Ensures user can only view their own payments
    """
    if usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view another user's payments"
        )
    return crud.get_pagos_by_usuario(db, usuario_id)

# Delete Payment
@router.delete("/{pago_id}")
def delete_pago(
    pago_id: int, 
    db: Session = Depends(get_db),
   
):
    """
    Delete a payment (Authenticated users only)
    """
    return crud.delete_pago(db=db, pago_id=pago_id)