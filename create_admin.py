"""
Script para crear usuario admin en local
"""
import requests

url = "http://localhost:8000/register"

data = {
    "email": "admin@njoy.com",
    "password": "admin123",
    "nombre": "Admin",
    "apellidos": "Sistema",
    "fecha_nacimiento": "1990-01-01"
}

try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("\n✅ Usuario creado exitosamente!")
        print("\nCredenciales:")
        print("  Email: admin@njoy.com")
        print("  Password: admin123")
except Exception as e:
    print(f"Error: {e}")
