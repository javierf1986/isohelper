"""
Template metadata and management
"""
ISO_CLAUSES = {
    "4.1": {
        "title": "Understanding the Organization and Its Context",
        "template": "clause_4_1_context.md",
        "category": "Context of the Organization"
    },
    "4.2": {
        "title": "Understanding the Needs and Expectations of Interested Parties",
        "template": "clause_4_2_interested_parties.md",
        "category": "Context of the Organization"
    },
    "5.1": {
        "title": "Leadership and Commitment",
        "template": "clause_5_1_leadership.md",
        "category": "Leadership"
    },
    "6.1": {
        "title": "Actions to Address Risks and Opportunities",
        "template": "clause_6_1_risks_opportunities.md",
        "category": "Planning"
    },
    "8.1": {
        "title": "Operational Planning and Control",
        "template": "clause_8_1_operational_planning.md",
        "category": "Operation"
    }
}

def get_template_path(clause: str) -> str:
    """Get the template file path for a given clause"""
    if clause in ISO_CLAUSES:
        return ISO_CLAUSES[clause]["template"]
    return None

def list_available_clauses():
    """List all available clause templates"""
    return ISO_CLAUSES
