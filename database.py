from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mariadb+mariadbconnector://root:1234@localhost/BBDDJoy"

engine = create_engine(
    DATABASE_URL,
    connect_args={"init_command": "SET NAMES 'utf8mb4' COLLATE 'utf8mb4_general_ci'"}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()