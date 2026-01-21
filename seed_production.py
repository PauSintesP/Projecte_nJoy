"""
Script SIMPLE para insertar eventos en Neon DB
"""
import os
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_eLdcSE4BHz5s@ep-nameless-cell-a4qzkz8e-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require'

from sqlalchemy import create_engine, text

engine = create_engine(os.environ['DATABASE_URL'])

with engine.connect() as conn:
    print("🔗 Conectado a Neon DB...")
    
    # 1. Limpiar
    print("🧹 Limpiando...")
    conn.execute(text('DELETE FROM "TICKET"'))
    conn.execute(text('DELETE FROM "EVENTO"'))
    conn.commit()
    
    # 2. Obtener un usuario existente para creador_id
    result = conn.execute(text('SELECT id FROM "USUARIO" LIMIT 1'))
    row = result.fetchone()
    creador_id = row[0] if row else None
    print(f"📌 Usando creador_id: {creador_id}")
    
    # 3. Asegurar dependencias básicas
    conn.execute(text('''
        INSERT INTO "GENERO" (id, nombre) VALUES 
        (1, 'Música'), (2, 'Tecnología'), (3, 'Arte'), (4, 'Gastronomía'), (5, 'Deportes'), (6, 'Teatro')
        ON CONFLICT (id) DO UPDATE SET nombre = EXCLUDED.nombre
    '''))
    
    conn.execute(text('''
        INSERT INTO "LOCALIDAD" (id, ciudad) VALUES 
        (1, 'Barcelona'), (2, 'Madrid'), (3, 'Valencia'), (4, 'Sevilla'), (5, 'Bilbao')
        ON CONFLICT (id) DO UPDATE SET ciudad = EXCLUDED.ciudad
    '''))
    
    conn.execute(text('''
        INSERT INTO "ORGANIZADOR" (dni, ncompleto, email, telefono, web) VALUES 
        ('12345678A', 'nJoy Events', 'events@njoy.com', '600111222', 'https://njoy.events')
        ON CONFLICT (dni) DO NOTHING
    '''))
    conn.commit()
    
    # 4. Insertar eventos (SIN creador_id si es NULL, CON creador_id si existe)
    print("🎉 Insertando eventos...")
    
    eventos_sql = """
    INSERT INTO "EVENTO" (nombre, descripcion, localidad_id, recinto, plazas, fechayhora, tipo, precio, organizador_dni, genero_id, imagen) VALUES
    ('Primavera Sound 2026', 'El festival de música más grande de Barcelona vuelve con un cartel increíble.', 1, 'Parc del Fòrum', 50000, '2026-06-04 18:00:00', 'Festival', 245.00, '12345678A', 1, 'https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=400'),
    ('AI & Future Tech Summit', 'Conferencia líder en inteligencia artificial y tecnología.', 2, 'IFEMA Madrid', 2500, '2026-09-15 09:00:00', 'Conferencia', 150.00, '12345678A', 2, 'https://images.unsplash.com/photo-1544531586-fde5298cdd40?w=400'),
    ('Noche de Jazz', 'Velada íntima con lo mejor del jazz contemporáneo.', 1, 'Palau de la Música', 500, '2026-03-20 21:00:00', 'Concierto', 45.00, '12345678A', 1, 'https://images.unsplash.com/photo-1511192336575-5a79af67a629?w=400'),
    ('Maratón de Valencia', 'Una de las maratones más rápidas del mundo.', 3, 'Ciudad de las Artes', 20000, '2026-12-06 08:30:00', 'Deporte', 60.00, '12345678A', 5, 'https://images.unsplash.com/photo-1552674605-5d226f5abdff?w=400'),
    ('Exposición Digital', 'Experiencia inmersiva de arte y tecnología futurista.', 1, 'Museu del Disseny', 300, '2026-04-10 10:00:00', 'Exposición', 15.00, '12345678A', 3, 'https://images.unsplash.com/photo-1550684848-fac1c5b4e853?w=400'),
    ('Gastronomía Sostenible', 'Feria de comida orgánica con los mejores chefs.', 4, 'Palacio de Congresos', 1000, '2026-05-22 11:00:00', 'Feria', 10.00, '12345678A', 4, 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=400'),
    ('Teatro Bernarda Alba', 'Adaptación moderna del clásico de Federico García Lorca.', 2, 'Teatro Real', 800, '2026-10-05 20:00:00', 'Teatro', 35.00, '12345678A', 6, 'https://images.unsplash.com/photo-1507676184212-d03ab07a11d0?w=400'),
    ('Yoga al Atardecer', 'Clase magistral de yoga frente al mar mediterráneo.', 1, 'Playa Barceloneta', 100, '2026-07-12 19:30:00', 'Taller', 12.00, '12345678A', 5, 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=400'),
    ('Rock Legends Live', 'Noche épica de rock clásico con bandas tributo.', 2, 'Wizink Center', 12000, '2026-11-18 21:00:00', 'Concierto', 30.00, '12345678A', 1, 'https://images.unsplash.com/photo-1459749411177-287ce3276916?w=400'),
    ('Hackathon 2026', '48 horas de programación, creatividad y premios increíbles.', 3, 'UPV Campus', 200, '2026-02-28 16:00:00', 'Competición', 5.00, '12345678A', 2, 'https://images.unsplash.com/photo-1504384308090-c54be3855091?w=400'),
    ('Cata de Vinos Premium', 'Degustación exclusiva guiada por sommeliers expertos.', 1, 'Bodega Urbana', 50, '2026-08-01 19:00:00', 'Gastronomía', 40.00, '12345678A', 4, 'https://images.unsplash.com/photo-1559339352-11d035aa65de?w=400'),
    ('E-Sports Championship', 'Torneo nacional de League of Legends y Valorant.', 1, 'Palau Sant Jordi', 15000, '2026-11-05 10:00:00', 'Competición', 25.00, '12345678A', 2, 'https://images.unsplash.com/photo-1542751371-adc38448a05e?w=400')
    """
    
    conn.execute(text(eventos_sql))
    conn.commit()
    
    # 5. Verificar
    result = conn.execute(text('SELECT COUNT(*) FROM "EVENTO"'))
    count = result.scalar()
    print(f"\n🎊 ¡Completado! {count} eventos insertados.")

print("✨ ¡Listo! Recarga https://web-njoy.vercel.app/ para ver los eventos.")
