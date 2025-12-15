import sqlite3
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Connect to local database
conn = sqlite3.connect('njoy_local.db')
cursor = conn.cursor()

# Create admin user
password_hash = hash_password('admin123')

try:
    cursor.execute("""
        INSERT INTO USUARIO (email, password, nombre, apellidos, fecha_nacimiento, is_active, is_banned, role, pais, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, (
        'admin@njoy.com',
        password_hash,
        'Admin',
        'Sistema',
        '1990-01-01',
        1,  # is_active
        0,  # is_banned = False
        'admin',
        None
    ))
    
    conn.commit()
    print("✅ Usuario admin creado exitosamente!")
    print("\nCredenciales:")
    print("  Email: admin@njoy.com")
    print("  Password: admin123")
    print("  Rol: admin")
    
except sqlite3.IntegrityError as e:
    print(f"❌ Error: El usuario ya existe - {e}")
except Exception as e:
    print(f"❌ Error inesperado: {e}")
    import traceback
    traceback.print_exc()
finally:
    conn.close()
