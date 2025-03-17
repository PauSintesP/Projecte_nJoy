from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import crud
import models
import schemas
from database import get_db
from datetime import datetime, timedelta
from crud import create_user
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Router configuration
router = APIRouter()


# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    """
    Create a JWT access token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Get the current authenticated user from the token
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user = crud.get_user_by_username(db, username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

# User Registration Endpoint
@router.post("/register", response_model=schemas.UsuarioResponse)
def register_user(user: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    return crud.create_user(db=db, user=user)

# User Login Endpoint
@router.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """
    Generate an access token for authentication
    """
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token = create_access_token(data={"sub": user.user})
    return {"access_token": access_token, "token_type": "bearer"}

# Get Current User Profile
@router.get("/me", response_model=schemas.UsuarioResponse)
def read_users_me(current_user: models.Usuario = Depends(get_current_user)):
    """
    Get the current authenticated user's profile
    """
    return current_user

# Get User by ID (Requires Authentication)
@router.get("/{user_id}", response_model=schemas.UsuarioResponse)
def read_user(
    user_id: int, 
    db: Session = Depends(get_db), 
   
):
    """
    Get a specific user by ID (authenticated users only)
    """
    return crud.get_user(db, user_id)

# List Users (Requires Authentication)
@router.get("/", response_model=List[schemas.UsuarioResponse])
def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
   
):
    """
    List users with pagination (authenticated users only)
    """
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

# Update User Profile
@router.put("/{user_id}", response_model=schemas.UsuarioResponse)
def update_user(
    user_id: int, 
    user: schemas.UsuarioCreate, 
    db: Session = Depends(get_db),
   
):
    """
    Update a user's profile (authenticated users only)
    """
    # Ensure user can only update their own profile
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    return crud.update_user(db=db, user_id=user_id, user=user)

# Delete User
@router.delete("/{user_id}")
def delete_user(
    user_id: int, 
    db: Session = Depends(get_db),
   
):
    """
    Delete a user (authenticated users only)
    """
    # Ensure user can only delete their own profile
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user"
        )
    return crud.delete_user(db=db, user_id=user_id)