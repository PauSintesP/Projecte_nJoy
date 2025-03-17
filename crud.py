from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

def update_item(db: Session, model, item_id: int, update_data: dict):
    db_item = db.query(model).filter(model.id == item_id).first()
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} no encontrado"
        )
    
    # Actualiza automáticamente los atributos que existan en la instancia
    for key, value in update_data.items():
        if hasattr(db_item, key):
            setattr(db_item, key, value)
    
    try:
        db.commit()
        db.refresh(db_item)
        return db_item
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))