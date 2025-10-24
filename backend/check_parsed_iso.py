"""
Simple script to check what was parsed from uploaded ISO documents
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database.database import SessionLocal
from backend.models.iso_models import ISOStandard, ISOClause

def check_parsed_standards():
    db = SessionLocal()
    
    try:
        standards = db.query(ISOStandard).all()
        print(f"\n{'='*80}")
        print(f"Found {len(standards)} ISO standard(s) in database")
        print(f"{'='*80}\n")
        
        for idx, std in enumerate(standards, 1):
            print(f"\n[{idx}] {std.name}")
            print(f"    ISO Number: {std.iso_number}")
            print(f"    Year: {std.year}")
            print(f"    Category: {std.category}")
            print(f"    Title: {std.full_title}")
            print(f"    Description: {std.description}")
            print(f"    Total Clauses: {len(std.clauses)}")
            print(f"    Active: {std.is_active}")
            print(f"    Imported: {std.imported_at}")
            
            # Show first 15 clauses
            print(f"\n    First 15 Clauses:")
            print(f"    {'-'*76}")
            for clause in std.clauses[:15]:
                title_preview = clause.title[:60] if clause.title else "No title"
                content_preview = clause.content[:40] if clause.content else "No content"
                mandatory = "✓ MANDATORY" if clause.is_mandatory else ""
                print(f"    {clause.clause_number:8} | {title_preview:60} | {mandatory}")
            
            if len(std.clauses) > 15:
                print(f"    ... and {len(std.clauses) - 15} more clauses")
            
            # Show some example clause content
            if std.clauses:
                print(f"\n    Example Clause Content (Clause {std.clauses[0].clause_number}):")
                print(f"    {'-'*76}")
                content = std.clauses[0].content[:300] if std.clauses[0].content else "No content"
                print(f"    {content}...")
        
        print(f"\n{'='*80}\n")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_parsed_standards()
