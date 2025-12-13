from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
import models
from auth import get_db, get_current_active_user, get_current_scanner

router = APIRouter()

@router.post("/tickets/purchase", tags=["Tickets"])
def purchase_tickets(
    evento_id: int,
    cantidad: int = 1,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Comprar entradas para un evento
    
    El usuario puede comprar múltiples entradas a la vez.
    Se valida que haya plazas disponibles.
    """
    #  Verificar que el evento existe
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento no encontrado"
        )
    
    # Verificar plazas disponibles
    tickets_vendidos = db.query(models.Ticket).filter(
        models.Ticket.evento_id == evento_id
    ).count()
    
    plazas_disponibles = evento.plazas - tickets_vendidos
    
    if cantidad > plazas_disponibles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Solo hay {plazas_disponibles} plazas disponibles"
        )
    
    # Crear los tickets
    tickets_created = []
    for i in range(cantidad):
        new_ticket = models.Ticket(
            evento_id=evento_id,
            usuario_id=current_user.id,
            activado=True,
            codigo_ticket=str(uuid.uuid4())
        )
        db.add(new_ticket)
        tickets_created.append(new_ticket)
    
    db.commit()
    
    # Refrescar los tickets para obtener los IDs
    for ticket in tickets_created:
        db.refresh(ticket)
    
    return {
        "message": f"¡Compra exitosa! {cantidad} entrada(s) adquirida(s)",
        "cantidad": cantidad,
        "total": evento.precio * cantidad if evento.precio else 0,
        "tickets": [{"id": t.id, "evento_id": t.evento_id} for t in tickets_created]
    }


@router.get("/tickets/my-tickets", tags=["Tickets"])
def get_my_tickets(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Obtener todos los tickets del usuario autenticado
    
    Retorna los tickets con información del evento
    """
    tickets = db.query(models.Ticket).filter(
        models.Ticket.usuario_id == current_user.id
    ).all()
    
    # Enriquecer con información del evento
    tickets_with_events = []
    for ticket in tickets:
        evento = db.query(models.Evento).filter(models.Evento.id == ticket.evento_id).first()
        if evento:
            tickets_with_events.append({
                "ticket_id": ticket.id,
                "codigo": ticket.codigo_ticket,  # Added code
                "activado": ticket.activado,
                "evento": {
                    "id": evento.id,
                    "nombre": evento.nombre,
                    "descripcion": evento.descripcion,
                    "fechayhora": evento.fechayhora.isoformat() if evento.fechayhora else None,
                    "recinto": evento.recinto,
                    "imagen": evento.imagen,
                    "precio": evento.precio
                }
            })
    
    return tickets_with_events


@router.get("/tickets/{ticket_id}", tags=["Tickets"])
def get_ticket_detail(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Obtener detalle de un ticket específico
    
    Solo el propietario del ticket puede verlo
    """
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket no encontrado"
        )
    
    # Verificar que el ticket pertenece al usuario
    if ticket.usuario_id != current_user.id and current_user.role not in ['admin', 'scanner']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este ticket"
        )
    
    # Obtener información del evento
    evento = db.query(models.Evento).filter(models.Evento.id == ticket.evento_id).first()
    
    return {
        "ticket_id": ticket.id,
        "activado": ticket.activado,
        "usuario": {
            "id": current_user.id,
            "nombre": current_user.nombre,
            "apellidos": current_user.apellidos,
            "email": current_user.email
        },
        "evento": {
            "id": evento.id,
            "nombre": evento.nombre,
            "descripcion": evento.descripcion,
            "fechayhora": evento.fechayhora.isoformat() if evento.fechayhora else None,
            "recinto": evento.recinto,
            "imagen": evento.imagen,
            "precio": evento.precio
        } if evento else None
    }
