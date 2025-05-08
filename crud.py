from sqlalchemy.orm import Session
import models, schemas

def login_user(db: Session, email: str, contrasena: str):
    return db.query(models.Usuario).filter_by(email=email, contrasena=contrasena).first()

def create_item(db: Session, model, schema):
    db_item = model(**schema.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_items(db: Session, model):
    return db.query(model).all()

def get_item(db: Session, model, item_id: int):
    return db.query(model).filter_by(id=item_id).first()

def update_item(db: Session, model, item_id: int, schema):
    db_item = db.query(model).filter_by(id=item_id).first()
    for key, value in schema.dict(exclude_unset=True).items():
        setattr(db_item, key, value)
    db.commit()
    return db_item

def delete_item(db: Session, model, item_id: int):
    db_item = db.query(model).filter_by(id=item_id).first()
    db.delete(db_item)
    db.commit()
    return db_item
