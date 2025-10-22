"""
Database Import Script for ISO Standards

This script imports ISO standards from PDF/DOCX files into the database.
It uses the UniversalISOImporter to extract text and structure, then
saves the data using SQLAlchemy models.

Usage:
    python backend/database/import_iso.py path/to/iso_standard.pdf
    
    # With options:
    python backend/database/import_iso.py path/to/iso.pdf --generate-templates
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.orm import Session
from backend.database.init_db import get_session, init_database
from backend.models.iso_models import (
    ISOStandard,
    ISOClause,
    StandardTemplate,
    StandardCategory,
    ClauseType as DBClauseType
)
from backend.services.iso_importer import (
    UniversalISOImporter,
    ClauseType as ImporterClauseType
)
from backend.services.ai_parser import AIISOParser
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def map_clause_type(importer_type: ImporterClauseType) -> DBClauseType:
    """Map importer ClauseType to database ClauseType"""
    mapping = {
        ImporterClauseType.REQUIREMENT: DBClauseType.REQUIREMENT,
        ImporterClauseType.GUIDANCE: DBClauseType.GUIDANCE,
        ImporterClauseType.DEFINITION: DBClauseType.INFORMATIVE,  # Map to informative
        ImporterClauseType.NOTE: DBClauseType.GUIDANCE,  # Notes are guidance
        ImporterClauseType.EXAMPLE: DBClauseType.GUIDANCE  # Examples are guidance
    }
    return mapping.get(importer_type, DBClauseType.GUIDANCE)


def map_category(category_str: str) -> StandardCategory:
    """Map category string to StandardCategory enum"""
    mapping = {
        'QMS': StandardCategory.QUALITY,         # ISO 9001
        'EMS': StandardCategory.ENVIRONMENTAL,   # ISO 14001
        'ISMS': StandardCategory.SECURITY,       # ISO 27001
        'OHSMS': StandardCategory.SAFETY,        # ISO 45001
        'FSMS': StandardCategory.FOOD_SAFETY,    # ISO 22000
        'EnMS': StandardCategory.ENERGY,         # ISO 50001
    }
    return mapping.get(category_str, StandardCategory.OTHER)


def import_iso_to_database(
    file_path: Path,
    session: Session,
    generate_templates: bool = False,
    use_ai: bool = True,
    overwrite: bool = False
) -> ISOStandard:
    """
    Import ISO standard from file to database
    
    Args:
        file_path: Path to ISO PDF/DOCX file
        session: SQLAlchemy session
        generate_templates: Whether to auto-generate Jinja2 templates
        use_ai: Whether to use AI for enhanced parsing
        overwrite: Whether to overwrite existing standard
        
    Returns:
        ISOStandard object
    """
    logger.info(f"Starting import of {file_path}")
    
    # Step 1: Extract text and structure using importer
    importer = UniversalISOImporter()
    result = importer.import_from_file(file_path)
    
    # Step 2: Enhance with AI if requested
    ai_parser = None
    if use_ai:
        try:
            logger.info("Using AI to enhance extraction...")
            ai_parser = AIISOParser()
            
            # Enhance metadata
            result['metadata'] = ai_parser.enhance_metadata_extraction(
                result['clean_text'],
                result['metadata']
            )
            
            # Enhance clause classification
            result['clauses'] = ai_parser.enhance_clause_detection(
                result['clean_text'],
                result['clauses']
            )
        except Exception as e:
            logger.warning(f"AI enhancement failed: {e}. Continuing with regex-based extraction.")
            ai_parser = None
    
    metadata = result['metadata']
    clauses = result['clauses']
    statistics = result['statistics']
    
    if not metadata:
        raise ValueError("Could not extract metadata from file")
    
    logger.info(f"Extracted {statistics['total_clauses']} clauses from {metadata.standard_number}")
    
    # Step 2: Check if standard already exists
    existing = session.query(ISOStandard).filter_by(
        number=metadata.standard_number,
        year=metadata.year
    ).first()
    
    if existing and not overwrite:
        logger.warning(f"Standard {metadata.standard_number}:{metadata.year} already exists")
        logger.info("Use --overwrite to replace existing standard")
        return existing
    
    if existing and overwrite:
        logger.info(f"Removing existing standard {existing.number}:{existing.year}")
        session.delete(existing)
        session.commit()
    
    # Step 3: Create ISO Standard record
    standard = ISOStandard(
        number=metadata.standard_number,
        year=metadata.year,
        title=metadata.title,
        category=map_category(metadata.category),
        description=f"{metadata.title} - Imported from {file_path.name} on {datetime.now().strftime('%Y-%m-%d')}",
        version=metadata.year,
        is_active=True
    )
    
    session.add(standard)
    session.flush()  # Get the ID
    
    logger.info(f"Created standard: {standard.number}:{standard.year} (ID: {standard.id})")
    
    # Step 4: Create clause records with hierarchy
    clause_map = {}  # Map clause numbers to database IDs
    
    for clause in clauses:
        # Find parent ID if exists
        parent_id = None
        if clause.parent_number:
            parent_id = clause_map.get(clause.parent_number)
        
        db_clause = ISOClause(
            standard_id=standard.id,
            number=clause.clause_number,
            title=clause.title,
            content=clause.content,
            level=clause.level,
            parent_id=parent_id,
            clause_type=map_clause_type(clause.clause_type),
            is_requirement=clause.is_requirement,
            order_index=len(clause_map)
        )
        
        session.add(db_clause)
        session.flush()  # Get the ID
        
        clause_map[clause.clause_number] = db_clause.id
    
    logger.info(f"Created {len(clause_map)} clause records")
    
    # Step 5: Generate templates if requested
    if generate_templates:
        logger.info("Generating templates for requirement clauses...")
        
        requirement_clauses = [c for c in clauses if c.is_requirement]
        template_count = 0
        
        # Use AI templates if requested and AI parser is available
        if use_ai and ai_parser:
            logger.info("Generating AI-powered templates...")
            ai_templates = ai_parser.generate_smart_templates(requirement_clauses)
            
            for clause_number, template_content in ai_templates.items():
                # Find clause title
                clause_title = next((c.title for c in requirement_clauses if c.clause_number == clause_number), "")
                
                template = StandardTemplate(
                    standard_id=standard.id,
                    clause_number=clause_number,
                    template_name=f"{clause_number} - {clause_title}",
                    template_content=template_content,
                    variables=['company_name', 'industry'],  # Extract from template
                    description=f"AI-generated template for {clause_number}",
                    is_active=True
                )
                session.add(template)
                template_count += 1
        else:
            # Use basic templates
            for clause in requirement_clauses:
                template_content = generate_template_from_clause(clause)
                
                template = StandardTemplate(
                    standard_id=standard.id,
                    clause_number=clause.clause_number,
                    template_name=f"{clause.clause_number} - {clause.title}",
                    template_content=template_content,
                    variables=['company_name', 'industry'],  # Basic variables
                    description=f"Auto-generated template for {clause.clause_number}",
                    is_active=True
                )
                
                session.add(template)
                template_count += 1
        
        logger.info(f"Generated {template_count} templates")
    
    # Step 6: Commit all changes
    session.commit()
    
    logger.info(f"✅ Successfully imported {standard.number}:{standard.year}")
    logger.info(f"   Clauses: {len(clause_map)}")
    logger.info(f"   Requirements: {statistics['requirements']}")
    logger.info(f"   Guidance: {statistics['guidance']}")
    
    return standard


def generate_template_from_clause(clause) -> str:
    """
    Generate a basic Jinja2 template from a clause
    
    This creates a simple template structure. In Phase 2 Task 3,
    we'll use AI to generate better templates.
    
    Args:
        clause: ExtractedClause object
        
    Returns:
        Jinja2 template string
    """
    # Replace common patterns with variables
    content = clause.content
    
    # Replace "the organization" with variable
    content = content.replace("the organization", "{{ company_name }}")
    content = content.replace("The organization", "{{ company_name }}")
    
    # Add conditional for industry-specific content
    template = f"""# {clause.clause_number} {clause.title}

{content}

{{% if industry %}}
## Industry-Specific Considerations for {{{{ industry }}}}

*This section will be enhanced based on industry requirements.*
{{% endif %}}

---
*Template auto-generated from ISO standard. Review and customize as needed.*
"""
    
    return template


def verify_import(session: Session, standard_number: str, year: str):
    """Verify that import was successful"""
    logger.info(f"\nVerifying import of {standard_number}:{year}...")
    
    # Find standard
    standard = session.query(ISOStandard).filter_by(
        number=standard_number,
        year=year
    ).first()
    
    if not standard:
        logger.error("❌ Standard not found in database!")
        return False
    
    logger.info(f"✓ Standard found: {standard.title}")
    
    # Count clauses
    clause_count = session.query(ISOClause).filter_by(
        standard_id=standard.id
    ).count()
    
    logger.info(f"✓ Clauses: {clause_count}")
    
    # Count templates
    template_count = session.query(StandardTemplate).filter_by(
        standard_id=standard.id
    ).count()
    
    logger.info(f"✓ Templates: {template_count}")
    
    # Check hierarchy
    top_level = session.query(ISOClause).filter_by(
        standard_id=standard.id,
        level=1
    ).count()
    
    logger.info(f"✓ Top-level clauses: {top_level}")
    
    logger.info("✅ Import verification complete!")
    return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Import ISO standards from PDF/DOCX files into database'
    )
    parser.add_argument(
        'file',
        type=str,
        help='Path to ISO PDF or DOCX file'
    )
    parser.add_argument(
        '--generate-templates',
        action='store_true',
        help='Auto-generate basic templates for requirement clauses'
    )
    parser.add_argument(
        '--use-ai',
        action='store_true',
        default=True,
        help='Use AI for enhanced parsing and template generation (default: True)'
    )
    parser.add_argument(
        '--no-ai',
        action='store_true',
        help='Disable AI enhancement, use only regex-based parsing'
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing standard if it exists'
    )
    parser.add_argument(
        '--init-db',
        action='store_true',
        help='Initialize database before import'
    )
    
    args = parser.parse_args()
    
    # Initialize database if requested
    if args.init_db:
        logger.info("Initializing database...")
        init_database(drop_existing=False)
    
    # Validate file path
    file_path = Path(args.file)
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return 1
    
    if file_path.suffix.lower() not in ['.pdf', '.docx', '.doc']:
        logger.error(f"Unsupported file format: {file_path.suffix}")
        logger.info("Supported formats: .pdf, .docx, .doc")
        return 1
    
    # Import to database
    try:
        session = get_session()
        
        # Determine AI usage
        use_ai = args.use_ai and not args.no_ai
        
        standard = import_iso_to_database(
            file_path=file_path,
            session=session,
            generate_templates=args.generate_templates,
            use_ai=use_ai,
            overwrite=args.overwrite
        )
        
        # Verify import
        verify_import(session, standard.number, str(standard.year))
        
        logger.info("\n" + "=" * 70)
        logger.info("Import complete!")
        logger.info("=" * 70)
        logger.info(f"\nStandard: {standard.number}:{standard.year}")
        logger.info(f"Title: {standard.title}")
        logger.info(f"Category: {standard.category.value}")
        logger.info(f"\nNext steps:")
        logger.info("  1. Review clauses in database")
        logger.info("  2. Generate/refine templates")
        logger.info("  3. Test document generation")
        
        session.close()
        return 0
        
    except Exception as e:
        logger.error(f"Import failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
