# API Testing Guide

## 🚀 Server Status
The FastAPI server is running at: **http://localhost:8000**

## 📖 Interactive Documentation
Open in browser: **http://localhost:8000/docs**

---

## 🧪 Quick API Tests

### 1. Health Check
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "environment": "development"
}
```

---

### 2. Root Endpoint
```bash
curl http://localhost:8000/
```

**Expected Response:**
```json
{
  "message": "ISO 9001 AI Documentation Generator API",
  "version": "0.1.0",
  "status": "operational",
  "docs": "/docs"
}
```

---

### 3. List Available Templates
```bash
curl http://localhost:8000/api/v1/templates/
```

**Expected Response:**
```json
[]
```
*Note: This returns empty for now - implementation pending*

---

### 4. Generate ISO 9001 Document
```bash
curl -X POST "http://localhost:8000/api/v1/documents/generate" \
  -H "Content-Type: application/json" \
  -d "{
    \"company_name\": \"TechCorp Industries\",
    \"industry\": \"technology\",
    \"company_size\": \"large\",
    \"clauses\": [\"4.1\", \"4.2\", \"5.1\"],
    \"language\": \"en\",
    \"custom_context\": \"We develop AI-powered software solutions\"
  }"
```

**Expected Response:**
```json
{
  "document_id": "temp-001",
  "status": "pending",
  "created_at": "2025-10-22T13:30:00",
  "download_url": null
}
```

---

## 🧪 Using PowerShell (Windows)

### Test with PowerShell:
```powershell
# Health Check
Invoke-RestMethod -Uri "http://localhost:8000/health" | ConvertTo-Json

# Generate Document
$body = @{
    company_name = "ABC Manufacturing"
    industry = "automotive"
    company_size = "medium"
    clauses = @("4.1", "4.2")
    language = "en"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/documents/generate" -Method POST -Body $body -ContentType "application/json" | ConvertTo-Json
```

---

## 🐍 Using Python Script

Run the included test script:
```bash
python test_manual.py
```

This will:
- ✅ Generate single ISO 9001 document (Clause 4.1)
- ✅ Generate complete manual with multiple clauses
- ✅ Save documents to `./generated_documents/`
- ✅ Show preview of generated content

---

## 📂 Generated Documents Location

All generated documents are saved to:
```
./generated_documents/
```

Example files:
- `Company_Name_ISO9001_Clause_4_1.md`
- `Company_Name_ISO9001_Complete_Manual.md`

---

## 🔍 Available ISO 9001 Clauses

Currently implemented templates:
- **4.1** - Understanding the Organization and Its Context
- **4.2** - Understanding Needs and Expectations of Interested Parties
- **5.1** - Leadership and Commitment
- **6.1** - Actions to Address Risks and Opportunities
- **8.1** - Operational Planning and Control

---

## 🛑 Stop the Server

To stop the FastAPI server:
```bash
# Press CTRL+C in the terminal where server is running
```

Or find and kill the process:
```powershell
# Find the process
Get-Process python | Where-Object {$_.MainWindowTitle -like "*uvicorn*"}

# Kill by PID
Stop-Process -Id <PID>
```

---

## 📊 Test Results Summary

✅ **Working Features:**
- FastAPI server startup
- API documentation (Swagger UI)
- Health check endpoint
- Document generation engine
- Template system with variable substitution
- Multi-clause manual generation

⏳ **Pending Implementation:**
- Template listing endpoint (returns empty)
- Document retrieval by ID
- Actual document generation via API (currently placeholder)
- MarkItDown PDF/DOCX export
- AI content enhancement

---

## 🎯 Next Development Steps

1. **Connect API to Document Generator**
   - Wire up `/documents/generate` to actual generator service
   - Implement document storage and retrieval
   - Add background task processing

2. **Add AI Enhancement**
   - Integrate OpenAI GPT-4
   - Enhance template content with company-specific details
   - Add natural language input processing

3. **Export Capabilities**
   - Implement MarkItDown for PDF export
   - Add DOCX export with formatting
   - Add HTML export for web viewing

4. **Database Integration**
   - Set up SQLite for document metadata
   - Add ChromaDB for semantic search
   - Implement version tracking

---

**Last Updated:** 2025-10-22  
**Status:** ✅ MVP Core Functional
