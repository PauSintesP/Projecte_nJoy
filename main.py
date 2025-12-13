# Version: 3.0.0 - CORS Fix Deployment
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List, Optional
from pydantic import BaseModel
import auth

# Imports locales
from database import SessionLocal, engine
import models, schemas, crud
import seed_data
from auth import (
    get_db,
    get_current_active_user,
    get_current_promotor,
    get_current_admin,
    get_current_scanner,
    create_access_token,
    create_refresh_token,
    authenticate_user,
    decode_token
)
from config import settings
import ticket_endpoints
import admin_crud
import admin_schemas
import admin_endpoints
import team_endpoints

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
            "name": "Admin",
            "description": "Panel de administración. Solo accesible para usuarios con rol admin. Permite gestionar usuarios, roles y baneos."
        },
        {
            "name": "Health",
            "description": "Endpoints de monitoreo y estado del servicio. Públicos."
        }
    ]
)



# CORS Configuration - Multiple layers for Vercel compatibility
# CORS Configuration - Multiple layers for Vercel compatibility
# Layer 1: FastAPI's built-in CORS middleware
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "https://njoy-web.vercel.app" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex="https://.*\.vercel\.app",  # Permitir cualquier subdominio de Vercel (previews)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROTERS REGISTRATION ---
# app.include_router(auth.router)  # Auth endpoints are in main.py
app.include_router(ticket_endpoints.router)
# app.include_router(ticket_endpoints.router) # DUPLICATE - Logic moved to main.py -> RESTORED for Mobile App compatibility
app.include_router(team_endpoints.router)
app.include_router(admin_endpoints.router)

# Crear tablas en la base de datos (Post-app creation safe check)
models.Base.metadata.create_all(bind=engine)

# Layer 2: Custom middleware to FORCE CORS headers (fallback for Vercel)
# IMPORTANT: When allow_credentials is True, allow_origin cannot be *
@app.middleware("http")
async def add_cors_headers(request, call_next):
    """
    Middleware personalizado que GARANTIZA que los headers CORS estén presentes
    y sean correctos para solicitudes con credenciales.
    """
    origin = request.headers.get("origin")
    
    # Handle OPTIONS requests (preflight) explicitly
    if request.method == "OPTIONS":
        from fastapi.responses import Response
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": origin if origin else "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Max-Age": "3600",
            }
        )
    
    response = await call_next(request)
    
    # Forzar headers CORS en TODAS las responses
    # Si hay origin, lo usamos para permitir credenciales. Si no, fallback a *
    response.headers["Access-Control-Allow-Origin"] = origin if origin else "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response

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
        print(f"DEBUG: Received user data: {user.model_dump()}")
        new_user = crud.create_item(db, models.Usuario, user)
        print(f"DEBUG: User created successfully with ID: {new_user.id}")
        return new_user
    except HTTPException as e:
        print(f"DEBUG: HTTPException raised: {e.status_code} - {e.detail}")
        raise e
    except Exception as e:
        print(f"DEBUG: Unexpected exception: {type(e).__name__}: {str(e)}")
        import traceback
        error_trace = traceback.format_exc()
        print(f"DEBUG: Full traceback:\n{error_trace}")
        
        # Return more detailed error for debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Error al crear usuario",
                "error_type": type(e).__name__,
                "error_details": str(e),
                "trace": error_trace.split('\n')[-3:] if error_trace else []
            }
        )

@app.post("/login", response_model=schemas.Token, tags=["Authentication"])
def login(credentials: schemas.LoginInput, db: Session = Depends(get_db)):
    """
    Login de usuario
    - Retorna access_token y refresh_token
    - Los tokens son JWT firmados
    - Email case-insensitive
    """
    # Convert email to lowercase for case-insensitive comparison
    email_lower = credentials.email.lower().strip()
    user = authenticate_user(db, email_lower, credentials.contrasena)
    
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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo administradores")
    
    # Email case-insensitive
    email_lower = user_data.email.lower().strip()
    if db.query(models.Usuario).filter(models.Usuario.email == email_lower).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email ya registrado")
    
    from auth import hash_password
    new_user = models.Usuario(
        nombre=user_data.nombre,
        apellidos=user_data.apellidos,
        email=email_lower,
        password=hash_password(user_data.password),
        fecha_nacimiento=user_data.fecha_nacimiento,
        pais=user_data.pais,
        role=user_data.role if hasattr(user_data, 'role') and user_data.role else 'user',
        is_active=True,
        is_banned=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# ============================================
# TICKET ENDPOINTS
# ============================================

@app.post("/tickets/purchase", tags=["Tickets"])
def purchase_tickets(
    evento_id: int,
    cantidad: int = 1,
    nombres_asistentes: list[str] = None,  # Optional list of attendee names
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Comprar entradas - Nombres opcionales (usa nombre comprador si no se especifica)"""
    import random
    import string
    
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    tickets_vendidos = db.query(models.Ticket).filter(models.Ticket.evento_id == evento_id).count()
    plazas_disponibles = evento.plazas - tickets_vendidos
    
    if cantidad > plazas_disponibles:
        raise HTTPException(status_code=400, detail=f"Solo hay {plazas_disponibles} plazas disponibles")
    
    # If no names provided, use buyer's name for all tickets
    if not nombres_asistentes:
        buyer_name = f"{current_user.nombre} {current_user.apellidos}"
        nombres_asistentes = [buyer_name] * cantidad
    elif len(nombres_asistentes) != cantidad:
        # If partial list, fill remaining with buyer's name
        buyer_name = f"{current_user.nombre} {current_user.apellidos}"
        while len(nombres_asistentes) < cantidad:
            nombres_asistentes.append(buyer_name)
    
    def generate_ticket_code():
        """Generate unique 6-digit alphanumeric ticket code (User Request: Short codes)"""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not db.query(models.Ticket).filter(models.Ticket.codigo_ticket == code).first():
                return code
    
    tickets_created = []
    for i in range(cantidad):
        ticket_code = generate_ticket_code()
        new_ticket = models.Ticket(
            codigo_ticket=ticket_code,
            nombre_asistente=nombres_asistentes[i].strip() if nombres_asistentes[i] else None,
            evento_id=evento_id,
            usuario_id=current_user.id,
            activado=True
        )
        db.add(new_ticket)
        tickets_created.append(new_ticket)
    
    db.commit()
    for ticket in tickets_created:
        db.refresh(ticket)
    
    return {
        "message": f"¡Compra exitosa! {cantidad} entrada(s) adquirida(s)",
        "cantidad": cantidad,
        "total": evento.precio * cantidad if evento.precio else 0,
        "tickets": [{"id": t.id, "codigo": t.codigo_ticket, "nombre": t.nombre_asistente, "evento_id": t.evento_id} for t in tickets_created]
    }

@app.get("/tickets/my-tickets", tags=["Tickets"])
def get_my_tickets(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Obtener todos los tickets del usuario autenticado"""
    tickets = db.query(models.Ticket).filter(models.Ticket.usuario_id == current_user.id).all()
    tickets_with_events = []
    for ticket in tickets:
        evento = db.query(models.Evento).filter(models.Evento.id == ticket.evento_id).first()
        if evento:
            tickets_with_events.append({
                "ticket_id": ticket.id,
                "codigo_ticket": ticket.codigo_ticket,
                "nombre_asistente": ticket.nombre_asistente,
                "activado": ticket.activado,
                "evento": {
                    "id": evento.id,
                    "nombre": evento.nombre,
                    "descripcion": evento.descripcion,
                    "fechayhora": evento.fechayhora.isoformat() if evento.fechayhora else None,
                    "recinto": evento.recinto,
                    "imagen": evento.imagen,
                    "precio": evento.precio,
                    "tipo": evento.tipo
                }
            })
    return tickets_with_events

@app.get("/tickets/{ticket_id}", tags=["Tickets"])
def get_ticket_detail(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Obtener detalle de un ticket específico"""
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    
    if ticket.usuario_id != current_user.id and current_user.role not in ['admin', 'scanner']:
        raise HTTPException(status_code=403, detail="Sin permiso")
    
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

@app.post("/tickets/scan/{codigo_ticket}", tags=["Tickets"])
def scan_ticket(
    codigo_ticket: str,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Escanear y validar ticket mediante código QR
    - Verde: Ticket válido (primera vez)
    - Rojo: Ticket ya usado
    - Rojo: Ticket no existe
    Solo accesible para roles: scanner, promotor, admin
    """
    # Verificar permisos
    # Modificado para permitir roles globales (scanner/admin) sin depender de Teams estrictamente
    evento = None # Initialize evento to None
    if current_user.role in ['admin', 'scanner', 'promotor', 'owner']:
        # Permitir acceso global
        pass
    else:
        # Fallback a lógica de equipos
        # =================================================================================
        # VERIFICACIÓN DE PERMISOS (TEAMS)
        # =================================================================================
        is_authorized = False
        
        # First, try to find the ticket to get the event_id for team checks
        ticket_for_event_check = db.query(models.Ticket).filter(
            models.Ticket.codigo_ticket.ilike(codigo_ticket.strip())
        ).first()
        if ticket_for_event_check:
            evento = db.query(models.Evento).filter(models.Evento.id == ticket_for_event_check.evento_id).first()

        # 1. Creador del Evento (Owner/Promotor) check extendido
        if evento and evento.creador_id == current_user.id:
            is_authorized = True
            
        # 2. Miembro de Equipo (Scanner)
        elif evento:
            # Verificar si el usuario activo pertenece a algún equipo liderado por el creador del evento
            membership = db.query(models.TeamMember).join(models.Team).filter(
                models.TeamMember.user_id == current_user.id,
                models.TeamMember.status == 'accepted',
                models.Team.leader_id == evento.creador_id
            ).first()
            
            if membership:
                is_authorized = True
                
        if not is_authorized:
            return {
                "success": False,
                "status": "error",
                "message": "NO AUTORIZADO (EQUIPO INCORRECTO)",
                "color": "red",
                "codigo": codigo_ticket,
                "evento": evento.nombre if evento else "Desconocido"
            }
        # =================================================================================

    # Buscar ticket por código (case insensitive)
    ticket = db.query(models.Ticket).filter(
        models.Ticket.codigo_ticket.ilike(codigo_ticket.strip())
    ).first()
    
    # FALLBACK: Si no se encuentra por código, verificar si es formato fallback "NJOY-TICKET-{ID}"
    if not ticket and "NJOY-TICKET-" in codigo_ticket.upper():
        try:
            # Extraer ID
            potential_id = codigo_ticket.upper().split("NJOY-TICKET-")[1]
            ticket_id = int(potential_id)
            ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
            print(f"DEBUG: Recuperado ticket por ID {ticket_id} desde QR String")
        except:
            print(f"DEBUG: Fallo al parsear ID de {codigo_ticket}")
            pass
    
    if not ticket:
        return {
            "success": False,
            "status": "error",
            "message": "TICKET NO ENCONTRADO",
            "color": "red",
            "codigo": codigo_ticket,
            "ticket": None
        }
    
    # Obtener información del evento (si no se obtuvo antes por team check)
    if not evento:
        evento = db.query(models.Evento).filter(models.Evento.id == ticket.evento_id).first()
    
    # Verificar si ya fue usado
    if not ticket.activado:
        return {
            "success": False,
            "status": "error",
            "message": "ENTRADA YA UTILIZADA",
            "color": "red",
            "codigo": codigo_ticket,
            "nombre_asistente": ticket.nombre_asistente,
            "evento": evento.nombre if evento else "Desconocido",
            "user_name": ticket.nombre_asistente, # Mobile compatibility
            "event_name": evento.nombre if evento else "Desconocido", # Mobile compatibility
            "ticket_id": ticket.id
        }
    
    # Ticket válido - marcarlo como usado
    ticket.activado = False
    db.commit()
    db.refresh(ticket)
    
    return {
        "success": True,
        "status": "success",
        "message": "ENTRADA VÁLIDA ✓",
        "color": "green",
        "codigo": codigo_ticket,
        "user_name": ticket.nombre_asistente,
        "event_name": evento.nombre if evento else "Desconocido",
        "ticket_id": ticket.id,
        "ticket": {"id": ticket.id, "activado": False} # Basic ticket info for mobile
    }

@app.post("/scanner/activate-ticket/{ticket_id}", tags=["Tickets"])
def activate_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Activar (usar) un ticket por ID.
    El paso previo /scan retorna el ID y valida.
    Este endpoint marca el ticket como usado.
    """
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    
    # Obtener evento
    evento = db.query(models.Evento).filter(models.Evento.id == ticket.evento_id).first()

    # --- VERIFICACIÓN DE PERMISOS (Igual que en scan) ---
    is_authorized = False
    if current_user.role == 'admin':
        is_authorized = True
    elif evento and evento.creador_id == current_user.id:
        is_authorized = True
    elif evento:
        membership = db.query(models.TeamMember).join(models.Team).filter(
            models.TeamMember.user_id == current_user.id,
            models.TeamMember.status == 'accepted',
            models.Team.leader_id == evento.creador_id
        ).first()
        if membership:
            is_authorized = True
            
    if not is_authorized:
        return {
            "success": False,
            "status": "error",
            "message": "NO AUTORIZADO",
            "color": "red"
        }
    # ----------------------------------------------------

    if not ticket.activado:
        # Ya fue usado (aunque el scan previo haya dicho que existía)
        return {
            "success": False,
            "status": "error",
            "message": "YA UTILIZADO",
            "user_name": ticket.nombre_asistente,
            "event_name": evento.nombre if evento else "Desconocido"
        }
    
    # MARCAR COMO USADO
    ticket.activado = False
    db.commit()
    
    return {
        "success": True,
        "status": "success",
        "message": "ENTRADA VÁLIDA",
        "user_name": ticket.nombre_asistente,
        "event_name": evento.nombre if evento else "Desconocido"
    }

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
    db: Session = Depends(get_db)
):
    """Obtener todas las localidades (público)"""
    try:
        return crud.get_items(db, models.Localidad, skip, limit)
    except Exception as e:
        print(f"ERROR in /localidad/: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return empty list instead of 500 error
        return []

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
    db: Session = Depends(get_db)
):
    """Obtener todos los géneros (público)"""
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
    db: Session = Depends(get_db)
):
    """Obtener todos los artistas (público)"""
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
# ENDPOINTS DE ADMINISTRACIÓN (SOLO ADMIN)
# ============================================

@app.get("/admin/users", response_model=List[schemas.Usuario], tags=["Admin"])
def admin_get_all_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_banned: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: models.Usuario = Depends(get_current_admin)
):
    """
    Obtener todos los usuarios con filtros opcionales (solo admin)
    
    Filtros disponibles:
    - role: Filtrar por rol (user, promotor, owner, admin)
    - is_active: Filtrar por estado activo
    - is_banned: Filtrar por estado baneado
    - search: Buscar por nombre, apellidos o email
    """
    return admin_crud.get_all_users_admin(
        db, skip, limit, role, is_active, is_banned, search
    )

@app.get("/admin/users/{user_id}", response_model=schemas.Usuario, tags=["Admin"])
def admin_get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Usuario = Depends(get_current_admin)
):
    """Obtener detalles de un usuario específico (solo admin)"""
    return crud.get_item(db, models.Usuario, user_id)

@app.put("/admin/users/{user_id}", response_model=schemas.Usuario, tags=["Admin"])
def admin_update_user(
    user_id: int,
    user_data: admin_schemas.AdminUserUpdate,
    db: Session = Depends(get_db),
    current_admin: models.Usuario = Depends(get_current_admin)
):
    """
    Actualizar un usuario desde el panel admin
    Permite modificar cualquier campo incluyendo role, is_active, is_banned
    """
    user = db.query(models.Usuario).filter(models.Usuario.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Actualizar campos proporcionados
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

@app.delete("/admin/users/{user_id}", tags=["Admin"])
def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Usuario = Depends(get_current_admin)
):
    """Eliminar un usuario (solo admin)"""
    return admin_crud.delete_user_admin(db, user_id)

@app.post("/admin/users/{user_id}/ban", response_model=schemas.Usuario, tags=["Admin"])
def admin_ban_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Usuario = Depends(get_current_admin)
):
    """Banear un usuario (solo admin)"""
    return admin_crud.ban_user(db, user_id)

@app.post("/admin/users/{user_id}/unban", response_model=schemas.Usuario, tags=["Admin"])
def admin_unban_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Usuario = Depends(get_current_admin)
):
    """Desbanear un usuario (solo admin)"""
    return admin_crud.unban_user(db, user_id)

@app.post("/admin/users/{user_id}/promote-owner", response_model=schemas.Usuario, tags=["Admin"])
def admin_promote_to_owner(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Usuario = Depends(get_current_admin)
):
    """Promover un usuario a rol 'owner' (solo admin)"""
    return admin_crud.update_user_role(db, user_id, "owner")

@app.get("/admin/statistics", response_model=admin_schemas.UserStatistics, tags=["Admin"])
def admin_get_statistics(
    db: Session = Depends(get_db),
    current_admin: models.Usuario = Depends(get_current_admin)
):
    """Obtener estadísticas de usuarios (solo admin)"""
    return admin_crud.get_user_statistics(db)


# ============================================
# ENDPOINTS DE EVENTO (PROTEGIDOS)
# ============================================

@app.post("/evento/", response_model=schemas.Evento, status_code=status.HTTP_201_CREATED, tags=["Events"])
def create_evento(
    item: schemas.EventoBase,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_promotor)
):
    """Crear un nuevo evento (requiere rol de promotor o admin)"""
    try:
        # Set creador_id automatically from current user
        event_data = item.dict()
        event_data['creador_id'] = current_user.id
        return crud.create_item(db, models.Evento, schemas.EventoBase(**event_data))
    except Exception as e:
        print(f"ERROR creating event: {str(e)}")
        # Check for IntegrityError (FK violation)
        if "Foreign key violation" in str(e) or "IntegrityError" in str(e) or "foreign key constraint" in str(e):
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Datos inválidos: Violación de integridad (verifique Organizador DNI, Localidad ID, Género ID). Detalle: {str(e)}"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear evento: {str(e)}"
        )

@app.get("/evento/", response_model=List[schemas.Evento], tags=["Events"])
def read_eventos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener todos los eventos (endpoint público)"""
    try:
        eventos = crud.get_items(db, models.Evento, skip, limit)
        # Calculate tickets sold for each event
        for event in eventos:
            count = db.query(models.Ticket).filter(models.Ticket.evento_id == event.id).count()
            setattr(event, "tickets_vendidos", count)
        return eventos
    except Exception as e:
        print(f"ERROR in /evento/: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return empty list instead of 500 error for better UX
        return []

@app.get("/evento/{item_id}", response_model=schemas.Evento, tags=["Events"])
def read_evento(
    item_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un evento por ID (endpoint público)"""
    evento = crud.get_item(db, models.Evento, item_id)
    if evento:
        count = db.query(models.Ticket).filter(models.Ticket.evento_id == evento.id).count()
        setattr(evento, "tickets_vendidos", count)
    return evento

@app.get("/eventos/mis-eventos", response_model=List[schemas.Evento], tags=["Events"])
def get_my_eventos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_promotor)
):
    """Obtener eventos creados por el usuario actual (promotor o admin)"""
    if current_user.role == 'admin':
        # Admin puede ver todos los eventos
        eventos = crud.get_items(db, models.Evento, skip, limit)
    else:
        # Promotor solo ve sus propios eventos
        eventos = db.query(models.Evento).filter(
            models.Evento.creador_id == current_user.id
        ).offset(skip).limit(limit).all()
    
    # Calculate tickets sold
    for event in eventos:
        count = db.query(models.Ticket).filter(models.Ticket.evento_id == event.id).count()
        setattr(event, "tickets_vendidos", count)
        
    return eventos

@app.put("/evento/{item_id}", response_model=schemas.Evento, tags=["Events"])
def update_evento(
    item_id: int,
    item: schemas.EventoBase,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_promotor)
):
    """Actualizar un evento (requiere rol de promotor o admin, promotor solo puede editar sus eventos)"""
    # Get the event
    evento = db.query(models.Evento).filter(models.Evento.id == item_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    # Check permissions: admin can edit all, promotor can only edit their own
    if current_user.role != 'admin' and evento.creador_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="No tienes permiso para editar este evento. Solo puedes editar tus propios eventos."
        )
    
    return crud.update_item(db, models.Evento, item_id, item)

@app.delete("/evento/{item_id}", tags=["Events"])
def delete_evento(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_promotor)
):
    """Eliminar un evento (requiere rol de promotor)"""
    return crud.delete_item(db, models.Evento, item_id)

# ============================================
# ENDPOINTS DE GÉNERO (PROTEGIDOS/PÚBLICOS)
# ============================================

@app.post("/genero/", response_model=schemas.Genero, status_code=status.HTTP_201_CREATED, tags=["Genres"])
def create_genero(
    item: schemas.GeneroBase,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Crear un nuevo género (requiere autenticación)"""
    return crud.create_item(db, models.Genero, item)

@app.post("/genero/auto", response_model=schemas.Genero, status_code=status.HTTP_201_CREATED, tags=["Genres"])
def create_or_get_genero(
    nombre: str,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Crear un género automáticamente si no existe, o devolver el existente.
    Ideal para formularios donde el usuario puede escribir un género nuevo.
    """
    # Buscar si ya existe un género con ese nombre (case-insensitive)
    existing = db.query(models.Genero).filter(
        models.Genero.nombre.ilike(nombre.strip())
    ).first()
    
    if existing:
        return existing
    
    # Si no existe, crear uno nuevo
    new_genero = models.Genero(nombre=nombre.strip())
    db.add(new_genero)
    db.commit()
    db.refresh(new_genero)
    return new_genero

@app.get("/genero/", response_model=List[schemas.Genero], tags=["Genres"])
def read_generos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener todos los géneros (endpoint público)"""
    return crud.get_items(db, models.Genero, skip, limit)

@app.get("/genero/{item_id}", response_model=schemas.Genero, tags=["Genres"])
def read_genero(
    item_id: int,
    db: Session = Depends(get_db)
):
    """Obtener un género por ID (endpoint público)"""
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
# ENDPOINTS DE LOCALIDAD (PROTEGIDOS/PÚBLICOS)
# ============================================

class LocalidadCreate(BaseModel):
    ciudad: str
    latitud: Optional[float] = None
    longitud: Optional[float] = None

@app.post("/localidad/", response_model=schemas.Localidad, status_code=status.HTTP_201_CREATED, tags=["Locations"])
def create_localidad(
    item: schemas.LocalidadBase,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Crear una nueva localidad (requiere autenticación)"""
    return crud.create_item(db, models.Localidad, item)

@app.post("/localidad/auto", response_model=schemas.Localidad, status_code=status.HTTP_201_CREATED, tags=["Locations"])
def create_or_get_localidad(
    ciudad: str,
    latitud: Optional[float] = None,
    longitud: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Crear una localidad automáticamente si no existe, o devolver la existente.
    Puede incluir coordenadas de latitud y longitud.
    """
    # Buscar si ya existe una localidad con ese nombre (case-insensitive)
    existing = db.query(models.Localidad).filter(
        models.Localidad.ciudad.ilike(ciudad.strip())
    ).first()
    
    if existing:
        return existing
    
    # Si no existe, crear una nueva
    new_localidad = models.Localidad(ciudad=ciudad.strip())
    db.add(new_localidad)
    db.commit()
    db.refresh(new_localidad)
    return new_localidad

@app.get("/localidad/", response_model=List[schemas.Localidad], tags=["Locations"])
def read_localidades(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener todas las localidades (endpoint público)"""
    return crud.get_items(db, models.Localidad, skip, limit)

@app.get("/localidad/{item_id}", response_model=schemas.Localidad, tags=["Locations"])
def read_localidad(
    item_id: int,
    db: Session = Depends(get_db)
):
    """Obtener una localidad por ID (endpoint público)"""
    return crud.get_item(db, models.Localidad, item_id)

@app.put("/localidad/{item_id}", response_model=schemas.Localidad, tags=["Locations"])
def update_localidad(
    item_id: int,
    item: schemas.LocalidadBase,
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
# ENDPOINTS DE ORGANIZADOR (PROTEGIDOS/PÚBLICOS)
# ============================================

@app.post("/organizador/", response_model=schemas.Organizador, status_code=status.HTTP_201_CREATED, tags=["Organizers"])
def create_organizador(
    item: schemas.OrganizadorBase,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Crear un nuevo organizador (requiere autenticación)"""
    return crud.create_item(db, models.Organizador, item)

@app.post("/organizador/auto", response_model=schemas.Organizador, status_code=status.HTTP_201_CREATED, tags=["Organizers"])
def create_or_get_organizador(
    dni: str,
    ncompleto: str,
    email: str,
    telefono: str,
    web: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Crear un organizador automáticamente si no existe, o devolver el existente.
    """
    # Buscar si ya existe un organizador con ese DNI
    existing = db.query(models.Organizador).filter(
        models.Organizador.dni == dni.strip()
    ).first()
    
    if existing:
        return existing
    
    # Si no existe, crear uno nuevo
    new_organizador = models.Organizador(
        dni=dni.strip(),
        ncompleto=ncompleto.strip(),
        email=email.strip(),
        telefono=telefono.strip(),
        web=web.strip() if web else None
    )
    db.add(new_organizador)
    db.commit()
    db.refresh(new_organizador)
    return new_organizador

@app.get("/organizador/", response_model=List[schemas.Organizador], tags=["Organizers"])
def read_organizadores(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener todos los organizadores (endpoint público)"""
    return crud.get_items(db, models.Organizador, skip, limit)

@app.get("/organizador/{dni}", response_model=schemas.Organizador, tags=["Organizers"])
def read_organizador(
    dni: str,
    db: Session = Depends(get_db)
):
    """Obtener un organizador por DNI (endpoint público)"""
    organizador = db.query(models.Organizador).filter(models.Organizador.dni == dni).first()
    if not organizador:
        raise HTTPException(status_code=404, detail="Organizador no encontrado")
    return organizador

@app.put("/organizador/{dni}", response_model=schemas.Organizador, tags=["Organizers"])
def update_organizador(
    dni: str,
    item: schemas.OrganizadorBase,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Actualizar un organizador (requiere autenticación)"""
    organizador = db.query(models.Organizador).filter(models.Organizador.dni == dni).first()
    if not organizador:
        raise HTTPException(status_code=404, detail="Organizador no encontrado")
    for key, value in item.model_dump(exclude_unset=True).items():
        setattr(organizador, key, value)
    db.commit()
    db.refresh(organizador)
    return organizador

@app.delete("/organizador/{dni}", tags=["Organizers"])
def delete_organizador(
    dni: str,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Eliminar un organizador (requiere autenticación)"""
    organizador = db.query(models.Organizador).filter(models.Organizador.dni == dni).first()
    if not organizador:
        raise HTTPException(status_code=404, detail="Organizador no encontrado")
    db.delete(organizador)
    db.commit()
    return {"message": "Organizador eliminado correctamente"}

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
# ENDPOINTS DE SCANNER (ESCANEO DE TICKETS)
# ============================================

@app.post("/scanner/validate-ticket", response_model=schemas.TicketScanResponse, tags=["Scanner"])
def validate_ticket(
    request: schemas.TicketScanRequest,
    db: Session = Depends(get_db),
    current_scanner: models.Usuario = Depends(get_current_scanner)
):
    """
    Validar un ticket (requiere rol scanner, promotor, owner o admin)
    Retorna información del ticket, evento y usuario
    """
    try:
        ticket = db.query(models.Ticket).filter(models.Ticket.id == request.ticket_id).first()
        
        if not ticket:
            return schemas.TicketScanResponse(
                success=False,
                message="Ticket no encontrado"
            )
        
        # PERMISSION CHECK (RELAXED)
        # ---------------------------------------------------------------------
        if current_scanner.role in ['admin', 'scanner', 'promotor', 'owner']:
             pass # Allow global access
        else:
             # Strict team check... (Simplified: if you are here via get_current_scanner, you have role 'scanner' or similar)
             # But get_current_scanner only checks for role existence.
             # We assume if you have the ROLE, you can scan.
             pass 
        # ---------------------------------------------------------------------
        
        # Get event details
        event = db.query(models.Evento).filter(models.Evento.id == ticket.evento_id).first()
        event_name = event.nombre if event else "Evento desconocido"
        
        # Get user details
        user = db.query(models.Usuario).filter(models.Usuario.id == ticket.usuario_id).first()
        user_name = f"{user.nombre} {user.apellidos}" if user else "Usuario desconocido"
        
        # Check if ticket is already used
        if not ticket.activado:
            return schemas.TicketScanResponse(
                success=False,
                message="⚠️ Ticket ya utilizado",
                ticket=ticket,
                event_name=event_name,
                user_name=user_name
            )
        
        return schemas.TicketScanResponse(
            success=True,
            message="✅ Ticket válido",
            ticket=ticket,
            event_name=event_name,
            user_name=user_name
        )
    
    except Exception as e:
        print(f"ERROR validating ticket: {type(e).__name__}: {str(e)}")
        return schemas.TicketScanResponse(
            success=False,
            message=f"Error al validar ticket: {str(e)}"
        )

@app.post("/scanner/activate-ticket/{ticket_id}", response_model=schemas.TicketScanResponse, tags=["Scanner"])
def activate_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_scanner: models.Usuario = Depends(get_current_scanner)
):
    """
    Marcar un ticket como utilizado/activado (requiere rol scanner)
    """
    try:
        ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
        
        if not ticket:
            return schemas.TicketScanResponse(
                success=False,
                message="Ticket no encontrado"
            )
        
        # PERMISSION CHECK (RELAXED) - Removed strict team checking
        if current_scanner.role in ['admin', 'scanner', 'promotor', 'owner']:
             pass 
        
        if not ticket.activado:
            return schemas.TicketScanResponse(
                success=False,
                message="Ticket ya fue utilizado anteriormente"
            )
        
        # Mark ticket as used
        ticket.activado = False
        db.commit()
        db.refresh(ticket)
        
        # Get event details
        event = db.query(models.Evento).filter(models.Evento.id == ticket.evento_id).first()
        event_name = event.nombre if event else "Evento desconocido"
        
        # Get user details
        user = db.query(models.Usuario).filter(models.Usuario.id == ticket.usuario_id).first()
        user_name = f"{user.nombre} {user.apellidos}" if user else "Usuario desconocido"
        
        return schemas.TicketScanResponse(
            success=True,
            message="✅ Ticket escaneado y marcado como utilizado",
            ticket=ticket,
            event_name=event_name,
            user_name=user_name
        )
    
    except Exception as e:
        print(f"ERROR activating ticket: {type(e).__name__}: {str(e)}")
        db.rollback()
        return schemas.TicketScanResponse(
            success=False,
            message=f"Error al escanear ticket: {str(e)}"
        )

@app.get("/scanner/my-events", response_model=List[schemas.Evento], tags=["Scanner"])
def get_scanner_events(
    db: Session = Depends(get_db),
    current_scanner: models.Usuario = Depends(get_current_scanner)
):
    """
    Obtener eventos disponibles para escanear (requiere rol scanner)
    """
    try:
        # Get all events - scanners can see all events to know which ones they can scan
        events = db.query(models.Evento).all()
        return events
    except Exception as e:
        print(f"ERROR getting scanner events: {type(e).__name__}: {str(e)}")
        return []


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
    Endpoint para inicializar las tablas de la base de datos.
    Útil para despliegues en Vercel donde no tenemos acceso a consola.
    ⚠️ ADVERTENCIA: Esto CREARÁ las tablas si no existen.
    """
    try:
        print("DEBUG: Creating database tables...")
        models.Base.metadata.create_all(bind=engine)
        print("DEBUG: Database tables created successfully")
        return {
            "message": "Tablas creadas correctamente en la base de datos",
            "tables": [table.name for table in models.Base.metadata.sorted_tables]
        }
    except Exception as e:
        print(f"DEBUG: Error creating tables: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear tablas: {str(e)}"
        )

@app.get("/seed-test-data", tags=["Admin"])
def seed_test_data(db: Session = Depends(get_db)):
    """
    Seed database with test users and events (PUBLIC - for initial setup)
    """
    
    from datetime import date
    
    users_data = [
        {"nombre": "Carlos", "apellidos": "Escáner", "email": "scanner@njoy.com", "password": "scanner123", "role": "scanner"},
        {"nombre": "María", "apellidos": "Promotora", "email": "promotor@njoy.com", "password": "promotor123", "role": "promotor"},
        {"nombre": "Juan", "apellidos": "Usuario", "email": "user@njoy.com", "password": "user123", "role": "user"}
    ]
    
    created = []
    for user_data in users_data:
        if db.query(models.Usuario).filter(models.Usuario.email == user_data["email"]).first():
            continue
        
        from auth import hash_password
        new_user = models.Usuario(
            nombre=user_data["nombre"],
            apellidos=user_data["apellidos"],
            email=user_data["email"],
            password=hash_password(user_data["password"]),
            fecha_nacimiento=date(1995, 1, 1),
            pais="España",
            role=user_data["role"],
            is_active=True,
            is_banned=False
        )
        db.add(new_user)
        created.append(user_data["email"])
    
    # Sample events
    from datetime import datetime
    events_data = [
        {
            "nombre": "Rock Festival 2025",
            "descripcion": "Festival de rock",
            "fechayhora": datetime(2025, 7, 15, 20, 0),
            "recinto": "Estadio Municipal",
            "precio": 45.0,
            "plazas": 5000,
            "tipo": "Concierto",
            "localidad_id": None,
            "organizador_dni": None,
            "genero_id": None
        },
        {
            "nombre": "Noche Electrónica",
            "descripcion": "DJs internacionales",
            "fechayhora": datetime(2025, 6, 20, 22, 0),
            "recinto": "Club Downtown",
            "precio": 30.0,
            "plazas": 1000,
            "tipo": "Concierto",
            "localidad_id": None,
            "organizador_dni": None,
            "genero_id": None
        },
        {
            "nombre": "Jazz en Vivo",
            "descripcion": "Velada íntima de jazz",
            "fechayhora": datetime(2025, 5, 10, 19, 30),
            "recinto": "Auditorio Cultural",
            "precio": 25.0,
            "plazas": 300,
            "tipo": "Concierto",
            "localidad_id": None,
            "organizador_dni": None,
            "genero_id": None
        }
    ]
    
    events_created = []
    for event_data in events_data:
        if db.query(models.Evento).filter(models.Evento.nombre == event_data["nombre"]).first():
            continue
        
        new_event = models.Evento(**event_data)
        db.add(new_event)
        events_created.append(event_data["nombre"])
    
    db.commit()
    
    return {
        "message": "Datos de prueba creados",
        "users_created": created,
        "events_created": events_created,
        "credentials": {
            "scanner": "scanner@njoy.com / scanner123",
            "promotor": "promotor@njoy.com / promotor123",
            "user": "user@njoy.com / user123"
        }
    }

@app.get("/drop-and-recreate-db")
def drop_and_recreate_db():
    """
    ⚠️ PELIGRO: Elimina TODAS las tablas y las recrea.
>>>>>>> Stashed changes
    Esto BORRARÁ TODOS LOS DATOS.
    Solo usar en desarrollo.
    """
    try:
        print("DEBUG: Dropping all tables...")
        models.Base.metadata.drop_all(bind=engine)
        print("DEBUG: Tables dropped successfully")
        
        print("DEBUG: Creating database tables...")
        models.Base.metadata.create_all(bind=engine)
        print("DEBUG: Database tables created successfully")
        
        return {
            "message": "⚠️ TODAS las tablas fueron eliminadas y recreadas",
            "warning": "TODOS LOS DATOS FUERON ELIMINADOS",
            "tables": [table.name for table in models.Base.metadata.sorted_tables]
        }
    except Exception as e:
        print(f"DEBUG: Error recreating tables: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error al recrear tablas: {str(e)}"
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

@app.get("/test-deployment-nov24")
def test_deployment():
    """Test endpoint to verify deployment is working - November 24 2025"""
    return {
        "status": "OK",
        "message": "Backend is deployed and running - November 24 16:15",
        "version": "3.1.0-test"
    }


@app.get("/debug/cors", tags=["Health"])
def debug_cors():
    """
    Endpoint de diagnóstico para verificar la configuración de CORS
    ⚠️ Solo para debugging - ELIMINAR en producción
    """
    import os
    return {
        "allowed_origins": settings.ALLOWED_ORIGINS,
        "allowed_origins_count": len(settings.ALLOWED_ORIGINS),
        "env_variable_raw": os.getenv("ALLOWED_ORIGINS", "NOT_SET"),
        "app_name": settings.APP_NAME
    }


