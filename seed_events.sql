-- SAFE SQL SCRIPT (No Transactions)
-- Ejecuta 'ROLLBACK' primero si tienes errores pendientes de ejecuciones anteriores
ROLLBACK;

-- 1. LIMPIEZA TOTAL (TRUNCATE limpia tablas y reinicia contadores si es posible)
-- El CASCADE borrará también los datos en TICKET (y PAGO si está configurado en cascada).
TRUNCATE TABLE "TICKET" CASCADE;
TRUNCATE TABLE "EVENTO" CASCADE;

-- Opcional: Descomenta si quieres limpiar todo (Recomendado para evitar conflictos de IDs)
TRUNCATE TABLE "TEAM_MEMBER" CASCADE;
TRUNCATE TABLE "TEAM" CASCADE;
TRUNCATE TABLE "ORGANIZADOR" CASCADE;
-- TRUNCATE TABLE "USUARIO" CASCADE; -- ¡Cuidado! Esto borra todos los usuarios.

-- 2. ASEGURAR DEPENDENCIAS

-- Generos
INSERT INTO "GENERO" (id, nombre) VALUES 
(1, 'Música'), (2, 'Tecnología'), (3, 'Arte'), (4, 'Gastronomía'), (5, 'Deportes'), (6, 'Teatro')
ON CONFLICT (id) DO NOTHING;

-- Localidades
INSERT INTO "LOCALIDAD" (id, ciudad, latitud, longitud) VALUES 
(1, 'Barcelona', 41.3851, 2.1734),
(2, 'Madrid', 40.4168, -3.7038),
(3, 'Valencia', 39.4699, -0.3763),
(4, 'Sevilla', 37.3891, -5.9845),
(5, 'Bilbao', 43.2630, -2.9350)
ON CONFLICT (id) DO NOTHING;

-- Organizador (DNI ficticio para demos)
INSERT INTO "ORGANIZADOR" (dni, ncompleto, email, telefono, web) VALUES 
('12345678A', 'nJoy Events', 'demo_organizer@njoy.events', '600111222', 'https://njoy.events')
ON CONFLICT (dni) DO NOTHING;

-- Usuario Admin (Para crear los eventos)
-- Si ya existe un usuario con ID 1, lo usaremos. Si no, lo creamos.
INSERT INTO "USUARIO" (id, nombre, apellidos, email, fecha_nacimiento, password, role, is_active, created_at, email_verified) VALUES 
(1, 'Admin', 'nJoy', 'admin_demo@njoy.com', '1995-01-01', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxwKc.6Iym.1Wz0.1', 'admin', TRUE, NOW(), TRUE)
ON CONFLICT (id) DO NOTHING;


-- 3. INSERTAR EVENTOS REALISTAS
-- NOTA: Asegúrate de que los IDs de localidad/genero/usuario coinciden con los de arriba.
INSERT INTO "EVENTO" (nombre, descripcion, localidad_id, recinto, plazas, fechayhora, tipo, precio, organizador_dni, genero_id, imagen, creador_id) VALUES

-- Music Festival
('Primavera Sound 2026', 'El festival de música más grande de Barcelona regresa con un cartel inolvidable. Disfruta de tres días de música indie, rock y pop con artistas internacionales de primer nivel.', 1, 'Parc del Fòrum', 50000, '2026-06-04 18:00:00', 'Festival', 245.00, '12345678A', 1, 'https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?auto=format&fit=crop&w=1080&q=80', 1),

-- Tech Conference
('AI & Future Tech Summit', 'Conferencia líder en innovación tecnológica e inteligencia artificial. Descubre cómo la IA transformará el mundo en los próximos años con ponentes de Google, OpenAI y más.', 2, 'IFEMA Madrid', 2500, '2026-09-15 09:00:00', 'Conferencia', 150.00, '12345678A', 2, 'https://images.unsplash.com/photo-1544531586-fde5298cdd40?auto=format&fit=crop&w=1080&q=80', 1),

-- Jazz Concert
('Noche de Jazz en el Palau', 'Una velada íntima con lo mejor del jazz contemporáneo en un entorno arquitectónico único. Incluye copa de bienvenida.', 1, 'Palau de la Música', 500, '2026-03-20 21:00:00', 'Concierto', 45.00, '12345678A', 1, 'https://images.unsplash.com/photo-1511192336575-5a79af67a629?auto=format&fit=crop&w=1080&q=80', 1),

-- Sports - Marathon
('Maratón de Valencia', 'Participa en una de las maratones más rápidas del mundo. Recorre las calles de Valencia en un evento deportivo sin igual, con miles de corredores internacionales.', 3, 'Ciudad de las Artes', 20000, '2026-12-06 08:30:00', 'Deporte', 60.00, '12345678A', 5, 'https://images.unsplash.com/photo-1552674605-5d226f5abdff?auto=format&fit=crop&w=1080&q=80', 1),

-- Art Exhibition
('Exposición: El Futuro Digital', 'Una experiencia inmersiva que explora cómo la tecnología transformará nuestras vidas. Instalaciones interactivas de luz y sonido.', 1, 'Museu del Disseny', 300, '2026-04-10 10:00:00', 'Exposición', 15.00, '12345678A', 3, 'https://images.unsplash.com/photo-1550684848-fac1c5b4e853?auto=format&fit=crop&w=1080&q=80', 1),

-- Food Market
('Gastronomía Sostenible', 'Feria de comida orgánica y sostenible. Degustaciones de chefs locales, talleres de cocina y venta de productos de proximidad.', 4, 'Palacio de Congresos', 1000, '2026-05-22 11:00:00', 'Feria', 10.00, '12345678A', 4, 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?auto=format&fit=crop&w=1080&q=80', 1),

-- Theater
('Teatro: La Casa de Bernarda Alba', 'Adaptación moderna del clásico de Lorca. Una visión fresca y conmovedora sobre la libertad y la represión en la sociedad actual.', 2, 'Teatro Real', 800, '2026-10-05 20:00:00', 'Teatro', 35.00, '12345678A', 6, 'https://images.unsplash.com/photo-1507676184212-d03ab07a11d0?auto=format&fit=crop&w=1080&q=80', 1),

-- Yoga Workshop
('Yoga al Atardecer', 'Clase magistral de yoga al aire libre frente al mar. Conecta cuerpo y mente mientras se pone el sol en la playa de la Barceloneta.', 1, 'Playa de la Barceloneta', 100, '2026-07-12 19:30:00', 'Taller', 12.00, '12345678A', 5, 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=1080&q=80', 1),

-- Rock Concert
('Concierto: The Eagles Legacy', 'La banda tributo más importante del mundo regresa para una noche de rock clásico. No te pierdas los himnos que marcaron una generación.', 2, 'Wizink Center', 12000, '2026-11-18 21:00:00', 'Concierto', 30.00, '12345678A', 1, 'https://images.unsplash.com/photo-1459749411177-287ce3276916?auto=format&fit=crop&w=1080&q=80', 1),

-- Hackathon
('Hackathon Universitario', '48 horas de programación, creatividad y café. Compite por premios increíbles y conoce a las mejores empresas del sector tecnológico.', 3, 'Universidad Politécnica', 200, '2026-02-28 16:00:00', 'Competición', 5.00, '12345678A', 2, 'https://images.unsplash.com/photo-1504384308090-c54be3855091?auto=format&fit=crop&w=1080&q=80', 1),

-- Wine Tasting
('Cata de Vinos', 'Descubre los mejores vinos de la región en una cata guiada por sommeliers expertos. Incluye maridaje con quesos artesanales.', 1, 'Bodega Urbana', 50, '2026-08-01 19:00:00', 'Gastronomía', 40.00, '12345678A', 4, 'https://images.unsplash.com/photo-1559339352-11d035aa65de?auto=format&fit=crop&w=1080&q=80', 1),

-- Gaming Tournament
('E-Sports Championship', 'Torneo nacional de League of Legends y Valorant. Ven a ver a los mejores equipos competir en directo en pantalla gigante.', 1, 'Palau Sant Jordi', 15000, '2026-11-05 10:00:00', 'Competición', 25.00, '12345678A', 2, 'https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=1080&q=80', 1);
