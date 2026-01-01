-- Production Database Migration Script
-- Adds missing columns to align with current models
-- Safe to run multiple times (uses IF NOT EXISTS where possible)

-- ============================================
-- 1. Add scanned_at to TICKET table
-- ============================================
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'TICKET' AND column_name = 'scanned_at'
    ) THEN
        ALTER TABLE "TICKET" ADD COLUMN scanned_at TIMESTAMP NULL;
        RAISE NOTICE 'Added scanned_at column to TICKET table';
    ELSE
        RAISE NOTICE 'scanned_at column already exists in TICKET table';
    END IF;
END $$;

-- ============================================
-- 2. Add email verification columns to USUARIO table
-- ============================================
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'USUARIO' AND column_name = 'email_verified'
    ) THEN
        ALTER TABLE "USUARIO" ADD COLUMN email_verified BOOLEAN NOT NULL DEFAULT FALSE;
        RAISE NOTICE 'Added email_verified column to USUARIO table';
    ELSE
        RAISE NOTICE 'email_verified column already exists in USUARIO table';
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'USUARIO' AND column_name = 'verification_token'
    ) THEN
        ALTER TABLE "USUARIO" ADD COLUMN verification_token VARCHAR(255) NULL;
        RAISE NOTICE 'Added verification_token column to USUARIO table';
    ELSE
        RAISE NOTICE 'verification_token column already exists in USUARIO table';
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'USUARIO' AND column_name = 'verification_token_expiry'
    ) THEN
        ALTER TABLE "USUARIO" ADD COLUMN verification_token_expiry TIMESTAMP NULL;
        RAISE NOTICE 'Added verification_token_expiry column to USUARIO table';
    ELSE
        RAISE NOTICE 'verification_token_expiry column already exists in USUARIO table';
    END IF;
END $$;

-- ============================================
-- 3. Verify changes
-- ============================================
SELECT 
    'TICKET' as table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'TICKET'
ORDER BY ordinal_position;

SELECT 
    'USUARIO' as table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'USUARIO'
ORDER BY ordinal_position;

-- Migration completed successfully
