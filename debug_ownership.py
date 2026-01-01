from sqlalchemy.orm import Session
from database import SessionLocal
import models
import sys

def check_event_ownership(event_id, user_email):
    db = SessionLocal()
    try:
        user = db.query(models.Usuario).filter(models.Usuario.email == user_email).first()
        if not user:
            print(f"User {user_email} not found")
            return

        event = db.query(models.Evento).filter(models.Evento.id == event_id).first()
        if not event:
            print(f"Event {event_id} not found")
            return

        print(f"User ID: {user.id}")
        print(f"Event Creator ID: {event.creador_id}")
        
        if event.creador_id == user.id:
            print("OWNERSHIP CONFIRMED: IDs match.")
        else:
            print("OWNERSHIP MISMATCH: The user is NOT the creator of this event.")

    finally:
        db.close()

if __name__ == "__main__":
    # Check for the last created event or just list some events
    db = SessionLocal()
    events = db.query(models.Evento).all()
    print(f"Total events found: {len(events)}")
    for e in events:
        print(f"Event ID: {e.id}, Name: {e.nombre}, Creator ID: {e.creador_id}")
    
    # Check specifically for the admin user
    check_event_ownership(events[-1].id if events else 1, "pausintespaul@gmail.com")
