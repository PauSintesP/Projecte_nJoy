import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect('njoy_local.db')
cursor = conn.cursor()

# Get all tickets with their scan times
cursor.execute("""
    SELECT id, codigo_ticket, evento_id, activado, scanned_at
    FROM TICKET
    ORDER BY id DESC
    LIMIT 20
""")

print("=" * 80)
print("TICKETS EN LA BASE DE DATOS")
print("=" * 80)

for row in cursor.fetchall():
    ticket_id, codigo, evento_id, activado, scanned_at = row
    print(f"ID: {ticket_id}, Código: {codigo}, Evento: {evento_id}")
    print(f"  Activado: {activado}, Scanned_at: {scanned_at}")
    
    if scanned_at:
        # Parse the datetime
        dt = datetime.fromisoformat(scanned_at.replace(' ', 'T'))
        print(f"  Hora de escaneo: {dt.hour}:00")
    print()

print("=" * 80)
print(f"Current time: {datetime.now()}")
print(f"Current hour: {datetime.now().hour}")

conn.close()
