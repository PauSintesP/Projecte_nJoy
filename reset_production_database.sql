-- ============================================
-- RESET PRODUCTION DATABASE
-- ============================================
-- This script will DROP all existing tables and recreate them
-- with the current schema. ALL DATA WILL BE LOST.
-- Use this to fix schema conflicts and start fresh.

-- ============================================
-- 1. DROP ALL TABLES (in correct order to avoid FK constraints)
-- ============================================

DROP TABLE IF EXISTS "TEAM_MEMBER" CASCADE;
DROP TABLE IF EXISTS "TEAM" CASCADE;
DROP TABLE IF EXISTS "PAGO" CASCADE;
DROP TABLE IF EXISTS "TICKET" CASCADE;
DROP TABLE IF EXISTS "EVENTO" CASCADE;
DROP TABLE IF EXISTS "USUARIO" CASCADE;
DROP TABLE IF EXISTS "ARTISTA" CASCADE;
DROP TABLE IF EXISTS "GENERO" CASCADE;
DROP TABLE IF EXISTS "ORGANIZADOR" CASCADE;
DROP TABLE IF EXISTS "LOCALIDAD" CASCADE;

-- ============================================
-- 2. CREATE TABLES WITH CURRENT SCHEMA
-- ============================================

-- LOCALIDAD Table
CREATE TABLE "LOCALIDAD" (
    id SERIAL PRIMARY KEY,
    ciudad VARCHAR(100) NOT NULL
);

CREATE INDEX idx_localidad_id ON "LOCALIDAD" (id);

-- ORGANIZADOR Table
CREATE TABLE "ORGANIZADOR" (
    dni VARCHAR(20) PRIMARY KEY,
    ncompleto VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    telefono VARCHAR(15) NOT NULL,
    web VARCHAR(255)
);

CREATE INDEX idx_organizador_dni ON "ORGANIZADOR" (dni);

-- GENERO Table
CREATE TABLE "GENERO" (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

CREATE INDEX idx_genero_id ON "GENERO" (id);

-- ARTISTA Table
CREATE TABLE "ARTISTA" (
    id SERIAL PRIMARY KEY,
    nartistico VARCHAR(100) NOT NULL,
    nreal VARCHAR(100) NOT NULL
);

CREATE INDEX idx_artista_id ON "ARTISTA" (id);

-- USUARIO Table (with email verification fields)
CREATE TABLE "USUARIO" (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    fecha_nacimiento DATE NOT NULL,
    pais VARCHAR(100),
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_banned BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    verification_token VARCHAR(255),
    verification_token_expiry TIMESTAMP
);

CREATE INDEX idx_usuario_id ON "USUARIO" (id);
CREATE INDEX idx_usuario_nombre ON "USUARIO" (nombre);
CREATE INDEX idx_usuario_email ON "USUARIO" (email);

-- EVENTO Table
CREATE TABLE "EVENTO" (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(201) NOT NULL,
    localidad_id INTEGER REFERENCES "LOCALIDAD"(id),
    recinto VARCHAR(100) NOT NULL,
    plazas INTEGER NOT NULL,
    fechayhora TIMESTAMP NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    precio FLOAT,
    organizador_dni VARCHAR(20) REFERENCES "ORGANIZADOR"(dni),
    genero_id INTEGER REFERENCES "GENERO"(id),
    imagen VARCHAR(100),
    creador_id INTEGER REFERENCES "USUARIO"(id)
);

CREATE INDEX idx_evento_id ON "EVENTO" (id);

-- TICKET Table (with scanned_at field)
CREATE TABLE "TICKET" (
    id SERIAL PRIMARY KEY,
    codigo_ticket VARCHAR UNIQUE NOT NULL,
    nombre_asistente VARCHAR,
    evento_id INTEGER REFERENCES "EVENTO"(id),
    usuario_id INTEGER REFERENCES "USUARIO"(id),
    activado BOOLEAN DEFAULT TRUE,
    scanned_at TIMESTAMP
);

CREATE INDEX idx_ticket_id ON "TICKET" (id);
CREATE INDEX idx_ticket_codigo ON "TICKET" (codigo_ticket);

-- PAGO Table
CREATE TABLE "PAGO" (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES "USUARIO"(id),
    metodo_pago VARCHAR(50) NOT NULL,
    total DECIMAL(10, 2) NOT NULL,
    fecha TIMESTAMP NOT NULL,
    ticket_id INTEGER UNIQUE REFERENCES "TICKET"(id)
);

CREATE INDEX idx_pago_id ON "PAGO" (id);

-- TEAM Table
CREATE TABLE "TEAM" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    leader_id INTEGER REFERENCES "USUARIO"(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_team_id ON "TEAM" (id);

-- TEAM_MEMBER Table
CREATE TABLE "TEAM_MEMBER" (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES "TEAM"(id),
    user_id INTEGER REFERENCES "USUARIO"(id),
    status VARCHAR(20) DEFAULT 'pending',
    invited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    joined_at TIMESTAMP
);

CREATE INDEX idx_team_member_id ON "TEAM_MEMBER" (id);

-- ============================================
-- 3. VERIFICATION - Show all tables
-- ============================================

SELECT 
    table_name,
    (SELECT COUNT(*) 
     FROM information_schema.columns 
     WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- ============================================
-- RESET COMPLETE
-- ============================================
-- All tables have been recreated with the current schema
-- Database is ready to use with FastAPI models
