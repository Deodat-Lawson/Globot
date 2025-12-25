from database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
columns = inspector.get_columns('handoffs')

print("Handoffs table columns:")
for col in columns:
    print(f"  - {col['name']}: {col['type']}")
    
# Check for required columns
required_cols = ['status', 'updated_at']
existing_cols = [c ['name'] for c in columns]

print("\nChecking required columns:")
for col_name in required_cols:
    if col_name in existing_cols:
        print(f"  ✓ {col_name} exists")
    else:
        print(f"  ✗ {col_name} MISSING!")
