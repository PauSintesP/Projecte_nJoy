# 🎉 nJoy API - Sistema de Gestión de Eventos

API REST segura para gestión de eventos musicales con autenticación JWT.

## 🔐 Características de Seguridad

- ✅ Autenticación JWT con tokens de acceso y refresh
- ✅ Contraseñas hasheadas con bcrypt
- ✅ Protección de endpoints sensibles
- ✅ CORS configurado para dominios específicos
- ✅ Validación de datos con Pydantic
- ✅ Control de acceso basado en usuario
- ✅ Variables de entorno para secretos

## 🚀 Instalación Local

### Prerrequisitos

- Python 3.8 o superior
- MySQL 5.7+ o compatible
- pip

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone <url-del-repositorio>
cd Projecte_nJoy
```

2. **Crear entorno virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
# Copiar el archivo de ejemplo
copy .env.example .env

# Editar .env con tus valores
notepad .env
```

**Importante**: Cambia `SECRET_KEY` a un valor aleatorio y seguro:
```bash
# Generar una clave secura (requiere OpenSSL)
openssl rand -hex 32
```

5. **Configurar la base de datos**

Asegúrate de que tu base de datos MySQL esté corriendo y actualiza la variable `DATABASE_URL` en `.env`:

```
DATABASE_URL=mysql+pymysql://usuario:contraseña@localhost/nombre_base_datos
```

6. **Iniciar el servidor**
```bash
uvicorn main:app --reload
```

La API estará disponible en `http://localhost:8000`

## 📚 Documentación de la API

Una vez que el servidor esté corriendo, puedes acceder a la documentación interactiva:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔑 Autenticación

### 1. Registrar un usuario

```bash
POST /register
Content-Type: application/json

{
  "user": "usuario123",
  "ncompleto": "Juan Pérez",
  "email": "juan@ejemplo.com",
  "fnacimiento": "2000-01-15",
  "contrasena": "MiPasswordSeguro123"
}
```

### 2. Hacer login

```bash
POST /login
Content-Type: application/json

{
  "email": "juan@ejemplo.com",
  "contrasena": "MiPasswordSeguro123"
}
```

**Respuesta**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Usar el token en requests

Incluye el token en el header `Authorization` de todas las requests a endpoints protegidos:

```bash
GET /evento/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 4. Renovar el token

Cuando el access token expire (después de 30 días por defecto), usa el refresh token:

```bash
POST /token/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## 🌐 Endpoints Principales

### Públicos (sin autenticación)

- `POST /register` - Registrar nuevo usuario
- `POST /login` - Iniciar sesión
- `GET /health` - Estado de la API
- `GET /` - Información de la API

### Protegidos (requieren autenticación)

#### Usuarios
- `GET /me` - Obtener usuario actual
- `GET /usuario/` - Listar usuarios
- `GET /usuario/{id}` - Obtener usuario
- `PUT /usuario/{id}` - Actualizar usuario (solo el propio)
- `DELETE /usuario/{id}` - Eliminar usuario (solo el propio)

#### Eventos
- `GET /evento/` - Listar eventos
- `POST /evento/` - Crear evento
- `GET /evento/{id}` - Obtener evento
- `PUT /evento/{id}` - Actualizar evento
- `DELETE /evento/{id}` - Eliminar evento

#### Tickets
- `GET /ticket/` - Listar mis tickets
- `POST /ticket/` - Comprar ticket
- `GET /ticket/{id}` - Ver mi ticket
- `PUT /ticket/{id}` - Actualizar mi ticket
- `DELETE /ticket/{id}` - Cancelar mi ticket

#### Otros recursos
- Localidades: `/localidad/`
- Organizadores: `/organizador/`
- Géneros: `/genero/`
- Artistas: `/artista/`
- Pagos: `/pago/`

## 🚀 Despliegue en Vercel

### 1. Preparar el proyecto

Asegúrate de que el archivo `vercel.json` esté en la raíz del proyecto.

### 2. Instalar Vercel CLI

```bash
npm install -g vercel
```

### 3. Hacer login en Vercel

```bash
vercel login
```

### 4. Configurar variables de entorno

En el dashboard de Vercel o mediante CLI:

```bash
vercel env add SECRET_KEY
# Pegar tu clave secreta

vercel env add DATABASE_URL
# Pegar la URL de tu base de datos en producción

vercel env add ALLOWED_ORIGINS
# Ejemplo: https://miapp.com,https://www.miapp.com
```

### 5. Desplegar

```bash
# Primer despliegue
vercel

# Despliegue a producción
vercel --prod
```

### Base de Datos en Producción

Vercel no incluye base de datos MySQL. Opciones recomendadas:

**Opción 1: Railway** (Gratuito hasta cierto uso)
1. Crear cuenta en https://railway.app
2. Crear nuevo proyecto MySQL
3. Copiar la URL de conexión
4. Añadir a Vercel como variable `DATABASE_URL`

**Opción 2: PlanetScale** (Gratuito hasta cierto uso)
1. Crear cuenta en https://planetscale.com
2. Crear nueva base de datos
3. Obtener credenciales de conexión
4. Añadir a Vercel como variable `DATABASE_URL`

**Opción 3: PostgreSQL en Vercel**
1. Ir a tu proyecto en Vercel
2. Storage → Create Database → Postgres
3. La variable `DATABASE_URL` se configura automáticamente
4. **Nota**: Tendrás que cambiar el driver de `mysql+pymysql` a `postgresql+psycopg2` y actualizar `requirements.txt`

## 🧪 Testing

### Prueba con curl

```bash
# 1. Registrar usuario
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"user":"test","ncompleto":"Test User","email":"test@test.com","fnacimiento":"2000-01-01","contrasena":"test123"}'

# 2. Login
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","contrasena":"test123"}'

# 3. Usar el token (reemplaza TOKEN con el access_token recibido)
curl -X GET http://localhost:8000/me \
  -H "Authorization: Bearer TOKEN"
```

### Prueba con Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Registrar
response = requests.post(f"{BASE_URL}/register", json={
    "user": "test",
    "ncompleto": "Test User",
    "email": "test@test.com",
    "fnacimiento": "2000-01-01",
    "contrasena": "test123"
})
print(response.json())

# Login
response = requests.post(f"{BASE_URL}/login", json={
    "email": "test@test.com",
    "contrasena": "test123"
})
tokens = response.json()
access_token = tokens["access_token"]

# Usar el token
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(f"{BASE_URL}/me", headers=headers)
print(response.json())
```

## 📝 Estructura del Proyecto

```
Projecte_nJoy/
├── main.py              # Aplicación principal FastAPI
├── auth.py              # Sistema de autenticación JWT
├── config.py            # Configuración y variables de entorno
├── database.py          # Configuración de base de datos
├── models.py            # Modelos SQLAlchemy
├── schemas.py           # Schemas Pydantic
├── crud.py              # Operaciones CRUD
├── requirements.txt     # Dependencias Python
├── vercel.json          # Configuración Vercel
├── .env.example         # Plantilla de variables de entorno
├── .env                 # Variables de entorno (NO commitear)
└── .gitignore           # Archivos ignorados por git
```

## 🛡️ Mejores Prácticas de Seguridad

1. **Nunca compartas tu SECRET_KEY**
2. **Cambia la SECRET_KEY en producción** (diferente a desarrollo)
3. **Usa HTTPS en producción** (Vercel lo hace automáticamente)
4. **Configura CORS solo para tus dominios** (no usar `*`)
5. **Cambia contraseñas de base de datos por defecto**
6. **Mantén las dependencias actualizadas**
7. **No commitees el archivo `.env`** al repositorio

## 🐛 Troubleshooting

### Error: "Token inválido o expirado"
- Verifica que el token se está enviando correctamente en el header
- Asegúrate de usar `Bearer ` antes del token
- El token puede haber expirado, usa el refresh token

### Error: "El email ya está registrado"
- El email debe ser único en el sistema
- Usa un email diferente o haz login con el existente

### Error de conexión a la base de datos
- Verifica que MySQL esté corriendo
- Comprueba las credenciales en `DATABASE_URL`
- Asegúrate de que la base de datos existe

### Error al importar módulos
- Activa el entorno virtual: `venv\Scripts\activate`
- Reinstala dependencias: `pip install -r requirements.txt`

## 📞 Soporte

Para preguntas o problemas, abre un issue en el repositorio.

## 📄 Licencia

Este proyecto es privado y confidencial.
