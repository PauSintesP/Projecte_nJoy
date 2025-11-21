"""
Script Python para migrar contraseñas existentes a bcrypt
Usar SOLO si tienes usuarios existentes con contraseñas en texto plano
"""

from passlib.context import CryptContext
import pymysql

# Configurar bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Conectar a la base de datos
connection = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='123',
    database='BBDDJoy'
)

try:
    with connection.cursor() as cursor:
        # Obtener todos los usuarios
        cursor.execute("SELECT id, contrasena FROM USUARIO")
        usuarios = cursor.fetchall()
        
        print(f"Encontrados {len(usuarios)} usuarios para migrar")
        
        for usuario_id, contrasena_actual in usuarios:
            # Verificar si ya está hasheada (bcrypt hashes empiezan con $2b$)
            if contrasena_actual.startswith('$2b$'):
                print(f"Usuario {usuario_id}: contraseña ya hasheada, saltando...")
                continue
            
            # Hashear la contraseña
            contrasena_hasheada = pwd_context.hash(contrasena_actual)
            
            # Actualizar en la base de datos
            cursor.execute(
                "UPDATE USUARIO SET contrasena = %s WHERE id = %s",
                (contrasena_hasheada, usuario_id)
            )
            
            print(f"Usuario {usuario_id}: contraseña migrada ✓")
        
        # Confirmar cambios
        connection.commit()
        print("\n✅ Migración completada exitosamente!")
        print("Los usuarios ahora pueden hacer login con sus contraseñas originales.")
        
except Exception as e:
    print(f"❌ Error durante la migración: {e}")
    connection.rollback()
    
finally:
    connection.close()
