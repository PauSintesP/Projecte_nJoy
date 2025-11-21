-- Script de migración para añadir campos de seguridad a la tabla USUARIO
-- Ejecutar este script en tu base de datos MySQL antes de usar la API actualizada

USE BBDDJoy;

-- Añadir campo is_active (usuario activo/inactivo)
ALTER TABLE USUARIO 
ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE AFTER contrasena;

-- Añadir campo created_at (fecha de creación del registro)
ALTER TABLE USUARIO 
ADD COLUMN created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP AFTER is_active;

-- Añadir índice en email para búsquedas rápidas
ALTER TABLE USUARIO 
ADD INDEX idx_email (email);

-- Añadir índice en user para búsquedas rápidas
ALTER TABLE USUARIO 
ADD INDEX idx_user (user);

-- Hacer email único (si no lo es ya)
ALTER TABLE USUARIO 
ADD UNIQUE INDEX unique_email (email);

-- Verificar los cambios
DESCRIBE USUARIO;

-- IMPORTANTE: Las contraseñas actuales en la base de datos NO funcionarán después de esta actualización
-- porque ahora se espera que estén hasheadas con bcrypt.
-- Opciones:
-- 1. Los usuarios deben registrarse de nuevo con /register
-- 2. Migrar contraseñas existentes (ver script opcional a continuación)

-- ============================================
-- SCRIPT OPCIONAL: Migrar contraseñas existentes
-- ============================================
-- Si tienes usuarios existentes y conoces sus contraseñas en texto plano,
-- puedes usar Python para hashearlas:

-- Python:
-- from passlib.context import CryptContext
-- pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
-- hashed = pwd_context.hash("contraseña_en_texto_plano")
-- print(hashed)

-- Luego actualizar en SQL:
-- UPDATE USUARIO SET contrasena = '$2b$12$...' WHERE id = 1;
