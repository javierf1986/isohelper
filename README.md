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

**Epic 1: Documentation Core Engine**
- ✅ FastAPI backend structure
- ✅ Document generator service
- ✅ Template repository with 5 ISO clauses (4.1, 4.2, 5.1, 6.1, 8.1)
- ✅ MarkItDown integration for document conversion
- ✅ API endpoints for document generation

### 🚧 In Progress
- Configuration and environment setup
- Frontend interface (planned)

### 📅 Planned Features (Phase 2-3)
- Epic 2: Compliance Intelligence (clause mapping, gap analysis)
- Epic 3: Version Control & Updates
- Epic 4: Full Export & Integration Layer
- Epic 5: Enhanced AI autonomy and learning

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
│   │       └── compliance.py # Compliance checking (Phase 2)
│   ├── services/
│   │   ├── document_generator.py # Core generation logic
│   │   └── document_converter.py # MarkItDown integration
│   ├── models/              # Data models
│   ├── utils/               # Helper functions
│   ├── main.py             # FastAPI application
│   └── requirements.txt    # Python dependencies
├── config/
│   └── settings.py         # Configuration management
├── templates/
│   └── iso9001/            # ISO 9001 clause templates
│       ├── clause_4_1_context.md
│       ├── clause_4_2_interested_parties.md
│       ├── clause_5_1_leadership.md
│       ├── clause_6_1_risks_opportunities.md
│       └── clause_8_1_operational_planning.md
├── frontend/               # React frontend (planned)
├── tests/                  # Test files
└── docs/                   # Additional documentation
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

### Phase 1 (Current - MVP)
- [x] Project structure
- [x] FastAPI backend
- [x] Document generator core
- [x] Basic templates (5 clauses)
- [x] MarkItDown integration
- [ ] Environment configuration
- [ ] Basic testing

### Phase 2 (Next 2-3 months)
- [ ] Complete all ISO 9001:2015 clause templates
- [ ] AI-enhanced content generation
- [ ] Compliance checking engine
- [ ] Gap analysis tool
- [ ] React frontend interface

### Phase 3 (4-6 months)
- [ ] Version control system
- [ ] Automated updates
- [ ] Full export capabilities (DOCX, PDF)
- [ ] API integrations
- [ ] Multi-language support

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
