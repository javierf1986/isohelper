"""
Simple test to generate ISO 9001 documents
"""
import sys
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent.parent))

from backend.services.document_generator import generator_service

# Test data
company_data = {
    "company_name": "ABC Manufacturing Ltd",
    "industry": "automotive",
    "company_size": "medium"
}

print("="*60)
print("Testing ISO 9001 Document Generator")
print("="*60)
print()

# Test single document generation
print("📄 Generating Clause 4.1 document...")
result = generator_service.generate_document("4.1", company_data)

if result:
    print(f"✅ Success! Document saved to: {result}")
    print()
    
    # Read and display first few lines
    content = Path(result).read_text(encoding="utf-8")
    lines = content.split('\n')[:15]
    print("Preview (first 15 lines):")
    print("-"*60)
    for line in lines:
        print(line)
    print("-"*60)
else:
    print("❌ Failed to generate document")

print()
print("📚 Generating full manual with multiple clauses...")
result = generator_service.generate_full_manual(
    ["4.1", "4.2", "5.1"],
    company_data
)

if result:
    print(f"✅ Success! Full manual saved to: {result}")
    file_size = Path(result).stat().st_size
    print(f"📊 File size: {file_size:,} bytes")
else:
    print("❌ Failed to generate full manual")

print()
print("✅ Test complete!")
