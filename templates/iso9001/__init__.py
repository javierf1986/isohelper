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
    "4.3": {
        "title": "Determining the Scope of the QMS",
        "template": "clause_4_3_scope.md",
        "category": "Context of the Organization"
    },
    "4.4": {
        "title": "Quality Management System and Its Processes",
        "template": "clause_4_4_processes.md",
        "category": "Context of the Organization"
    },
    "5.1": {
        "title": "Leadership and Commitment",
        "template": "clause_5_1_leadership.md",
        "category": "Leadership"
    },
    "5.2": {
        "title": "Quality Policy",
        "template": "clause_5_2_quality_policy.md",
        "category": "Leadership"
    },
    "5.3": {
        "title": "Organizational Roles, Responsibilities and Authorities",
        "template": "clause_5_3_roles_responsibilities.md",
        "category": "Leadership"
    },
    "6.1": {
        "title": "Actions to Address Risks and Opportunities",
        "template": "clause_6_1_risks_opportunities.md",
        "category": "Planning"
    },
    "6.2": {
        "title": "Quality Objectives and Planning",
        "template": "clause_6_2_quality_objectives.md",
        "category": "Planning"
    },
    "7.1": {
        "title": "Resources",
        "template": "clause_7_1_resources.md",
        "category": "Support"
    },
    "7.5": {
        "title": "Documented Information",
        "template": "clause_7_5_documented_information.md",
        "category": "Support"
    },
    "8.1": {
        "title": "Operational Planning and Control",
        "template": "clause_8_1_operational_planning.md",
        "category": "Operation"
    },
    "8.5": {
        "title": "Production and Service Provision",
        "template": "clause_8_5_production_service.md",
        "category": "Operation"
    },
    "9.1": {
        "title": "Monitoring, Measurement, Analysis and Evaluation",
        "template": "clause_9_1_monitoring_measurement.md",
        "category": "Performance Evaluation"
    },
    "10.2": {
        "title": "Nonconformity and Corrective Action",
        "template": "clause_10_2_nonconformity.md",
        "category": "Improvement"
    }
}

def get_template_path(clause: str) -> str | None:
    """Get the template file path for a given clause"""
    if clause in ISO_CLAUSES:
        return ISO_CLAUSES[clause]["template"]
    return None

def list_available_clauses():
    """List all available clause templates"""
    return ISO_CLAUSES
