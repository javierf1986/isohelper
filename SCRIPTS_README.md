# ISO Helper - Quick Start Scripts

This directory contains convenient batch scripts for starting and stopping the development servers on Windows.

## Available Scripts

### 🚀 start-servers.bat
**Start both backend and frontend servers simultaneously**

- Opens two separate terminal windows
- Backend starts on http://localhost:8000
- Frontend starts on http://localhost:3000
- Servers continue running even after closing the initial window

**Usage:**
```cmd
start-servers.bat
```
Or simply double-click the file in Windows Explorer.

---

### 🔧 start-backend.bat
**Start only the backend server**

- Starts FastAPI backend on port 8000
- API documentation available at http://localhost:8000/docs
- Runs in the current terminal window

**Usage:**
```cmd
start-backend.bat
```

---

### 🎨 start-frontend.bat
**Start only the frontend server**

- Starts Next.js frontend on port 3000
- Accessible at http://localhost:3000
- Runs in the current terminal window

**Usage:**
```cmd
start-frontend.bat
```

---

### 🛑 stop-servers.bat
**Stop all running servers**

- Kills processes running on ports 8000 and 3000
- Cleans up both backend and frontend servers
- Safe to run even if servers aren't running

**Usage:**
```cmd
stop-servers.bat
```

---

## First Time Setup

Before using these scripts, make sure you have:

1. **Python 3.13+** installed and in your PATH
2. **Node.js 18+** installed and in your PATH
3. **Backend dependencies** installed:
   ```cmd
   cd backend
   pip install -r requirements.txt
   ```
4. **Frontend dependencies** installed:
   ```cmd
   cd frontend
   npm install
   ```

---

## Troubleshooting

### Port Already in Use
If you get an error that ports 8000 or 3000 are already in use:
```cmd
stop-servers.bat
```
Then try starting again.

### Python/Node Not Found
Make sure Python and Node.js are installed and added to your system PATH.

Check with:
```cmd
python --version
node --version
```

### Permission Errors
Run Command Prompt or PowerShell as Administrator if you encounter permission issues.

---

## What's Running?

After starting the servers, you can access:

- **Frontend:** http://localhost:3000
  - Dashboard: http://localhost:3000/dashboard
  - ISO Standards: http://localhost:3000/iso-standards
  - Document Generator: http://localhost:3000/generate
  - Gap Analysis: http://localhost:3000/gap-analysis

- **Backend API:** http://localhost:8000
  - API Documentation: http://localhost:8000/docs
  - ReDoc: http://localhost:8000/redoc

---

## Manual Startup (Alternative)

If you prefer to start servers manually or need more control:

**Backend:**
```cmd
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```cmd
cd frontend
npm run dev
```

---

For more detailed information, see `STARTUP_GUIDE.md`.
