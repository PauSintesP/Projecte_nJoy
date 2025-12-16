import requests
import json

url = "http://localhost:8000/register"
data = {
    "nombre": "TestUser",
    "apellidos": "EmailTest",
    "email": "emailtest@example.com",
    "fecha_nacimiento": "2000-01-01",
    "pais": "España",
    "password":  "TestPassword123"
}

print("Sending registration request...")
print(f"Data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
    if hasattr(e, 'response'):
        print(f"Response text: {e.response.text}")
