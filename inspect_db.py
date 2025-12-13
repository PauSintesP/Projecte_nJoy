import os

# Set env vars BEFORE importing other modules that might use them
os.environ["DATABASE_URL"] = "sqlite:///./njoy_local.db"
os.environ["ENV"] = "local"

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
# Import Base to ensure mappers are registered if needed, though we can query tables directly
from database import Base 
# Dynamically import models to trigger mapper registration
import models 

# Use the same DB URL as the bat file
DATABASE_URL = "sqlite:///./njoy_local.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

print("--- Usuarios ---")
try:
    # Use raw SQL if ORM fails, or try ORM
    users = session.query(models.Usuario).all()
    for u in users:
        print(f"ID: {u.id}, Email: {u.email}, Name: {u.nombre}")
except Exception as e:
    print(f"Error querying users: {e}")

print("\n--- Tickets ---")
try:
    tickets = session.query(models.Ticket).all()
    for t in tickets:
        print(f"ID: {t.id}, EventoID: {t.evento_id}, UserID: {t.usuario_id}, Code: {t.codigo_ticket}")
except Exception as e:
    print(f"Error querying tickets: {e}")

session.close()
