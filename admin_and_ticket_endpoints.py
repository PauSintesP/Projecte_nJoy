# ============================================
# ADMIN ENDPOINTS
# ============================================

@app.post("/admin/users", tags=["Admin"], response_model=schemas.Usuario)
def create_user_admin(
    user_data: schemas.UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Crear un nuevo usuario (Solo Admin)"""
    if current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo admin")
    
    # Email case-insensitive
    email_lower = user_data.email.lower().strip()
    if db.query(models.Usuario).filter(models.Usuario.email == email_lower).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email ya registrado")
    
    from auth import hash_password
    new_user = models.Usuario(
        nombre=user_data.nombre, apellidos=user_data.apellidos,
        email=email_lower, password=hash_password(user_data.password),
        fecha_nacimiento=user_data.fecha_nacimiento, pais=user_data.pais,
        role=user_data.role if hasattr(user_data, 'role') and user_data.role else 'user',
        is_active=True, is_banned=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# ============================================
# TICKET ENDPOINTS
# ============================================

@app.post("/tickets/purchase", tags=["Tickets"])
def purchase_tickets(evento_id: int, cantidad: int = 1, db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_active_user)):
    """Comprar entradas"""
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    tickets_vendidos = db.query(models.Ticket).filter(models.Ticket.evento_id == evento_id).count()
    if cantidad > (evento.plazas - tickets_vendidos):
        raise HTTPException(status_code=400, detail=f"Solo hay {evento.plazas - tickets_vendidos} plazas")
    
    tickets_created = []
    for i in range(cantidad):
        tickets_created.append(models.Ticket(evento_id=evento_id, usuario_id=current_user.id, activado=True))
        db.add(tickets_created[-1])
    db.commit()
    for t in tickets_created:
        db.refresh(t)
    
    return {"message": f"¡Compra exitosa! {cantidad} entrada(s)", "cantidad": cantidad, "total": evento.precio * cantidad if evento.precio else 0, "tickets": [{"id": t.id, "evento_id": t.evento_id} for t in tickets_created]}

@app.get("/tickets/my-tickets", tags=["Tickets"])
def get_my_tickets(db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_active_user)):
    """Obtener tickets del usuario"""
    tickets = db.query(models.Ticket).filter(models.Ticket.usuario_id == current_user.id).all()
    result = []
    for ticket in tickets:
        evento = db.query(models.Evento).filter(models.Evento.id == ticket.evento_id).first()
        if evento:
            result.append({"ticket_id": ticket.id, "activado": ticket.activado, "evento": {"id": evento.id, "nombre": evento.nombre, "descripcion": evento.descripcion, "fechayhora": evento.fechayhora.isoformat() if evento.fechayhora else None, "recinto": evento.recinto, "imagen": evento.imagen, "precio": evento.precio}})
    return result

@app.get("/tickets/{ticket_id}", tags=["Tickets"])
def get_ticket_detail(ticket_id: int, db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_active_user)):
    """Detalle de ticket"""
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    if ticket.usuario_id != current_user.id and current_user.role not in ['admin', 'scanner']:
        raise HTTPException(status_code=403, detail="Sin permiso")
    
    evento = db.query(models.Evento).filter(models.Evento.id == ticket.evento_id).first()
    return {"ticket_id": ticket.id, "activado": ticket.activado, "usuario": {"id": current_user.id, "nombre": current_user.nombre, "apellidos": current_user.apellidos, "email": current_user.email}, "evento": {"id": evento.id, "nombre": evento.nombre, "descripcion": evento.descripcion, "fechayhora": evento.fechayhora.isoformat() if evento.fechayhora else None, "recinto": evento.recinto, "imagen": evento.imagen, "precio": evento.precio} if evento else None}
