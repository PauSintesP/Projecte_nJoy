-- Migración: Tabla de relación evento-equipos para permisos de escaneo
-- Permite asignar equipos a eventos para que sus miembros puedan escanear

CREATE TABLE IF NOT EXISTS evento_equipos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evento_id INTEGER NOT NULL,
    equipo_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (evento_id) REFERENCES evento(id) ON DELETE CASCADE,
    FOREIGN KEY (equipo_id) REFERENCES equipos(id) ON DELETE CASCADE,
    UNIQUE(evento_id, equipo_id)
);

-- Índices para mejorar performance en consultas
CREATE INDEX IF NOT EXISTS idx_evento_equipos_evento ON evento_equipos(evento_id);
CREATE INDEX IF NOT EXISTS idx_evento_equipos_equipo ON evento_equipos(equipo_id);
