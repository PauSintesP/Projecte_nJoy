from database import SessionLocal
from auth import authenticate_user, create_access_token
import models

def get_token():
    db = SessionLocal()
    try:
        user = authenticate_user(db, "admin@njoy.com", "admin123")
        if user:
            token = create_access_token(data={"sub": str(user.id)})
            with open("token.txt", "w") as f:
                f.write(token)
            print(f"Token saved to token.txt")
        else:
            print("Auth failed")
    finally:
        db.close()

if __name__ == "__main__":
    get_token()
