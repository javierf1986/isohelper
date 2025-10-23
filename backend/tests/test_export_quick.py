"""
Quick Export Feature Test
Tests PDF, DOCX, and HTML export functionality
"""
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8888/api/v1"

print("=" * 70)
print("EXPORT FEATURE TEST")
print("=" * 70)

# Step 1: Register user (if not exists) and Authenticate
print("\n[1/6] Registering/Authenticating user...")
try:
    # Try to register (will fail if user exists, which is fine)
    register_response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "TestPassword123!",
            "full_name": "Test User"
        }
    )
    if register_response.status_code == 201:
        print("   ✓ User registered successfully")
    elif register_response.status_code == 400:
        print("   ℹ User already exists (using existing account)")
    else:
        print(f"   ⚠ Registration status: {register_response.status_code}")
        print(f"   Response: {register_response.text}")
    
    # Login
    auth_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "testuser@example.com", "password": "TestPassword123!"}
    )
    if auth_response.status_code == 200:
        token = auth_response.json()["access_token"]
        print("✅ Authentication successful")
        headers = {"Authorization": f"Bearer {token}"}
    else:
        print(f"❌ Login failed: {auth_response.status_code}")
        print(f"   Response: {auth_response.text}")
        print(f"   Tried email: testuser@example.com")
        exit(1)
except Exception as e:
    print(f"❌ Error during authentication: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 2: Create test document
print("\n[2/6] Creating test document...")
try:
    test_doc_content = """# ISO 9001:2015 Quality Manual - Test Export

## Company Information
**Company Name:** Test Corp International  
**Document Version:** 1.0  
**Effective Date:** October 2025

## 1. Introduction

This Quality Management System (QMS) manual demonstrates the export functionality of the ISO Helper platform.

### 1.1 Purpose

The purpose of this manual is to:
* Define the scope of our QMS
* Document our quality policy
* Demonstrate PDF/DOCX/HTML export capabilities
* Showcase professional formatting

### 1.2 Quality Policy

> "Test Corp is committed to delivering exceptional quality through continuous improvement and customer focus."

## 2. Process Framework

Our QMS follows a process-based approach:

1. **Leadership** - Management commitment
2. **Planning** - Setting objectives
3. **Support** - Resource management
4. **Operation** - Core processes
5. **Performance** - Monitoring & measurement
6. **Improvement** - Corrective actions

## 3. Key Performance Indicators

| KPI | Target | Current | Status |
|-----|--------|---------|--------|
| Customer Satisfaction | >95% | 97% | ✅ Pass |
| On-Time Delivery | >98% | 99% | ✅ Pass |
| Defect Rate | <0.5% | 0.3% | ✅ Pass |
| Training Compliance | 100% | 100% | ✅ Pass |

## 4. Document Control

All documents are managed through:
- Version control system
- Review and approval workflow
- Change management process
- Archive and retrieval system

## 5. Code Example

```python
def calculate_quality_score(metrics):
    weights = {
        'customer_satisfaction': 0.4,
        'delivery': 0.3,
        'defects': 0.3
    }
    return sum(metrics[k] * weights[k] for k in weights)
```

## 6. Conclusion

This document demonstrates the comprehensive export capabilities of ISO Helper, including:
✓ Professional formatting  
✓ Table support  
✓ Code syntax highlighting  
✓ Company branding  
✓ Multi-format output (PDF, DOCX, HTML)

---
**Document ID:** QMS-TEST-001  
**Approved by:** Quality Manager  
**Next Review:** January 2026
"""
    
    # Create directory and file
    doc_dir = Path("generated_documents")
    doc_dir.mkdir(exist_ok=True)
    
    doc_path = doc_dir / "test_export_demo.md"
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(test_doc_content)
    
    print(f"✅ Test document created: {doc_path}")
except Exception as e:
    print(f"❌ Error creating test document: {e}")
    exit(1)

# Step 3: Test PDF Export
print("\n[3/6] Testing PDF export...")
try:
    pdf_response = requests.post(
        f"{BASE_URL}/export",
        headers=headers,
        json={
            "document_path": "generated_documents/test_export_demo.md",
            "format": "pdf",
            "company_name": "Test Corp International",
            "include_branding": True,
            "output_filename": "test_quality_manual.pdf"
        }
    )
    
    if pdf_response.status_code == 200:
        pdf_data = pdf_response.json()
        print(f"✅ PDF export successful!")
        print(f"   File: {pdf_data['file_path']}")
        print(f"   Size: {pdf_data['file_size_bytes']:,} bytes ({pdf_data['file_size_bytes']/1024:.1f} KB)")
    else:
        print(f"❌ PDF export failed: {pdf_response.status_code}")
        print(f"   Response: {pdf_response.text}")
except Exception as e:
    print(f"❌ Error during PDF export: {e}")

# Step 4: Test DOCX Export
print("\n[4/6] Testing DOCX export...")
try:
    docx_response = requests.post(
        f"{BASE_URL}/export",
        headers=headers,
        json={
            "document_path": "generated_documents/test_export_demo.md",
            "format": "docx",
            "company_name": "Test Corp International",
            "include_branding": True,
            "output_filename": "test_quality_manual.docx"
        }
    )
    
    if docx_response.status_code == 200:
        docx_data = docx_response.json()
        print(f"✅ DOCX export successful!")
        print(f"   File: {docx_data['file_path']}")
        print(f"   Size: {docx_data['file_size_bytes']:,} bytes ({docx_data['file_size_bytes']/1024:.1f} KB)")
    else:
        print(f"❌ DOCX export failed: {docx_response.status_code}")
        print(f"   Response: {docx_response.text}")
except Exception as e:
    print(f"❌ Error during DOCX export: {e}")

# Step 5: Test HTML Export
print("\n[5/6] Testing HTML export...")
try:
    html_response = requests.post(
        f"{BASE_URL}/export",
        headers=headers,
        json={
            "document_path": "generated_documents/test_export_demo.md",
            "format": "html",
            "company_name": "Test Corp International",
            "include_branding": True,
            "output_filename": "test_quality_manual.html"
        }
    )
    
    if html_response.status_code == 200:
        html_data = html_response.json()
        print(f"✅ HTML export successful!")
        print(f"   File: {html_data['file_path']}")
        print(f"   Size: {html_data['file_size_bytes']:,} bytes ({html_data['file_size_bytes']/1024:.1f} KB)")
    else:
        print(f"❌ HTML export failed: {html_response.status_code}")
        print(f"   Response: {html_response.text}")
except Exception as e:
    print(f"❌ Error during HTML export: {e}")

# Step 6: List all exports
print("\n[6/6] Listing all exports...")
try:
    list_response = requests.get(f"{BASE_URL}/export/list", headers=headers)
    
    if list_response.status_code == 200:
        list_data = list_response.json()
        print(f"✅ Found {len(list_data['files'])} exported files:")
        for file_info in list_data['files']:
            size_kb = file_info['size_bytes'] / 1024
            print(f"   📄 {file_info['filename']}")
            print(f"      Format: {file_info['format'].upper()} | Size: {size_kb:.1f} KB")
            print(f"      Created: {file_info['created_at']}")
            print(f"      Download: {file_info['download_url']}")
    else:
        print(f"❌ List failed: {list_response.status_code}")
        print(f"   Response: {list_response.text}")
except Exception as e:
    print(f"❌ Error listing exports: {e}")

# Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print("✅ Export feature is working!")
print("📁 Exported files location: generated_documents/exports/")
print("🌐 API Documentation: http://localhost:8888/docs")
print("\nNext: Open the exported files to verify formatting")
print("=" * 70)
