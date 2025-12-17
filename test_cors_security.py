"""
Test CORS Security - Verificar que solo dominios autorizados puedan acceder
"""
import requests

API_BASE = "http://localhost:8000"

def test_unauthorized_origin():
    """Test que un origen no autorizado sea rechazado con 403"""
    print("🔍 Test 1: Origen NO autorizado (debe ser bloqueado)")
    print("-" * 60)
    
    headers = {'Origin': 'https://malicious-site.com'}
    
    try:
        response = requests.get(f'{API_BASE}/', headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 403:
            print("✅ PASS: Origen bloqueado correctamente (403 Forbidden)")
        else:
            print(f"❌ FAIL: Esperaba 403, recibió {response.status_code}")
            
        print(f"Response: {response.json()}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print()

def test_authorized_origin():
    """Test que un origen autorizado sea aceptado"""
    print("🔍 Test 2: Origen autorizado (debe ser aceptado)")
    print("-" * 60)
    
    headers = {'Origin': 'http://localhost:5173'}
    
    try:
        response = requests.get(f'{API_BASE}/', headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ PASS: Origen autorizado correctamente (200 OK)")
        else:
            print(f"⚠️  WARNING: Status inesperado {response.status_code}")
            
        cors_header = response.headers.get('Access-Control-Allow-Origin')
        print(f"Access-Control-Allow-Origin: {cors_header}")
        
        if cors_header == 'http://localhost:5173':
            print("✅ PASS: Header CORS correcto")
        else:
            print(f"❌ FAIL: Header CORS incorrecto: {cors_header}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print()

def test_production_origin():
    """Test que el dominio de producción sea aceptado"""
    print("🔍 Test 3: Dominio de producción (debe ser aceptado)")
    print("-" * 60)
    
    headers = {'Origin': 'https://web-njoy.vercel.app'}
    
    try:
        response = requests.get(f'{API_BASE}/', headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ PASS: Dominio de producción autorizado (200 OK)")
        else:
            print(f"⚠️  WARNING: Status inesperado {response.status_code}")
            
        cors_header = response.headers.get('Access-Control-Allow-Origin')
        print(f"Access-Control-Allow-Origin: {cors_header}")
        
        if cors_header == 'https://web-njoy.vercel.app':
            print("✅ PASS: Header CORS correcto")
        else:
            print(f"❌ FAIL: Header CORS incorrecto: {cors_header}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print()

def test_preview_vercel_blocked():
    """Test que subdominios de Vercel NO autorizados sean bloqueados"""
    print("🔍 Test 4: Preview deployment de Vercel (debe ser bloqueado)")
    print("-" * 60)
    
    headers = {'Origin': 'https://web-njoy-git-feature-branch.vercel.app'}
    
    try:
        response = requests.get(f'{API_BASE}/', headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 403:
            print("✅ PASS: Preview deployment bloqueado correctamente")
        else:
            print(f"❌ FAIL: Preview deployment NO fue bloqueado (recibió {response.status_code})")
            
        print(f"Response: {response.json()}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print()

def test_no_origin_header():
    """Test que peticiones sin Origin (como apps móviles) sean aceptadas"""
    print("🔍 Test 5: Sin header Origin - App móvil (debe ser aceptado)")
    print("-" * 60)
    
    try:
        response = requests.get(f'{API_BASE}/')
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ PASS: Request sin Origin aceptado (compatible con móvil)")
        else:
            print(f"❌ FAIL: Request sin Origin rechazado")
            
        cors_header = response.headers.get('Access-Control-Allow-Origin')
        print(f"Access-Control-Allow-Origin: {cors_header or '(no header)'}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🔒 PRUEBAS DE SEGURIDAD CORS - nJoy API")
    print("=" * 60 + "\n")
    
    print("⚠️  IMPORTANTE: Asegúrate de que el servidor esté corriendo:")
    print("   cd c:\\Users\\pausi\\Documents\\Projectes Pau\\Projecte_nJoy")
    print("   python -m uvicorn main:app --reload")
    print("\n" + "=" * 60 + "\n")
    
    test_unauthorized_origin()
    test_authorized_origin()
    test_production_origin()
    test_preview_vercel_blocked()
    test_no_origin_header()
    
    print("=" * 60)
    print("✅ Tests completados")
    print("=" * 60)
