import urllib.request
import json
import urllib.error

BASE_URL = "http://localhost:8000"

def test_create_user():
    # 1. Login
    login_data = {
        "email": "admin@njoy.com",
        "contrasena": "1234"
    }
    
    print("Logging in...")
    try:
        req = urllib.request.Request(
            f"{BASE_URL}/login",
            data=json.dumps(login_data).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
            token = data.get("access_token")
            print(f"Login successful, token: {token[:10]}...")
        
        # 2. Create User
        user_data = {
            "nombre": "Test",
            "apellidos": "User",
            "email": "testuser500@njoy.com",
            "password": "password123",
            "fecha_nacimiento": "2000-01-01",
            "pais": "Spain",
            "role": "user",
            "is_active": True,
            "is_banned": False
        }
        
        print(f"Creating user with data: {json.dumps(user_data, indent=2)}")
        
        req = urllib.request.Request(
            f"{BASE_URL}/admin/users",
            data=json.dumps(user_data).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                 print(f"Create API Response: {response.status}")
                 print(f"Response Body: {response.read().decode('utf-8')}")
        except urllib.error.HTTPError as e:
            print(f"HTTPError: {e.code}")
            print(f"Error Body: {e.read().decode('utf-8')}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_create_user()
