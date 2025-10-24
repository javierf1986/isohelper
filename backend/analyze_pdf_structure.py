"""
Analyze PDF structure to understand clause detection issues
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.iso_importer import UniversalISOImporter

def analyze_pdf():
    # Find uploaded PDFs
    upload_dir = Path(__file__).parent / "uploads" / "iso_standards"
    pdf_files = list(upload_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in uploads/iso_standards/")
        return
    
    print(f"\nFound {len(pdf_files)} PDF file(s)")
    pdf_file = pdf_files[0]
    print(f"Analyzing: {pdf_file.name}\n")
    
    # Import and parse
    importer = UniversalISOImporter()
    result = importer.import_from_file(pdf_file)
    
    # Show raw text sample
    print("="*80)
    print("RAW TEXT SAMPLE (first 3000 characters)")
    print("="*80)
    print(result['raw_text'][:3000])
    
    print("\n" + "="*80)
    print("CLEAN TEXT SAMPLE (first 3000 characters)")
    print("="*80)
    print(result['clean_text'][:3000])
    
    # Show detected clauses
    print("\n" + "="*80)
    print(f"DETECTED CLAUSES ({len(result['clauses'])} total)")
    print("="*80)
    for i, clause in enumerate(result['clauses'][:15]):
        print(f"\n[{i+1}] Clause {clause.clause_number}")
        print(f"    Title: {clause.title}")
        print(f"    Content (first 100 chars): {clause.content[:100]}...")
        print(f"    Level: {clause.level}, Type: {clause.clause_type}")

if __name__ == "__main__":
    analyze_pdf()
