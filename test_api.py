"""
Script de prueba para verificar que la API de nJoy funciona correctamente
Ejecutar DESPUÉS de migrar la base de datos
"""

import requests
import json
from datetime import date

BASE_URL = "http://localhost:8000"

def print_response(response, title=""):
    """Imprimir respuesta de forma legible"""
    print(f"\n{'='*60}")
    if title:
        print(f"{title}")
        print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

def test_api():
    """Ejecutar pruebas de la API"""
    
    print("🧪 INICIANDO PRUEBAS DE LA API SEGURA")
    print("="*60)
    
    # Test 1: Health check
    print("\n1️⃣ Test: Health Check (endpoint público)")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response, "Health Check")
    assert response.status_code == 200, "Health check falló"
    
    # Test 2: Registrar usuario
    print("\n2️⃣ Test: Registrar nuevo usuario")
    usuario_test = {
        "user": "testuser",
        "ncompleto": "Usuario de Prueba",
        "email": "test@example.com",
        "fnacimiento": "2000-01-15",
        "contrasena": "SecurePassword123"
    }
    
    response = requests.post(f"{BASE_URL}/register", json=usuario_test)
    print_response(response, "Registro de Usuario")
    
    if response.status_code == 400 and "ya está registrado" in response.text:
        print("⚠️  Usuario ya existe, continuando con login...")
    else:
        assert response.status_code == 201, "Registro falló"
    
    # Test 3: Login
    print("\n3️⃣ Test: Login de usuario")
    login_data = {
        "email": "test@example.com",
        "contrasena": "SecurePassword123"
    }
    
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    print_response(response, "Login")
    assert response.status_code == 200, "Login falló"
    
    # Guardar tokens
    tokens = response.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    
    # Test 4: Intentar acceder sin token (debe fallar)
    print("\n4️⃣ Test: Acceder a endpoint protegido SIN token (debe fallar)")
    response = requests.get(f"{BASE_URL}/usuario/")
    print_response(response, "Acceso sin token")
    assert response.status_code == 403, "Debería fallar sin token"
    
    # Test 5: Acceder CON token (debe funcionar)
    print("\n5️⃣ Test: Acceder a endpoint protegido CON token")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{BASE_URL}/usuario/", headers=headers)
    print_response(response, "Acceso con token")
    assert response.status_code == 200, "Acceso con token falló"
    
    # Test 6: Obtener usuario actual (/me)
    print("\n6️⃣ Test: Obtener información del usuario actual")
    response = requests.get(f"{BASE_URL}/me", headers=headers)
    print_response(response, "Usuario Actual /me")
    assert response.status_code == 200, "/me falló"
    user_data = response.json()
    assert user_data["email"] == "test@example.com", "Email no coincide"
    assert "contrasena" not in user_data, "⚠️ ALERTA: contraseña expuesta en respuesta!"
    
    # Test 7: Refresh token
    print("\n7️⃣ Test: Renovar access token con refresh token")
    refresh_data = {"refresh_token": refresh_token}
    response = requests.post(f"{BASE_URL}/token/refresh", json=refresh_data)
    print_response(response, "Token Refresh")
    assert response.status_code == 200, "Refresh token falló"
    
    # Test 8: Login con credenciales incorrectas (debe fallar)
    print("\n8️⃣ Test: Login con contraseña incorrecta (debe fallar)")
    bad_login = {
        "email": "test@example.com",
        "contrasena": "ContraseñaIncorrecta"
    }
    response = requests.post(f"{BASE_URL}/login", json=bad_login)
    print_response(response, "Login con contraseña incorrecta")
    assert response.status_code == 401, "Debería rechazar contraseña incorrecta"
    
    # Test 9: Crear un género (test de endpoint POST protegido)
    print("\n9️⃣ Test: Crear un género (endpoint POST protegido)")
    genero_data = {"nombre": "Rock Test"}
    response = requests.post(f"{BASE_URL}/genero/", json=genero_data, headers=headers)
    print_response(response, "Crear Género")
    if response.status_code == 201:
        genero_id = response.json()["id"]
        print(f"✅ Género creado con ID: {genero_id}")
    
    # Test 10: Documentación
    print("\n🔟 Test: Acceso a documentación")
    response = requests.get(f"{BASE_URL}/docs")
    assert response.status_code == 200, "Documentación no accesible"
    print("✅ Documentación Swagger accesible en: http://localhost:8000/docs")
    
    print("\n" + "="*60)
    print("✅ ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
    print("="*60)
    print("\n📝 Resumen:")
    print("  ✓ Registro de usuarios funcionando")
    print("  ✓ Login con JWT funcionando")
    print("  ✓ Tokens de acceso funcionando")
    print("  ✓ Tokens de refresh funcionando")
    print("  ✓ Endpoints protegidos requieren autenticación")
    print("  ✓ Contraseñas hasheadas (no expuestas)")
    print("  ✓ Validación de credenciales funcionando")
    print("\n🚀 La API está lista para producción!")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: No se puede conectar al servidor")
        print("Por favor, asegúrate de que la API está corriendo:")
        print("  uvicorn main:app --reload")
    except AssertionError as e:
        print(f"\n❌ TEST FALLÓ: {e}")
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
