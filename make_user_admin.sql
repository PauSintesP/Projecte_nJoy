-- ============================================
-- CONVERT EXISTING USER TO ADMIN
-- ============================================
-- This script updates your registered user to admin role
-- Use this if you already registered an account

-- Update the user you just registered to admin
-- Replace 'pausintespaul@gmail.com' with your actual email if different
UPDATE "USUARIO" 
SET role = 'admin',
    email_verified = TRUE
WHERE email = 'pausintespaul@gmail.com';

-- Verify the change
SELECT id, nombre, apellidos, email, role, is_active, email_verified 
FROM "USUARIO" 
WHERE email = 'pausintespaul@gmail.com';

-- ============================================
-- USER UPDATED TO ADMIN
-- ============================================
-- Now you can login with your registered credentials
-- and have full admin access
