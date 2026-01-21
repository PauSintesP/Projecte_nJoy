-- =============================================
-- MIGRACIÓN DE BD PARA VERCEL - nJoy
-- Fecha: 2026-01-16
-- =============================================

-- 1. Añadir campos de perfil de usuario
ALTER TABLE "USUARIO" ADD COLUMN IF NOT EXISTS foto_perfil VARCHAR(500);
ALTER TABLE "USUARIO" ADD COLUMN IF NOT EXISTS bio VARCHAR(500);

-- 2. Añadir campo de pausa de ventas en eventos
ALTER TABLE "EVENTO" ADD COLUMN IF NOT EXISTS venta_pausada BOOLEAN DEFAULT FALSE NOT NULL;

-- Verificar que las columnas fueron creadas
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'USUARIO' AND column_name IN ('foto_perfil', 'bio');

SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'EVENTO' AND column_name = 'venta_pausada';
