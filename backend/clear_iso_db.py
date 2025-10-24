"""Clean ISO standards from database"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from database.init_db import get_session
from models.iso_models import ISOStandard, ISOClause

session = get_session()
deleted_clauses = session.query(ISOClause).delete()
deleted_standards = session.query(ISOStandard).delete()
session.commit()

print(f"✅ Deleted {deleted_clauses} clauses and {deleted_standards} standards")
