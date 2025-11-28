from schemas import UsuarioCreate
from datetime import date
import json

# Test data que debería ser válido
test_data = {
    "email": "pausintespaul@gmail.com",
    "password": "DEW0001",
    "nombre": "Pau",
    "apellidos": "Sintes",
    "fecha_nacimiento": "2005-12-12",
    "pais": "Alemania"
}

print("=== Testing UsuarioCreate Schema ===\n")
print("Input data:")
print(json.dumps(test_data, indent=2))
print("\n")

try:
    # Try to create a UsuarioCreate instance
    user = UsuarioCreate(**test_data)
    print("✅ Schema validation PASSED!")
    print("\nValidated user object:")
    print(user.model_dump())
    print("\nJSON representation:")
    print(user.model_dump_json(indent=2))
except Exception as e:
    print(f"❌ Schema validation FAILED!")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Schema Definition ===")
print(json.dumps(UsuarioCreate.model_json_schema(), indent=2))
