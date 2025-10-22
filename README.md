# ISO Helper - Universal ISO Standards Platform

An AI-powered platform for managing, generating, and maintaining documentation for **any ISO standard**. Supporting ISO 9001, 14001, 27001, 45001, and custom standards with intelligent automation and multi-tenant architecture.

## 🎯 Vision

Transform compliance documentation from a burden into an intelligent, automated process. ISO Helper is not just an ISO 9001 tool - it's a **universal ISO management hub** where:

- **Any ISO standard** can be uploaded and managed (Quality, Environmental, Security, OH&S, etc.)
- **AI-powered intelligence** generates comprehensive, client-specific documentation
- **Multi-standard integration** for organizations with multiple certifications
- **Client workspaces** provide isolated, customizable environments
- **Template marketplace** enables sharing and monetization

## 🌟 Key Capabilities

- **Universal ISO Importer**: Upload any ISO standard (PDF/DOCX), AI parses structure automatically
- **AI Document Generation**: Intelligent, context-aware content creation for any standard
- **Multi-Standard Integration**: Combine ISO 9001 + 14001 + 27001 with shared procedures
- **Artifact Management**: Non-conformities, corrective actions, audits, training records
- **Client Workspaces**: Multi-tenant architecture for consultants managing multiple clients
- **Template Marketplace**: Share or sell custom templates
- **White-Label Ready**: Rebrand for consulting firms
- **Version Management**: Seamlessly update when new standard versions release

## 📋 Current Status: MVP Phase 1

### ✅ Completed Features

**Epic 1: ISO 9001 Foundation** (Phase 1 - 85% Complete)
- ✅ FastAPI backend structure with REST API
- ✅ Document generator service with Jinja2 templating
- ✅ **15 comprehensive ISO 9001:2015 templates** (90+ KB, ~30 pages)
  - Complete coverage: Context, Leadership, Planning, Support, Operation, Evaluation, Improvement
  - Dynamic variables and conditional logic
  - Industry and company size adaptations
- ✅ Template metadata system (15 clauses mapped)
- ✅ Configuration management with Pydantic
- ✅ Test suite with full validation
- ✅ Comprehensive documentation

### 🚧 In Progress (Phase 1 - Final 15%)
- ⏳ Connect API endpoints to document generator
- ⏳ PDF/DOCX export functionality

### 📅 Planned Features

**Phase 2: Multi-ISO Platform** (4-6 months)
- 🎯 Universal ISO standard importer (any ISO standard)
- 🎯 AI-powered clause parsing and template generation
- 🎯 Client workspace management (multi-tenant)
- 🎯 Artifact engine (NC, CA, audits, training records)
- 🎯 Standard integration mapper (ISO 9001 + 14001 + 27001)
- 🎯 Template marketplace (share/sell templates)

**Phase 3: Enterprise Features** (6-9 months)
- White-label capabilities for consultants
- Gap analysis and compliance intelligence
- Multi-language support (ES, FR, DE, PT)
- Advanced reporting and analytics
- ERP/DMS integrations

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- pip
- (Optional) Virtual environment tool

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/javierf1986/isohelper.git
cd isohelper
```

2. **Create virtual environment**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

3. **Install dependencies**
```bash
cd backend
pip install -r requirements.txt
```

4. **Configure environment**
```bash
# Copy example environment file
copy .env.example .env  # Windows
# or
cp .env.example .env    # Linux/Mac

# Edit .env and add your OpenAI API key
```

5. **Run the application**
```bash
python main.py
```

The API will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## 📁 Project Structure

```
isohelper/
├── backend/
│   ├── api/
│   │   └── routes/          # API endpoints
│   │       ├── documents.py # Document generation routes
│   │       ├── templates.py # Template management routes
│   │       ├── standards.py # Multi-ISO standard management (Phase 2)
│   │       ├── workspaces.py # Client workspace management (Phase 2)
│   │       ├── artifacts.py # NC, CA, audits, etc. (Phase 2)
│   │       └── compliance.py # Compliance checking (Phase 2)
│   ├── services/
│   │   ├── document_generator.py # Core generation logic
│   │   ├── document_converter.py # MarkItDown integration
│   │   ├── iso_importer.py # Universal ISO parser (Phase 2)
│   │   └── artifact_engine.py # Artifact management (Phase 2)
│   ├── models/              # Data models
│   │   ├── iso_standard.py  # Universal standard model (Phase 2)
│   │   ├── client_workspace.py # Multi-tenant model (Phase 2)
│   │   └── artifacts.py     # NC, CA, audit models (Phase 2)
│   ├── utils/               # Helper functions
│   ├── main.py             # FastAPI application
│   └── requirements.txt    # Python dependencies
├── config/
│   └── settings.py         # Configuration management
├── templates/
│   ├── iso9001/            # ISO 9001:2015 clause templates (15 files)
│   ├── iso14001/           # ISO 14001 templates (Phase 2)
│   ├── iso27001/           # ISO 27001 templates (Phase 2)
│   └── [other-standards]/  # Dynamically created (Phase 2)
├── frontend/               # React frontend (planned)
├── tests/                  # Test files
└── docs/                   # Additional documentation
    ├── MULTI_ISO_PLATFORM_ARCHITECTURE.md  # Multi-ISO platform design
    ├── ARTIFACTS_AND_UPDATES_SYSTEM.md     # Artifact management design
    └── [other docs]
```

## 🔧 Configuration

Edit `.env` file to configure:

```env
# Environment
ENVIRONMENT=development
DEBUG=True

# AI Configuration
OPENAI_API_KEY=your_api_key_here
AI_MODEL=gpt-4
AI_TEMPERATURE=0.7

# Paths
DOCUMENTS_PATH=./generated_documents
TEMPLATES_PATH=./templates/iso9001
```

## 📖 API Usage Examples

### Generate a Single Document

```bash
curl -X POST "http://localhost:8000/api/v1/documents/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "ABC Manufacturing",
    "industry": "automotive",
    "company_size": "medium",
    "clauses": ["4.1", "4.2"],
    "language": "en"
  }'
```

### List Available Templates

```bash
curl "http://localhost:8000/api/v1/templates/"
```

### Health Check

```bash
curl "http://localhost:8000/health"
```

## 🧪 Testing

### Run Document Generator Tests
```bash
python tests/test_manual.py
```

### Run API Tests (requires server running)
```bash
python tests/test_api_quick.py
```

### Run All Tests with Pytest
```bash
pytest tests/
```

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3.10+
- **AI/LLM**: OpenAI GPT-4, LangChain
- **Document Processing**: Microsoft MarkItDown, python-docx
- **Database**: SQLAlchemy (SQLite for dev, PostgreSQL for prod)
- **Frontend** (planned): React + Tailwind CSS

## 📈 Roadmap

### Phase 1: ISO 9001 Foundation (Current - 85% Complete)
- [x] FastAPI backend structure
- [x] Document generator with Jinja2
- [x] 15 comprehensive ISO 9001:2015 templates
- [x] Template metadata system
- [x] Configuration management
- [x] Test suite validation
- [ ] Connect API endpoints
- [ ] PDF/DOCX export

### Phase 2: Multi-ISO Platform (4-6 months)
- [ ] Universal ISO standard model
- [ ] ISO importer (PDF/DOCX parsing with AI)
- [ ] AI-powered clause extraction
- [ ] Client workspace management (multi-tenant)
- [ ] Template generation engine (any standard)
- [ ] Artifact management (NC, CA, audits)
- [ ] Standard integration mapper
- [ ] Template marketplace

### Phase 3: Enterprise Features (6-9 months)
- [ ] White-label capabilities
- [ ] Gap analysis engine
- [ ] Multi-language support (ES, FR, DE, PT)
- [ ] Advanced reporting and analytics
- [ ] ERP/DMS integrations
- [ ] Mobile app
- [ ] API for third-party integrations

### Future Vision
- AI-powered continuous compliance monitoring
- Predictive analytics for audit readiness
- Blockchain-based certification verification
- Industry-specific accelerators
- Automated regulatory update tracking

## 🤝 Contributing

This is currently a private development project. For questions or collaboration:

Contact: javierf1986@github

## 📄 License

[To be determined]

## 🔗 Related Resources

- [ISO 9001:2015 Standard](https://www.iso.org/standard/62085.html)
- [Microsoft MarkItDown](https://github.com/microsoft/markitdown)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Version**: 0.1.0  
**Last Updated**: 2025-10-22  
**Status**: Active Development
