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
        
        # Count existing tickets for this event
        existing_tickets = db.query(models.Ticket).filter(models.Ticket.evento_id == ticket.evento_id).count()
        if existing_tickets >= evento.plazas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No more tickets available for this event"
            )
        
        # Create ticket model instance
        db_ticket = models.Ticket(
            evento_id=ticket.evento_id
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
    evento_id: int = None
):
    """
    Retrieve multiple tickets with optional filtering
    """
    query = db.query(models.Ticket)
    
    if evento_id:
        query = query.filter(models.Ticket.evento_id == evento_id)
    
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

def get_tickets_by_evento(db: Session, evento_id: int):
    """
    Retrieve tickets for a specific event
    """
    return db.query(models.Ticket).filter(models.Ticket.evento_id == evento_id).all()