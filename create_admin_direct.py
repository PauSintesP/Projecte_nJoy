import sqlite3
from datetime import date
import sys
sys.path.append('.')
from auth import hash_password

# Connect to local database
conn = sqlite3.connect('njoy_local.db')
cursor = conn.cursor()

# Create admin user
admin_data = (
    'admin@njoy.com',  # email
    hash_password('admin123'),  # password
    'Admin',  # nombre
    'Sistema',  # apellidos
    '1990-01-01',  # fecha_nacimiento
    True,  # is_active
    'admin',  # role
    None  # pais
)

try:
    cursor.execute("""
        INSERT INTO USUARIO (email, password, nombre, apellidos, fecha_nacimiento, is_active, role, pais)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, admin_data)
    
    conn.commit()
    print("✅ Usuario admin creado exitosamente!")
    print("\nCredenciales:")
    print("  Email: admin@njoy.com")
    print("  Password: admin123")
    print("  Rol: admin")
    
except sqlite3.IntegrityError as e:
    print(f"❌ Error: El usuario ya existe - {e}")
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    conn.close()
