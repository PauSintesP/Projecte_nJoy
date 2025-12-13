"""
Script para migrar la columna 'precio' de String a Float en la tabla EVENTO
"""

from database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

try:
    print("🔄 Migrando columna 'precio' de String a Float...")
    
    # SQLite no soporta ALTER COLUMN directamente, necesitamos recrear la tabla
    # Primero, verificar si ya existe una columna precio_new
    
    # Paso 1: Crear nueva columna precio_new como REAL (Float en SQLite)
    print("📝 Paso 1: Creando columna temporal precio_new...")
    db.execute(text("ALTER TABLE EVENTO ADD COLUMN precio_new REAL"))
    db.commit()
    
    # Paso 2: Copiar datos convirtiendo string a float
    print("📝 Paso 2: Copiando datos de precio a precio_new...")
    # Actualizar precio_new con los valores de precio convertidos a float
    db.execute(text("""
        UPDATE EVENTO 
        SET precio_new = CAST(precio AS REAL) 
        WHERE precio IS NOT NULL AND precio != ''
    """))
    db.commit()
    
    # Paso 3: Eliminar columna precio antigua (SQLite requiere recrear tabla)
    print("📝 Paso 3: Recreando tabla sin columna precio antigua...")
    
    # Crear tabla temporal con la estructura correcta
    db.execute(text("""
        CREATE TABLE EVENTO_temp (
            id INTEGER PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            descripcion VARCHAR(201) NOT NULL,
            localidad_id INTEGER,
            recinto VARCHAR(100) NOT NULL,
            plazas INTEGER NOT NULL,
            fechayhora DATETIME NOT NULL,
            tipo VARCHAR(50) NOT NULL,
            precio REAL,
            organizador_dni VARCHAR(20),
            genero_id INTEGER,
            imagen VARCHAR(100),
            FOREIGN KEY(localidad_id) REFERENCES LOCALIDAD(id),
            FOREIGN KEY(organizador_dni) REFERENCES ORGANIZADOR(dni),
            FOREIGN KEY(genero_id) REFERENCES GENERO(id)
        )
    """))
    
    # Copiar datos a la tabla temporal
    db.execute(text("""
        INSERT INTO EVENTO_temp 
        SELECT id, nombre, descripcion, localidad_id, recinto, plazas, 
               fechayhora, tipo, precio_new, organizador_dni, genero_id, imagen
        FROM EVENTO
    """))
    
    # Eliminar tabla antigua
    db.execute(text("DROP TABLE EVENTO"))
    
    # Renombrar tabla temporal
    db.execute(text("ALTER TABLE EVENTO_temp RENAME TO EVENTO"))
    
    db.commit()
    
    print("✅ ¡Migración completada exitosamente!")
    print("   La columna 'precio' ahora es de tipo REAL (Float)")
    
except Exception as e:
    print(f"❌ Error durante la migración: {e}")
    db.rollback()
    import traceback
    traceback.print_exc()
finally:
    db.close()
