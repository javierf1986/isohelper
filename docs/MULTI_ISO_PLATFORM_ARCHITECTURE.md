# Multi-ISO Platform Architecture
## Universal ISO Management Hub

---

## 🎯 Vision Statement

Transform ISO Helper into a **universal ISO standards management platform** where:
- **Any ISO standard** can be uploaded and managed (9001, 14001, 27001, 45001, 13485, 22000, etc.)
- **Client-specific adaptations** for industry, region, or organizational needs
- **Cross-standard integration** when clients need multiple certifications
- **Template marketplace** where consultants can share/sell configurations
- **White-label capability** for consulting firms

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   ISO Platform Core Engine                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Standard   │  │   Template   │  │  Artifact    │         │
│  │   Manager    │  │   Engine     │  │  Engine      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│         │                  │                  │                  │
│         └──────────────────┴──────────────────┘                 │
│                        │                                         │
│              ┌─────────▼──────────┐                             │
│              │  Universal Parser  │                             │
│              │  (ISO Importer)    │                             │
│              └────────────────────┘                             │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐│
│  │              Multi-Tenant Client Workspace                  ││
│  ├────────────────────────────────────────────────────────────┤│
│  │  Client 1: ISO 9001 + 14001 (Manufacturing)                ││
│  │  Client 2: ISO 27001 (IT Security)                          ││
│  │  Client 3: ISO 13485 + 9001 (Medical Devices)              ││
│  │  Client 4: Custom Standard (Internal QMS)                   ││
│  └────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Core Components

### 1. Universal ISO Standard Model

Instead of hardcoding ISO 9001, create a flexible model that can represent ANY standard:

```python
# backend/models/iso_standard.py

from enum import Enum
from typing import List, Dict, Optional
from datetime import date
from pydantic import BaseModel, Field

class StandardCategory(str, Enum):
    """Types of ISO standards"""
    QUALITY = "quality"  # ISO 9001
    ENVIRONMENTAL = "environmental"  # ISO 14001
    INFORMATION_SECURITY = "information_security"  # ISO 27001
    OCCUPATIONAL_HEALTH = "occupational_health"  # ISO 45001
    FOOD_SAFETY = "food_safety"  # ISO 22000
    MEDICAL_DEVICES = "medical_devices"  # ISO 13485
    ENERGY = "energy"  # ISO 50001
    AUTOMOTIVE = "automotive"  # IATF 16949
    RISK_MANAGEMENT = "risk_management"  # ISO 31000
    CUSTOM = "custom"  # Client-specific standards

class ClauseType(str, Enum):
    """Types of clauses in standards"""
    REQUIREMENT = "requirement"  # Must be implemented
    GUIDANCE = "guidance"  # Recommended approach
    DEFINITION = "definition"  # Terms and definitions
    SCOPE = "scope"  # Applicability statement
    NORMATIVE_REFERENCE = "normative_reference"  # Related standards
    INFORMATIVE = "informative"  # Additional information

class ISOStandard(BaseModel):
    """Universal model for any ISO standard"""
    
    # Identity
    id: str = Field(default_factory=lambda: f"STD-{uuid4().hex[:8]}")
    name: str  # "ISO 9001", "ISO 14001", etc.
    full_title: str  # "Quality management systems — Requirements"
    standard_number: str  # "9001"
    version: str  # "2015", "2018", etc.
    category: StandardCategory
    
    # Metadata
    published_date: date
    effective_date: Optional[date]
    revision_date: Optional[date]
    status: str  # "active", "superseded", "draft"
    issuing_body: str = "ISO"  # ISO, ANSI, BSI, etc.
    
    # Standard Structure
    clauses: List["ISOClause"] = []
    total_pages: Optional[int]
    language: str = "en"
    
    # Relationships
    replaces: Optional[str]  # Previous version ID
    related_standards: List[str] = []  # Compatible/complementary standards
    compatible_with: List[str] = []  # Standards that can be integrated
    
    # Source
    source_file: Optional[str]  # Original PDF/DOCX path
    import_date: date = Field(default_factory=date.today)
    imported_by: Optional[str]
    
    # Customization
    client_id: Optional[str]  # If client-specific version
    customizations: Dict = {}  # Client-specific modifications
    
    class Config:
        schema_extra = {
            "example": {
                "name": "ISO 9001",
                "full_title": "Quality management systems — Requirements",
                "standard_number": "9001",
                "version": "2015",
                "category": "quality",
                "published_date": "2015-09-15"
            }
        }

class ISOClause(BaseModel):
    """Individual clause within any ISO standard"""
    
    id: str = Field(default_factory=lambda: f"CLS-{uuid4().hex[:8]}")
    standard_id: str
    
    # Clause Structure
    clause_number: str  # "4.1", "5.2.1", "A.5" (for annexes)
    title: str
    content: str  # Full text of the clause
    clause_type: ClauseType
    
    # Hierarchy
    level: int  # 1, 2, 3 (for 4, 4.1, 4.1.1)
    parent_clause: Optional[str]  # Parent clause number
    child_clauses: List[str] = []  # Child clause numbers
    
    # Requirements
    is_mandatory: bool = True
    is_auditable: bool = True
    requires_documentation: bool = False
    requires_records: bool = False
    
    # Cross-References
    references: List[str] = []  # Other clause numbers referenced
    related_clauses: List[str] = []  # Related clauses in same standard
    external_references: List[str] = []  # References to other standards
    
    # Implementation Guidance
    implementation_notes: Optional[str]
    examples: List[str] = []
    common_nonconformities: List[str] = []
    
    # Metadata
    keywords: List[str] = []  # For search/AI
    ai_summary: Optional[str]  # AI-generated summary
    
    # Customization
    client_notes: Optional[str]  # Client-specific interpretation
    excluded: bool = False  # If client excludes this clause
    exclusion_justification: Optional[str]

class StandardTemplate(BaseModel):
    """Template for implementing a clause"""
    
    id: str = Field(default_factory=lambda: f"TPL-{uuid4().hex[:8]}")
    standard_id: str
    clause_id: str
    
    # Template Content
    template_name: str
    template_file: str  # Path to .md/.docx template
    template_type: str  # "document", "procedure", "form", "checklist"
    
    # Applicability
    industries: List[str] = []  # ["manufacturing", "healthcare", "IT"]
    company_sizes: List[str] = []  # ["small", "medium", "large"]
    maturity_levels: List[str] = []  # ["basic", "intermediate", "advanced"]
    
    # Content
    variables: Dict = {}  # Template variables and defaults
    sections: List[str] = []  # Template sections
    required_inputs: List[str] = []  # User inputs needed
    
    # Metadata
    author: Optional[str]
    created_date: date = Field(default_factory=date.today)
    version: str = "1.0"
    license: str = "proprietary"  # or "open", "commercial"
    price: float = 0.0  # For marketplace templates
    
    # Quality Metrics
    usage_count: int = 0
    rating: Optional[float]  # User ratings
    reviews: List[str] = []

class IntegratedStandardSet(BaseModel):
    """Set of integrated standards for a client"""
    
    id: str = Field(default_factory=lambda: f"ISET-{uuid4().hex[:8]}")
    client_id: str
    name: str  # "QMS + EMS Integration"
    
    standards: List[str]  # Standard IDs
    integration_mapping: Dict  # Maps clauses across standards
    
    # Example: {"iso9001_4.1": ["iso14001_4.1", "iso45001_4.1"]}
    # Shows which clauses align across standards
    
    shared_procedures: List[str] = []  # Procedures that satisfy multiple standards
    combined_audits: bool = True  # Can audit together
    
    created_date: date = Field(default_factory=date.today)
```

---

## 🔄 Universal ISO Importer

Allow users to upload ANY ISO standard document and have the system parse it:

```python
# backend/services/iso_importer.py

from typing import Union
import PyPDF2
import docx
import re
from openai import OpenAI

class UniversalISOImporter:
    """
    Import and parse any ISO standard document
    Supports: PDF, DOCX, TXT, XML
    """
    
    def __init__(self):
        self.ai_client = OpenAI()
        self.supported_formats = ['.pdf', '.docx', '.txt', '.xml']
    
    async def import_standard(
        self,
        file_path: str,
        standard_metadata: Dict = None,
        auto_parse: bool = True
    ) -> ISOStandard:
        """
        Import an ISO standard from file
        
        Steps:
        1. Extract text from file
        2. Identify standard (name, version, category)
        3. Parse clause structure
        4. Extract requirements
        5. Generate AI summaries
        6. Create template placeholders
        """
        
        # Step 1: Extract text
        text = await self._extract_text(file_path)
        
        # Step 2: Identify standard
        if not standard_metadata:
            standard_metadata = await self._identify_standard(text)
        
        # Step 3: Parse structure
        clauses = await self._parse_clauses(text, standard_metadata)
        
        # Step 4: Extract requirements
        for clause in clauses:
            clause.is_mandatory = await self._is_mandatory(clause.content)
            clause.requires_documentation = await self._requires_docs(clause.content)
        
        # Step 5: AI enhancement
        for clause in clauses:
            clause.ai_summary = await self._generate_summary(clause)
            clause.keywords = await self._extract_keywords(clause)
        
        # Step 6: Create standard object
        standard = ISOStandard(
            **standard_metadata,
            clauses=clauses,
            source_file=file_path
        )
        
        # Step 7: Save to database
        await self._save_standard(standard)
        
        return standard
    
    async def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF or DOCX"""
        ext = Path(file_path).suffix.lower()
        
        if ext == '.pdf':
            return self._extract_from_pdf(file_path)
        elif ext == '.docx':
            return self._extract_from_docx(file_path)
        elif ext == '.txt':
            return Path(file_path).read_text(encoding='utf-8')
        else:
            raise ValueError(f"Unsupported format: {ext}")
    
    async def _identify_standard(self, text: str) -> Dict:
        """Use AI to identify standard metadata from text"""
        
        prompt = f"""
        Analyze this ISO standard document and extract:
        - Standard name (e.g., "ISO 9001")
        - Full title
        - Version/year (e.g., "2015")
        - Category (quality, environmental, security, etc.)
        - Published date
        
        First 2000 characters:
        {text[:2000]}
        
        Return as JSON.
        """
        
        response = await self.ai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def _parse_clauses(self, text: str, metadata: Dict) -> List[ISOClause]:
        """Parse clause structure from text"""
        
        clauses = []
        
        # Regex to find clauses (e.g., "4.1 ", "5.2.1 ", etc.)
        clause_pattern = r'^(\d+(?:\.\d+)*)\s+(.+?)$'
        
        lines = text.split('\n')
        current_clause = None
        current_content = []
        
        for line in lines:
            match = re.match(clause_pattern, line.strip())
            
            if match:
                # Save previous clause
                if current_clause:
                    current_clause.content = '\n'.join(current_content)
                    clauses.append(current_clause)
                
                # Start new clause
                clause_number = match.group(1)
                title = match.group(2)
                
                current_clause = ISOClause(
                    standard_id=metadata.get('id', ''),
                    clause_number=clause_number,
                    title=title,
                    level=clause_number.count('.') + 1,
                    parent_clause=self._get_parent_clause(clause_number)
                )
                current_content = []
            else:
                if current_clause:
                    current_content.append(line)
        
        # Save last clause
        if current_clause:
            current_clause.content = '\n'.join(current_content)
            clauses.append(current_clause)
        
        return clauses
    
    async def _is_mandatory(self, content: str) -> bool:
        """Determine if clause is mandatory using AI"""
        
        # Look for "shall" (mandatory) vs "should" (recommended)
        mandatory_indicators = ['shall', 'must', 'required']
        optional_indicators = ['should', 'may', 'can', 'recommended']
        
        content_lower = content.lower()
        
        has_mandatory = any(word in content_lower for word in mandatory_indicators)
        has_optional = any(word in content_lower for word in optional_indicators)
        
        # If both, use AI to decide
        if has_mandatory and has_optional:
            prompt = f"Is this clause mandatory (shall/must) or optional (should/may)?\n\n{content[:500]}"
            # AI decision...
            return True  # Default to mandatory
        
        return has_mandatory
    
    async def _generate_summary(self, clause: ISOClause) -> str:
        """AI-generated plain-language summary"""
        
        prompt = f"""
        Summarize this ISO clause in simple language (2-3 sentences):
        
        {clause.clause_number} {clause.title}
        {clause.content[:1000]}
        
        Focus on: What must the organization do?
        """
        
        response = await self.ai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content
    
    async def generate_templates_for_standard(
        self,
        standard: ISOStandard,
        template_style: str = "comprehensive"
    ) -> List[StandardTemplate]:
        """
        Auto-generate templates for all clauses in standard
        """
        
        templates = []
        
        for clause in standard.clauses:
            if not clause.requires_documentation:
                continue
            
            template = await self._generate_clause_template(
                standard=standard,
                clause=clause,
                style=template_style
            )
            
            templates.append(template)
        
        return templates
    
    async def _generate_clause_template(
        self,
        standard: ISOStandard,
        clause: ISOClause,
        style: str
    ) -> StandardTemplate:
        """Generate template for a specific clause using AI"""
        
        prompt = f"""
        Create a comprehensive document template for this ISO requirement:
        
        Standard: {standard.name} {standard.version}
        Clause: {clause.clause_number} - {clause.title}
        
        Requirements:
        {clause.content}
        
        Generate a Markdown template that includes:
        1. Purpose statement
        2. Scope and applicability
        3. Required procedures
        4. Forms/records needed
        5. Responsibilities
        6. Implementation guidance
        
        Use template variables: {{company_name}}, {{industry}}, {{date}}, etc.
        Style: {style}
        """
        
        response = await self.ai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        template_content = response.choices[0].message.content
        
        # Save template file
        template_file = f"clause_{clause.clause_number.replace('.', '_')}.md"
        template_path = f"templates/{standard.name.lower()}/{template_file}"
        
        Path(template_path).parent.mkdir(parents=True, exist_ok=True)
        Path(template_path).write_text(template_content)
        
        return StandardTemplate(
            standard_id=standard.id,
            clause_id=clause.id,
            template_name=f"{clause.clause_number} - {clause.title}",
            template_file=template_path,
            template_type="document"
        )
```

---

## 🏢 Client Workspace Model

Multi-tenant architecture where each client has their own workspace:

```python
# backend/models/client_workspace.py

class ClientWorkspace(BaseModel):
    """Client-specific workspace with their standards and customizations"""
    
    id: str = Field(default_factory=lambda: f"WS-{uuid4().hex[:8]}")
    
    # Client Info
    client_name: str
    client_type: str  # "enterprise", "consultant", "individual"
    industry: str
    company_size: str
    region: str  # For regional compliance (EU, US, etc.)
    
    # Active Standards
    active_standards: List[str] = []  # Standard IDs
    integrated_standards: List[str] = []  # IntegratedStandardSet IDs
    
    # Customizations
    custom_templates: List[str] = []  # Custom template IDs
    custom_procedures: List[str] = []
    branding: Dict = {
        "logo": None,
        "colors": {},
        "letterhead": None
    }
    
    # Document Library
    generated_documents: List[str] = []
    artifacts: List[str] = []  # NC, CA, Audits, etc.
    
    # Users
    users: List[str] = []  # User IDs with access
    roles: Dict = {}  # User roles and permissions
    
    # Subscription
    plan: str  # "free", "professional", "enterprise"
    features_enabled: List[str] = []
    storage_used: int = 0  # MB
    storage_limit: int = 1000  # MB
    
    # Settings
    settings: Dict = {
        "default_language": "en",
        "date_format": "YYYY-MM-DD",
        "ai_assistance": True,
        "auto_save": True
    }
    
    created_date: date = Field(default_factory=date.today)
    last_accessed: date = Field(default_factory=date.today)

class ClientConfiguration(BaseModel):
    """Client-specific configuration for a standard"""
    
    workspace_id: str
    standard_id: str
    
    # Scope Definition
    included_clauses: List[str]  # Clause IDs
    excluded_clauses: List[str]
    exclusion_justifications: Dict  # {clause_id: justification}
    
    # Customizations
    custom_variables: Dict  # Client-specific template variables
    custom_workflows: List[str]
    approval_matrix: Dict  # Who approves what
    
    # Integration
    erp_integration: Optional[Dict]  # SAP, Oracle, etc.
    document_management: Optional[Dict]  # SharePoint, etc.
    
    # Compliance
    additional_requirements: List[str]  # Regulatory, customer-specific
    audit_schedule: Dict
    certification_body: Optional[str]
```

---

## 🔌 API Endpoints for Multi-ISO Platform

```python
# backend/api/routes/standards.py

@router.post("/standards/import")
async def import_iso_standard(
    file: UploadFile,
    metadata: Optional[Dict] = None,
    workspace_id: str = None
):
    """
    Upload and import any ISO standard
    
    Supports: PDF, DOCX, TXT, XML
    Auto-detects standard metadata
    Parses clause structure
    Generates AI summaries
    """
    
@router.get("/standards/marketplace")
async def list_available_standards():
    """
    Browse standards marketplace
    
    Returns:
    - Pre-loaded standards (ISO 9001, 14001, etc.)
    - Community-contributed standards
    - Custom standards
    """

@router.get("/standards/{standard_id}")
async def get_standard_details(standard_id: str):
    """Get full standard details with all clauses"""

@router.get("/standards/{standard_id}/clauses")
async def get_standard_clauses(
    standard_id: str,
    level: Optional[int] = None,
    auditable_only: bool = False
):
    """Get clauses with filtering"""

@router.post("/standards/{standard_id}/customize")
async def create_custom_standard(
    standard_id: str,
    workspace_id: str,
    customizations: Dict
):
    """
    Create client-specific version of standard
    
    Customizations:
    - Exclude non-applicable clauses
    - Add client-specific requirements
    - Modify template variables
    - Set approval workflows
    """

@router.post("/standards/integrate")
async def create_integrated_standard_set(
    workspace_id: str,
    standard_ids: List[str],
    integration_config: Dict
):
    """
    Create integrated management system
    
    Examples:
    - ISO 9001 + ISO 14001 (QMS + EMS)
    - ISO 9001 + ISO 13485 (QMS + Medical)
    - ISO 27001 + ISO 22301 (Security + BCM)
    """

# backend/api/routes/templates.py

@router.post("/templates/generate")
async def generate_templates_for_standard(
    standard_id: str,
    style: str = "comprehensive",
    industries: List[str] = None
):
    """
    AI-generate templates for all clauses in standard
    
    Styles:
    - minimal: Basic compliance
    - standard: Typical implementation
    - comprehensive: Detailed procedures
    - advanced: Best practices included
    """

@router.get("/templates/marketplace")
async def browse_template_marketplace(
    standard: Optional[str] = None,
    industry: Optional[str] = None,
    rating_min: float = 4.0
):
    """
    Browse community/commercial templates
    
    Filters:
    - By standard (ISO 9001, etc.)
    - By industry (manufacturing, healthcare, etc.)
    - By rating
    - Free vs paid
    """

@router.post("/templates/{template_id}/customize")
async def customize_template(
    template_id: str,
    workspace_id: str,
    customizations: Dict
):
    """
    Fork and customize a template for client
    
    Customizations:
    - Add/remove sections
    - Modify variables
    - Change formatting
    - Add company branding
    """

# backend/api/routes/workspaces.py

@router.post("/workspaces/")
async def create_client_workspace(workspace: ClientWorkspace):
    """Create new client workspace"""

@router.get("/workspaces/{workspace_id}")
async def get_workspace(workspace_id: str):
    """Get workspace details"""

@router.post("/workspaces/{workspace_id}/add-standard")
async def add_standard_to_workspace(
    workspace_id: str,
    standard_id: str,
    configuration: Optional[ClientConfiguration] = None
):
    """Add a standard to client workspace"""

@router.get("/workspaces/{workspace_id}/dashboard")
async def get_workspace_dashboard(workspace_id: str):
    """
    Get workspace dashboard data
    
    Returns:
    - Active standards
    - Compliance status
    - Recent documents
    - Pending artifacts
    - Upcoming audits
    """

@router.post("/workspaces/{workspace_id}/generate-manual")
async def generate_integrated_manual(
    workspace_id: str,
    standards: List[str],
    style: str = "integrated"
):
    """
    Generate integrated management system manual
    
    Combines multiple standards into single manual
    Eliminates redundant sections
    Shows cross-references
    """
```

---

## 🎨 User Interface Updates

### Landing Page - Standard Selection

```
┌───────────────────────────────────────────────────────────────┐
│  ISO Helper - Universal Standards Platform         [My Account]│
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  🎯 What standard(s) do you need?                             │
│                                                                │
│  Popular Standards                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ ISO 9001    │  │ ISO 14001   │  │ ISO 27001   │          │
│  │ Quality     │  │ Environment │  │ Information │          │
│  │ 📘 2015     │  │ 📗 2015     │  │ Security    │          │
│  │             │  │             │  │ 📕 2022     │          │
│  │ [Select]    │  │ [Select]    │  │ [Select]    │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│                                                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ ISO 45001   │  │ ISO 13485   │  │ ISO 22000   │          │
│  │ OH&S        │  │ Medical Dev │  │ Food Safety │          │
│  │ 📙 2018     │  │ 📘 2016     │  │ 📗 2018     │          │
│  │ [Select]    │  │ [Select]    │  │ [Select]    │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│                                                                │
│  ✨ Need Multiple Standards?                                  │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ [✓] Integrate standards (shared procedures/audits)      │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                                │
│  📤 Upload Your Own Standard                                  │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Drop ISO document here (PDF, DOCX)                      │ │
│  │  We'll parse it automatically using AI                   │ │
│  │                                                           │ │
│  │  [Browse Files]                                          │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                                │
│  [Browse All Standards →]  [View Marketplace →]               │
└───────────────────────────────────────────────────────────────┘
```

### Workspace Dashboard

```
┌───────────────────────────────────────────────────────────────┐
│  Acme Manufacturing - Workspace Dashboard          [Settings]  │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  Active Standards                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ ISO 9001:2015  │  87% Complete  │  Next Audit: Jan 2026 │  │
│  │ ISO 14001:2015 │  65% Complete  │  Next Audit: Mar 2026 │  │
│  │ [+ Add Standard]                                         │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  Quick Actions                                                 │
│  [Generate Document]  [Create NC]  [Schedule Audit]           │
│                                                                │
│  Integrated View (QMS + EMS)                                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Shared Clauses: 15                                       │  │
│  │ Shared Procedures: 8                                     │  │
│  │ Combined Audit Plan: Available                           │  │
│  │ [View Integration Map]                                   │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  Recent Activity                                               │
│  • NC-20251022-A3F2 created (ISO 9001 - Clause 8.5)          │
│  • Document "Quality Policy" updated (ISO 9001 - Clause 5.2)  │
│  • Audit checklist generated (ISO 14001 - Environmental)      │
│                                                                │
└───────────────────────────────────────────────────────────────┘
```

### Standard Importer

```
┌───────────────────────────────────────────────────────────────┐
│  Import New Standard                                      [×]  │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  Step 1: Upload Document                                       │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  📄 ISO_27001_2022.pdf (2.4 MB)                         │  │
│  │  [✓] Uploaded successfully                              │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  Step 2: AI Analysis Complete ✓                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Detected Information:                                   │  │
│  │  • Name: ISO/IEC 27001                                   │  │
│  │  • Version: 2022                                         │  │
│  │  • Category: Information Security                        │  │
│  │  • Clauses Found: 93                                     │  │
│  │  • Language: English                                     │  │
│  │                                                           │  │
│  │  [Edit Metadata]                                         │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  Step 3: Generate Templates                                    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Template Style:                                         │  │
│  │  ○ Minimal (Basic compliance only)                       │  │
│  │  ● Standard (Recommended)                                │  │
│  │  ○ Comprehensive (Detailed + best practices)             │  │
│  │                                                           │  │
│  │  Industry Focus: [IT Services ▼]                         │  │
│  │  Company Size: [Medium ▼]                                │  │
│  │                                                           │  │
│  │  [✓] Generate AI templates for all clauses              │  │
│  │  Estimated time: 15-20 minutes                           │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
│  [Cancel]                           [Import & Generate →]     │
└───────────────────────────────────────────────────────────────┘
```

---

## 🌟 Advanced Features

### 1. Standard Integration Mapper

Shows how clauses align across multiple standards:

```python
class StandardIntegrationMapper:
    """Map aligned requirements across standards"""
    
    async def map_standards(
        self,
        standard_ids: List[str]
    ) -> Dict:
        """
        Find clause alignments across standards
        
        Example Result:
        {
            "context_understanding": {
                "iso9001": "4.1",
                "iso14001": "4.1",
                "iso45001": "4.1",
                "alignment": "exact",
                "shared_procedure": "Context Analysis Procedure"
            },
            "risk_management": {
                "iso9001": "6.1",
                "iso14001": "6.1",
                "iso27001": "6.1.2",
                "alignment": "similar",
                "notes": "ISO 27001 has more detailed risk assessment"
            }
        }
        """
```

### 2. Compliance Gap Analysis

Compare client's current state vs requirements:

```python
@router.post("/workspaces/{workspace_id}/gap-analysis")
async def perform_gap_analysis(
    workspace_id: str,
    standard_id: str
):
    """
    Analyze compliance gaps
    
    Returns:
    - Missing documents
    - Incomplete procedures
    - Non-conformities
    - Risk areas
    - Implementation timeline
    - Cost estimate
    """
```

### 3. Template Marketplace

Community/commercial template sharing:

```python
class TemplateMarketplace:
    """Marketplace for buying/selling templates"""
    
    async def publish_template(
        self,
        template_id: str,
        price: float,
        license: str
    ):
        """Publish template for sale/sharing"""
    
    async def search_templates(
        self,
        filters: Dict
    ) -> List[StandardTemplate]:
        """Search marketplace"""
    
    async def purchase_template(
        self,
        template_id: str,
        workspace_id: str
    ):
        """Buy and add template to workspace"""
```

### 4. White-Label for Consultants

```python
class WhiteLabelConfig(BaseModel):
    """White-label configuration for consulting firms"""
    
    firm_name: str
    logo: str
    primary_color: str
    domain: str  # custom-domain.com
    email_templates: Dict
    report_headers: Dict
    
    # Revenue sharing
    template_commission: float = 0.30  # 30% commission on sales
    subscription_commission: float = 0.20
```

---

## 📊 Database Schema Updates

```sql
-- New tables for multi-ISO platform

CREATE TABLE iso_standards (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100),
    full_title VARCHAR(500),
    standard_number VARCHAR(20),
    version VARCHAR(10),
    category VARCHAR(50),
    published_date DATE,
    status VARCHAR(20),
    source_file VARCHAR(500),
    import_date TIMESTAMP,
    customizations JSONB
);

CREATE TABLE iso_clauses (
    id VARCHAR(50) PRIMARY KEY,
    standard_id VARCHAR(50) REFERENCES iso_standards(id),
    clause_number VARCHAR(20),
    title VARCHAR(200),
    content TEXT,
    clause_type VARCHAR(20),
    level INTEGER,
    parent_clause VARCHAR(20),
    is_mandatory BOOLEAN,
    is_auditable BOOLEAN,
    requires_documentation BOOLEAN,
    ai_summary TEXT,
    keywords TEXT[]
);

CREATE TABLE standard_templates (
    id VARCHAR(50) PRIMARY KEY,
    standard_id VARCHAR(50) REFERENCES iso_standards(id),
    clause_id VARCHAR(50) REFERENCES iso_clauses(id),
    template_name VARCHAR(200),
    template_file VARCHAR(500),
    template_type VARCHAR(50),
    industries TEXT[],
    company_sizes TEXT[],
    author VARCHAR(100),
    version VARCHAR(10),
    license VARCHAR(50),
    price DECIMAL(10,2),
    usage_count INTEGER,
    rating DECIMAL(3,2)
);

CREATE TABLE client_workspaces (
    id VARCHAR(50) PRIMARY KEY,
    client_name VARCHAR(200),
    client_type VARCHAR(50),
    industry VARCHAR(100),
    company_size VARCHAR(20),
    region VARCHAR(50),
    active_standards TEXT[],
    branding JSONB,
    settings JSONB,
    plan VARCHAR(50),
    created_date TIMESTAMP
);

CREATE TABLE workspace_standards (
    workspace_id VARCHAR(50) REFERENCES client_workspaces(id),
    standard_id VARCHAR(50) REFERENCES iso_standards(id),
    configuration JSONB,
    included_clauses TEXT[],
    excluded_clauses TEXT[],
    PRIMARY KEY (workspace_id, standard_id)
);

CREATE TABLE integrated_standard_sets (
    id VARCHAR(50) PRIMARY KEY,
    workspace_id VARCHAR(50) REFERENCES client_workspaces(id),
    name VARCHAR(200),
    standard_ids TEXT[],
    integration_mapping JSONB,
    shared_procedures TEXT[],
    created_date TIMESTAMP
);
```

---

## 🚀 Implementation Roadmap

### Phase 1: Core Multi-ISO Infrastructure (4-6 weeks)
- [ ] Universal ISO standard model
- [ ] ISO importer (PDF/DOCX parsing)
- [ ] AI-powered clause extraction
- [ ] Template generation engine
- [ ] Client workspace model
- [ ] Database migrations

### Phase 2: UI & Workspace Management (3-4 weeks)
- [ ] Standard selection interface
- [ ] Import wizard
- [ ] Workspace dashboard
- [ ] Standard configuration tools
- [ ] Template customization UI

### Phase 3: Integration Features (3-4 weeks)
- [ ] Standard integration mapper
- [ ] Shared procedure identification
- [ ] Combined audit planning
- [ ] Integrated manual generation

### Phase 4: Marketplace & Community (4-5 weeks)
- [ ] Template marketplace
- [ ] Sharing/selling platform
- [ ] Rating and review system
- [ ] Community templates
- [ ] Revenue sharing system

### Phase 5: Advanced Features (4-6 weeks)
- [ ] Gap analysis engine
- [ ] White-label capabilities
- [ ] Multi-language support
- [ ] Advanced reporting
- [ ] API for integrations

**Total Estimated Time**: 18-25 weeks (4.5-6 months)

---

## 💰 Business Model Updates

### Pricing Tiers

**Free Tier:**
- 1 standard (ISO 9001)
- Pre-built templates only
- 100 MB storage
- Community support

**Professional ($99/month):**
- Up to 3 standards
- Custom templates
- 1 GB storage
- Standard integration
- Priority support

**Enterprise ($499/month):**
- Unlimited standards
- Upload custom standards
- Unlimited storage
- White-label option
- Template marketplace access
- Dedicated support

**Consultant Edition ($299/month):**
- Unlimited client workspaces
- Template marketplace seller access
- 30% commission on template sales
- White-label capabilities
- Priority support

---

## 🎯 Success Metrics

- Number of standards in library: **Target 50+ by end of year**
- Client workspaces created: **Target 1,000+**
- Templates in marketplace: **Target 500+**
- Average implementation time reduction: **Target 60%**
- Client satisfaction score: **Target 4.5/5.0**

---

This transforms ISO Helper from a single-standard tool into a **comprehensive ISO management platform** that can handle any standard, any client, any industry! 🚀
