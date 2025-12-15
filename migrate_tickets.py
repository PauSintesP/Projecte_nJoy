"""
Script para migrar tickets con UUID a códigos de 6 caracteres
"""
import sqlite3
import random
import string

def generate_short_code():
    """Generate unique 6-character alphanumeric code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Connect to local database
conn = sqlite3.connect('njoy_local.db')
cursor = conn.cursor()

try:
    # Find all tickets with UUID codes (contain dashes)
    cursor.execute("SELECT id, codigo_ticket FROM TICKET WHERE codigo_ticket LIKE '%-%'")
    tickets_to_migrate = cursor.fetchall()
    
    print(f"Encontrados {len(tickets_to_migrate)} tickets con códigos UUID")
    
    migrated = 0
    for ticket_id, old_code in tickets_to_migrate:
        # Generate unique 6-char code
        while True:
            new_code = generate_short_code()
            # Check if unique
            cursor.execute("SELECT id FROM TICKET WHERE codigo_ticket = ?", (new_code,))
            if not cursor.fetchone():
                break
        
        # Update ticket
        cursor.execute("UPDATE TICKET SET codigo_ticket = ? WHERE id = ?", (new_code, ticket_id))
        print(f"  Ticket {ticket_id}: {old_code[:20]}... → {new_code}")
        migrated += 1
    
    conn.commit()
    print(f"\n✅ {migrated} tickets migrados exitosamente!")
    
except Exception as e:
    conn.rollback()
    print(f"❌ Error: {e}")
finally:
    conn.close()
