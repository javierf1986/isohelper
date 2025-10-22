"""
Quick Manual Test - Document Generation
Run this while the server is running in another terminal
"""
from pathlib import Path
import sys

# Setup paths - now in tests/ folder, so parent is project root
project_root = Path(__file__).parent.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(project_root))

# Now import
from backend.services.document_generator import DocumentGenerator

def main():
    print("="*70)
    print(" ISO 9001 Document Generator - Manual Test")
    print("="*70)
    print()
    
    # Create generator
    gen = DocumentGenerator()
    
    # Company data
    company = {
        "company_name": "Test Industries Inc",
        "industry": "manufacturing",
        "company_size": "medium",
    }
    
    print(f"🏢 Company: {company['company_name']}")
    print(f"🏭 Industry: {company['industry']}")
    print(f"📊 Size: {company['company_size']}")
    print()
    
    # Test 1: Single document
    print("📄 TEST 1: Generate single document (Clause 4.1)")
    print("-"*70)
    doc_path = gen.generate_document("4.1", company)
    
    if doc_path:
        print(f"✅ Generated: {Path(doc_path).name}")
        content = Path(doc_path).read_text(encoding="utf-8")
        print(f"📏 Length: {len(content)} characters")
        print()
        print("Preview (first 300 characters):")
        print(content[:300] + "...")
    else:
        print("❌ FAILED")
    
    print()
    print()
    
    # Test 2: Multiple documents
    print("📚 TEST 2: Generate full manual (Clauses 4.1, 4.2, 5.1)")
    print("-"*70)
    manual_path = gen.generate_full_manual(["4.1", "4.2", "5.1"], company)
    
    if manual_path:
        print(f"✅ Generated: {Path(manual_path).name}")
        size = Path(manual_path).stat().st_size
        print(f"📦 Size: {size:,} bytes ({size/1024:.1f} KB)")
        
        # Count pages (rough estimate: 3000 chars per page)
        content = Path(manual_path).read_text(encoding="utf-8")
        estimated_pages = len(content) / 3000
        print(f"📄 Estimated pages: {estimated_pages:.1f}")
    else:
        print("❌ FAILED")
    
    print()
    print("="*70)
    print("✅ Testing Complete!")
    print()
    print("📂 Generated documents are in: ./generated_documents/")
    print()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
