from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

# Imports locales
from database import SessionLocal, engine
import models, schemas, crud
import seed_data
from auth import (
    get_db,
    get_current_active_user,
    create_access_token,
    create_refresh_token,
    authenticate_user,
    decode_token
)
from config import settings

# Crear tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

# Inicializar FastAPI con metadata completa para documentación
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## 🎉 nJoy API - Plataforma de Gestión de Eventos

API RESTful completa para la gestión de eventos, artistas, tickets y pagos.

### Características principales:

* 🔐 **Autenticación JWT** - Sistema seguro con access y refresh tokens
* 👥 **Gestión de usuarios** - Registro, login y perfiles de usuario
* 🎭 **Eventos y artistas** - CRUD completo para eventos musicales
* 🎫 **Sistema de tickets** - Compra y gestión de entradas
* 💳 **Procesamiento de pagos** - Registro de transacciones
* 🏢 **Organizadores** - Gestión de promotores de eventos
* 📍 **Localidades** - Gestión de ubicaciones y recintos

### Seguridad

Todos los endpoints (excepto `/register`, `/login`, `/health` y `/`) requieren autenticación mediante Bearer token.

Para autenticarte:
1. Registra un usuario en `/register`
2. Obtén tokens en `/login`
3. Incluye el header: `Authorization: Bearer <access_token>`

### Soporte

Para más información, consulta la documentación completa o contacta con el equipo de desarrollo.
    """,
    contact={
        "name": "nJoy Development Team",
        "email": "support@njoy.com",
        "url": "https://njoy.com/support"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "Operaciones de autenticación y gestión de tokens. Estos endpoints son **públicos**."
        },
        {
            "name": "Users",
            "description": "Gestión de usuarios registrados. Requiere autenticación."
        },
        {
            "name": "Events",
            "description": "CRUD completo para eventos musicales. Requiere autenticación."
        },
        {
            "name": "Tickets",
            "description": "Gestión de tickets de eventos. Los usuarios solo pueden gestionar sus propios tickets."
        },
        {
            "name": "Payments",
            "description": "Registro y consulta de pagos. Los usuarios solo pueden ver sus propios pagos."
        },
        {
            "name": "Artists",
            "description": "Gestión de artistas musicales. Requiere autenticación."
        },
        {
            "name": "Genres",
            "description": "Gestión de géneros musicales. Requiere autenticación."
        },
        {
            "name": "Organizers",
            "description": "Gestión de organizadores de eventos. Requiere autenticación."
        },
        {
            "name": "Locations",
            "description": "Gestión de localidades y ciudades. Requiere autenticación."
        },
        {
            "name": "Health",
            "description": "Endpoints de monitoreo y estado del servicio. Públicos."
        }
    ]
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://web-njoy.vercel.app",
        "https://*.vercel.app",            
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# ENDPOINTS DE AUTENTICACIÓN (PÚBLICOS)
# ============================================

@app.post("/register", response_model=schemas.Usuario, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
def register(user: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    """
    Registrar un nuevo usuario
    - Password se hashea automáticamente
    - Email debe ser único
    - Username debe ser único
    """
    try:
        new_user = crud.create_item(db, models.Usuario, user)
        return new_user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear usuario: {str(e)}"
        )

@app.post("/login", response_model=schemas.Token, tags=["Authentication"])
def login(credentials: schemas.LoginInput, db: Session = Depends(get_db)):
    """
    Login de usuario
    - Retorna access_token y refresh_token
    - Los tokens son JWT firmados
    """
    user = authenticate_user(db, credentials.email, credentials.contrasena)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    # Crear tokens
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.post("/token/refresh", response_model=schemas.Token, tags=["Authentication"])
def refresh_token(token_request: schemas.RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Renovar access token usando refresh token
    """
    try:
        payload = decode_token(token_request.refresh_token)
        
        # Verificar que sea un refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        # Verificar que el usuario existe
        user = crud.get_item(db, models.Usuario, int(user_id))
        
        # Crear nuevos tokens
        access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )

@app.get("/me", response_model=schemas.Usuario, tags=["Users"])
def get_current_user_info(current_user: models.Usuario = Depends(get_current_active_user)):
    """
    Obtener información del usuario actual autenticado
    """
    return current_user

# ============================================
# ENDPOINTS DE LOCALIDAD (PROTEGIDOS)
# ============================================

@app.post("/localidad/", response_model=schemas.Localidad, status_code=status.HTTP_201_CREATED, tags=["Locations"])
def create_localidad(
    item: schemas.LocalidadCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Crear una nueva localidad (requiere autenticación)"""
    return crud.create_item(db, models.Localidad, item)

@app.get("/localidad/", response_model=List[schemas.Localidad], tags=["Locations"])
def read_localidades(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Obtener todas las localidades (requiere autenticación)"""
    return crud.get_items(db, models.Localidad, skip, limit)

@app.get("/localidad/{item_id}", response_model=schemas.Localidad, tags=["Locations"])
def read_localidad(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Obtener una localidad por ID (requiere autenticación)"""
    return crud.get_item(db, models.Localidad, item_id)

@app.put("/localidad/{item_id}", response_model=schemas.Localidad, tags=["Locations"])
def update_localidad(
    item_id: int,
    item: schemas.LocalidadCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Actualizar una localidad (requiere autenticación)"""
    return crud.update_item(db, models.Localidad, item_id, item)

@app.delete("/localidad/{item_id}", tags=["Locations"])
def delete_localidad(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Eliminar una localidad (requiere autenticación)"""
    return crud.delete_item(db, models.Localidad, item_id)

# ============================================
# ENDPOINTS DE ORGANIZADOR (PROTEGIDOS)
# ============================================

@app.post("/organizador/", response_model=schemas.Organizador, status_code=status.HTTP_201_CREATED, tags=["Organizers"])
def create_organizador(
    item: schemas.Organizador,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Crear un nuevo organizador (requiere autenticación)"""
    db_item = models.Organizador(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/organizador/", response_model=List[schemas.Organizador], tags=["Organizers"])
def read_organizadores(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Obtener todos los organizadores (requiere autenticación)"""
    return db.query(models.Organizador).offset(skip).limit(limit).all()

@app.get("/organizador/{item_id}", response_model=schemas.Organizador, tags=["Organizers"])
def read_organizador(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Obtener un organizador por DNI (requiere autenticación)"""
    org = db.query(models.Organizador).filter_by(dni=item_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organizador no encontrado")
    return org

@app.put("/organizador/{item_id}", response_model=schemas.Organizador, tags=["Organizers"])
def update_organizador(
    item_id: str,
    item: schemas.Organizador,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Actualizar un organizador (requiere autenticación)"""
    db_item = db.query(models.Organizador).filter_by(dni=item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Organizador no encontrado")
    for key, value in item.dict(exclude_unset=True).items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/organizador/{item_id}", tags=["Organizers"])
def delete_organizador(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Eliminar un organizador (requiere autenticación)"""
    db_item = db.query(models.Organizador).filter_by(dni=item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Organizador no encontrado")
    db.delete(db_item)
    db.commit()
    return {"detail": "Organizador eliminado correctamente"}

# ============================================
# ENDPOINTS DE GÉNERO (PROTEGIDOS)
# ============================================

@app.post("/genero/", response_model=schemas.Genero, status_code=status.HTTP_201_CREATED, tags=["Genres"])
def create_genero(
    item: schemas.GeneroBase,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Crear un nuevo género (requiere autenticación)"""
    return crud.create_item(db, models.Genero, item)

@app.get("/genero/", response_model=List[schemas.Genero], tags=["Genres"])
def read_generos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Obtener todos los géneros (requiere autenticación)"""
    return crud.get_items(db, models.Genero, skip, limit)

@app.get("/genero/{item_id}", response_model=schemas.Genero, tags=["Genres"])
def read_genero(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Obtener un género por ID (requiere autenticación)"""
    return crud.get_item(db, models.Genero, item_id)

@app.put("/genero/{item_id}", response_model=schemas.Genero, tags=["Genres"])
def update_genero(
    item_id: int,
    item: schemas.GeneroBase,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Actualizar un género (requiere autenticación)"""
    return crud.update_item(db, models.Genero, item_id, item)

@app.delete("/genero/{item_id}", tags=["Genres"])
def delete_genero(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Eliminar un género (requiere autenticación)"""
    return crud.delete_item(db, models.Genero, item_id)

# ============================================
# ENDPOINTS DE ARTISTA (PROTEGIDOS)
# ============================================

@app.post("/artista/", response_model=schemas.Artista, status_code=status.HTTP_201_CREATED, tags=["Artists"])
def create_artista(
    item: schemas.ArtistaBase,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Crear un nuevo artista (requiere autenticación)"""
    return crud.create_item(db, models.Artista, item)

@app.get("/artista/", response_model=List[schemas.Artista], tags=["Artists"])
def read_artistas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Obtener todos los artistas (requiere autenticación)"""
    return crud.get_items(db, models.Artista, skip, limit)

@app.get("/artista/{item_id}", response_model=schemas.Artista, tags=["Artists"])
def read_artista(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Obtener un artista por ID (requiere autenticación)"""
    return crud.get_item(db, models.Artista, item_id)

@app.put("/artista/{item_id}", response_model=schemas.Artista, tags=["Artists"])
def update_artista(
    item_id: int,
    item: schemas.ArtistaBase,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Actualizar un artista (requiere autenticación)"""
    return crud.update_item(db, models.Artista, item_id, item)

@app.delete("/artista/{item_id}", tags=["Artists"])
def delete_artista(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Eliminar un artista (requiere autenticación)"""
    return crud.delete_item(db, models.Artista, item_id)

# ============================================
# ENDPOINTS DE USUARIO (PROTEGIDOS)
# ============================================

@app.get("/usuario/", response_model=List[schemas.Usuario], tags=["Users"])
def read_usuarios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Obtener todos los usuarios (requiere autenticación)"""
    return crud.get_items(db, models.Usuario, skip, limit)

@app.get("/usuario/{item_id}", response_model=schemas.Usuario, tags=["Users"])
def read_usuario(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Obtener un usuario por ID (requiere autenticación)"""
    return crud.get_item(db, models.Usuario, item_id)

@app.put("/usuario/{item_id}", response_model=schemas.Usuario, tags=["Users"])
def update_usuario(
    item_id: int,
    item: schemas.UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Actualizar un usuario (requiere autenticación)
    Los usuarios solo pueden actualizar su propia información
    """
    if current_user.id != item_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar este usuario"
        )
    return crud.update_item(db, models.Usuario, item_id, item)

@app.delete("/usuario/{item_id}", tags=["Users"])
def delete_usuario(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Eliminar un usuario (requiere autenticación)
    Los usuarios solo pueden eliminarse a sí mismos
    """
    if current_user.id != item_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar este usuario"
        )
    return crud.delete_item(db, models.Usuario, item_id)

# ============================================
# ENDPOINTS DE EVENTO (PROTEGIDOS)
# ============================================

@app.post("/evento/", response_model=schemas.Evento, status_code=status.HTTP_201_CREATED, tags=["Events"])
def create_evento(
    item: schemas.EventoBase,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Crear un nuevo evento (requiere autenticación)"""
    return crud.create_item(db, models.Evento, item)

@app.get("/evento/", response_model=List[schemas.Evento], tags=["Events"])
def read_eventos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Obtener todos los eventos (requiere autenticación)"""
    return crud.get_items(db, models.Evento, skip, limit)

@app.get("/evento/{item_id}", response_model=schemas.Evento, tags=["Events"])
def read_evento(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Obtener un evento por ID (requiere autenticación)"""
    return crud.get_item(db, models.Evento, item_id)

@app.put("/evento/{item_id}", response_model=schemas.Evento, tags=["Events"])
def update_evento(
    item_id: int,
    item: schemas.EventoBase,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Actualizar un evento (requiere autenticación)"""
    return crud.update_item(db, models.Evento, item_id, item)

@app.delete("/evento/{item_id}", tags=["Events"])
def delete_evento(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Eliminar un evento (requiere autenticación)"""
    return crud.delete_item(db, models.Evento, item_id)

# ============================================
# ENDPOINTS DE TICKET (PROTEGIDOS)
# ============================================

@app.post("/ticket/", response_model=schemas.Ticket, status_code=status.HTTP_201_CREATED, tags=["Tickets"])
def create_ticket(
    item: schemas.TicketBase,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Crear un nuevo ticket (requiere autenticación)
    Los usuarios solo pueden crear tickets para sí mismos
    """
    if item.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes crear tickets para otros usuarios"
        )
    return crud.create_item(db, models.Ticket, item)

@app.get("/ticket/", response_model=List[schemas.Ticket], tags=["Tickets"])
def read_tickets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Obtener tickets (requiere autenticación)
    Los usuarios solo ven sus propios tickets
    """
    return db.query(models.Ticket).filter(
        models.Ticket.usuario_id == current_user.id
    ).offset(skip).limit(limit).all()

@app.get("/ticket/{item_id}", response_model=schemas.Ticket, tags=["Tickets"])
def read_ticket(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Obtener un ticket por ID (requiere autenticación)
    Los usuarios solo pueden ver sus propios tickets
    """
    ticket = crud.get_item(db, models.Ticket, item_id)
    if ticket.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este ticket"
        )
    return ticket

@app.put("/ticket/{item_id}", response_model=schemas.Ticket, tags=["Tickets"])
def update_ticket(
    item_id: int,
    item: schemas.TicketBase,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Actualizar un ticket (requiere autenticación)
    Los usuarios solo pueden actualizar sus propios tickets
    """
    ticket = crud.get_item(db, models.Ticket, item_id)
    if ticket.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar este ticket"
        )
    return crud.update_item(db, models.Ticket, item_id, item)

@app.delete("/ticket/{item_id}", tags=["Tickets"])
def delete_ticket(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Eliminar un ticket (requiere autenticación)
    Los usuarios solo pueden eliminar sus propios tickets
    """
    ticket = crud.get_item(db, models.Ticket, item_id)
    if ticket.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar este ticket"
        )
    return crud.delete_item(db, models.Ticket, item_id)

# ============================================
# ENDPOINTS DE PAGO (PROTEGIDOS)
# ============================================

@app.post("/pago/", response_model=schemas.Pago, status_code=status.HTTP_201_CREATED, tags=["Payments"])
def create_pago(
    item: schemas.PagoBase,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Crear un nuevo pago (requiere autenticación)
    Los usuarios solo pueden crear pagos para sí mismos
    """
    if item.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes crear pagos para otros usuarios"
        )
    return crud.create_item(db, models.Pago, item)

@app.get("/pago/", response_model=List[schemas.Pago], tags=["Payments"])
def read_pagos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Obtener pagos (requiere autenticación)
    Los usuarios solo ven sus propios pagos
    """
    return db.query(models.Pago).filter(
        models.Pago.usuario_id == current_user.id
    ).offset(skip).limit(limit).all()

@app.get("/pago/{item_id}", response_model=schemas.Pago, tags=["Payments"])
def read_pago(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Obtener un pago por ID (requiere autenticación)
    Los usuarios solo pueden ver sus propios pagos
    """
    pago = crud.get_item(db, models.Pago, item_id)
    if pago.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este pago"
        )
    return pago

@app.put("/pago/{item_id}", response_model=schemas.Pago, tags=["Payments"])
def update_pago(
    item_id: int,
    item: schemas.PagoBase,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Actualizar un pago (requiere autenticación)
    Los usuarios solo pueden actualizar sus propios pagos
    """
    pago = crud.get_item(db, models.Pago, item_id)
    if pago.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar este pago"
        )
    return crud.update_item(db, models.Pago, item_id, item)

@app.delete("/pago/{item_id}", tags=["Payments"])
def delete_pago(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Eliminar un pago (requiere autenticación)
    Los usuarios solo pueden eliminar sus propios pagos
    """
    pago = crud.get_item(db, models.Pago, item_id)
    if pago.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar este pago"
        )
    return crud.delete_item(db, models.Pago, item_id)

# ============================================
# ENDPOINT DE SALUD (PÚBLICO)
# ============================================

@app.get("/health", tags=["Health"])
def health_check():
    """Verificar que la API está funcionando"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

@app.get("/init-db")
def init_db():
    """
    Endpoint temporal para inicializar las tablas de la base de datos.
    Útil para despliegues en Vercel donde no tenemos acceso a consola.
    """
    try:
        models.Base.metadata.create_all(bind=engine)
        return {"message": "Tablas creadas correctamente en la base de datos"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear tablas: {str(e)}"
        )

@app.get("/seed-db")
def seed_db(db: Session = Depends(get_db)):
    """
    Endpoint para poblar la base de datos con datos ficticios.
    ⚠️ ADVERTENCIA: Esto BORRARÁ todos los datos existentes.
    Solo usar en desarrollo/testing.
    """
    try:
        stats = seed_data.seed_database(db)
        return {
            "message": "Base de datos poblada con datos ficticios",
            "datos_creados": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al poblar la base de datos: {str(e)}"
        )

@app.get("/")
def root():
    """Endpoint raíz con información de la API"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }

