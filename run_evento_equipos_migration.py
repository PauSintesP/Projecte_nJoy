import sqlite3
import os

# Migración: Tabla evento_equipos
db_path = 'njoy_local.db'

print(f"📁 Conectando a base de datos: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Leer el archivo de migración
with open('migrations/add_evento_equipos.sql', 'r', encoding='utf-8') as f:
    migration_sql = f.read()

try:
    # Ejecutar la migración
    cursor.executescript(migration_sql)
    conn.commit()
    print("✅ Migración ejecutada correctamente")
    print("✅ Tabla evento_equipos creada")
    print("✅ Índices creados")
    
    # Verificar que la tabla existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='evento_equipos'")
    result = cursor.fetchone()
    if result:
        print(f"✅ Verificado: Tabla {result[0]} existe en la base de datos")
    else:
        print("⚠️ Advertencia: No se pudo verificar la tabla")
        
except Exception as e:
    print(f"❌ Error al ejecutar migración: {e}")
    conn.rollback()
finally:
    conn.close()
    print("\n🔌 Conexión cerrada")
