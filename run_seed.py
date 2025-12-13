from database import SessionLocal, engine
import models
import seed_data
import sys

def run_seed():
    # Ensure tables exist
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("Seeding database...")
        result = seed_data.seed_database(db)
        print("Database seeded successfully!")
        print(result)
    except Exception as e:
        print(f"Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    run_seed()
