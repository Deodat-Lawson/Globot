"""
Database migration: Drop and recreate handoffs table with proper schema
"""
from database import engine, Base
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        # Drop the existing handoffs table
        print("Dropping existing handoffs table...")
        conn.execute(text("DROP TABLE IF EXISTS handoffs CASCADE"))
        conn.commit()
        print("✓ handoffs table dropped")
        
        # Drop the enum type if it exists
        print("\nDropping existing handoffstatus enum...")
        conn.execute(text("DROP TYPE IF EXISTS handoffstatus CASCADE"))
        conn.commit()
        print("✓ handoffstatus enum dropped")
        
    print("\nRecreating tables from models...")
    # Now recreate all tables from models
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully!")
    
    print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    migrate()
