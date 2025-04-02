from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from typing import List

import crud
import schemas
from database import get_db

router = APIRouter()

# Variable global para almacenar el estado de los usuarios autenticados
authenticated_users = {}

@router.post("/login")
def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Login with email and password
    """
    user = crud.authenticate_user(db, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Almacenar el usuario autenticado en la variable global
    authenticated_users[user.id] = user
    return {"message": "Login successful", "user_id": user.id, "email": user.email}

@router.post("/logout")
def logout(user_id: int):
    """
    Logout a user by removing them from the authenticated users
    """
    if user_id in authenticated_users:
        del authenticated_users[user_id]
        return {"message": "Logout successful"}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="User not logged in"
    )

def get_current_user(user_id: int):
    """
    Retrieve the currently authenticated user
    """
    user = authenticated_users.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not logged in"
        )
    return user

# User Registration Endpoint (No changes made)
@router.post("/register", response_model=schemas.UsuarioResponse)
def register_user(user: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    return crud.create_user(db=db, user=user)

# Update User Profile
@router.put("/{user_id}", response_model=schemas.UsuarioResponse)
def update_user(
    user_id: int, 
    user: schemas.UsuarioCreate, 
    db: Session = Depends(get_db),
    current_user_id: int = Form(...)
):
    """
    Update a user's profile (authenticated users only)
    """
    # Ensure user can only update their own profile
    current_user = get_current_user(current_user_id)
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    return crud.update_user(db=db, user_id=user_id, user=user)