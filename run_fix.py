import requests
import json
import time
import sys

# URL base de producción
BASE_URL = "https://projecte-n-joy.vercel.app"

def run_fix():
    print("Espere mientras se despliega la nueva versión en Vercel...")
    print("Intentando ejecutar la migración de base de datos...")
    
    url = f"{BASE_URL}/fix-db-schema"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Resultado de la migración:")
            print(json.dumps(response.json(), indent=2))
        elif response.status_code == 404:
            print("El endpoint aún no está disponible. Es posible que Vercel aún esté desplegando.")
            # Un pequeño reintento
            return False
        else:
            print("Error inesperado:")
            print(response.text)
            
    except Exception as e:
        print(f"Error de conexión: {e}")
        return False
        
    return True

if __name__ == "__main__":
    # Intentar hasta 5 veces con espera de 10 segundos
    for i in range(10):
        print(f"Intento {i+1}/10...")
        if run_fix():
            print("¡Éxito! Base de datos actualizada.")
            break
        print("Esperando 10 segundos...")
        time.sleep(10)
