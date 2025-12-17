# 🔒 Guía de Seguridad - nJoy API

Esta guía describe las medidas de seguridad implementadas en la API y las mejores prácticas para mantenerla segura.

## 🛡️ Características de Seguridad Implementadas

### 1. Autenticación JWT

La API usa JSON Web Tokens (JWT) para autenticar usuarios:

- **Access Tokens**: Tokens de corta duración (30 días por defecto) para acceder a recursos
- **Refresh Tokens**: Tokens de larga duración (7 días) para renovar access tokens
- **Firmados con HS256**: Algoritmo criptográfico seguro
- **Información mínima**: Solo ID y email del usuario en el payload

### 2. Hash de Contraseñas

Las contraseñas NUNCA se almacenan en texto plano:

- **Bcrypt**: Algoritmo de hashing robusto y probado
- **Salt automático**: Cada contraseña tiene un salt único
- **Cost factor**: Configurable para ajustar la seguridad vs rendimiento
- **Unidireccional**: Imposible obtener la contraseña original del hash

### 3. Validación de Datos

Todas las entradas son validadas con Pydantic:

- **Validación de tipos**: Email, fechas, strings, números
- **Validación de rangos**: Longitudes mínimas/máximas
- **Validación de formato**: EmailStr para emails válidos
- **Validación personalizada**: Edad mínima, etc.

### 4. Protección de Endpoints

- **Endpoints públicos**: Solo `/register`, `/login`, `/health`, `/`
- **Endpoints protegidos**: Requieren token JWT válido
- **Control de acceso**: Los usuarios solo pueden modificar sus propios datos
- **Validación de permisos**: Verificación de propiedad en tickets y pagos

### 5. CORS Configurado con Validación Estricta

Control **muy estricto** de orígenes permitidos con doble capa de seguridad:

**Capa 1: CORSMiddleware de FastAPI**
- **Lista blanca explícita**: Solo dominios en `ALLOWED_ORIGINS` pueden acceder
- **Sin regex permisivo**: Eliminado `allow_origin_regex` para evitar subdominios no autorizados
- **Credenciales permitidas**: Solo para dominios autorizados

**Capa 2: Middleware de Validación Personalizado**
- **Validación activa**: Verifica el header `Origin` en cada request
- **Rechazo automático**: Retorna `403 Forbidden` para orígenes no autorizados
- **Logging de seguridad**: Registra intentos de acceso no autorizados
- **Compatible con apps móviles**: Permite requests sin header `Origin` (apps nativas)

**Configuración Actual:**
```python
# En main.py - Validación estricta
@app.middleware("http")
async def validate_origin_middleware(request, call_next):
    origin = request.headers.get("origin")
    
    if origin and origin not in settings.ALLOWED_ORIGINS:
        # BLOCKED - Log y retornar 403
        return JSONResponse(status_code=403, content={
            "detail": "Origin not allowed"
        })
    # ...
```

**Agregar nuevos dominios autorizados:**
```bash
# En archivo .env o variables de entorno de Vercel
ALLOWED_ORIGINS=https://web-njoy.vercel.app,https://otro-dominio.com,http://localhost:5173
```

**IMPORTANTE**: Apps móviles (Android/iOS) NO están afectadas por CORS porque hacen peticiones HTTP nativas (no desde navegador).

### 6. Variables de Entorno

Secretos y configuraciones sensibles externalizadas:

- **SECRET_KEY**: Clave para firmar JWT
- **DATABASE_URL**: Credenciales de base de datos
- **ALLOWED_ORIGINS**: Dominios permitidos
- **No hardcodeadas**: Nunca en el código fuente

## 🚨 Vectores de Ataque Mitigados

### 1. Inyección SQL
- **✅ Protegido**: SQLAlchemy ORM previene inyección SQL
- **Cómo**: Usa queries parametrizadas automáticamente

### 2. Cross-Site Scripting (XSS)
- **✅ Protegido**: Validación de inputs con Pydantic
- **✅ Protegido**: FastAPI escapa automáticamente las salidas JSON

### 3. Fuerza Bruta
- **⚠️ Parcialmente protegido**: Bcrypt hace lento verificar contraseñas
- **Mejora recomendada**: Implementar rate limiting (ver abajo)

### 4. Session Hijacking
- **✅ Protegido**: Tokens JWT firmados criptográficamente
- **✅ Protegido**: Verificación de firma en cada request

### 5. Man-in-the-Middle (MITM)
- **✅ Protegido en producción**: Vercel usa HTTPS automáticamente
- **⚠️ Vulnerable en local**: Usar HTTPS también en desarrollo si es posible

### 6. CSRF (Cross-Site Request Forgery)
- **✅ Protegido**: JWT en header (no en cookies)
- **Cómo**: Los tokens deben ser enviados explícitamente

## 🔐 Mejores Prácticas para Desarrolladores

### 1. Gestión de Tokens

**DO ✅**
```javascript
// Guardar en memoria o sessionStorage
sessionStorage.setItem('access_token', token);

// Enviar en header
fetch('/api/evento/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

**DON'T ❌**
```javascript
// NO guardar en localStorage (vulnerable a XSS)
localStorage.setItem('access_token', token);

// NO enviar en URL
fetch(`/api/evento/?token=${token}`);
```

### 2. Renovación de Tokens

```javascript
async function refreshAccessToken(refreshToken) {
  const response = await fetch('/token/refresh', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({refresh_token: refreshToken})
  });
  
  if (response.ok) {
    const tokens = await response.json();
    sessionStorage.setItem('access_token', tokens.access_token);
    sessionStorage.setItem('refresh_token', tokens.refresh_token);
    return tokens.access_token;
  }
  
  // Token refresh falló, redirigir a login
  window.location.href = '/login';
}
```

### 3. Manejo de Errores de Autenticación

```javascript
async function apiRequest(url, options = {}) {
  const token = sessionStorage.getItem('access_token');
  
  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (response.status === 401) {
    // Token expirado, intentar renovar
    const refreshToken = sessionStorage.getItem('refresh_token');
    const newToken = await refreshAccessToken(refreshToken);
    
    // Reintentar request con nuevo token
    return fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${newToken}`
      }
    });
  }
  
  return response;
}
```

## 🔧 Configuración de Seguridad Recomendada

### Variables de Entorno en Producción

```bash
# Generar SECRET_KEY segura (Linux/Mac)
openssl rand -hex 32

# Generar SECRET_KEY segura (Python)
python -c "import secrets; print(secrets.token_hex(32))"
```

Configurar en Vercel:
```bash
vercel env add SECRET_KEY production
# Pegar la clave generada

vercel env add ALLOWED_ORIGINS production
# Solo dominios de producción: https://miapp.com,https://www.miapp.com
```

### Configuración CORS Segura

**Desarrollo**
```
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Producción**
```
ALLOWED_ORIGINS=https://web-njoy.vercel.app
```

**Con múltiples dominios (si es necesario)**
```
ALLOWED_ORIGINS=https://web-njoy.vercel.app,https://admin.web-njoy.vercel.app
```

**❌ NUNCA en producción**
```
ALLOWED_ORIGINS=*
allow_origin_regex=https://.*\.vercel\.app  # Permite TODOS los subdominios
```

## 🚀 Mejoras de Seguridad Recomendadas

### 1. Rate Limiting

Limitar requests por IP para prevenir fuerza bruta:

```python
# Instalar: pip install slowapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/login")
@limiter.limit("5/minute")  # Máximo 5 intentos por minuto
def login(...):
    ...
```

### 2. HTTPS en Desarrollo

Usar certificado autofirmado para desarrollo:

```bash
# Generar certificado
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Ejecutar con HTTPS
uvicorn main:app --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

### 3. Headers de Seguridad

Añadir headers de seguridad adicionales:

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

# Solo permitir hosts conocidos
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["miapp.com", "*.miapp.com"]
)

# Redirigir HTTP a HTTPS
if not settings.DEBUG:
    app.add_middleware(HTTPSRedirectMiddleware)
```

### 4. Logging de Seguridad

Registrar eventos de seguridad:

```python
import logging

security_logger = logging.getLogger("security")

@app.post("/login")
def login(credentials: schemas.LoginInput, request: Request):
    user = authenticate_user(...)
    
    if not user:
        security_logger.warning(
            f"Failed login attempt for {credentials.email} from {request.client.host}"
        )
        raise HTTPException(...)
    
    security_logger.info(
        f"Successful login for {credentials.email} from {request.client.host}"
    )
    ...
```

### 5. Expiración de Tokens Más Corta

Para aplicaciones muy sensibles:

```
# En producción
ACCESS_TOKEN_EXPIRE_MINUTES=15  # 15 minutos en lugar de 30 días
REFRESH_TOKEN_EXPIRE_DAYS=1     # 1 día en lugar de 7
```

### 6. Roles y Permisos

Implementar RBAC (Role-Based Access Control):

```python
# En models.py
class Usuario(Base):
    ...
    role = Column(String(20), default="user")  # user, admin, organizer

# En auth.py
def require_role(required_role: str):
    def role_checker(current_user: models.Usuario = Depends(get_current_active_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permisos insuficientes"
            )
        return current_user
    return role_checker

# En main.py
@app.delete("/evento/{item_id}")
def delete_evento(
    item_id: int,
    current_user: models.Usuario = Depends(require_role("admin"))
):
    ...
```

## 📋 Checklist de Seguridad

Antes de desplegar a producción:

- [ ] SECRET_KEY única y aleatoria (mínimo 32 caracteres)
- [ ] SECRET_KEY diferente entre dev y prod
- [ ] ALLOWED_ORIGINS configurado solo con dominios específicos
- [ ] DATABASE_URL con contraseñas fuertes
- [ ] Archivo `.env` NO está en el repositorio
- [ ] `.gitignore` incluye `.env`
- [ ] HTTPS habilitado (automático en Vercel)
- [ ] Contraseñas de base de datos cambiadas del default
- [ ] Tokens con tiempo de expiración razonable
- [ ] Logs de seguridad configurados
- [ ] Dependencies actualizadas: `pip list --outdated`

## 🐛 Reportar Vulnerabilidades

Si encuentras una vulnerabilidad de seguridad, **NO** abras un issue público.

Contacta directamente al equipo de desarrollo.

## 📚 Referencias

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/14/faq/security.html)
