-- ============================================
-- CREATE ADMIN USER FOR PRODUCTION
-- ============================================
-- This script creates an admin user for production
-- Execute this AFTER the database reset

-- Delete existing admin user if exists (to avoid duplicate key error)
DELETE FROM "USUARIO" WHERE email = 'admin@njoy.com';

-- Insert admin user
-- Password: Admin123 (change this after first login!)
-- Email: admin@njoy.com
-- Password hash generated with bcrypt

INSERT INTO "USUARIO" (
    nombre,
    apellidos,
    email,
    fecha_nacimiento,
    pais,
    password,
    role,
    is_active,
    is_banned,
    created_at,
    email_verified
) VALUES (
    'Admin',
    'Sistema',
    'admin@njoy.com',
    '1990-01-01',
    'España',
    '$2b$12$yWrh8qXgx9hMVF5rj/8J1.f9yg86yVDKpJNgmQv6L7J0aaLeWqpyW',  -- Password: Admin123 (freshly generated hash)
    'admin',
    TRUE,
    FALSE,
    CURRENT_TIMESTAMP,
    TRUE  -- Email pre-verified for admin
);

-- Verify admin user was created
SELECT id, nombre, apellidos, email, role, is_active, email_verified 
FROM "USUARIO" 
WHERE email = 'admin@njoy.com';

-- ============================================
-- ADMIN USER CREATED
-- ============================================
-- You can now login with:
-- Email: admin@njoy.com
-- Password: Admin123
-- 
-- IMPORTANT: Change this password after first login!
