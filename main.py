from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from routers import (
    artista, 
    evento, 
    genero, 
    localidad, 
    organizador, 
    pago, 
    ticket, 
    usuario
)


import models
from database import engine

# Create all database tables
models.Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Joy Events Management System",
    description="Backend API for event management and ticketing",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(artista.router, prefix="/artistas", tags=["Artistas"])
app.include_router(evento.router, prefix="/eventos", tags=["Eventos"])
app.include_router(genero.router, prefix="/generos", tags=["Generos"])
app.include_router(localidad.router, prefix="/localidades", tags=["Localidades"])
app.include_router(organizador.router, prefix="/organizadores", tags=["Organizadores"])
app.include_router(pago.router, prefix="/pagos", tags=["Pagos"])
app.include_router(ticket.router, prefix="/tickets", tags=["Tickets"])
app.include_router(usuario.router, prefix="/usuarios", tags=["Usuarios"])

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Joy Events Management System"}