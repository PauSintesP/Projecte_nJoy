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



# ============================================
# CORS CONFIGURATION - SECURITY LAYER 1
# ============================================
# STRICT CORS: Only allow requests from explicitly authorized origins
# Mobile apps are not affected by CORS (native HTTP requests)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # Use explicit list from environment config
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# --- ROTERS REGISTRATION ---
# app.include_router(auth.router)  # Auth endpoints are in main.py
app.include_router(ticket_endpoints.router)
# app.include_router(ticket_endpoints.router) # DUPLICATE - Logic moved to main.py -> RESTORED for Mobile App compatibility
app.include_router(team_endpoints.router)
app.include_router(admin_endpoints.router)

# Crear tablas en la base de datos (Post-app creation safe check)
models.Base.metadata.create_all(bind=engine)

# ============================================
# CORS CONFIGURATION - SECURITY LAYER 2
# ============================================
# Custom middleware for strict origin validation
@app.middleware("http")
async def validate_origin_middleware(request, call_next):
    """
    STRICT ORIGIN VALIDATION MIDDLEWARE
    
    - Rejects requests from unauthorized origins with 403 Forbidden
    - Allows requests without Origin header (native mobile apps, direct API calls)
    - Enforces ALLOWED_ORIGINS from environment configuration
    """
    from fastapi.responses import JSONResponse
    
    origin = request.headers.get("origin")
    
    # If Origin header is present (browser request), validate it
    if origin:
        # Check if origin is in allowed list
        is_allowed = origin in settings.ALLOWED_ORIGINS
        
        if not is_allowed:
            # LOG SECURITY EVENT
            print(f"🚫 BLOCKED REQUEST from unauthorized origin: {origin}")
            print(f"   Path: {request.url.path}")
            print(f"   Method: {request.method}")
            
            # Return 403 Forbidden for unauthorized origins
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "Origin not allowed",
                    "error": "CORS policy: This origin is not authorized to access this API"
                },
                headers={
                    "Access-Control-Allow-Origin": origin,  # Required for browser to show error
                }
            )
    
    # Handle OPTIONS preflight requests
    if request.method == "OPTIONS":
        from fastapi.responses import Response
        # Only return success if origin is allowed (or no origin header)
        allowed_origin = origin if (not origin or origin in settings.ALLOWED_ORIGINS) else settings.ALLOWED_ORIGINS[0]
        
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": allowed_origin,
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Max-Age": "3600",
            }
        )
    
    # Process request
    response = await call_next(request)
    
    # Add CORS headers to response (only for allowed origins)
    if origin and origin in settings.ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    elif not origin:
        # No origin header (mobile app, server-to-server, etc.)
        # Don't add CORS headers - not needed for native requests
        pass
    
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
    - Envía email de verificación automáticamente
    """
    try:
        print(f"DEBUG: Received user data: {user.model_dump()}")
        new_user = crud.create_item(db, models.Usuario, user)
        print(f"DEBUG: User created successfully with ID: {new_user.id}")
        
        # EMAIL VERIFICATION ENABLED
        # Generate verification token and send email
        import secrets
        from datetime import datetime, timedelta
        from email_service import EmailService
        
        # Generate unique token
        verification_token = secrets.token_urlsafe(32)
        new_user.verification_token = verification_token
        new_user.verification_token_expiry = datetime.now() + timedelta(hours=settings.VERIFICATION_TOKEN_EXPIRY_HOURS)
        db.commit()
        
        # Send verification email
        try:
            EmailService.send_verification_email(
                to_email=new_user.email,
                user_name=new_user.nombre,
                verification_token=verification_token
            )
            print(f"✓ Verification email sent to {new_user.email}")
        except Exception as email_error:
            print(f"⚠️  Failed to send verification email: {email_error}")
            # Don't fail registration if email fails, user can resend later
        
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

# ============================================
# EMAIL VERIFICATION ENDPOINTS (PÚBLI COS)
# ============================================

@app.get("/verify-email/{token}", response_model=dict, tags=["Authentication"])
def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Verificar email usando token del enlace
    - Marca el email como verificado
    - Token de un solo uso (se borra después de usarse)
    """
    from datetime import datetime
    
    # Find user by verification token
    user = db.query(models.Usuario).filter(
        models.Usuario.verification_token == token
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token de verificación inválido"
        )
    
    # Check if already verified
    if user.email_verified:
        return {
            "success": True,
            "message": "Email ya estaba verificado",
            "email": user.email
        }
    
    # Check if token expired
    if user.verification_token_expiry < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de verificación expirado. Solicita uno nuevo."
        )
    
    # Verify email
    user.email_verified = True
    user.verification_token = None  # Invalidate token after use
    user.verification_token_expiry = None
    db.commit()
    
    return {
        "success": True,
        "message": "¡Email verificado correctamente!",
        "email": user.email
    }

@app.post("/resend-verification", response_model=dict, tags=["Authentication"])
def resend_verification(email_request: dict, db: Session = Depends(get_db)):
    """
    Reenviar email de verificación
    - Genera nuevo token
    - Envía nuevo email
    """
    import secrets
    from datetime import datetime, timedelta
    from email_service import EmailService
    
    email = email_request.get("email", "").lower().strip()
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email requerido"
        )
    
    user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    
    if not user:
        # Don't reveal if email exists or not (security)
        return {
            "success": True,
            "message": "Si el email existe, recibirás un correo de verificación"
        }
    
    if user.email_verified:
        return {
            "success": True,
            "message": "Email ya está verificado"
        }
    
    # Generate new token
    verification_token = secrets.token_urlsafe(32)
    user.verification_token = verification_token
    user.verification_token_expiry = datetime.now() + timedelta(hours=settings.VERIFICATION_TOKEN_EXPIRY_HOURS)
    db.commit()
    
    # Send email
    try:
        EmailService.send_verification_email(
            to_email=user.email,
            user_name=user.nombre,
            verification_token=verification_token
        )
    except Exception as e:
        print(f"Error sending verification email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al enviar email"
        )
    
    return {
        "success": True,
        "message": "Email de verificación enviado"
    }

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
                "propietario": f"{current_user.nombre} {current_user.apellidos}",
                "evento": {
                    "id": evento.id,
                    "nombre": evento.nombre,
                    "descripcion": evento.descripcion,
                    "fechayhora": evento.fechayhora.isoformat() if evento.fechayhora else None,
                    "recinto": evento.recinto,
                    "imagen": evento.imagen,
                    "precio": evento.precio,
                    "tipo": evento.tipo,
                    "genero": evento.genero if hasattr(evento, 'genero') else None
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
    # 0. LIMPIEZA / PARSEO DE ENTRADA (Safety Net)
    # Si el frontend envía un JSON string en vez del código limpio, lo parseamos aquí.
    try:
        if codigo_ticket.strip().startswith("{") and "codigo" in codigo_ticket:
            import json
            data = json.loads(codigo_ticket)
            if "codigo" in data:
                codigo_ticket = data["codigo"]
                print(f"DEBUG: JSON parseado en backend. Nuevo código: {codigo_ticket}")
    except:
        pass # Si falla, usamos el string original

    # 1. BUSCAR TICKET (Priority Search)
    # Buscar ticket por código (case insensitive)
    ticket = db.query(models.Ticket).filter(
        models.Ticket.codigo_ticket.ilike(codigo_ticket.strip())
    ).first()
    
    # FALLBACK: Si no se encuentra por código, verificar si es formato fallback "NJOY-TICKET-{ID}"
    if not ticket and "NJOY-TICKET-" in codigo_ticket.upper():
        try:
            potential_id = codigo_ticket.upper().split("NJOY-TICKET-")[1]
            ticket_id = int(potential_id)
            ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
        except:
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

    # 2. OBTENER EVENTO PARA PERMISOS
    evento = db.query(models.Evento).filter(models.Evento.id == ticket.evento_id).first()
    if not evento:
         return {
            "success": False,
            "status": "error",
            "message": "Evento asociado no encontrado",
            "color": "red",
            "codigo": codigo_ticket
        }

    # 3. VERIFICACIÓN DE PERMISOS STRICT (TEAMS)
    is_authorized = False
    
    # A. Admin Global
    if current_user.role == 'admin':
        is_authorized = True

    # B. Creador del Evento
    elif evento.creador_id == current_user.id:
        is_authorized = True
        
    # C. Miembro de Equipo
    else:
        membership = db.query(models.TeamMember).join(models.Team).filter(
            models.TeamMember.user_id == current_user.id,
            models.TeamMember.status == 'accepted',
            models.Team.leader_id == evento.creador_id
        ).first()
        
        if membership:
            is_authorized = True
            
    if not is_authorized:
        debug_msg = f"User[{current_user.id}] vs Creator[{evento.creador_id}]"
        return {
            "success": False,
            "status": "error",
            "message": f"⛔ NO AUTORIZADO: {debug_msg}. (No eres miembro del equipo)",
            "color": "red",
            "codigo": codigo_ticket,
            "evento": evento.nombre
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
    
    
    # Ticket válido - marcarlo como usado y guardar timestamp
    from datetime import datetime
    ticket.activado = False
    ticket.scanned_at = datetime.now()  # Track scan time for hourly stats
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

@app.delete("/evento/{item_id}", tags=["Events"])
def delete_evento(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """Eliminar un evento (requiere autenticación)"""
    evento = db.query(models.Evento).filter(models.Evento.id == item_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    try:
        # Delete associated tickets first to avoid foreign key constraint error
        tickets_to_delete = db.query(models.Ticket).filter(models.Ticket.evento_id == item_id).all()
        for ticket in tickets_to_delete:
            db.delete(ticket)
        
        # Now delete the event
        db.delete(evento)
        db.commit()
        return {"message": "Evento y tickets asociados eliminados correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar evento: {str(e)}"
        )

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
# GEOCODING UTILITY
# ============================================

import httpx

def geocode_city(city_name: str) -> tuple:
    """
    Get latitude and longitude for a city using OpenStreetMap Nominatim API.
    Returns (lat, lon) or (None, None) if not found.
    """
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": city_name,
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "nJoy-App/1.0 (contact@njoy.com)"
        }
        
        response = httpx.get(url, params=params, headers=headers, timeout=10.0)
        data = response.json()
        
        if data and len(data) > 0:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return (lat, lon)
    except Exception as e:
        print(f"Geocoding error for {city_name}: {e}")
    
    return (None, None)

# ============================================
# ENDPOINTS DE LOCALIDAD
# ============================================

@app.get("/localidad/", response_model=List[schemas.Localidad], tags=["Locations"])
def get_localidades(db: Session = Depends(get_db)):
    """Obtener todas las localidades (público)"""
    return db.query(models.Localidad).all()

@app.post("/localidad/", response_model=schemas.Localidad, status_code=status.HTTP_201_CREATED, tags=["Locations"])
def create_localidad(
    localidad: schemas.LocalidadCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_promotor)
):
    """
    Crear una nueva localidad con geocoding automático.
    Las coordenadas se obtienen automáticamente del nombre de la ciudad.
    """
    # Check if ciudad already exists
    existing = db.query(models.Localidad).filter(models.Localidad.ciudad == localidad.ciudad).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La localidad '{localidad.ciudad}' ya existe"
        )
    
    # Auto-geocode if coordinates not provided
    lat = localidad.latitud
    lon = localidad.longitud
    if lat is None or lon is None:
        lat, lon = geocode_city(localidad.ciudad)
    
    # Create localidad
    new_localidad = models.Localidad(
        ciudad=localidad.ciudad,
        latitud=lat,
        longitud=lon
    )
    db.add(new_localidad)
    db.commit()
    db.refresh(new_localidad)
    return new_localidad

@app.put("/localidad/{localidad_id}", response_model=schemas.Localidad, tags=["Locations"])
def update_localidad(
    localidad_id: int,
    localidad: schemas.LocalidadCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_promotor)
):
    """
    Actualizar una localidad. Re-geocodifica si el nombre cambia.
    """
    db_localidad = db.query(models.Localidad).filter(models.Localidad.id == localidad_id).first()
    if not db_localidad:
        raise HTTPException(status_code=404, detail="Localidad no encontrada")
    
    # If city name changed, re-geocode
    if db_localidad.ciudad != localidad.ciudad:
        lat, lon = geocode_city(localidad.ciudad)
        db_localidad.latitud = lat
        db_localidad.longitud = lon
    elif localidad.latitud is not None:
        db_localidad.latitud = localidad.latitud
    elif localidad.longitud is not None:
        db_localidad.longitud = localidad.longitud
        
    db_localidad.ciudad = localidad.ciudad
    db.commit()
    db.refresh(db_localidad)
    return db_localidad

@app.post("/localidad/geocode-all", tags=["Locations"])
def geocode_all_localidades(
    db: Session = Depends(get_db),
    current_admin: models.Usuario = Depends(get_current_admin)
):
    """
    Geocodificar todas las localidades que no tienen coordenadas (solo admin).
    Útil para actualizar localidades existentes.
    """
    localidades = db.query(models.Localidad).filter(
        (models.Localidad.latitud == None) | (models.Localidad.longitud == None)
    ).all()
    
    updated = 0
    for loc in localidades:
        lat, lon = geocode_city(loc.ciudad)
        if lat and lon:
            loc.latitud = lat
            loc.longitud = lon
            updated += 1
    
    db.commit()
    return {"message": f"Geocodificadas {updated} localidades de {len(localidades)} sin coordenadas"}


# ============================================
# ENDPOINTS DE EVENTO (PROTEGIDOS)
# ============================================

@app.get("/evento/tipos", tags=["Events"])
def get_event_types(db: Session = Depends(get_db)):
    """
    Obtener lista de tipos de eventos únicos existentes en la BD
    Endpoint público para filtros dinámicos
    """
    tipos = db.query(models.Evento.tipo).distinct().all()
    return [t[0] for t in tipos if t[0]]

@app.get("/evento/search", response_model=List[schemas.Evento], tags=["Events"])
def search_events(
    q: Optional[str] = None,           # Búsqueda por nombre
    tipo: Optional[str] = None,         # Filtro por tipo
    precio_min: Optional[float] = None, # Precio mínimo
    precio_max: Optional[float] = None, # Precio máximo
    localidad_id: Optional[int] = None, # Filtro por localidad
    fecha_desde: Optional[str] = None,  # Fecha desde (YYYY-MM-DD)
    fecha_hasta: Optional[str] = None,  # Fecha hasta (YYYY-MM-DD)
    user_lat: Optional[float] = None,   # Latitud del usuario
    user_lon: Optional[float] = None,   # Longitud del usuario
    order_by_distance: bool = False,    # Ordenar por distancia
    db: Session = Depends(get_db)
):
    """
    Búsqueda avanzada de eventos con múltiples filtros
    Endpoint público - soporta ordenación por distancia y filtro por fecha
    """
    import math
    from datetime import datetime
    
    def haversine(lat1, lon1, lat2, lon2):
        """Calcula la distancia en km entre dos puntos geográficos"""
        if None in (lat1, lon1, lat2, lon2):
            return float('inf')
        R = 6371  # Radio de la Tierra en km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    query = db.query(models.Evento)
    
    if q:
        query = query.filter(models.Evento.nombre.ilike(f"%{q}%"))
    if tipo:
        query = query.filter(models.Evento.tipo == tipo)
    if precio_min is not None:
        query = query.filter(models.Evento.precio >= precio_min)
    if precio_max is not None:
        query = query.filter(models.Evento.precio <= precio_max)
    if localidad_id:
        query = query.filter(models.Evento.localidad_id == localidad_id)
    
    # Date filters
    if fecha_desde:
        try:
            desde = datetime.strptime(fecha_desde, "%Y-%m-%d")
            query = query.filter(models.Evento.fechayhora >= desde)
        except ValueError:
            pass  # Ignore invalid date format
    
    if fecha_hasta:
        try:
            hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d")
            # Include the entire day
            hasta = hasta.replace(hour=23, minute=59, second=59)
            query = query.filter(models.Evento.fechayhora <= hasta)
        except ValueError:
            pass  # Ignore invalid date format
    
    eventos = query.all()
    
    # Calculate tickets sold and distance for each event
    eventos_with_data = []
    for event in eventos:
        count = db.query(models.Ticket).filter(models.Ticket.evento_id == event.id).count()
        setattr(event, "tickets_vendidos", count)
        
        # Calculate distance if user location provided
        distance = None
        if user_lat is not None and user_lon is not None:
            localidad = db.query(models.Localidad).filter(models.Localidad.id == event.localidad_id).first()
            if localidad and localidad.latitud and localidad.longitud:
                distance = haversine(user_lat, user_lon, localidad.latitud, localidad.longitud)
        setattr(event, "distancia_km", distance)
        eventos_with_data.append(event)
    
    # Sort by distance if requested
    if order_by_distance and user_lat is not None and user_lon is not None:
        eventos_with_data.sort(key=lambda e: e.distancia_km if e.distancia_km is not None else float('inf'))
    
    return eventos_with_data

@app.post("/evento/", response_model=schemas.Evento, status_code=status.HTTP_201_CREATED, tags=["Events"])
def create_evento(
    item: schemas.EventoBase,
    equipos_ids: List[int] = [],  # NUEVO: IDs de equipos autorizados para escanear
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_promotor)
):
    """Crear un nuevo evento (requiere rol de promotor o admin)"""
    try:
        # Set creador_id automatically from current user
        event_data = item.dict()
        event_data['creador_id'] = current_user.id
        
        # Create the event
        new_event = crud.create_item(db, models.Evento, schemas.EventoBase(**event_data))
        
        # Assign teams to event if provided
        if equipos_ids:
            for equipo_id in equipos_ids:
                # Verify team exists and belongs to current user
                team = db.query(models.Team).filter(
                    models.Team.id == equipo_id,
                    models.Team.leader_id == current_user.id
                ).first()
                
                if team:
                    # Insert into evento_equipos table (PostgreSQL compatible)
                    db.execute(
                        "INSERT INTO evento_equipos (evento_id, equipo_id) VALUES (:evento_id, :equipo_id) ON CONFLICT DO NOTHING",
                        {"evento_id": new_event.id, "equipo_id": equipo_id}
                    )
            db.commit()
        
        return new_event
        
    except Exception as e:
        db.rollback()
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

@app.get("/evento/{evento_id}/equipos", tags=["Events"])
def get_evento_equipos(
    evento_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_promotor)
):
    """Obtener equipos asignados a un evento"""
    # Verify event exists and user has permission
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    if current_user.role != 'admin' and evento.creador_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver los equipos de este evento")
    
    # Get teams assigned to this event
    result = db.execute(
        "SELECT equipo_id FROM evento_equipos WHERE evento_id = :evento_id",
        {"evento_id": evento_id}
    )
    team_ids = [row[0] for row in result.fetchall()]
    
    # Get full team details
    teams = db.query(models.Team).filter(models.Team.id.in_(team_ids)).all() if team_ids else []
    
    return {
        "evento_id": evento_id,
        "equipos": [{"id": t.id, "nombre_equipo": t.nombre_equipo} for t in teams]
    }

@app.put("/evento/{evento_id}/equipos", tags=["Events"])
def update_evento_equipos(
    evento_id: int,
    equipos_ids: List[int],
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_promotor)
):
    """Actualizar equipos asignados a un evento"""
    # Verify event exists and user has permission
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    if current_user.role != 'admin' and evento.creador_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar los equipos de este evento")
    
    try:
        # Delete existing assignments
        db.execute(
            "DELETE FROM evento_equipos WHERE evento_id = :evento_id",
            {"evento_id": evento_id}
        )
        
        # Add new assignments
        for equipo_id in equipos_ids:
            # Verify team exists and belongs to current user
            team = db.query(models.Team).filter(
                models.Team.id == equipo_id,
                models.Team.leader_id == current_user.id
            ).first()
            
            if team:
                db.execute(
                    "INSERT INTO evento_equipos (evento_id, equipo_id) VALUES (:evento_id, :equipo_id) ON CONFLICT DO NOTHING",
                    {"evento_id": evento_id, "equipo_id": equipo_id}
                )
        
        db.commit()
        
        return {"message": "Equipos actualizados correctamente", "evento_id": evento_id, "equipos_ids": equipos_ids}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar equipos: {str(e)}")

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

@app.post("/localidad/auto", response_model=schemas.Localidad, tags=["Locations"])
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
    try:
        # Buscar si ya existe una localidad con ese nombre (case-insensitive)
        existing = db.query(models.Localidad).filter(
            models.Localidad.ciudad.ilike(ciudad.strip())
        ).first()
        
        if existing:
            # Update coordinates if provided and missing
            if (latitud is not None and longitud is not None) and (existing.latitud is None or existing.longitud is None):
                existing.latitud = latitud
                existing.longitud = longitud
                db.commit()
                db.refresh(existing)
            return existing
        
        # Si no existe, crear una nueva con coordenadas
        new_localidad = models.Localidad(
            ciudad=ciudad.strip(),
            latitud=latitud,
            longitud=longitud
        )
        db.add(new_localidad)
        db.commit()
        db.refresh(new_localidad)
        return new_localidad
    except Exception as e:
        db.rollback()
        print(f"Error in /localidad/auto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating/getting location: {str(e)}"
        )

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
        
        if not ticket:
            return schemas.TicketScanResponse(
                success=False,
                message="Ticket no encontrado"
            )
        
        # Get event details
        event = db.query(models.Evento).filter(models.Evento.id == ticket.evento_id).first()
        event_name = event.nombre if event else "Evento desconocido"
        
        # PERMISSION CHECK STRICT (TEAMS BASED ON EVENTO_EQUIPOS)
        # ---------------------------------------------------------------------
        is_authorized = False
        if current_scanner.role == 'admin':
            is_authorized = True
        elif event and event.creador_id == current_scanner.id:
            is_authorized = True
        elif event:
            # Check if user belongs to a team assigned to this event
            result = db.execute(
                """
                SELECT 1 FROM evento_equipos ee
                JOIN miembros_equipo me ON ee.equipo_id = me.equipo_id
                WHERE ee.evento_id = :evento_id 
                AND me.usuario_id = :usuario_id
                AND me.estado = 'accepted'
                LIMIT 1
                """,
                {"evento_id": event.id, "usuario_id": current_scanner.id}
            )
            if result.fetchone():
                is_authorized = True
        
        if not is_authorized:
             return schemas.TicketScanResponse(
                success=False,
                message="⛔ No tienes permiso para escanear este evento (No estás en un equipo asignado)",
                event_name=event_name
            )
        # ---------------------------------------------------------------------
        
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
        
        if not ticket:
            return schemas.TicketScanResponse(
                success=False,
                message="Ticket no encontrado"
            )

        # Get event details
        event = db.query(models.Evento).filter(models.Evento.id == ticket.evento_id).first()
        event_name = event.nombre if event else "Evento desconocido"

        # PERMISSION CHECK STRICT (TEAMS)
        is_authorized = False
        if current_scanner.role == 'admin':
            is_authorized = True
        elif event and event.creador_id == current_scanner.id:
            is_authorized = True
        elif event:
             membership = db.query(models.TeamMember).join(models.Team).filter(
                models.TeamMember.user_id == current_scanner.id,
                models.TeamMember.status == 'accepted',
                models.Team.leader_id == event.creador_id
            ).first()
             if membership:
                 is_authorized = True
        
        if not is_authorized:
             return schemas.TicketScanResponse(
                success=False,
                message="⛔ No tienes permiso para escanear este evento"
            )
        
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

@app.get("/", tags=["Root"])
def read_root():
    """health check"""
    return {
        "message": "Welcome to nJoy API",
        "status": "online",
        "docs": "/docs"
    }

@app.get("/debug/recent-tickets", tags=["Debug"])
def get_recent_tickets_debug(db: Session = Depends(get_db)):
    """
    TEMPORARY DEBUG ENDPOINT - Shows last 10 tickets in database
    Used to verify QR code data in production
    """
    try:
        tickets = db.query(models.Ticket).order_by(models.Ticket.id.desc()).limit(10).all()
        results = []
        for t in tickets:
            results.append({
                "id": t.id,
                "codigo_ticket": t.codigo_ticket,
                "evento_id": t.evento_id,
                "activado": t.activado,
                "nombre_asistente": t.nombre_asistente
            })
        return {"count": len(results), "tickets": results}
    except Exception as e:
        return {"error": str(e)}

@app.post("/admin/migrate-ticket-codes", tags=["Admin"])
def migrate_ticket_codes(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    ADMIN ONLY: Migrate tickets with NULL or UUID codigo_ticket to 6-char codes
    """
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Find tickets with NULL or UUID-format codes
        tickets_to_migrate = db.query(models.Ticket).filter(
            (models.Ticket.codigo_ticket == None) | 
            (models.Ticket.codigo_ticket.like('%-%'))  # UUID format contains dashes
        ).all()
        
        migrated_count = 0
        skipped_count = 0
        
        for ticket in tickets_to_migrate:
            # Generate unique 6-char code
            while True:
                new_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                # Check if code is unique
                existing = db.query(models.Ticket).filter(
                    models.Ticket.codigo_ticket == new_code
                ).first()
                if not existing:
                    ticket.codigo_ticket = new_code
                    migrated_count += 1
                    break
        
        db.commit()
        
        return {
            "success": True,
            "migrated": migrated_count,
            "total_found": len(tickets_to_migrate),
            "message": f"Successfully migrated {migrated_count} tickets to 6-character codes"
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}

# ============================================
# EVENT STATISTICS ENDPOINTS
# ============================================

import estadisticas_schemas
from datetime import datetime

@app.post("/evento/{evento_id}/verificar-acceso-estadisticas", tags=["Events"])
def verify_stats_access(
    evento_id: int,
    verification: estadisticas_schemas.PasswordVerificationRequest,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Verify user password and ownership to grant temporary access to event statistics
    
    Security:
    - User must be the creator of the event (strict ownership)
    - Password must be correct
    - Returns temporary JWT token valid for 5 minutes
    """
    # 1. Verify event exists
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    # 2. Verify ownership (STRICT - Only creator can see stats)
    if evento.creador_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para ver las estadísticas de este evento"
        )
    
    # 3. Verify password
    user = authenticate_user(db, current_user.email, verification.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Contraseña incorrecta"
        )
    
    # 4. Generate temporary stats token (5 minutes expiration)
    stats_token = create_access_token(
        data={"sub": str(user.id), "evento_id": evento_id, "type": "stats"},
        expires_delta=timedelta(minutes=5)
    )
    
    return estadisticas_schemas.StatsAccessTokenResponse(
        access_token=stats_token,
        expires_in=300,  # 5 minutes in seconds
        token_type="bearer"
    )


@app.get("/evento/{evento_id}/estadisticas", tags=["Events"])
def get_event_statistics(
    evento_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Get comprehensive event statistics with hourly breakdown
    
    Returns:
    - Financial metrics (total revenue, average ticket price)
    - Capacity metrics (sold, available)
    - Attendance metrics (scanned tickets, attendance rate)
    - Hourly entry breakdown for analysis
    
    Security:
    - Only event creator can access (strict ownership)
    - No admin override (privacy guaranteed)
    """
    # 1. Verify event exists
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    # 2. STRICT ownership check - Only creator
    if evento.creador_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Solo el creador del evento puede ver estas estadísticas"
        )
    
    # 3. Calculate statistics
    # Total tickets sold
    total_tickets = db.query(models.Ticket).filter(
        models.Ticket.evento_id == evento_id
    ).count()
    
    # Scanned tickets (attended)
    scanned_tickets = db.query(models.Ticket).filter(
        models.Ticket.evento_id == evento_id,
        models.Ticket.activado == False  # False means it was scanned
    ).count()
    
    # Financial calculations
    precio = evento.precio if evento.precio else 0
    ingreso_total = total_tickets * precio
    ingreso_promedio = precio if total_tickets > 0 else 0
    
    # Capacity calculations
    capacidad_total = evento.plazas
    tickets_disponibles = capacidad_total - total_tickets
    
    # Attendance rate
    tasa_asistencia = (scanned_tickets / total_tickets * 100) if total_tickets > 0 else 0
    
    # 4. Get all scanned tickets with timestamps (needed for time range and hourly breakdown)
    tickets_escaneados_list = db.query(models.Ticket).filter(
        models.Ticket.evento_id == evento_id,
        models.Ticket.scanned_at != None
    ).all()
    
    # 5. Calculate time range for charts (from first scan to current hour + 1)
    from datetime import datetime
    now = datetime.now()
    current_hour = now.hour
    event_hour = evento.fechayhora.hour
    
    # Find the range: from first scan (or event start) to current hour + 1
    if tickets_escaneados_list:
        first_scan_hour = min(t.scanned_at.hour for t in tickets_escaneados_list)
        last_scan_hour = max(t.scanned_at.hour for t in tickets_escaneados_list)
        
        # Start from the earlier of: event hour or first scan
        start_hour = min(event_hour, first_scan_hour)
        
        # End at the later of: current hour + 1 or last scan
        end_hour = max(current_hour + 1, last_scan_hour)
        end_hour = min(23, end_hour)  # Don't exceed 23:00
    else:
        # No scans yet, show event hour ± 2
        start_hour = max(0, event_hour - 2)
        end_hour = min(23, current_hour + 1)
    
    # 6. Hourly breakdown - Group by hour
    hourly_stats_dict = {}
    max_hour_count = 0
    peak_hour = None
    
    for ticket in tickets_escaneados_list:
        hour = ticket.scanned_at.hour
        if hour not in hourly_stats_dict:
            hourly_stats_dict[hour] = 0
        hourly_stats_dict[hour] += 1
        
        if hourly_stats_dict[hour] > max_hour_count:
            max_hour_count = hourly_stats_dict[hour]
            peak_hour = f"{hour:02d}:00"
    
    # Build hourly entries (only hours with data for bar chart)
    entradas_por_hora = []
    for hour in range(start_hour, end_hour + 1):
        count = hourly_stats_dict.get(hour, 0)
        if count > 0:
            entradas_por_hora.append(
                estadisticas_schemas.HourlyEntryStats(
                    hour=hour,
                    count=count,
                    hour_label=f"{hour:02d}:00"
                )
            )
    
    # 7. Temporal Flow (cumulative entries over time)
    # Build cumulative flow data using the same time range
    flujo_temporal = []
    cumulative = 0
    
    for hour in range(start_hour, end_hour + 1):
        count = hourly_stats_dict.get(hour, 0)
        cumulative += count
        
        flujo_temporal.append(
            estadisticas_schemas.TemporalFlowPoint(
                hour=hour,
                count=count,
                cumulative=cumulative,
                hour_label=f"{hour:02d}:00"
            )
        )
    
    # 8. Build response
    response = estadisticas_schemas.EventStatsResponse(
        ingreso_total=ingreso_total,
        ingreso_promedio_ticket=ingreso_promedio,
        capacidad_total=capacidad_total,
        tickets_vendidos=total_tickets,
        tickets_disponibles=tickets_disponibles,
        tickets_escaneados=scanned_tickets,
        tasa_asistencia=tasa_asistencia,
        entradas_por_hora=entradas_por_hora,
        hora_pico=peak_hour,
        max_entradas_hora=max_hour_count,
        flujo_temporal=flujo_temporal,
        hora_evento=event_hour
    )
    
    return response



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


