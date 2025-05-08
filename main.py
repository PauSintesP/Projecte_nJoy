from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas, crud

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------
# Registro y Login
# -------------------

@app.post("/register", response_model=schemas.Usuario)
def register(user: schemas.UsuarioBase, db: Session = Depends(get_db)):
    return crud.create_item(db, models.Usuario, user)

@app.post("/login", response_model=schemas.Usuario)
def login(data: schemas.LoginInput, db: Session = Depends(get_db)):
    user = crud.login_user(db, data.email, data.contrasena)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return user

# -------------------
# CRUD Endpoints
# -------------------

# Localidad
@app.post("/localidad/", response_model=schemas.Localidad)
def create_localidad(item: schemas.LocalidadCreate, db: Session = Depends(get_db)):
    return crud.create_item(db, models.Localidad, item)

@app.get("/localidad/", response_model=list[schemas.Localidad])
def read_localidades(db: Session = Depends(get_db)):
    return crud.get_items(db, models.Localidad)

@app.get("/localidad/{item_id}", response_model=schemas.Localidad)
def read_localidad(item_id: int, db: Session = Depends(get_db)):
    return crud.get_item(db, models.Localidad, item_id)

@app.put("/localidad/{item_id}", response_model=schemas.Localidad)
def update_localidad(item_id: int, item: schemas.LocalidadCreate, db: Session = Depends(get_db)):
    return crud.update_item(db, models.Localidad, item_id, item)

@app.delete("/localidad/{item_id}")
def delete_localidad(item_id: int, db: Session = Depends(get_db)):
    return crud.delete_item(db, models.Localidad, item_id)

# Organizador
@app.post("/organizador/", response_model=schemas.Organizador)
def create_organizador(item: schemas.Organizador, db: Session = Depends(get_db)):
    return crud.create_item(db, models.Organizador, item)

@app.get("/organizador/", response_model=list[schemas.Organizador])
def read_organizadores(db: Session = Depends(get_db)):
    return crud.get_items(db, models.Organizador)

@app.get("/organizador/{item_id}", response_model=schemas.Organizador)
def read_organizador(item_id: str, db: Session = Depends(get_db)):
    return db.query(models.Organizador).filter_by(dni=item_id).first()

@app.put("/organizador/{item_id}", response_model=schemas.Organizador)
def update_organizador(item_id: str, item: schemas.Organizador, db: Session = Depends(get_db)):
    db_item = db.query(models.Organizador).filter_by(dni=item_id).first()
    for key, value in item.dict(exclude_unset=True).items():
        setattr(db_item, key, value)
    db.commit()
    return db_item

@app.delete("/organizador/{item_id}")
def delete_organizador(item_id: str, db: Session = Depends(get_db)):
    db_item = db.query(models.Organizador).filter_by(dni=item_id).first()
    db.delete(db_item)
    db.commit()
    return db_item

# Genero
@app.post("/genero/", response_model=schemas.Genero)
def create_genero(item: schemas.GeneroBase, db: Session = Depends(get_db)):
    return crud.create_item(db, models.Genero, item)

@app.get("/genero/", response_model=list[schemas.Genero])
def read_generos(db: Session = Depends(get_db)):
    return crud.get_items(db, models.Genero)

@app.get("/genero/{item_id}", response_model=schemas.Genero)
def read_genero(item_id: int, db: Session = Depends(get_db)):
    return crud.get_item(db, models.Genero, item_id)

@app.put("/genero/{item_id}", response_model=schemas.Genero)
def update_genero(item_id: int, item: schemas.GeneroBase, db: Session = Depends(get_db)):
    return crud.update_item(db, models.Genero, item_id, item)

@app.delete("/genero/{item_id}")
def delete_genero(item_id: int, db: Session = Depends(get_db)):
    return crud.delete_item(db, models.Genero, item_id)

# Artista
@app.post("/artista/", response_model=schemas.Artista)
def create_artista(item: schemas.ArtistaBase, db: Session = Depends(get_db)):
    return crud.create_item(db, models.Artista, item)

@app.get("/artista/", response_model=list[schemas.Artista])
def read_artistas(db: Session = Depends(get_db)):
    return crud.get_items(db, models.Artista)

@app.get("/artista/{item_id}", response_model=schemas.Artista)
def read_artista(item_id: int, db: Session = Depends(get_db)):
    return crud.get_item(db, models.Artista, item_id)

@app.put("/artista/{item_id}", response_model=schemas.Artista)
def update_artista(item_id: int, item: schemas.ArtistaBase, db: Session = Depends(get_db)):
    return crud.update_item(db, models.Artista, item_id, item)

@app.delete("/artista/{item_id}")
def delete_artista(item_id: int, db: Session = Depends(get_db)):
    return crud.delete_item(db, models.Artista, item_id)

# Usuario
@app.get("/usuario/", response_model=list[schemas.Usuario])
def read_usuarios(db: Session = Depends(get_db)):
    return crud.get_items(db, models.Usuario)

@app.get("/usuario/{item_id}", response_model=schemas.Usuario)
def read_usuario(item_id: int, db: Session = Depends(get_db)):
    return crud.get_item(db, models.Usuario, item_id)

@app.put("/usuario/{item_id}", response_model=schemas.Usuario)
def update_usuario(item_id: int, item: schemas.UsuarioBase, db: Session = Depends(get_db)):
    return crud.update_item(db, models.Usuario, item_id, item)

@app.delete("/usuario/{item_id}")
def delete_usuario(item_id: int, db: Session = Depends(get_db)):
    return crud.delete_item(db, models.Usuario, item_id)

# Evento
@app.post("/evento/", response_model=schemas.Evento)
def create_evento(item: schemas.EventoBase, db: Session = Depends(get_db)):
    return crud.create_item(db, models.Evento, item)

@app.get("/evento/", response_model=list[schemas.Evento])
def read_eventos(db: Session = Depends(get_db)):
    return crud.get_items(db, models.Evento)

@app.get("/evento/{item_id}", response_model=schemas.Evento)
def read_evento(item_id: int, db: Session = Depends(get_db)):
    return crud.get_item(db, models.Evento, item_id)

@app.put("/evento/{item_id}", response_model=schemas.Evento)
def update_evento(item_id: int, item: schemas.EventoBase, db: Session = Depends(get_db)):
    return crud.update_item(db, models.Evento, item_id, item)

@app.delete("/evento/{item_id}")
def delete_evento(item_id: int, db: Session = Depends(get_db)):
    return crud.delete_item(db, models.Evento, item_id)

# Ticket
@app.post("/ticket/", response_model=schemas.Ticket)
def create_ticket(item: schemas.TicketBase, db: Session = Depends(get_db)):
    return crud.create_item(db, models.Ticket, item)

@app.get("/ticket/", response_model=list[schemas.Ticket])
def read_tickets(db: Session = Depends(get_db)):
    return crud.get_items(db, models.Ticket)

@app.get("/ticket/{item_id}", response_model=schemas.Ticket)
def read_ticket(item_id: int, db: Session = Depends(get_db)):
    return crud.get_item(db, models.Ticket, item_id)

@app.put("/ticket/{item_id}", response_model=schemas.Ticket)
def update_ticket(item_id: int, item: schemas.TicketBase, db: Session = Depends(get_db)):
    return crud.update_item(db, models.Ticket, item_id, item)

@app.delete("/ticket/{item_id}")
def delete_ticket(item_id: int, db: Session = Depends(get_db)):
    return crud.delete_item(db, models.Ticket, item_id)

# Pago
@app.post("/pago/", response_model=schemas.Pago)
def create_pago(item: schemas.PagoBase, db: Session = Depends(get_db)):
    return crud.create_item(db, models.Pago, item)

@app.get("/pago/", response_model=list[schemas.Pago])
def read_pagos(db: Session = Depends(get_db)):
    return crud.get_items(db, models.Pago)

@app.get("/pago/{item_id}", response_model=schemas.Pago)
def read_pago(item_id: int, db: Session = Depends(get_db)):
    return crud.get_item(db, models.Pago, item_id)

@app.put("/pago/{item_id}", response_model=schemas.Pago)
def update_pago(item_id: int, item: schemas.PagoBase, db: Session = Depends(get_db)):
    return crud.update_item(db, models.Pago, item_id, item)

@app.delete("/pago/{item_id}")
def delete_pago(item_id: int, db: Session = Depends(get_db)):
    return crud.delete_item(db, models.Pago, item_id)
