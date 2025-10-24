"""
Clear ISO standards from the database
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database.database import SessionLocal
from backend.models.iso_models import ISOStandard, ISOClause

def clear_iso_database():
    db = SessionLocal()
    
    try:
        # Count existing records
        standards_count = db.query(ISOStandard).count()
        clauses_count = db.query(ISOClause).count()
        
        print(f"\n{'='*80}")
        print(f"Current database state:")
        print(f"  - ISO Standards: {standards_count}")
        print(f"  - ISO Clauses: {clauses_count}")
        print(f"{'='*80}\n")
        
        if standards_count == 0:
            print("Database is already empty!")
            return
        
        # List standards before deletion
        standards = db.query(ISOStandard).all()
        print("Standards to be deleted:")
        for std in standards:
            print(f"  - {std.name} ({std.iso_number}:{std.year}) - {len(std.clauses)} clauses")
        
        print(f"\nDeleting {clauses_count} clauses...")
        db.query(ISOClause).delete()
        
        print(f"Deleting {standards_count} standards...")
        db.query(ISOStandard).delete()
        
        db.commit()
        
        print(f"\n{'='*80}")
        print(f"✓ Database cleared successfully!")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"\n✗ Error clearing database: {e}")
        db.rollback()
        
    finally:
        db.close()

if __name__ == "__main__":
    clear_iso_database()
