"""
Test script for Universal ISO Importer

This script demonstrates how to use the ISO importer to:
1. Extract text from sample ISO documents
2. Detect clause structure
3. Classify requirements vs guidance
4. Prepare data for database import

Since we don't have actual ISO PDF files in the repo, this script
shows how to use the importer and provides mock testing capabilities.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.iso_importer import (
    UniversalISOImporter,
    ISOTextExtractor,
    ISOClauseDetector,
    ClauseType
)
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def create_mock_iso_text() -> str:
    """
    Create mock ISO text for testing clause detection
    
    This simulates the structure of an actual ISO standard document
    """
    return """
ISO 9001:2015
Quality management systems — Requirements

--- Page 1 ---

1 Scope
This document specifies requirements for a quality management system when an organization:
a) needs to demonstrate its ability to consistently provide products and services that meet customer requirements;
b) aims to enhance customer satisfaction through the effective application of the system.

--- Page 2 ---

3 Terms and definitions
For the purposes of this document, the terms and definitions given in ISO 9000:2015 apply.

3.1 Organization
Person or group of people that has its own functions with responsibilities.

--- Page 3 ---

4 Context of the organization

4.1 Understanding the organization and its context
The organization shall determine external and internal issues that are relevant to its purpose.

NOTE: Issues can include positive and negative factors or conditions for consideration.

4.2 Understanding the needs and expectations of interested parties
The organization shall determine:
a) the interested parties that are relevant to the QMS;
b) the requirements of these interested parties that are relevant to the QMS.

--- Page 4 ---

4.3 Determining the scope of the quality management system
The organization shall determine the boundaries and applicability of the QMS to establish its scope.

4.4 Quality management system and its processes
The organization shall establish, implement, maintain and continually improve a QMS.

4.4.1 Process approach
The organization should determine the processes needed for the QMS and their application throughout the organization.

--- Page 5 ---

5 Leadership

5.1 Leadership and commitment

5.1.1 General
Top management shall demonstrate leadership and commitment with respect to the QMS.

EXAMPLE: Management review meetings, resource allocation decisions, strategic planning sessions.

5.2 Policy

5.2.1 Establishing the quality policy
Top management shall establish, implement and maintain a quality policy that:
a) is appropriate to the purpose and context of the organization;
b) provides a framework for setting quality objectives.

--- Page 6 ---

6 Planning

6.1 Actions to address risks and opportunities

6.1.1 General
When planning for the QMS, the organization shall consider the issues referred to in 4.1 and the requirements referred to in 4.2.

6.2 Quality objectives and planning to achieve them

6.2.1 Quality objectives
The organization shall establish quality objectives at relevant functions, levels and processes.
"""


def test_text_extraction():
    """Test text extraction and cleaning"""
    print("\n" + "=" * 70)
    print("TEST 1: Text Extraction and Cleaning")
    print("=" * 70)
    
    extractor = ISOTextExtractor()
    
    # Create mock text
    raw_text = create_mock_iso_text()
    
    print(f"\n✓ Created mock ISO text: {len(raw_text)} characters")
    
    # Clean text
    clean_text = extractor.clean_text(raw_text)
    print(f"✓ Cleaned text: {len(clean_text)} characters")
    
    # Extract metadata
    metadata = extractor.extract_metadata_from_text(raw_text)
    
    if metadata:
        print(f"\n📋 Extracted Metadata:")
        print(f"   Standard: {metadata.standard_number}:{metadata.year}")
        print(f"   Title: {metadata.title}")
        print(f"   Category: {metadata.category}")
        print(f"   Pages: {metadata.total_pages}")
    else:
        print("\n⚠️  No metadata detected")
    
    return clean_text


def test_clause_detection(text: str):
    """Test clause detection and classification"""
    print("\n" + "=" * 70)
    print("TEST 2: Clause Detection and Classification")
    print("=" * 70)
    
    detector = ISOClauseDetector()
    
    # Detect all clauses
    clauses = detector.detect_clauses(text)
    
    print(f"\n✓ Detected {len(clauses)} clauses\n")
    
    # Show first 10 clauses with details
    print("Clause Structure:")
    print("-" * 70)
    
    for clause in clauses[:10]:
        indent = "  " * (clause.level - 1)
        type_emoji = {
            ClauseType.REQUIREMENT: "📌",
            ClauseType.GUIDANCE: "💡",
            ClauseType.NOTE: "📝",
            ClauseType.EXAMPLE: "📖",
            ClauseType.DEFINITION: "📚"
        }
        
        emoji = type_emoji.get(clause.clause_type, "•")
        print(f"{indent}{emoji} {clause.clause_number} {clause.title}")
        print(f"{indent}   Type: {clause.clause_type.value}")
        print(f"{indent}   Level: {clause.level}")
        if clause.parent_number:
            print(f"{indent}   Parent: {clause.parent_number}")
        print(f"{indent}   Content: {clause.content[:100]}...")
        print()
    
    if len(clauses) > 10:
        print(f"... and {len(clauses) - 10} more clauses")
    
    # Statistics by type
    print("\n📊 Clause Statistics:")
    print("-" * 70)
    
    type_counts = {}
    for clause in clauses:
        type_counts[clause.clause_type] = type_counts.get(clause.clause_type, 0) + 1
    
    for clause_type, count in sorted(type_counts.items()):
        print(f"   {clause_type.value.title()}: {count}")
    
    # Requirements analysis
    requirements = detector.filter_requirements_only(clauses)
    print(f"\n📌 Total Requirements: {len(requirements)}")
    print(f"💡 Total Guidance: {type_counts.get(ClauseType.GUIDANCE, 0)}")
    
    # Level distribution
    print("\n📊 Hierarchy Levels:")
    for level in range(1, 5):
        level_clauses = detector.filter_by_level(clauses, level)
        if level_clauses:
            print(f"   Level {level}: {len(level_clauses)} clauses")
    
    return clauses


def test_full_import_workflow():
    """Test the complete import workflow"""
    print("\n" + "=" * 70)
    print("TEST 3: Full Import Workflow")
    print("=" * 70)
    
    # Create a mock importer (without actual file)
    importer = UniversalISOImporter()
    
    print("\n✓ UniversalISOImporter initialized")
    print("\nWorkflow Steps:")
    print("  1. Extract text from PDF/DOCX → extract_from_pdf() / extract_from_docx()")
    print("  2. Clean and normalize text → clean_text()")
    print("  3. Extract metadata → extract_metadata_from_text()")
    print("  4. Detect clause structure → detect_clauses()")
    print("  5. Classify clause types → _classify_clause()")
    print("  6. Export to database format → export_to_database_format()")
    
    print("\n📦 Database Export Format:")
    print("-" * 70)
    print("""
    {
        'standard': {
            'number': 'ISO 9001',
            'year': '2015',
            'title': 'Quality management systems — Requirements',
            'category': 'QMS',
            'description': '...',
            'version': '2015',
            'is_active': True
        },
        'clauses': [
            {
                'number': '4.1',
                'title': 'Understanding the organization',
                'content': '...',
                'level': 2,
                'parent_number': '4',
                'clause_type': 'requirement',
                'is_requirement': True
            },
            ...
        ],
        'statistics': {
            'total_clauses': 45,
            'requirements': 32,
            'guidance': 10,
            'notes': 2,
            'examples': 1
        }
    }
    """)


def test_with_sample_file():
    """Test with actual PDF/DOCX file if available"""
    print("\n" + "=" * 70)
    print("TEST 4: Import from Real File (Optional)")
    print("=" * 70)
    
    # Check for sample files in tests directory
    test_dir = Path(__file__).parent.parent / "tests" / "fixtures"
    sample_files = []
    
    if test_dir.exists():
        sample_files = list(test_dir.glob("*.pdf")) + list(test_dir.glob("*.docx"))
    
    if not sample_files:
        print("\n⚠️  No sample PDF/DOCX files found in tests/fixtures/")
        print("\nTo test with a real ISO document:")
        print("  1. Place ISO PDF/DOCX in tests/fixtures/")
        print("  2. Run: python backend/services/test_iso_importer.py")
        print("\nExample usage:")
        print("  importer = UniversalISOImporter()")
        print("  result = importer.import_from_file(Path('ISO_9001_2015.pdf'))")
        print("  print(result['statistics'])")
        return
    
    print(f"\n✓ Found {len(sample_files)} sample file(s):")
    for file in sample_files:
        print(f"   - {file.name}")
    
    print("\n💡 To import a file, use:")
    print(f"   importer = UniversalISOImporter()")
    print(f"   result = importer.import_from_file(Path('{sample_files[0].name}'))")


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("Universal ISO Importer - Test Suite")
    print("=" * 70)
    print("\nThis test suite demonstrates the ISO importer capabilities:")
    print("  ✓ Text extraction from PDF/DOCX")
    print("  ✓ Clause detection and hierarchy")
    print("  ✓ Requirement vs guidance classification")
    print("  ✓ Database export format preparation")
    
    try:
        # Run tests
        clean_text = test_text_extraction()
        clauses = test_clause_detection(clean_text)
        test_full_import_workflow()
        test_with_sample_file()
        
        print("\n" + "=" * 70)
        print("✅ All tests completed successfully!")
        print("=" * 70)
        
        print("\n📚 Next Steps:")
        print("  1. Place an ISO PDF/DOCX in tests/fixtures/")
        print("  2. Import it: importer.import_from_file(Path('file.pdf'))")
        print("  3. Save to database using backend/database/import_iso.py")
        print("  4. Add AI parsing for better accuracy (Phase 2 Task 3)")
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
