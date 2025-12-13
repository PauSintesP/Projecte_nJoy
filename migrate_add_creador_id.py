"""
Migración para agregar campo creador_id a la tabla EVENTO
"""

from database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

try:
    print("🔄 Agregando columna creador_id a tabla EVENTO...")
    
    # Agregar columna creador_id
    db.execute(text("ALTER TABLE EVENTO ADD COLUMN creador_id INTEGER"))
    db.commit()
    
    print("✅ ¡Migración completada exitosamente!")
    print("   La columna 'creador_id' fue agregada a EVENTO")
    print("   Los eventos existentes tendrán creador_id = NULL")
    
except Exception as e:
    if "duplicate column name" in str(e).lower():
        print("ℹ️  La columna 'creador_id' ya existe, saltando migración...")
    else:
        print(f"❌ Error durante la migración: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
finally:
    db.close()
