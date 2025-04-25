from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import models
import schemas
from typing import List

def create_evento(db: Session, evento: schemas.EventoCreate):
    """
    Create a new event and associate it with artists
    """
    try:
        # Check if localidad and organizador exist
        db.query(models.Localidad).filter(models.Localidad.id == evento.localidad_id).first()
        db.query(models.Organizador).filter(models.Organizador.dni == evento.organizador_dni).first()

        # Create event model instance
        db_evento = models.Evento(
            nombre=evento.nombre,
            descripcion=evento.descripcion,
            localidad_id=evento.localidad_id,
            recinto=evento.recinto,
            plazas=evento.plazas,
            fechayhora=evento.fechayhora,
            tipo=evento.tipo,
            categoria_precio=evento.categoria_precio,
            organizador_dni=evento.organizador_dni
        )
        
        db.add(db_evento)
        db.commit()
        db.refresh(db_evento)

        # Associate artists with the event
        for artista_id in evento.artistas:
            db_evento_artista = models.EventoArtista(
                evento_id=db_evento.id,
                artista_id=artista_id
            )
            db.add(db_evento_artista)
        
        db.commit()
        return db_evento
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create event. Check related entities."
        )


def get_evento(db: Session, evento_id: int):
    """
    Retrieve an event by its ID, including associated artists
    """
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return evento

def get_eventos(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    nombre: str = None, 
    tipo: str = None
):
    """
    Retrieve multiple events with optional filtering
    """
    query = db.query(models.Evento)
    
    if nombre:
        query = query.filter(models.Evento.nombre.ilike(f"%{nombre}%"))
    
    if tipo:
        query = query.filter(models.Evento.tipo == tipo)
    
    return query.offset(skip).limit(limit).all()

def update_evento(db: Session, evento_id: int, evento: schemas.EventoCreate):
    """
    Update an existing event
    """
    db_evento = get_evento(db, evento_id)
    
    try:
        # Check if localidad and organizador exist
        db.query(models.Localidad).filter(models.Localidad.id == evento.localidad_id).first()
        db.query(models.Organizador).filter(models.Organizador.dni == evento.organizador_dni).first()

        # Update fields
        db_evento.nombre = evento.nombre
        db_evento.descripcion = evento.descripcion
        db_evento.localidad_id = evento.localidad_id
        db_evento.recinto = evento.recinto
        db_evento.plazas = evento.plazas
        db_evento.fechayhora = evento.fechayhora
        db_evento.tipo = evento.tipo
        db_evento.categoria_precio = evento.categoria_precio
        db_evento.organizador_dni = evento.organizador_dni
        
        db.commit()
        db.refresh(db_evento)
        return db_evento
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update event. Check related entities."
        )

def delete_evento(db: Session, evento_id: int):
    """
    Delete an event by its ID
    """
    db_evento = get_evento(db, evento_id)
    
    try:
        db.delete(db_evento)
        db.commit()
        return {"detail": "Event deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not delete event: {str(e)}"
        )

def get_eventos_by_organizador(db: Session, organizador_dni: str):
    """
    Retrieve events by a specific organizer
    """
    return db.query(models.Evento).filter(models.Evento.organizador_dni == organizador_dni).all()

def get_eventos_by_localidad(db: Session, localidad_id: int):
    """
    Retrieve events in a specific location
    """
    return db.query(models.Evento).filter(models.Evento.localidad_id == localidad_id).all()