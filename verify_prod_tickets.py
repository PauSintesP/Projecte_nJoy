
import os
import sys
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, SessionLocal
from models import Ticket, Evento, TeamMember, Team, Usuario

# Ensure we can import from current directory
sys.path.append(os.getcwd())

def test_scanner():
    print("--- VERIFICANDO TICKETS EN BDD ---")
    db = SessionLocal()
    try:
        # Get last 5 tickets
        tickets = db.query(Ticket).order_by(Ticket.id.desc()).limit(5).all()
        
        if not tickets:
            print("❌ No se encontraron tickets en la base de datos.")
            return

        print(f"✅ Se encontraron {len(tickets)} tickets recientes.")
        
        valid_ticket = None
        for t in tickets:
            print(f"ID: {t.id} | Código: '{t.codigo_ticket}' | EventoID: {t.evento_id} | Activado: {t.activado}")
            if t.activado: # Prefer testing with an active ticket
                valid_ticket = t
        
        if not valid_ticket:
            valid_ticket = tickets[0] # Fallback to any ticket
            
        print("\n--- PRUEBA DE SCANNER (LIVE) ---")
        target_code = valid_ticket.codigo_ticket
        # Cleaning code if it looks like JSON just in case DB has dirty data (unlikely but possible)
        if target_code.startswith("{"):
             import json
             try:
                 target_code = json.loads(target_code)["codigo"]
             except:
                 pass

        print(f"Probando escaneo para código: {target_code}")
        
        # Test against PROD URL
        url = f"https://projecte-n-joy.vercel.app/tickets/scan/{target_code}"
        
        # We need a token for a valid user (Creator or Admin) to test permissions
        # Since I cannot easily get a valid JWT without login, I will try to login first if possible,
        # or just hit the endpoint and observe the 401/403 vs 404/500 logic.
        
        # Actually, let's just see if it returns 404 (Not Found) or 401 (Unauthorized).
        # If it returns 401/403, it means IT FOUND THE TICKET but denied access (which proves code exists).
        # If it returns 404 (from my logic), then it didn't find the ticket.
        
        print(f"Requesting: {url}")
        # Note: Without Authorization header this will fail with 401 Not Authenticated usually.
        # But specific scanner error 'Ticket no encontrado' is what we want to rule out.
        # However, looking at main.py, 'get_current_active_user' dependency is called first.
        # So we really need a token. 
        
        # Let's try to login as a user if we can find one.
        # Inspecting a user...
        user = db.query(Usuario).filter(Usuario.email.like("%@%")).first()
        if user:
            print(f"Intentando login simulado para usuario: {user.email}")
            # We can't easily login without password.
            pass
            
        response = requests.post(url)
        
        print(f"Status Code: {response.status_code}")
        try:
            print(f"Response Body: {response.json()}")
        except:
            print(f"Response Text: {response.text}")

    except Exception as e:
        print(f"❌ Error verificando DB: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_scanner()
