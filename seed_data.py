"""
Script para poblar la base de datos con datos ficticios
"""
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
import models
from auth import hash_password

def seed_database(db: Session):
    """Poblar la base de datos con datos de prueba"""
    
    # Limpiar datos existentes (solo para testing)
    # CUIDADO: Esto borra todos los datos
    db.query(models.Pago).delete()
    db.query(models.Ticket).delete()
    db.query(models.Evento).delete()
    db.query(models.Artista).delete()
    db.query(models.Genero).delete()
    db.query(models.Organizador).delete()
    db.query(models.Localidad).delete()
    db.query(models.Usuario).delete()
    db.commit()
    
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
    
    # 5. USUARIOS
    usuarios = [
        models.Usuario(
            user="juan_perez",
            ncompleto="Juan Pérez García",
            email="juan@example.com",
            fnacimiento=date(1995, 3, 15),
            contrasena=hash_password("password123"),
            is_active=True,
            created_at=datetime.now()
        ),
        models.Usuario(
            user="maria_lopez",
            ncompleto="María López Martínez",
            email="maria@example.com",
            fnacimiento=date(1998, 7, 22),
            contrasena=hash_password("password123"),
            is_active=True,
            created_at=datetime.now()
        ),
        models.Usuario(
            user="carlos_ruiz",
            ncompleto="Carlos Ruiz Sánchez",
            email="carlos@example.com",
            fnacimiento=date(2000, 11, 8),
            contrasena=hash_password("password123"),
            is_active=True,
            created_at=datetime.now()
        ),
        models.Usuario(
            user="ana_garcia",
            ncompleto="Ana García Fernández",
            email="ana@example.com",
            fnacimiento=date(1997, 5, 30),
            contrasena=hash_password("password123"),
            is_active=True,
            created_at=datetime.now()
        ),
        models.Usuario(
            user="admin",
            ncompleto="Administrador del Sistema",
            email="admin@njoy.com",
            fnacimiento=date(1990, 1, 1),
            contrasena=hash_password("admin123"),
            is_active=True,
            created_at=datetime.now()
        ),
    ]
    db.add_all(usuarios)
    db.commit()
    
    # 6. EVENTOS
    now = datetime.now()
    eventos = [
        models.Evento(
            nombre="Rosalía - Motomami World Tour",
            descripcion="La gira mundial de Rosalía llega a Barcelona con su esperado álbum Motomami",
            localidad_id=1,  # Barcelona
            recinto="Palau Sant Jordi",
            plazas=15000,
            fechayhora=now + timedelta(days=30),
            tipo="Concierto",
            categoria_precio="Premium",
            organizador_dni="12345678A",
            genero_id=2,  # Pop
            imagen="rosalia_motomami.jpg"
        ),
        models.Evento(
            nombre="Bad Bunny - Un Verano Sin Ti",
            descripcion="El Rey del Reggaeton presenta su último álbum en directo",
            localidad_id=2,  # Madrid
            recinto="WiZink Center",
            plazas=18000,
            fechayhora=now + timedelta(days=45),
            tipo="Concierto",
            categoria_precio="VIP",
            organizador_dni="12345678A",
            genero_id=5,  # Reggaeton
            imagen="badbunny.jpg"
        ),
        models.Evento(
            nombre="Primavera Sound 2025",
            descripcion="El festival de música indie y alternativa más importante de Europa",
            localidad_id=1,  # Barcelona
            recinto="Parc del Fòrum",
            plazas=75000,
            fechayhora=now + timedelta(days=120),
            tipo="Festival",
            categoria_precio="Normal",
            organizador_dni="87654321B",
            genero_id=8,  # Indie
            imagen="primavera_sound.jpg"
        ),
        models.Evento(
            nombre="Arctic Monkeys - The Car Tour",
            descripcion="La banda británica presenta su nuevo álbum The Car",
            localidad_id=3,  # Valencia
            recinto="Ciutat de les Arts i les Ciències",
            plazas=25000,
            fechayhora=now + timedelta(days=60),
            tipo="Concierto",
            categoria_precio="Premium",
            organizador_dni="11223344C",
            genero_id=1,  # Rock
            imagen="arctic_monkeys.jpg"
        ),
        models.Evento(
            nombre="Billie Eilish - Happier Than Ever",
            descripcion="La sensación del pop presenta su aclamado segundo álbum",
            localidad_id=2,  # Madrid
            recinto="Estadio Metropolitano",
            plazas=45000,
            fechayhora=now + timedelta(days=75),
            tipo="Concierto",
            categoria_precio="Normal",
            organizador_dni="12345678A",
            genero_id=2,  # Pop
            imagen="billie_eilish.jpg"
        ),
        models.Evento(
            nombre="FIB Festival 2025",
            descripcion="Festival Internacional de Benicàssim con los mejores artistas del momento",
            localidad_id=3,  # Valencia
            recinto="Recinto FIB",
            plazas=50000,
            fechayhora=now + timedelta(days=150),
            tipo="Festival",
            categoria_precio="Normal",
            organizador_dni="11223344C",
            genero_id=8,  # Indie
            imagen="fib.jpg"
        ),
        models.Evento(
            nombre="C. Tangana - Sin Cantar ni Afinar",
            descripcion="El Madrileño trae su espectáculo único a Sevilla",
            localidad_id=4,  # Sevilla
            recinto="Estadio de la Cartuja",
            plazas=30000,
            fechayhora=now + timedelta(days=90),
            tipo="Concierto",
            categoria_precio="Premium",
            organizador_dni="12345678A",
            genero_id=2,  # Pop
            imagen="c_tangana.jpg"
        ),
        models.Evento(
            nombre="Jazz Vitoria Festival",
            descripcion="El festival de jazz más importante del norte de España",
            localidad_id=5,  # Bilbao
            recinto="Plaza de la Virgen Blanca",
            plazas=5000,
            fechayhora=now + timedelta(days=100),
            tipo="Festival",
            categoria_precio="Normal",
            organizador_dni="87654321B",
            genero_id=4,  # Jazz
            imagen="jazz_festival.jpg"
        ),
    ]
    db.add_all(eventos)
    db.commit()
    
    # 7. TICKETS
    tickets = [
        # Juan tiene 2 tickets
        models.Ticket(evento_id=1, usuario_id=1, activado=True),
        models.Ticket(evento_id=3, usuario_id=1, activado=True),
        # María tiene 3 tickets
        models.Ticket(evento_id=2, usuario_id=2, activado=True),
        models.Ticket(evento_id=4, usuario_id=2, activado=True),
        models.Ticket(evento_id=5, usuario_id=2, activado=False),  # Desactivado
        # Carlos tiene 1 ticket
        models.Ticket(evento_id=6, usuario_id=3, activado=True),
        # Ana tiene 2 tickets
        models.Ticket(evento_id=7, usuario_id=4, activado=True),
        models.Ticket(evento_id=8, usuario_id=4, activado=True),
    ]
    db.add_all(tickets)
    db.commit()
    
    # 8. PAGOS
    pagos = [
        models.Pago(
            usuario_id=1,
            metodo_pago="Tarjeta de Crédito",
            total=89.99,
            fecha=now - timedelta(days=5),
            ticket_id=1
        ),
        models.Pago(
            usuario_id=1,
            metodo_pago="PayPal",
            total=175.00,
            fecha=now - timedelta(days=3),
            ticket_id=2
        ),
        models.Pago(
            usuario_id=2,
            metodo_pago="Tarjeta de Débito",
            total=120.50,
            fecha=now - timedelta(days=7),
            ticket_id=3
        ),
        models.Pago(
            usuario_id=2,
            metodo_pago="Tarjeta de Crédito",
            total=95.00,
            fecha=now - timedelta(days=2),
            ticket_id=4
        ),
        models.Pago(
            usuario_id=2,
            metodo_pago="Bizum",
            total=85.00,
            fecha=now - timedelta(days=1),
            ticket_id=5
        ),
        models.Pago(
            usuario_id=3,
            metodo_pago="Transferencia",
            total=150.00,
            fecha=now - timedelta(days=10),
            ticket_id=6
        ),
        models.Pago(
            usuario_id=4,
            metodo_pago="Tarjeta de Crédito",
            total=110.00,
            fecha=now - timedelta(days=4),
            ticket_id=7
        ),
        models.Pago(
            usuario_id=4,
            metodo_pago="PayPal",
            total=45.00,
            fecha=now - timedelta(days=6),
            ticket_id=8
        ),
    ]
    db.add_all(pagos)
    db.commit()
    
    return {
        "localidades": len(localidades),
        "generos": len(generos),
        "organizadores": len(organizadores),
        "artistas": len(artistas),
        "usuarios": len(usuarios),
        "eventos": len(eventos),
        "tickets": len(tickets),
        "pagos": len(pagos)
    }
