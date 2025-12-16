"""
Migration: Add email verification fields to Usuario table
Adds: email_verified, verification_token, verification_token_expiry
"""
import sqlite3
from pathlib import Path

def add_verification_fields():
    """Add email verification fields to USUARIO table"""
    print("=" * 60)
    print("  MIGRATION: Adding Email Verification Fields")
    print("=" * 60)
    
    # Connect to SQLite database
    db_path = Path(__file__).parent / "njoy_local.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Create the new columns using raw SQL
        print("\n1. Adding email_verified column...")
        cursor.execute("""
            ALTER TABLE USUARIO 
            ADD COLUMN email_verified BOOLEAN DEFAULT 0 NOT NULL
        """)
        
        print("2. Adding verification_token column...")
        cursor.execute("""
            ALTER TABLE USUARIO 
            ADD COLUMN verification_token VARCHAR(255)
        """)
        
        print("3. Adding verification_token_expiry column...")
        cursor.execute("""
            ALTER TABLE USUARIO 
            ADD COLUMN verification_token_expiry DATETIME
        """)
        
        conn.commit()
        print("\n✓ Columns added successfully!")
        
        # Mark existing users as verified (since they're test users)
        print("\n4. Marking existing users as verified...")
        cursor.execute("""
            UPDATE USUARIO 
            SET email_verified = 1 
            WHERE email_verified = 0 OR email_verified IS NULL
        """)
        conn.commit()
        
        affected = cursor.rowcount
        print(f"✓ Marked {affected} existing users as verified\n")
        
        print("=" * 60)
        print("  ✓ MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print(f"\n  NOTE: Columns already exist - skipping")
            print("        This is expected if migration was already run.")
        else:
            print(f"\n✗ Error during migration: {e}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    add_verification_fields()
