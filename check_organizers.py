from database import SessionLocal
import models
from sqlalchemy import text

db = SessionLocal()
try:
    print("Checking Organizadores...")
    orgs = db.query(models.Organizador).all()
    print(f"Found {len(orgs)} organizers.")
    for o in orgs:
        print(f" - {o.dni}: {o.ncompleto}")

    print("Checking Eventos...")
    evts = db.query(models.Evento).all()
    print(f"Found {len(evts)} events.")

    # Try force delete
    # print("Force deleting...")
    # db.execute(text('TRUNCATE TABLE "ORGANIZADOR" CASCADE'))
    # db.commit()
    # print("Deleted.")

except Exception as e:
    print(e)
finally:
    db.close()
