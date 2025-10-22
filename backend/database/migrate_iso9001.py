"""
Migrate ISO 9001:2015 data to universal ISO model
Phase 2: Data migration from templates to database
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.orm import Session
from backend.models.iso_models import ISOStandard, ISOClause, StandardTemplate, StandardCategory, ClauseType
from backend.database.init_db import get_session
from templates.iso9001 import ISO_CLAUSES
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_iso9001_to_database(session: Session):
    """
    Migrate existing ISO 9001:2015 templates to universal database model
    """
    logger.info("📦 Starting ISO 9001:2015 migration...")
    
    # 1. Create ISO 9001:2015 standard record
    logger.info("1️⃣  Creating ISO 9001:2015 standard...")
    
    iso9001 = ISOStandard(
        id="ISO-9001-2015",
        name="ISO 9001:2015",
        full_title="Quality management systems - Requirements",
        iso_number="9001",
        year=2015,
        category=StandardCategory.QUALITY.value,
        description="Specifies requirements for a quality management system when an organization needs to demonstrate its ability to consistently provide products and services that meet customer and applicable statutory and regulatory requirements.",
        purpose="To help organizations ensure that they meet the needs of customers and other stakeholders while meeting statutory and regulatory requirements related to a product or service.",
        scope="Applies to any organization, regardless of its size or the products and services it provides.",
        keywords=["quality", "QMS", "quality management", "ISO 9001", "certification", "compliance"],
        total_clauses=len(ISO_CLAUSES),
        has_annexes=True,
        structure_levels=3,
        import_method="template",
        imported_by="system",
        is_active=True,
        is_template=True,
        version="1.0"
    )
    
    session.add(iso9001)
    logger.info(f"✅ Created standard: {iso9001.name}")
    
    # 2. Create clauses from existing templates
    logger.info("2️⃣  Creating clauses...")
    
    templates_path = Path("templates/iso9001")
    clauses_created = 0
    
    for clause_num, clause_info in ISO_CLAUSES.items():
        # Extract hierarchy level (4.1 = level 2, 4.1.1 = level 3)
        level = clause_num.count('.') + 1
        
        # Determine parent clause
        parent_id = None
        if '.' in clause_num:
            parent_num = '.'.join(clause_num.split('.')[:-1])
            parent_id = f"ISO-9001-2015-{parent_num}"
        
        # Create clause
        clause = ISOClause(
            id=f"ISO-9001-2015-{clause_num}",
            standard_id="ISO-9001-2015",
            clause_number=clause_num,
            parent_clause_id=parent_id,
            level=level,
            sequence=int(clause_num.split('.')[-1]),
            title=clause_info["title"],
            content=f"See template: {clause_info['template']}",
            clause_type=ClauseType.REQUIREMENT.value,
            is_mandatory=True,
            is_documentable=True,
            has_template=True,
            keywords=clause_info.get("keywords", []),
            ai_generated=False
        )
        
        session.add(clause)
        clauses_created += 1
        
        # 3. Create template record
        template_file = templates_path / clause_info["template"]
        
        if template_file.exists():
            template_content = template_file.read_text(encoding='utf-8')
            
            # Extract variables from Jinja2 template
            import re
            variables = {}
            var_pattern = r'\{\{\s*(\w+)\s*\}\}'
            found_vars = re.findall(var_pattern, template_content)
            
            for var in set(found_vars):
                variables[var] = {
                    "type": "string",
                    "description": f"Company {var.replace('_', ' ')}",
                    "required": True
                }
            
            template = StandardTemplate(
                id=f"TPL-9001-{clause_num}",
                standard_id="ISO-9001-2015",
                clause_id=clause.id,
                template_name=f"ISO 9001 Clause {clause_num} - {clause_info['title']}",
                template_path=str(template_file),
                template_content=template_content,
                variables=variables,
                format="markdown",
                category=clause_info.get("category", "General"),
                description=f"Template for ISO 9001:2015 Clause {clause_num}",
                generation_method="manual",
                generated_by="system",
                is_active=True,
                is_approved=True,
                version="1.0"
            )
            
            session.add(template)
    
    logger.info(f"✅ Created {clauses_created} clauses")
    
    # 4. Commit all changes
    logger.info("3️⃣  Saving to database...")
    session.commit()
    logger.info("✅ Migration complete!")
    
    # 5. Summary
    logger.info("\n📊 Migration Summary:")
    logger.info(f"   Standard: {iso9001.name}")
    logger.info(f"   Clauses: {clauses_created}")
    logger.info(f"   Templates: {len(ISO_CLAUSES)}")
    logger.info(f"   Category: {iso9001.category}")
    
    return iso9001


def verify_migration(session: Session):
    """Verify the migration was successful"""
    logger.info("\n🔍 Verifying migration...")
    
    # Check standard
    standard = session.query(ISOStandard).filter_by(id="ISO-9001-2015").first()
    if not standard:
        logger.error("❌ Standard not found!")
        return False
    
    logger.info(f"✅ Standard found: {standard.name}")
    
    # Check clauses
    clauses = session.query(ISOClause).filter_by(standard_id="ISO-9001-2015").all()
    logger.info(f"✅ Clauses found: {len(clauses)}")
    
    # Check templates
    templates = session.query(StandardTemplate).filter_by(standard_id="ISO-9001-2015").all()
    logger.info(f"✅ Templates found: {len(templates)}")
    
    # Sample queries
    logger.info("\n📋 Sample queries:")
    
    # Find top-level clauses
    top_clauses = session.query(ISOClause).filter_by(
        standard_id="ISO-9001-2015",
        level=2
    ).all()
    logger.info(f"   Top-level clauses: {len(top_clauses)}")
    for clause in top_clauses[:5]:
        logger.info(f"      {clause.clause_number}: {clause.title}")
    
    return True


if __name__ == "__main__":
    # Get database session
    session = get_session()
    
    try:
        # Run migration
        migrate_iso9001_to_database(session)
        
        # Verify migration
        verify_migration(session)
        
        logger.info("\n✅ ISO 9001:2015 successfully migrated to universal model!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        session.rollback()
        raise
    
    finally:
        session.close()
