"""
Seed database with test users and events
"""
from database import SessionLocal
from models import Usuario, Evento
from auth import hash_password
from datetime import datetime, date

db = SessionLocal()

def seed_users():
    """Create test users with different roles"""
    
    users_data = [
        {
            "nombre": "Admin",
            "apellidos": "Sistema",
            "email": "admin@njoy.com",
            "password": "admin123",
            "fecha_nacimiento": date(1990, 1, 1),
            "pais": "España",
            "role": "admin"
        },
        {
            "nombre": "Carlos",
            "apellidos": "Escáner",
            "email": "scanner@njoy.com",
            "password": "scanner123",
            "fecha_nacimiento": date(1995, 5, 15),
            "pais": "España",
            "role": "scanner"
        },
        {
            "nombre": "María",
            "apellidos": "Promotora",
            "email": "promotor@njoy.com",
            "password": "promotor123",
            "fecha_nacimiento": date(1992, 8, 20),
            "pais": "España",
            "role": "promotor"
        },
        {
            "nombre": "Juan",
            "apellidos": "Usuario",
            "email": "user@njoy.com",
            "password": "user123",
            "fecha_nacimiento": date(1998, 3, 10),
            "pais": "España",
            "role": "user"
        }
    ]
    
    created_users = []
    for user_data in users_data:
        # Check if user already exists
        existing = db.query(Usuario).filter(Usuario.email == user_data["email"]).first()
        if existing:
            print(f"✓ Usuario ya existe: {user_data['email']}")
            created_users.append(existing)
            continue
        
        # Create user
        new_user = Usuario(
            nombre=user_data["nombre"],
            apellidos=user_data["apellidos"],
            email=user_data["email"],
            password=hash_password(user_data["password"]),
            fecha_nacimiento=user_data["fecha_nacimiento"],
            pais=user_data["pais"],
            role=user_data["role"],
            is_active=True,
            is_banned=False
        )
        db.add(new_user)
        created_users.append(new_user)
        print(f"✓ Usuario creado: {user_data['email']} (role: {user_data['role']})")
    
    db.commit()
    return created_users

def seed_events():
    """Create sample events"""
    
    # Get a promotor user to assign as creator
    promotor = db.query(Usuario).filter(Usuario.role == "promotor").first()
    if not promotor:
        promotor = db.query(Usuario).filter(Usuario.role == "admin").first()
    
    events_data = [
        {
            "nombre": "Concierto Rock Festival 2025",
            "descripcion": "El mejor festival de rock del año con bandas internacionales",
            "fechayhora": datetime(2025, 7, 15, 20, 0),
            "recinto": "Estadio Municipal",
            "precio": 45.00,
            "plazas": 5000,
            "tipo": "Concierto",
            "imagen": "https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=800"
        },
        {
            "nombre": "Noche Electrónica",
            "descripcion": "Los mejores DJs de la escena electrónica en una noche inolvidable",
            "fechayhora": datetime(2025, 6, 20, 22, 0),
            "recinto": "Club Nocturno Downtown",
            "precio": 30.00,
            "plazas": 1000,
            "tipo": "Festival",
            "imagen": "https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=800"
        },
        {
            "nombre": "Jazz en Vivo",
            "descripcion": "Una velada íntima con los mejores músicos de jazz",
            "fechayhora": datetime(2025, 5, 10, 19, 30),
            "recinto": "Auditorio Cultural",
            "precio": 25.00,
            "plazas": 300,
            "tipo": "Concierto",
            "imagen": "https://images.unsplash.com/photo-1511192336575-5a79af67a629?w=800"
        }
    ]
    
    for event_data in events_data:
        # Check if event exists
        existing = db.query(Evento).filter(Evento.nombre == event_data["nombre"]).first()
        if existing:
            print(f"✓ Evento ya existe: {event_data['nombre']}")
            continue
        
        new_event = Evento(
            nombre=event_data["nombre"],
            descripcion=event_data["descripcion"],
            fechayhora=event_data["fechayhora"],
            recinto=event_data["recinto"],
            precio=event_data["precio"],
            plazas=event_data["plazas"],
            tipo=event_data["tipo"],
            imagen=event_data["imagen"]
        )
        db.add(new_event)
        print(f"✓ Evento creado: {event_data['nombre']}")
    
    db.commit()

if __name__ == "__main__":
    print("\n" + "="*50)
    print("  SEEDING DATABASE - nJoy")
    print("="*50 + "\n")
    
    print("📝 Creando usuarios de prueba...")
    seed_users()
    
    print("\n🎉 Creando eventos de prueba...")
    seed_events()
    
    db.close()
    
    print("\n" + "="*50)
    print("  ✅ DATABASE SEEDED SUCCESSFULLY!")
    print("="*50)
    print("\n📋 USUARIOS CREADOS:\n")
    print("  👤 Admin:     admin@njoy.com     / admin123")
    print("  📷 Scanner:   scanner@njoy.com   / scanner123")
    print("  🎭 Promotor:  promotor@njoy.com  / promotor123")
    print("  👥 Usuario:   user@njoy.com      / user123")
    print("\n" + "="*50 + "\n")
