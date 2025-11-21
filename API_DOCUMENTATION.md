# API Documentation for **nJoy API**

> This document provides a public overview of every endpoint exposed by the FastAPI application, including HTTP method, URL, purpose, request body (if any), and example response payloads. All schemas are defined in `schemas.py` and the database models in `models.py`.

---

## Table of Contents
1. [Health & Root](#health--root)
2. [Authentication](#authentication)
3. [User Endpoints](#user-endpoints)
4. [Localidad (Location)](#localidad-location)
5. [Organizador (Organizer)](#organizador-organizer)
6. [Genero (Genre)](#genero-genre)
7. [Artista (Artist)](#artista-artist)
8. [Evento (Event)](#evento-event)
9. [Ticket](#ticket)
10. [Pago (Payment)](#pago-payment)

---

## Health & Root
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Returns a simple JSON confirming the service is up. |
| `GET` | `/` | Returns basic API metadata (name, version, docs URLs). |

**Responses**
```json
// /health
{ "status": "healthy", "app": "nJoy API", "version": "2.0.0" }

// /
{ "app": "nJoy API", "version": "2.0.0", "docs": "/docs", "redoc": "/redoc" }
```

---

## Authentication
### Register
- **Method**: `POST`
- **Path**: `/register`
- **Request Body**: `UsuarioCreate` (see schemas)
- **Response**: `Usuario` (user data without password)

```json
{
  "user": "jdoe",
  "ncompleto": "John Doe",
  "email": "john@example.com",
  "fnacimiento": "1990-05-12",
  "id": 1,
  "is_active": true,
  "created_at": "2025-11-21T14:00:00"
}
```

### Login
- **Method**: `POST`
- **Path**: `/login`
- **Request Body**: `LoginInput`
- **Response**: `Token`

```json
{ "access_token": "<jwt>", "refresh_token": "<jwt>", "token_type": "bearer" }
```

### Refresh Token
- **Method**: `POST`
- **Path**: `/token/refresh`
- **Request Body**: `RefreshTokenRequest`
- **Response**: `Token`

---

## User Endpoints
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/me` | Returns the authenticated user's data (`Usuario`). |
| `GET` | `/usuario/` | List all users (admin‑only). |
| `GET` | `/usuario/{item_id}` | Get user by ID. |
| `PUT` | `/usuario/{item_id}` | Update own user (`UsuarioUpdate`). |
| `DELETE` | `/usuario/{item_id}` | Delete own user. |

All responses use the `Usuario` schema.

---

## Localidad (Location)
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/localidad/` | Create a new location (`LocalidadCreate`). |
| `GET` | `/localidad/` | List all locations. |
| `GET` | `/localidad/{item_id}` | Retrieve a location by ID. |
| `PUT` | `/localidad/{item_id}` | Update a location. |
| `DELETE` | `/localidad/{item_id}` | Delete a location. |

**Schemas**
- `LocalidadBase`: `{ "ciudad": "Madrid" }`
- `Localidad`: adds `id`.

---

## Organizador (Organizer)
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/organizador/` | Create organizer (`Organizador`). |
| `GET` | `/organizador/` | List organizers. |
| `GET` | `/organizador/{item_id}` | Get organizer by DNI. |
| `PUT` | `/organizador/{item_id}` | Update organizer. |
| `DELETE` | `/organizador/{item_id}` | Delete organizer. |

**Schema** `OrganizadorBase` includes `dni`, `ncompleto`, `email`, `telefono`, optional `web`.

---

## Genero (Genre)
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/genero/` | Create genre (`GeneroBase`). |
| `GET` | `/genero/` | List genres. |
| `GET` | `/genero/{item_id}` | Get genre by ID. |
| `PUT` | `/genero/{item_id}` | Update genre. |
| `DELETE` | `/genero/{item_id}` | Delete genre. |

---

## Artista (Artist)
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/artista/` | Create artist (`ArtistaBase`). |
| `GET` | `/artista/` | List artists. |
| `GET` | `/artista/{item_id}` | Get artist by ID. |
| `PUT` | `/artista/{item_id}` | Update artist. |
| `DELETE` | `/artista/{item_id}` | Delete artist. |

---

## Evento (Event)
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/evento/` | Create event (`EventoBase`). |
| `GET` | `/evento/` | List events. |
| `GET` | `/evento/{item_id}` | Get event by ID. |
| `PUT` | `/evento/{item_id}` | Update event. |
| `DELETE` | `/evento/{item_id}` | Delete event. |

**EventoBase** fields include `nombre`, `descripcion`, `localidad_id`, `recinto`, `plazas`, `fechayhora`, `tipo`, `categoria_precio`, `organizador_dni`, `genero_id`, optional `imagen`.

---

## Ticket
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/ticket/` | Create ticket (`TicketBase`). Only the owner can create. |
| `GET` | `/ticket/` | List tickets belonging to the authenticated user. |
| `GET` | `/ticket/{item_id}` | Retrieve a ticket (owner only). |
| `PUT` | `/ticket/{item_id}` | Update a ticket (owner only). |
| `DELETE` | `/ticket/{item_id}` | Delete a ticket (owner only). |

**TicketBase**: `{ "evento_id": 5, "usuario_id": 1, "activado": true }`

---

## Pago (Payment)
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/pago/` | Create a payment (`PagoBase`). Owner only. |
| `GET` | `/pago/` | List payments of the authenticated user. |
| `GET` | `/pago/{item_id}` | Retrieve a payment (owner only). |
| `PUT` | `/pago/{item_id}` | Update a payment (owner only). |
| `DELETE` | `/pago/{item_id}` | Delete a payment (owner only). |

**PagoBase** fields: `usuario_id`, `metodo_pago`, `total`, `fecha`, `ticket_id`.

---

## Authentication & Authorization
All protected routes require a valid **Bearer** token in the `Authorization` header:
```
Authorization: Bearer <access_token>
```
The token is generated by `/login` and contains the user ID and email. Refresh tokens are used via `/token/refresh`.

---

### How to Test
You can explore the full OpenAPI specification at `/docs` (Swagger UI) or `/redoc`. Each endpoint shows request/response models automatically generated from the Pydantic schemas.

---

*Generated on 2025‑11‑21 by Antigravity – your AI coding assistant.*
