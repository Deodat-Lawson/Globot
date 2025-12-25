"""
Database migration: Add status and updated_at columns to handoffs table
"""
from database import engine
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        # Check if HandoffStatus enum type exists
        print("Checking for HandoffStatus enum type...")
        result = conn.execute(text("""
            SELECT 1 FROM pg_type WHERE typname = 'handoffstatus'
        """))
        enum_exists = result.fetchone() is not None
        
        if not enum_exists:
            print("Creating HandoffStatus enum type...")
            conn.execute(text("""
                CREATE TYPE handoffstatus AS ENUM ('pending', 'processing', 'completed')
            """))
            conn.commit()
            print("✓ HandoffStatus enum created")
        else:
            print("✓ HandoffStatus enum already exists")
        
        # Check if status column exists
        print("\nChecking foratus column...")
        result = conn.execute(text("""
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'handoffs' AND column_name = 'status'
        """))
        status_exists = result.fetchone() is not None
        
        if not status_exists:
            print("Adding status column...")
            conn.execute(text("""
                ALTER TABLE handoffs 
                ADD COLUMN status handoffstatus DEFAULT 'pending'
            """))
            conn.commit()
            print("✓ status column added")
        else:
            print("✓ status column already exists")
        
        # Check if updated_at column exists
        print("\nChecking for updated_at column...")
        result = conn.execute(text("""
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'handoffs' AND column_name = 'updated_at'
        """))
        updated_at_exists = result.fetchone() is not None
        
        if not updated_at_exists:
            print("Adding updated_at column...")
            conn.execute(text("""
                ALTER TABLE handoffs 
                ADD COLUMN updated_at TIMESTAMP DEFAULT NOW()
            """))
            conn.commit()
            print("✓ updated_at column added")
        else:
            print("✓ updated_at column already exists")
        
        print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    migrate()
