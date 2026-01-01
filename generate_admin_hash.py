"""
Generate bcrypt password hash for admin user
"""
import bcrypt

# Generate hash for password "Admin123"
password = "Admin123"
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

print("="*60)
print("ADMIN PASSWORD HASH GENERATOR")
print("="*60)
print(f"Password: {password}")
print(f"Bcrypt Hash: {hashed.decode('utf-8')}")
print("="*60)
print("\nCopy this hash and use it in the SQL script")
