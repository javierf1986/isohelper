# ISOHelper Application: Quick Start & URL Guide

## 1. Quick Start (Windows)

### Option A: Start Both Servers (Recommended)
Simply double-click `start-servers.bat` in the project root, or run:
```cmd
start-servers.bat
```
This will open two terminal windows:
- Backend server on http://localhost:8000
- Frontend server on http://localhost:3000

### Option B: Start Servers Individually
```cmd
start-backend.bat   # Backend only
start-frontend.bat  # Frontend only
```

### Stop Servers
```cmd
stop-servers.bat
```

---

## 2. Prerequisites
- Python 3.13+ (with pip)
- Node.js 18+ (with npm)
- (Optional) Virtual environment for Python

## 3. Manual Backend Setup
1. Navigate to the backend directory:
   ```sh
   cd backend
   ```
2. Install Python dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Start the FastAPI backend:
   ```sh
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## 4. Manual Frontend Setup
1. Navigate to the frontend directory:
   ```sh
   cd frontend
   ```
2. Install frontend dependencies:
   ```sh
   npm install
   ```
3. Start the Next.js development server:
   ```sh
   npm run dev
   ```

## 5. Accessing the Application

### Main URLs
- **Frontend (User Interface):**
  - http://localhost:3000/
- **Backend (API docs):**
  - http://localhost:8000/docs (Swagger UI)
  - http://localhost:8000/redoc (ReDoc UI)

### Key API Endpoints
- **ISO Standards:** `/api/v1/iso-standards/` (NEW!)
- **Documents:** `/api/v1/documents/`
- **Templates:** `/api/v1/templates/`
- **Gap Analysis:** `/api/gap-analysis/`
- **Compliance:** `/api/v1/compliance/`
- **Authentication:** `/api/v1/auth/`
- **Export:** `/api/export/`
- **Analytics:** `/api/analytics/`

> For a full list, see the Swagger UI at `/docs`.

### Frontend Pages
- **Dashboard:** http://localhost:3000/dashboard
- **ISO Standards Library:** http://localhost:3000/iso-standards
- **Upload ISO Standard:** http://localhost:3000/iso-standards/upload
- **Generate Documents:** http://localhost:3000/generate
- **Gap Analysis:** http://localhost:3000/gap-analysis
- **Documents:** http://localhost:3000/documents

### Other Useful URLs
- **Admin Panel (if enabled):** `/admin/`
- **Generated Documents:** `/generated_documents/`

## 6. Stopping the App

### Using Batch Scripts
```cmd
stop-servers.bat
```

### Manual Method
- Press `Ctrl+C` in the terminal where the backend or frontend is running.

## 7. Troubleshooting
- Ensure ports 8000 (backend) and 3000 (frontend) are free.
- Check `.env` or `config/settings.py` for environment variables if needed.
- For database issues, check your DB connection string in the backend config.
- If you get import errors, make sure you're in the correct directory when starting servers.

## 8. New Features

### ISO Standards Management
The platform now supports uploading and managing multiple ISO standards:
- Upload PDF, DOCX, or TXT ISO standard documents
- Automatic parsing and clause extraction
- Support for ISO 9001, ISO 14001, ISO 27001, ISO 45001, and more
- View detailed clause information
- Manage multiple standards simultaneously

---
For more details, see the `README.md` files in the `backend/` and `frontend/` folders.
