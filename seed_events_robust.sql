-- ROBUST SQL SCRIPT
-- 1. Limpia cualquier error anterior
ROLLBACK;

-- 2. Limpia tablas de forma completa
TRUNCATE TABLE "TICKET" CASCADE;
TRUNCATE TABLE "EVENTO" CASCADE;
TRUNCATE TABLE "EVENTO_EQUIPOS" CASCADE; -- Si existe

-- 3. GARANTIZA DEPENDENCIAS (Usando IDs fijos y actualizando si ya existen)

-- Generos (IDs 1-6)
INSERT INTO "GENERO" (id, nombre) VALUES 
(1, 'Música'), (2, 'Tecnología'), (3, 'Arte'), (4, 'Gastronomía'), (5, 'Deportes'), (6, 'Teatro')
ON CONFLICT (id) DO UPDATE SET nombre = EXCLUDED.nombre;

-- Localidades (IDs 1-5)
INSERT INTO "LOCALIDAD" (id, ciudad, latitud, longitud) VALUES 
(1, 'Barcelona', 41.3851, 2.1734),
(2, 'Madrid', 40.4168, -3.7038),
(3, 'Valencia', 39.4699, -0.3763),
(4, 'Sevilla', 37.3891, -5.9845),
(5, 'Bilbao', 43.2630, -2.9350)
ON CONFLICT (id) DO UPDATE SET ciudad = EXCLUDED.ciudad, latitud = EXCLUDED.latitud, longitud = EXCLUDED.longitud;

-- Organizador
INSERT INTO "ORGANIZADOR" (dni, ncompleto, email, telefono, web) VALUES 
('12345678A', 'nJoy Events', 'events@njoy.com', '600111222', 'https://njoy.events')
ON CONFLICT (dni) DO UPDATE SET ncompleto = EXCLUDED.ncompleto;

-- Usuario Admin (ID 1) - Necesario para creador_id
-- NOTA: Si el usuario 1 no existe, se crea. Si existe, NO tocamos la contraseña ni email para no romper login.
INSERT INTO "USUARIO" (id, nombre, apellidos, email, fecha_nacimiento, password, role, is_active, created_at, email_verified) VALUES 
(1, 'Admin', 'nJoy', 'admin@njoy.com', '1995-01-01', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxwKc.6Iym.1Wz0.1', 'admin', TRUE, NOW(), TRUE)
ON CONFLICT (id) DO UPDATE SET role = 'admin', is_active = TRUE; 
-- Forzamos role admin y activo, pero mantenemos pass original si existe.

-- 4. INSERTAR EVENTOS
-- ATENCIÓN: URLs de imagen acortadas para cumplir límite de String(100)
INSERT INTO "EVENTO" (nombre, descripcion, localidad_id, recinto, plazas, fechayhora, tipo, precio, organizador_dni, genero_id, imagen, creador_id) VALUES

-- Music Festival (Barcelona - ID 1, Música - ID 1)
('Primavera Sound 2026', 'El festival de música más grande regresa.', 1, 'Parc del Fòrum', 50000, '2026-06-04 18:00:00', 'Festival', 245.00, '12345678A', 1, 'https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=600', 1),

-- Tech Conference (Madrid - ID 2, Tech - ID 2)
('AI & Future Tech Summit', 'Conferencia líder en IA.', 2, 'IFEMA Madrid', 2500, '2026-09-15 09:00:00', 'Conferencia', 150.00, '12345678A', 2, 'https://images.unsplash.com/photo-1544531586-fde5298cdd40?w=600', 1),

-- Jazz Concert (Barcelona - ID 1, Música - ID 1)
('Noche de Jazz en el Palau', 'Velada íntima de jazz.', 1, 'Palau de la Música', 500, '2026-03-20 21:00:00', 'Concierto', 45.00, '12345678A', 1, 'https://images.unsplash.com/photo-1511192336575-5a79af67a629?w=600', 1),

-- Sports - Marathon (Valencia - ID 3, Deporte - ID 5)
('Maratón de Valencia', 'Una de las maratones más rápidas.', 3, 'Ciudad de las Artes', 20000, '2026-12-06 08:30:00', 'Deporte', 60.00, '12345678A', 5, 'https://images.unsplash.com/photo-1552674605-5d226f5abdff?w=600', 1),

-- Art Exhibition (Barcelona - ID 1, Arte - ID 3)
('Exposición: El Futuro', 'Experiencia inmersiva futurista.', 1, 'Museu del Disseny', 300, '2026-04-10 10:00:00', 'Exposición', 15.00, '12345678A', 3, 'https://images.unsplash.com/photo-1550684848-fac1c5b4e853?w=600', 1),

-- Food Market (Sevilla - ID 4, Gastronomía - ID 4)
('Gastronomía Sostenible', 'Feria de comida orgánica.', 4, 'Palacio de Congresos', 1000, '2026-05-22 11:00:00', 'Feria', 10.00, '12345678A', 4, 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=600', 1),

-- Theater (Madrid - ID 2, Teatro - ID 6)
('Teatro: Bernarda Alba', 'Adaptación moderna del clásico.', 2, 'Teatro Real', 800, '2026-10-05 20:00:00', 'Teatro', 35.00, '12345678A', 6, 'https://images.unsplash.com/photo-1507676184212-d03ab07a11d0?w=600', 1),

-- Yoga Workshop (Barcelona - ID 1, Deporte - ID 5)
('Yoga al Atardecer', 'Clase magistral al aire libre.', 1, 'Playa de la Barceloneta', 100, '2026-07-12 19:30:00', 'Taller', 12.00, '12345678A', 5, 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=600', 1),

-- Rock Concert (Madrid - ID 2, Música - ID 1)
('Concierto: The Eagles', 'Noche de rock clásico.', 2, 'Wizink Center', 12000, '2026-11-18 21:00:00', 'Concierto', 30.00, '12345678A', 1, 'https://images.unsplash.com/photo-1459749411177-287ce3276916?w=600', 1),

-- Hackathon (Valencia - ID 3, Tech - ID 2)
('Hackathon Universitario', '48 horas de programación.', 3, 'Universidad Politécnica', 200, '2026-02-28 16:00:00', 'Competición', 5.00, '12345678A', 2, 'https://images.unsplash.com/photo-1504384308090-c54be3855091?w=600', 1),

-- Wine Tasting (Barcelona - ID 1, Gastronomía - ID 4)
('Cata de Vinos', 'Cata guiada por sommeliers.', 1, 'Bodega Urbana', 50, '2026-08-01 19:00:00', 'Gastronomía', 40.00, '12345678A', 4, 'https://images.unsplash.com/photo-1559339352-11d035aa65de?w=600', 1),

-- Gaming Tournament (Barcelona - ID 1, Tech - ID 2)
('E-Sports Championship', 'Torneo de LoL y Valorant.', 1, 'Palau Sant Jordi', 15000, '2026-11-05 10:00:00', 'Competición', 25.00, '12345678A', 2, 'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=600', 1);

-- 5. Confirmar cambios
COMMIT;
