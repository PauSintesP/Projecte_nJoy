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

# Ticket Creation Endpoint
@router.post("/", response_model=schemas.TicketResponse)
def create_ticket(
    ticket: schemas.TicketCreate, 
    db: Session = Depends(get_db),
    current_user: schemas.UsuarioResponse = Depends(get_current_user)  # Cambiado a UsuarioResponse
):
    """
    Create a new ticket (Authenticated users only)
    """
    return crud.create_ticket(db=db, ticket=ticket)

# Get Ticket by ID
@router.get("/{ticket_id}", response_model=schemas.TicketResponse)
def read_ticket(
    ticket_id: int, 
    db: Session = Depends(get_db),
    current_user: schemas.UsuarioResponse = Depends(get_current_user)  # Cambiado a UsuarioResponse
):
    """
    Retrieve a specific ticket by ID (Authenticated users only)
    """
    return crud.get_ticket(db, ticket_id)

# List Tickets with Optional Filtering
@router.get("/", response_model=List[schemas.TicketResponse])
def read_tickets(
    skip: int = 0, 
    limit: int = 100,
    evento_id: Optional[int] = None,
    activo: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: schemas.UsuarioResponse = Depends(get_current_user)  # Cambiado a UsuarioResponse
):
    """
    List tickets with optional filtering by event and active status (Authenticated users only)
    """
    return crud.get_tickets(db, skip=skip, limit=limit, evento_id=evento_id, activo=activo)

# Delete Ticket
@router.delete("/{ticket_id}")
def delete_ticket(
    ticket_id: int, 
    db: Session = Depends(get_db),
    current_user: schemas.UsuarioResponse = Depends(get_current_user)  # Cambiado a UsuarioResponse
):
    """
    Delete a ticket (Authenticated users only)
    """
    return crud.delete_ticket(db=db, ticket_id=ticket_id)

# Get Tickets by Event
@router.get("/evento/{evento_id}", response_model=List[schemas.TicketResponse])
def read_tickets_by_evento(
    evento_id: int, 
    activo: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: schemas.UsuarioResponse = Depends(get_current_user)  # Cambiado a UsuarioResponse
):
    """
    Retrieve tickets for a specific event with optional active status filter (Authenticated users only)
    """
    return crud.get_tickets_by_evento(db, evento_id, activo=activo)

# Deactivate Ticket
@router.patch("/{ticket_id}/desactivar", response_model=schemas.TicketResponse)
def deactivate_ticket(
    ticket_id: int, 
    db: Session = Depends(get_db),
    current_user: schemas.UsuarioResponse = Depends(get_current_user)  # Cambiado a UsuarioResponse
):
    """
    Deactivate a ticket (Authenticated users only)
    """
    return crud.deactivate_ticket(db=db, ticket_id=ticket_id)

# Activate Ticket
@router.patch("/{ticket_id}/activar", response_model=schemas.TicketResponse)
def activate_ticket(
    ticket_id: int, 
    db: Session = Depends(get_db),
    current_user: schemas.UsuarioResponse = Depends(get_current_user)  # Cambiado a UsuarioResponse
):
    """
    Activate a ticket (Authenticated users only)
    """
    return crud.activate_ticket(db=db, ticket_id=ticket_id)