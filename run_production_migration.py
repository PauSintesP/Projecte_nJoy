"""
Migration script to update production database schema
Adds missing columns that were added to models but not yet migrated to production
"""
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

# Load PRODUCTION environment variables
env_file = os.path.join(os.path.dirname(__file__), '.env.production')
if not os.path.exists(env_file):
    print(f"❌ ERROR: {env_file} not found!")
    print("Please create .env.production with your production DATABASE_URL")
    exit(1)

load_dotenv(env_file)
print(f"✅ Loaded environment from: {env_file}")

def run_migration():
    """Execute the migration SQL script on production database"""
    
    # Get production database URL from environment
    database_url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")
    
    if not database_url:
        print("❌ ERROR: No DATABASE_URL or POSTGRES_URL found in .env.production")
        print("Available environment variables:")
        for key in sorted(os.environ.keys()):
            if 'URL' in key or 'POSTGRES' in key or 'DATABASE' in key:
                print(f"  {key}: {os.environ[key][:50]}...")
        return False
    
    # Clean up the database URL
    database_url = database_url.strip()
    
    # Convert postgres:// to postgresql:// if needed
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    print("="*60)
    print("🔧 PRODUCTION DATABASE MIGRATION")
    print("="*60)
    print(f"Database URL (first 50 chars): {database_url[:50]}...")
    print(f"URL starts with: {database_url.split('://')[0]}://")
    print()
    
    # Read migration SQL
    script_path = os.path.join(os.path.dirname(__file__), "migrate_production_db.sql")
    with open(script_path, 'r', encoding='utf-8') as f:
        migration_sql = f.read()
    
    try:
        # Connect to database
        print("📡 Connecting to production database...")
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✅ Connected successfully")
        print()
        print("🚀 Executing migration...")
        print("-"*60)
        
        # Execute migration
        cursor.execute(migration_sql)
        
        # Fetch all results to see the NOTICE messages
        if cursor.description:
            results = cursor.fetchall()
            for row in results:
                print(row)
        
        print("-"*60)
        print()
        print("✅ Migration completed successfully!")
        print()
        print("📊 Verifying column additions...")
        
        # Verify TICKET table
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'TICKET'
            ORDER BY ordinal_position
        """)
        
        print("\n📋 TICKET table columns:")
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]} (nullable: {row[2]})")
        
        # Verify USUARIO table
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'USUARIO'
            ORDER BY ordinal_position
        """)
        
        print("\n📋 USUARIO table columns:")
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]} (nullable: {row[2]})")
        
        cursor.close()
        conn.close()
        
        print()
        print("="*60)
        print("✅ MIGRATION SUCCESSFUL - Database schema updated")
        print("="*60)
        return True
        
    except Exception as e:
        print()
        print("="*60)
        print("❌ MIGRATION FAILED")
        print("="*60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_migration()
    exit(0 if success else 1)
