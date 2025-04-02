from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://admin:yXtYxQQS8YW2my2bb9SK@njoy-rds.cf0sio0i6581.us-east-1.rds.amazonaws.com/BBDDJoy"


engine = create_engine(
    DATABASE_URL,
    connect_args={"init_command": "SET NAMES 'utf8mb4' COLLATE 'utf8mb4_general_ci'"},
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_timeout=10
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()