-- Migration script to add admin system support
-- Adds is_banned column and updates role constraints

-- Add is_banned column to USUARIO table
ALTER TABLE USUARIO ADD COLUMN is_banned BOOLEAN DEFAULT FALSE NOT NULL;

-- Update existing users to ensure they have is_banned = FALSE
UPDATE USUARIO SET is_banned = FALSE WHERE is_banned IS NULL;

-- Note: SQLite doesn't support modifying CHECK constraints easily
-- If you need to enforce role constraints at the database level, 
-- you may need to recreate the table with the new constraint:
-- Valid roles are now: 'user', 'promotor', 'owner', 'admin'

-- For MySQL/PostgreSQL, you would use:
-- ALTER TABLE USUARIO DROP CONSTRAINT IF EXISTS check_role;
-- ALTER TABLE USUARIO ADD CONSTRAINT check_role 
--   CHECK (role IN ('user', 'promotor', 'owner', 'admin'));

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_usuario_role ON USUARIO(role);
CREATE INDEX IF NOT EXISTS idx_usuario_is_banned ON USUARIO(is_banned);
