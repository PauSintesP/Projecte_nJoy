"""
Script para crear muchos eventos de prueba en la base de datos
para probar la paginación
"""

from database import SessionLocal
from models import Evento, Usuario, Localidad
from datetime import datetime, timedelta
import random

db = SessionLocal()

# Listas de datos variados para generar eventos aleatorios
nombres_eventos = [
    "Festival de Música", "Concierto de Rock", "Noche de Jazz", 
    "Festival Electrónico", "Concierto Acústico", "Opera Night",
    "Party en la Playa", "Fiesta de Verano", "Festival de Arte",
    "Noche de Flamenco", "Concierto Sinfónico", "Tributo a Queen",
    "Reggaeton Night", "Indie Music Fest", "Blues Night",
    "Festival de Hip Hop", "Country Music Show", "Salsa Night",
    "Techno Underground", "House Music Party", "Disco Night",
    "Metal Fest", "Punk Rock Show", "Soul & Funk Night",
    "Acoustic Sessions", "DJ Set Marathon", "Live Band Night",
    "Karaoke Party", "Comedy Show", "Teatro Musical"
]

adjetivos = [
    "Épico", "Increíble", "Legendario", "Memorable", "Fantástico",
    "Espectacular", "Único", "Extraordinario", "Místico", "Eléctrico",
    "Brillante", "Radiante", "Vibrante", "Intenso", "Mágico"
]

años = ["2025", "2026"]
recintos = [
    "Palau Sant Jordi", "Sala Apolo", "Razzmatazz", "Sala Bikini",
    "BARTS", "Luz de Gas", "Jamboree", "Harlem Jazz Club",
    "Teatre Grec", "Parc del Fòrum", "Sala Bóveda", "Shôko Barcelona",
    "Opium Barcelona", "Pacha Barcelona", "Amnesia", "Club Apollo"
]

tipos = ["Concierto", "Festival", "Fiesta", "Show", "Evento Cultural"]

descripciones = [
    "Una experiencia musical inolvidable con los mejores artistas",
    "La mejor noche de música en directo de la ciudad",
    "Un evento único que no te puedes perder",
    "Disfruta de una velada llena de música y diversión",
    "El encuentro perfecto para los amantes de la música",
    "Una celebración de la música y la cultura",
    "Vive la música como nunca antes",
    "Un espectáculo que quedará en tu memoria",
    "La fiesta más esperada del año",
    "Música, diversión y buena compañía garantizadas"
]

imagenes_unsplash = [
    "https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=800",
    "https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=800",
    "https://images.unsplash.com/photo-1511192336575-5a79af67a629?w=800",
    "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800",
    "https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=800",
    "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=800",
    "https://images.unsplash.com/photo-1506157786151-b8491531f063?w=800",
    "https://images.unsplash.com/photo-1540039155733-5bb30b53aa14?w=800",
    "https://images.unsplash.com/photo-1501612780327-45045538702b?w=800",
    "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=800"
]

def create_many_events(count=50):
    """Crear muchos eventos variados"""
    
    print(f"🎉 Creando {count} eventos de prueba...")
    
    # Obtener un promotor o admin para asignar como creador
    promotor = db.query(Usuario).filter(Usuario.role == "promotor").first()
    if not promotor:
        promotor = db.query(Usuario).filter(Usuario.role == "admin").first()
    
    if not promotor:
        print("❌ No se encontró ningún promotor o admin. Por favor, ejecuta seed_test_data.py primero.")
        return
    
    # Intentar obtener Barcelona como localidad
    barcelona = db.query(Localidad).filter(Localidad.ciudad == "Barcelona").first()
    
    eventos_creados = 0
    
    # Fecha inicial (hoy + 1 día)
    fecha_base = datetime.now() + timedelta(days=1)
    
    for i in range(count):
        # Generar nombre aleatorio
        nombre_base = random.choice(nombres_eventos)
        adjetivo = random.choice(adjetivos)
        año = random.choice(años)
        nombre = f"{nombre_base} {adjetivo} {año}"
        
        # Agregar número si ya existe
        numero_version = random.randint(1, 100)
        nombre_final = f"{nombre} #{numero_version}"
        
        # Verificar si ya existe
        existe = db.query(Evento).filter(Evento.nombre == nombre_final).first()
        if existe:
            nombre_final = f"{nombre} V{random.randint(100, 999)}"
        
        # Generar fecha aleatoria (próximos 6 meses)
        dias_adelante = random.randint(1, 180)
        hora = random.randint(18, 23)
        minutos = random.choice([0, 30])
        fecha_evento = fecha_base + timedelta(days=dias_adelante, hours=hora, minutes=minutos)
        
        # Datos aleatorios
        recinto = random.choice(recintos)
        tipo = random.choice(tipos)
        descripcion = random.choice(descripciones)
        imagen = random.choice(imagenes_unsplash)
        precio = round(random.uniform(15.0, 75.0), 2)
        plazas = random.choice([100, 200, 300, 500, 1000, 2000, 5000])
        
        # Crear evento
        nuevo_evento = Evento(
            nombre=nombre_final,
            descripcion=f"{descripcion} - {nombre_final}",
            fechayhora=fecha_evento,
            recinto=recinto,
            precio=precio,
            plazas=plazas,
            tipo=tipo,
            imagen=imagen,
            localidad_id=barcelona.id if barcelona else None
        )
        
        db.add(nuevo_evento)
        eventos_creados += 1
        
        # Commit cada 10 eventos para no perder todo si falla
        if (i + 1) % 10 == 0:
            db.commit()
            print(f"✅ Creados {i + 1}/{count} eventos...")
    
    # Commit final
    db.commit()
    
    print(f"\n🎊 ¡Completado! Se crearon {eventos_creados} eventos nuevos.")
    print(f"📍 Todos los eventos están asignados a: {barcelona.ciudad if barcelona else 'Sin localidad'}")
    print(f"\n💡 Ahora puedes ver la paginación en: http://localhost:5173/")

if __name__ == "__main__":
    try:
        # Crear 50 eventos por defecto (puedes cambiar este número)
        create_many_events(count=50)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
