# Project Structure

```
isohelper/
│
├── .env                        # Environment configuration (git-ignored)
├── .env.example               # Template for environment variables
├── .gitignore                 # Git ignore rules
├── README.md                  # Main project documentation
├── PROJECT_STATUS.md          # Development progress tracker
│
├── backend/                   # FastAPI Backend
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── documents.py   # Document generation endpoints
│   │       ├── templates.py   # Template management endpoints
│   │       └── compliance.py  # Compliance checking endpoints
│   │
│   ├── services/              # Business logic layer
│   │   ├── __init__.py
│   │   ├── document_generator.py  # Core document generation
│   │   └── document_converter.py  # MarkItDown integration
│   │
│   ├── models/                # Data models
│   │   └── __init__.py
│   │
│   ├── utils/                 # Utility functions
│   │   └── __init__.py
│   │
│   ├── main.py               # FastAPI application entry point
│   └── requirements.txt      # Python dependencies
│
├── config/                    # Configuration management
│   ├── __init__.py
│   └── settings.py           # Pydantic settings
│
├── templates/                 # ISO 9001 document templates
│   └── iso9001/
│       ├── __init__.py
│       ├── clause_4_1_context.md
│       ├── clause_4_2_interested_parties.md
│       ├── clause_5_1_leadership.md
│       ├── clause_6_1_risks_opportunities.md
│       └── clause_8_1_operational_planning.md
│
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── test_manual.py        # Document generator tests
│   ├── test_api_quick.py     # Quick API endpoint tests
│   ├── test_api.py           # Comprehensive API tests
│   └── test_generator.py     # Generator-specific tests
│
├── docs/                      # Additional documentation
│   ├── API_TESTING_GUIDE.md  # How to test the API
│   └── TESTING_SUMMARY.md    # Test results summary
│
├── frontend/                  # React frontend (planned)
│   └── (to be implemented)
│
└── generated_documents/       # Output directory for generated docs
    └── (auto-created, git-ignored)
```

## Key Directories Explained

### `/backend/` - Core Application
- **api/routes/**: REST API endpoints organized by feature
- **services/**: Business logic separated from API layer
- **models/**: Pydantic models for data validation
- **utils/**: Shared utility functions

### `/config/` - Configuration
- Centralized settings management
- Environment-based configuration
- Shared across all modules

### `/templates/` - ISO 9001 Templates
- Markdown templates for each ISO clause
- Variable substitution using Jinja2
- Organized by standard (iso9001/)

### `/tests/` - Test Suite
- All test files in one location
- Easy to run with pytest
- Separate files for different test types

### `/docs/` - Documentation
- Technical guides
- API documentation
- Development notes

### `/frontend/` - Web Interface (Future)
- React-based UI
- User-friendly document generation
- Dashboard and analytics

### `/generated_documents/` - Output
- Auto-created directory
- Stores all generated documents
- Git-ignored (not tracked)

## Running Components

### Start Backend Server
```bash
cd backend
python main.py
```
Server runs on: http://localhost:8000

### Run Tests
```bash
# Document generation test
python tests/test_manual.py

# API endpoint test (requires server running)
python tests/test_api_quick.py

# All tests
pytest tests/
```

### Access API Docs
http://localhost:8000/docs

## Best Practices Followed

✅ **Separation of Concerns**: API, services, and models are separate  
✅ **Configuration Management**: Centralized in config/  
✅ **Test Organization**: All tests in tests/ folder  
✅ **Documentation**: Comprehensive docs in docs/  
✅ **Git Hygiene**: .gitignore properly configured  
✅ **Modular Design**: Each module has clear responsibility  
✅ **Type Hints**: Used throughout for better IDE support  
✅ **Package Init Files**: Proper Python package structure  

---

**Last Updated:** 2025-10-22  
**Structure Version:** 1.0
