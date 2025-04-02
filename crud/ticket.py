from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import models
import schemas
from typing import List

def create_ticket(db: Session, ticket: schemas.TicketCreate):
    """
    Create a new ticket
    """
    try:
        # Check if event exists and has available spaces
        evento = db.query(models.Evento).filter(models.Evento.id == ticket.evento_id).first()
        if not evento:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event not found"
            )
        
        # Count only active tickets for this event
        existing_tickets = db.query(models.Ticket).filter(
            models.Ticket.evento_id == ticket.evento_id,
            models.Ticket.activo == True
        ).count()
        
        if existing_tickets >= evento.plazas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No more tickets available for this event"
            )
        
        # Create ticket model instance (activo=True by default)
        db_ticket = models.Ticket(
            evento_id=ticket.evento_id,
            activo=True
        )
        
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)
        return db_ticket
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create ticket"
        )

def get_ticket(db: Session, ticket_id: int):
    """
    Retrieve a ticket by its ID
    """
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    return ticket

def get_tickets(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    evento_id: int = None,
    activo: bool = None
):
    """
    Retrieve multiple tickets with optional filtering
    """
    query = db.query(models.Ticket)
    
    if evento_id:
        query = query.filter(models.Ticket.evento_id == evento_id)
    
    if activo is not None:
        query = query.filter(models.Ticket.activo == activo)
    
    return query.offset(skip).limit(limit).all()

def delete_ticket(db: Session, ticket_id: int):
    """
    Delete a ticket by its ID
    """
    db_ticket = get_ticket(db, ticket_id)
    
    try:
        db.delete(db_ticket)
        db.commit()
        return {"detail": "Ticket deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not delete ticket: {str(e)}"
        )

def get_tickets_by_evento(db: Session, evento_id: int, activo: bool = None):
    """
    Retrieve tickets for a specific event with optional active status filter
    """
    query = db.query(models.Ticket).filter(models.Ticket.evento_id == evento_id)
    
    if activo is not None:
        query = query.filter(models.Ticket.activo == activo)
    
    return query.all()

def deactivate_ticket(db: Session, ticket_id: int):
    """
    Deactivate a ticket (set activo=False)
    """
    db_ticket = get_ticket(db, ticket_id)
    
    if not db_ticket.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket is already inactive"
        )
    
    db_ticket.activo = False
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

def activate_ticket(db: Session, ticket_id: int):
    """
    Activate a ticket (set activo=True)
    """
    db_ticket = get_ticket(db, ticket_id)
    
    if db_ticket.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket is already active"
        )
    
    # Check if event still has available spaces before activating
    evento = db.query(models.Evento).filter(models.Evento.id == db_ticket.evento_id).first()
    if evento:
        active_tickets = db.query(models.Ticket).filter(
            models.Ticket.evento_id == db_ticket.evento_id,
            models.Ticket.activo == True
        ).count()
        
        if active_tickets >= evento.plazas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No more spaces available in this event"
            )
    
    db_ticket.activo = True
    db.commit()
    db.refresh(db_ticket)
    return db_ticket