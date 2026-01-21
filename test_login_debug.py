import requests
import json

url = "https://projecte-n-joy.vercel.app/login"
headers = {"Content-Type": "application/json"}
data = {
    "email": "test@example.com", 
    "contrasena": "password123" 
}

try:
    print(f"Enviando petición a {url}...")
    response = requests.post(url, json=data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    try:
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
    except:
        print("Response Text:")
        print(response.text)
        
except Exception as e:
    print(f"Error al conectar: {e}")
