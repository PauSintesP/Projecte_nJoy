from database import SessionLocal
import models

db = SessionLocal()
try:
    print("Checking Users...")
    users = db.query(models.Usuario).all()
    print(f"Found {len(users)} users.")
    for u in users:
        print(f" - {u.email} ({u.role})")
    
    print("Checking Tickets...")
    tickets = db.query(models.Ticket).all()
    print(f"Found {len(tickets)} tickets.")

except Exception as e:
    print(e)
finally:
    db.close()
