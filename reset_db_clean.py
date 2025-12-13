import os
from datetime import datetime

# Set env vars BEFORE importing other modules
os.environ["DATABASE_URL"] = "sqlite:///./njoy_local.db"
os.environ["ENV"] = "local"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from auth import hash_password
from models import Base, Usuario

# Use the same DB URL
DATABASE_URL = "sqlite:///./njoy_local.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

print("🚨 DROPPING ALL TABLES...")
Base.metadata.drop_all(bind=engine)

print("✨ RECREATING TABLES...")
Base.metadata.create_all(bind=engine)

print("👤 CREATING ADMIN USER...")
admin_user = Usuario(
    nombre="Admin",
    apellidos="System",
    email="admin@njoy.com",
    password=hash_password("1234"),
    role="admin",
    fecha_nacimiento=datetime(1990, 1, 1).date(),
    is_active=True
    # is_verified removed, adding fecha_nacimiento
)

session.add(admin_user)
session.commit()

print("✅ DATABASE RESET COMPLETE!")
print(f"Created Admin: {admin_user.email} / 1234")

session.close()
