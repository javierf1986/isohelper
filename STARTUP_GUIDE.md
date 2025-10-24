# ISOHelper Application: Quick Start & URL Guide

## 1. Prerequisites
- Python 3.9+
- Node.js 18+
- (Recommended) Virtual environment for Python
- (Recommended) Yarn or npm for frontend

## 2. Backend Setup
1. Navigate to the backend directory:
   ```sh
   cd backend
   ```
2. Install Python dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. (Optional) Run database migrations (if using Alembic):
   ```sh
   alembic upgrade head
   ```
4. Start the FastAPI backend:
   ```sh
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## 3. Frontend Setup
1. Navigate to the frontend directory:
   ```sh
   cd frontend
   ```
2. Install frontend dependencies:
   ```sh
   npm install
   # or
   yarn install
   ```
3. Start the Next.js development server:
   ```sh
   npm run dev
   # or
   yarn dev
   ```

## 4. Accessing the Application

### Main URLs
- **Frontend (User Interface):**
  - http://localhost:3000/
- **Backend (API docs):**
  - http://localhost:8000/docs (Swagger UI)
  - http://localhost:8000/redoc (ReDoc UI)

### Key API Endpoints
- **Artifacts:** `/api/artifacts/`
- **Languages:** `/api/languages/`
- **Authentication:** `/api/auth/`
- **Users:** `/api/users/`
- **Analytics:** `/api/analytics/`
- **Templates:** `/api/templates/`
- **Uploads:** `/api/uploads/`

> For a full list, see the Swagger UI at `/docs`.

### Other Useful URLs
- **Admin Panel (if enabled):** `/admin/`
- **Static Files:** `/static/` (if configured)
- **Generated Documents:** `/generated_documents/`

## 5. Stopping the App
- Press `Ctrl+C` in the terminal where the backend or frontend is running.

## 6. Troubleshooting
- Ensure ports 8000 (backend) and 3000 (frontend) are free.
- Check `.env` or `config/settings.py` for environment variables if needed.
- For database issues, check your DB connection string in the backend config.

---
For more details, see the `README.md` files in the `backend/` and `frontend/` folders.
