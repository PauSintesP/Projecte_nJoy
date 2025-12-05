"""
Script para crear usuario administrador y sembrar datos iniciales
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from auth import hash_password
from datetime import date

# Crear tablas si no existen
models.Base.metadata.create_all(bind=engine)

def create_admin_user(db: Session):
    """Crear usuario administrador si no existe"""
    
    admin_email = "pausintespaul@gmail.com"
    
    # Verificar si ya existe
    existing_admin = db.query(models.Usuario).filter(
        models.Usuario.email == admin_email
    ).first()
    
    if existing_admin:
        print(f"✓ Usuario admin '{admin_email}' ya existe.")
        # Actualizar a admin si no lo es
        if existing_admin.role != 'admin':
            existing_admin.role = 'admin'
            db.commit()
            print(f"✓ Usuario actualizado a rol 'admin'.")
        return existing_admin
    
    # Crear nuevo usuario admin
    admin_user = models.Usuario(
        nombre="Pau",
        apellidos="Sintes Paul",
        email=admin_email,
        fecha_nacimiento=date(1990, 1, 1),  # Fecha de ejemplo
        pais="España",
        password=hash_password("DEMO1234"),
        role="admin",
        is_active=True,
        is_banned=False
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    print(f"✓ Usuario admin creado exitosamente:")
    print(f"  Email: {admin_email}")
    print(f"  Contraseña: DEMO1234")
    print(f"  Rol: admin")
    
    return admin_user


def seed_menorca_locations(db: Session):
    """Sembrar localidades de Menorca"""
    
    menorca_cities = [
        "Mahón",
        "Ciutadella",
        "Alaior",
        "Es Castell",
        "Ferreries",
        "Es Mercadal",
        "Sant Lluís",
        "Es Migjorn Gran"
    ]
    
    created_count = 0
    
    for city in menorca_cities:
        # Verificar si ya existe
        existing = db.query(models.Localidad).filter(
            models.Localidad.ciudad == city
        ).first()
        
        if not existing:
            localidad = models.Localidad(ciudad=city)
            db.add(localidad)
            created_count += 1
    
    if created_count > 0:
        db.commit()
        print(f"✓ {created_count} localidades de Menorca añadidas.")
    else:
        print("✓ Todas las localidades de Menorca ya existen.")
    
    # Mostrar total
    total = db.query(models.Localidad).count()
    print(f"  Total de localidades en la base de datos: {total}")


def main():
    """Ejecutar todas las operaciones de seed"""
    print("=" * 50)
    print("Inicializando datos de administración...")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        # Crear usuario admin
        create_admin_user(db)
        print()
        
        # Sembrar localidades
        seed_menorca_locations(db)
        print()
        
        print("=" * 50)
        print("✓ Proceso completado exitosamente!")
        print("=" * 50)
        
    except Exception as e:
        print(f"✗ Error durante el proceso: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
