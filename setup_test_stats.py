"""
Script para crear un promotor de prueba con eventos
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from auth import hash_password
from datetime import date, datetime

# Crear tablas si no existen
models.Base.metadata.create_all(bind=engine)

def create_test_promotor(db: Session):
    """Crear usuario promotor de prueba"""
    
    promotor_email = "promotor@test.com"
    
    # Verificar si ya existe
    existing = db.query(models.Usuario).filter(
        models.Usuario.email == promotor_email
    ).first()
    
    if existing:
        print(f"✓ Promotor '{promotor_email}' ya existe (ID: {existing.id})")
        return existing
    
    # Crear nuevo promotor
    promotor = models.Usuario(
        nombre="Test",
        apellidos="Promotor",
        email=promotor_email,
        fecha_nacimiento=date(1990, 1, 1),
        pais="España",
        password=hash_password("test123"),
        role="promotor",
        is_active=True,
        is_banned=False
    )
    
    db.add(promotor)
    db.commit()
    db.refresh(promotor)
    
    print(f"✓ Promotor creado exitosamente:")
    print(f"  Email: {promotor_email}")
    print(f"  Contraseña: test123")
    print(f"  Rol: promotor")
    print(f"  ID: {promotor.id}")
    
    return promotor


def create_test_event(db: Session, promotor_id: int):
    """Crear evento de prueba para el promotor"""
    
    # Verificar si existe localidad
    localidad = db.query(models.Localidad).first()
    if not localidad:
        localidad = models.Localidad(ciudad="Barcelona")
        db.add(localidad)
        db.commit()
        db.refresh(localidad)
        print(f"✓ Localidad 'Barcelona' creada")
    
    # Crear evento
    evento = models.Evento(
        nombre="Fiesta de Prueba - Estadísticas",
        descripcion="Evento de prueba para demostrar el sistema de estadísticas",
        localidad_id=localidad.id,
        recinto="Sala Demo",
        plazas=100,
        fechayhora=datetime(2025, 12, 20, 21, 0, 0),
        tipo="Fiesta",
        precio=25.00,
        creador_id=promotor_id
    )
    
    db.add(evento)
    db.commit()
    db.refresh(evento)
    
    print(f"✓ Evento creado:")
    print(f"  Nombre: {evento.nombre}")
    print(f"  ID: {evento.id}")
    print(f"  Precio: {evento.precio}€")
    print(f"  Plazas: {evento.plazas}")
    
    return evento


def create_test_tickets(db: Session, evento_id: int, promotor_id: int):
    """Crear tickets de prueba y simular escaneos"""
    import random
    import string
    from datetime import datetime, timedelta
    
    # Crear 20 tickets vendidos
    print(f"\n✓ Creando 20 tickets de prueba...")
    
    for i in range(20):
        # Generar código único
        codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        ticket = models.Ticket(
            codigo_ticket=codigo,
            nombre_asistente=f"Asistente {i+1}",
            evento_id=evento_id,
            usuario_id=promotor_id,
            activado=True if i >= 15 else False  # 15 tickets escaneados, 5 sin escanear
        )
        
        # Si el ticket fue escaneado, agregar timestamp
        if not ticket.activado:
            # Simular diferentes horas de escaneo
            base_time = datetime(2025, 12, 20, 20, 0, 0)
            
            # Distribuir en diferentes horas para el gráfico
            if i < 3:
                hour_offset = 0  # 20:00
            elif i < 8:
                hour_offset = 1  # 21:00 (hora pico)
            elif i < 12:
                hour_offset = 2  # 22:00
            elif i < 15:
                hour_offset = 3  # 23:00
            
            ticket.scanned_at = base_time + timedelta(hours=hour_offset, minutes=random.randint(0, 59))
        
        db.add(ticket)
    
    db.commit()
    print(f"✓  20 tickets creados (15 escaneados, 5 pendientes)")


def main():
    """Ejecutar el setup completo"""
    print("=" * 60)
    print("  SETUP DE DATOS DE PRUEBA PARA ESTADÍSTICAS")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # 1. Crear promotor
        print("\n1. Creando promotor de prueba...")
        promotor = create_test_promotor(db)
        
        # 2. Crear evento
        print("\n2. Creando evento de prueba...")
        evento = create_test_event(db, promotor.id)
        
        # 3. Crear tickets
        print("\n3. Creando tickets de prueba...")
        create_test_tickets(db, evento.id, promotor.id)
        
        print("\n" + "=" * 60)
        print("  ✓ SETUP COMPLETADO EXITOSAMENTE!")
        print("=" * 60)
        print("\n📋 CREDENCIALES DE PRUEBA:")
        print(f"  Email: promotor@test.com")
        print(f"  Contraseña: test123")
        print("\n📊 DATOS CREADOS:")
        print(f"  - 1 Promotor")
        print(f"  - 1 Evento: {evento.nombre}")
        print(f"  - 20 Tickets (15 escaneados en diferentes horas)")
        print("\n🎯 AHORA PUEDES:")
        print("  1. Login con promotor@test.com / test123")
        print("  2. Ir a 'Mis Eventos'")
        print("  3. Click en 'Estadísticas' del evento")
        print("  4. Confirmar contraseña: test123")
        print("  5. Ver estadísticas completas con gráfico por horas")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error durante el setup: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
