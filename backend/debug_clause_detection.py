"""
Debug tool to see exact clause detection issues
"""
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database.database import SessionLocal
from backend.models.iso_models import ISOStandard, ISOClause

def debug_clauses():
    db = SessionLocal()
    
    try:
        standard = db.query(ISOStandard).first()
        
        if not standard:
            print("No ISO standard found in database")
            return
        
        print("="*80)
        print(f"DEBUGGING: {standard.name} ({standard.iso_number}:{standard.year})")
        print(f"Total clauses detected: {len(standard.clauses)}")
        print("="*80)
        
        # Group by level
        by_level = {}
        for clause in standard.clauses:
            level = clause.level
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(clause)
        
        print("\nClauses grouped by hierarchy level:")
        for level in sorted(by_level.keys()):
            print(f"\n--- Level {level} ({len(by_level[level])} clauses) ---")
            for clause in by_level[level][:10]:  # Show first 10
                print(f"  {clause.clause_number:10} | {clause.title[:70]}")
            if len(by_level[level]) > 10:
                print(f"  ... and {len(by_level[level]) - 10} more")
        
        # Show some problematic clauses
        print("\n" + "="*80)
        print("DETAILED VIEW OF FIRST 5 CLAUSES")
        print("="*80)
        
        for i, clause in enumerate(standard.clauses[:5]):
            print(f"\n[{i+1}] Clause Number: {clause.clause_number}")
            print(f"    Level: {clause.level}")
            print(f"    Title: {clause.title}")
            print(f"    Title Length: {len(clause.title)}")
            print(f"    Content Length: {len(clause.content) if clause.content else 0}")
            print(f"    Is Mandatory: {clause.is_mandatory}")
            if clause.content:
                print(f"    Content Preview: {clause.content[:200]}...")
        
        # Check for missing main clauses
        print("\n" + "="*80)
        print("CHECKING FOR EXPECTED CLAUSE STRUCTURE")
        print("="*80)
        
        expected_top_level = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
        found_numbers = {c.clause_number for c in standard.clauses}
        
        print("\nExpected top-level clauses (1-10):")
        for num in expected_top_level:
            status = "✓ FOUND" if num in found_numbers else "✗ MISSING"
            matching = [c for c in standard.clauses if c.clause_number == num]
            if matching:
                print(f"  {num}: {status} - {matching[0].title[:60]}")
            else:
                print(f"  {num}: {status}")
        
        # Look for clauses with numbers that look wrong
        print("\n" + "="*80)
        print("SUSPICIOUS CLAUSE NUMBERS (might be incorrectly parsed)")
        print("="*80)
        
        suspicious = [c for c in standard.clauses if len(c.clause_number) > 10 or not re.match(r'^\d+(\.\d+)*$', c.clause_number)]
        if suspicious:
            for clause in suspicious[:10]:
                print(f"  {clause.clause_number} - {clause.title[:60]}")
        else:
            print("  No suspicious clause numbers found")
        
    finally:
        db.close()

if __name__ == "__main__":
    debug_clauses()
