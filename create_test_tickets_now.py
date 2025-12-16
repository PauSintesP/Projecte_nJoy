"""
Script para crear tickets de prueba y escanearlos AHORA
"""
import sqlite3
from datetime import datetime
import random
import string

# Connect
conn = sqlite3.connect('njoy_local.db')
cursor = conn.cursor()

# Get the test event (should be the one we created)
cursor.execute("SELECT id, nombre FROM EVENTO ORDER BY id DESC LIMIT 1")
event = cursor.fetchone()

if not event:
    print("⚠️  No hay eventos. Crea un evento primero.")
    exit(1)

evento_id, evento_nombre = event
print(f"📅 Evento encontrado: {evento_nombre} (ID: {evento_id})")

# Get promotor user
cursor.execute("SELECT id FROM USUARIO WHERE email = 'promotor@test.com'")
user = cursor.fetchone()
if not user:
    print("⚠️  Usuario promotor no encontrado")
    exit(1)

usuario_id = user[0]
print(f"👤 Usuario: {usuario_id}")

# Create and scan 5 tickets NOW
now = datetime.now()
current_hour = now.hour
print(f"\n⏰ Hora actual: {current_hour}:00")
print(f"Creando 5 tickets escaneados en la última hora...\n")

for i in range(5):
    # Generate unique code
    codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    # Calculate scan time (spread across last hour)
    minutes_ago = random.randint(0, 59)
    scan_time = now.replace(minute=minutes_ago, second=0, microsecond=0)
    
    # Insert ticket (activado=False means scanned)
    cursor.execute("""
        INSERT INTO TICKET (codigo_ticket, nombre_asistente, evento_id, usuario_id, activado, scanned_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (codigo, f"Asistente {i+1}", evento_id, usuario_id, False, scan_time.isoformat()))
    
    print(f"✅ Ticket {codigo} escaneado a las {scan_time.strftime('%H:%M')}")

conn.commit()
print(f"\n🎉 5 tickets creados y escaneados!")
print(f"Recarga las estadísticas para verlos en el gráfico.")

conn.close()
