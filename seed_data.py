"""
Script para poblar la base de datos con datos ficticios
CONFIRMADO: Schema coincide con models.py
"""
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import text
import models
from auth import hash_password

def seed_database(db: Session):
    """Poblar la base de datos con datos de prueba"""
    
    print("Limpiando datos existentes...")
    # Limpiar datos existentes (solo para testing)
    db.query(models.TeamMember).delete()
    db.query(models.Team).delete()
    db.query(models.Pago).delete()
    db.query(models.Ticket).delete()
    db.query(models.Evento).delete()
    db.query(models.Artista).delete()
    db.query(models.Genero).delete()
    db.query(models.Organizador).delete()
    db.query(models.Localidad).delete()
    db.query(models.Usuario).delete()
    
    # Try to reset autoincrement if sqlite
    try:
        db.execute(text("DELETE FROM sqlite_sequence"))
    except Exception as e:
        print(f"Warning: Could not reset sqlite_sequence: {e}")
        
    db.commit()
    
    print("Creando Localidades...")
    # 1. LOCALIDADES
    localidades = [
        models.Localidad(ciudad="Barcelona"),
        models.Localidad(ciudad="Madrid"),
        models.Localidad(ciudad="Valencia"),
        models.Localidad(ciudad="Sevilla"),
        models.Localidad(ciudad="Bilbao"),
    ]
    db.add_all(localidades)
    db.commit()
    for l in localidades: db.refresh(l)
    
    print("Creando Géneros...")
    # 2. GÉNEROS MUSICALES
    generos = [
        models.Genero(nombre="Rock"),
        models.Genero(nombre="Pop"),
        models.Genero(nombre="Electrónica"),
        models.Genero(nombre="Jazz"),
        models.Genero(nombre="Reggaeton"),
        models.Genero(nombre="Hip Hop"),
        models.Genero(nombre="Metal"),
        models.Genero(nombre="Indie"),
    ]
    db.add_all(generos)
    db.commit()
    for g in generos: db.refresh(g)
    
    print("Creando Organizadores...")
    # 3. ORGANIZADORES
    organizadores = [
        models.Organizador(
            dni="12345678A",
            ncompleto="Live Nation España",
            email="info@livenation.es",
            telefono="934567890",
            web="https://www.livenation.es"
        ),
        models.Organizador(
            dni="87654321B",
            ncompleto="Primavera Sound",
            email="info@primaverasound.com",
            telefono="932345678",
            web="https://www.primaverasound.com"
        ),
        models.Organizador(
            dni="11223344C",
            ncompleto="FIB Festival",
            email="contacto@fiberfib.com",
            telefono="965123456",
            web="https://www.fiberfib.com"
        ),
    ]
    db.add_all(organizadores)
    db.commit()
    
    print("Creando Artistas...")
    # 4. ARTISTAS
    artistas = [
        models.Artista(nartistico="Rosalía", nreal="Rosalía Vila Tobella"),
        models.Artista(nartistico="C. Tangana", nreal="Antón Álvarez Alfaro"),
        models.Artista(nartistico="The Weeknd", nreal="Abel Makkonen Tesfaye"),
        models.Artista(nartistico="Bad Bunny", nreal="Benito Antonio Martínez"),
        models.Artista(nartistico="Dua Lipa", nreal="Dua Lipa"),
        models.Artista(nartistico="Arctic Monkeys", nreal="Arctic Monkeys Band"),
        models.Artista(nartistico="Daft Punk", nreal="Thomas Bangalter & Guy-Manuel"),
        models.Artista(nartistico="Billie Eilish", nreal="Billie Eilish O'Connell"),
    ]
    db.add_all(artistas)
    db.commit()
    
    print("Creando Usuarios...")
    # 5. USUARIOS
    usuarios = [
        models.Usuario(
            nombre="Juan",
            apellidos="Pérez García",
            email="juan@example.com",
            fecha_nacimiento=date(1995, 3, 15),
            password=hash_password("password123"),
            is_active=True,
            role="user"
        ),
        models.Usuario(
            nombre="María",
            apellidos="López Martínez",
            email="maria@example.com",
            fecha_nacimiento=date(1998, 7, 22),
            password=hash_password("password123"),
            is_active=True,
            role="user"
        ),
        models.Usuario(
            nombre="Carlos",
            apellidos="Ruiz Sánchez",
            email="carlos@example.com",
            fecha_nacimiento=date(2000, 11, 8),
            password=hash_password("password123"),
            is_active=True,
            role="scanner"
        ),
        models.Usuario(
            nombre="Ana",
            apellidos="García Fernández",
            email="ana@example.com",
            fecha_nacimiento=date(1997, 5, 30),
            password=hash_password("password123"),
            is_active=True,
            role="promotor"
        ),
        models.Usuario(
            nombre="Admin",
            apellidos="Sistema",
            email="admin@njoy.com",
            fecha_nacimiento=date(1990, 1, 1),
            password=hash_password("admin123"),
            is_active=True,
            role="admin"
        ),
    ]
    db.add_all(usuarios)
    db.commit()
    for u in usuarios: db.refresh(u)
    
    # Identify users by specific variables for clarity
    juan = usuarios[0]
    maria = usuarios[1]
    carlos_scanner = usuarios[2]
    ana_promotor = usuarios[3]
    admin = usuarios[4]
    
    print("Creando Eventos...")
    # 6. EVENTOS
    now = datetime.now()
    
    eventos = [
        models.Evento(
            nombre="Rosalía - Motomami World Tour",
            descripcion="La gira mundial de Rosalía llega a Barcelona",
            localidad_id=localidades[0].id,  # Barcelona
            recinto="Palau Sant Jordi",
            plazas=15000,
            fechayhora=now + timedelta(days=30),
            tipo="Concierto",
            precio=89.99,
            organizador_dni=organizadores[0].dni,
            genero_id=generos[1].id,  # Pop
            imagen="rosalia_motomami.jpg",
            creador_id=admin.id
        ),
        models.Evento(
            nombre="Bad Bunny - Un Verano Sin Ti",
            descripcion="El Rey del Reggaeton presenta su último álbum",
            localidad_id=localidades[1].id,  # Madrid
            recinto="WiZink Center",
            plazas=18000,
            fechayhora=now + timedelta(days=45),
            tipo="Concierto",
            precio=120.00,
            organizador_dni=organizadores[0].dni,
            genero_id=generos[4].id,  # Reggaeton
            imagen="badbunny.jpg",
            creador_id=admin.id
        ),
        models.Evento(
            nombre="Primavera Sound 2025",
            descripcion="El festival de música indie más importante",
            localidad_id=localidades[0].id,  # Barcelona
            recinto="Parc del Fòrum",
            plazas=75000,
            fechayhora=now + timedelta(days=120),
            tipo="Festival",
            precio=250.00,
            organizador_dni=organizadores[1].dni,
            genero_id=generos[7].id,  # Indie
            imagen="primavera_sound.jpg",
            creador_id=admin.id
        ),
        models.Evento(
            nombre="Arctic Monkeys - The Car Tour",
            descripcion="La banda británica presenta su álbum",
            localidad_id=localidades[2].id,  # Valencia
            recinto="Ciutat de les Arts",
            plazas=25000,
            fechayhora=now + timedelta(days=60),
            tipo="Concierto",
            precio=75.50,
            organizador_dni=organizadores[2].dni,
            genero_id=generos[0].id,  # Rock
            imagen="arctic_monkeys.jpg",
            creador_id=ana_promotor.id # Promotor Ana
        ),
        models.Evento(
            nombre="Billie Eilish - Live",
            descripcion="La sensación del pop en directo",
            localidad_id=localidades[1].id,  # Madrid
            recinto="Estadio Metropolitano",
            plazas=45000,
            fechayhora=now + timedelta(days=75),
            tipo="Concierto",
            precio=95.00,
            organizador_dni=organizadores[0].dni,
            genero_id=generos[1].id,  # Pop
            imagen="billie_eilish.jpg",
            creador_id=admin.id
        ),
    ]
    db.add_all(eventos)
    db.commit()
    for e in eventos: db.refresh(e)
    
    print("Creando Tickets...")
    # 7. TICKETS
    import uuid
    def gen_code():
        return f"NJOY-{str(uuid.uuid4())[:8].upper()}"

    tickets = [
        # Juan buys tickets
        models.Ticket(evento_id=eventos[0].id, usuario_id=juan.id, activado=True, codigo_ticket=gen_code(), nombre_asistente="Juan Pérez"),
        models.Ticket(evento_id=eventos[2].id, usuario_id=juan.id, activado=True, codigo_ticket=gen_code(), nombre_asistente="Juan Pérez"),
        # María buys tickets
        models.Ticket(evento_id=eventos[1].id, usuario_id=maria.id, activado=True, codigo_ticket=gen_code(), nombre_asistente="María López"),
        models.Ticket(evento_id=eventos[3].id, usuario_id=maria.id, activado=True, codigo_ticket=gen_code(), nombre_asistente="María López"),
        models.Ticket(evento_id=eventos[4].id, usuario_id=maria.id, activado=False, codigo_ticket=gen_code(), nombre_asistente="María López"),
        # Carlos scanner buys ticket
        models.Ticket(evento_id=eventos[0].id, usuario_id=carlos_scanner.id, activado=True, codigo_ticket=gen_code(), nombre_asistente="Carlos Ruiz"),
    ]
    
    db.add_all(tickets)
    db.commit()
    for t in tickets: db.refresh(t)

    print("Creando Pagos...")
    # 8. PAGOS
    # Need to match ticket IDs
    pagos = [
        models.Pago(
            usuario_id=juan.id,
            metodo_pago="Tarjeta de Crédito",
            total=89.99,
            fecha=now - timedelta(days=5),
            ticket_id=tickets[0].id
        ),
        models.Pago(
            usuario_id=juan.id,
            metodo_pago="PayPal",
            total=250.00,
            fecha=now - timedelta(days=3),
            ticket_id=tickets[1].id
        ),
    ]
    db.add_all(pagos)
    db.commit()
    
    return {
        "message": "Datos insertados correctamente"
    }
