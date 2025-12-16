"""
Migration script to add scanned_at column to TICKET table
This allows tracking when tickets are validated for hourly entry statistics
"""
import sqlite3
import os
from datetime import datetime

def run_migration():
    """Add scanned_at column to TICKET table"""
    
    # Database path
    db_path = os.path.join(os.path.dirname(__file__), 'njoy_local.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(TICKET)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'scanned_at' in columns:
            print("✅ Column 'scanned_at' already exists in TICKET table")
            return True
        
        # Add the column
        print("📝 Adding 'scanned_at' column to TICKET table...")
        cursor.execute("""
            ALTER TABLE TICKET
            ADD COLUMN scanned_at DATETIME NULL
        """)
        
        conn.commit()
        print("✅ Migration completed successfully!")
        print("   - Added 'scanned_at' column to TICKET table")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(TICKET)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'scanned_at' in columns:
            print("✅ Verification passed: Column exists in database")
        else:
            print("❌ Verification failed: Column not found")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("\n" + "="*50)
    print("  TICKET TABLE MIGRATION")
    print("  Adding scanned_at column")
    print("="*50 + "\n")
    
    success = run_migration()
    
    if success:
        print("\n✅ Migration completed successfully!")
    else:
        print("\n❌ Migration failed!")
    
    print("\n" + "="*50 + "\n")
