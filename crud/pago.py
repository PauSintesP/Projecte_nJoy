from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import models
import schemas
from typing import List
from datetime import datetime

def create_pago(db: Session, pago: schemas.PagoCreate):
    """
    Create a new payment
    """
    try:
        # Check if user and ticket exist
        db.query(models.Usuario).filter(models.Usuario.id == pago.usuario_id).first()
        db.query(models.Ticket).filter(models.Ticket.id == pago.ticket_id).first()
        
        # Check if ticket is already paid
        existing_pago = db.query(models.Pago).filter(models.Pago.ticket_id == pago.ticket_id).first()
        if existing_pago:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ticket already paid"
            )
        
        # Create payment model instance
        db_pago = models.Pago(
            usuario_id=pago.usuario_id,
            metodo_pago=pago.metodo_pago,
            total=pago.total,
            fecha=datetime.now(),
            ticket_id=pago.ticket_id
        )
        
        db.add(db_pago)
        db.commit()
        db.refresh(db_pago)
        return db_pago
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create payment"
        )

def get_pago(db: Session, pago_id: int):
    """
    Retrieve a payment by its ID
    """
    pago = db.query(models.Pago).filter(models.Pago.id == pago_id).first()
    if not pago:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    return pago

def get_pagos(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    usuario_id: int = None,
    metodo_pago: str = None
):
    """
    Retrieve multiple payments with optional filtering
    """
    query = db.query(models.Pago)
    
    if usuario_id:
        query = query.filter(models.Pago.usuario_id == usuario_id)
    
    if metodo_pago:
        query = query.filter(models.Pago.metodo_pago == metodo_pago)
    
    return query.offset(skip).limit(limit).all()

def get_pagos_by_usuario(db: Session, usuario_id: int):
    """
    Retrieve payments for a specific user
    """
    return db.query(models.Pago).filter(models.Pago.usuario_id == usuario_id).all()

def delete_pago(db: Session, pago_id: int):
    """
    Delete a payment by its ID
    """
    db_pago = get_pago(db, pago_id)
    
    try:
        db.delete(db_pago)
        db.commit()
        return {"detail": "Payment deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not delete payment: {str(e)}"
        )