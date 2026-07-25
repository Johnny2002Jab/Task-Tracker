Here's the complete Module 1 Task Tracker skeleton, following your ADR (JSON storage, no CRUD yet, no auth/db/docker).

## Step 1: Create folders and files

**Linux/macOS (bash):**
```bash
mkdir -p task-tracker/backend/app/routes
mkdir -p task-tracker/backend/app/services
mkdir -p task-tracker/backend/app/storage

touch task-tracker/backend/app/__init__.py
touch task-tracker/backend/app/main.py
touch task-tracker/backend/app/schemas.py
touch task-tracker/backend/app/routes/__init__.py
touch task-tracker/backend/app/routes/tasks.py
touch task-tracker/backend/app/services/__init__.py
touch task-tracker/backend/app/services/task_service.py
touch task-tracker/backend/app/storage/tasks.json

touch task-tracker/backend/requirements.txt
touch task-tracker/backend/.env.example
touch task-tracker/backend/.gitignore
touch task-tracker/backend/README.md
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path task-tracker\backend\app\routes
New-Item -ItemType Directory -Force -Path task-tracker\backend\app\services
New-Item -ItemType Directory -Force -Path task-tracker\backend\app\storage

New-Item -ItemType File -Force -Path task-tracker\backend\app\__init__.py
New-Item -ItemType File -Force -Path task-tracker\backend\app\main.py
New-Item -ItemType File -Force -Path task-tracker\backend\app\schemas.py
New-Item -ItemType File -Force -Path task-tracker\backend\app\routes\__init__.py
New-Item -ItemType File -Force -Path task-tracker\backend\app\routes\tasks.py
New-Item -ItemType File -Force -Path task-tracker\backend\app\services\__init__.py
New-Item -ItemType File -Force -Path task-tracker\backend\app\services\task_service.py
New-Item -ItemType File -Force -Path task-tracker\backend\app\storage\tasks.json

New-Item -ItemType File -Force -Path task-tracker\backend\requirements.txt
New-Item -ItemType File -Force -Path task-tracker\backend\.env.example
New-Item -ItemType File -Force -Path task-tracker\backend\.gitignore
New-Item -ItemType File -Force -Path task-tracker\backend\README.md
```

Resulting structure:
```
task-tracker/
└── backend/
    ├── app/
    │   ├── __init__.py
    │   ├── main.py
    │   ├── schemas.py
    │   ├── routes/
    │   │   ├── __init__.py
    │   │   └── tasks.py
    │   ├── services/
    │   │   ├── __init__.py
    │   │   └── task_service.py
    │   └── storage/
    │       └── tasks.json
    ├── requirements.txt
    ├── .env.example
    ├── .gitignore
    └── README.md
```

`routes/tasks.py`, `services/task_service.py`, and `tasks.json` are empty placeholders for now — no CRUD is wired in yet, per your constraints. `schemas.py` is also left empty for the same reason (no Pydantic models needed until CRUD is added).

---

## Step 2: File contents

### Open `task-tracker/backend/app/main.py` and paste the following:

```python
from datetime import datetime, timezone

from fastapi import FastAPI

app = FastAPI(
    title="Task Tracker API",
    description="Module 1 Task Tracker learning project backend.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
```

### Open `task-tracker/backend/app/__init__.py` and paste the following:

```python
```

*(empty file — marks `app` as a Python package)*

### Open `task-tracker/backend/app/routes/__init__.py` and paste the following:

```python
```

*(empty file — marks `routes` as a Python package)*

### Open `task-tracker/backend/app/services/__init__.py` and paste the following:

```python
```

*(empty file — marks `services` as a Python package)*

### Open `task-tracker/backend/app/schemas.py` and paste the following:

```python
# Pydantic models for Task Tracker will be defined here in a later step.
# Intentionally left minimal for this skeleton (no CRUD endpoints yet).
```

### Open `task-tracker/backend/app/routes/tasks.py` and paste the following:

```python
# Task-related route handlers will be added here in a later step.
# Intentionally left minimal for this skeleton (no CRUD endpoints yet).
```

### Open `task-tracker/backend/app/services/task_service.py` and paste the following:

```python
# JSON file storage read/write logic for tasks will be implemented here
# in a later step. Intentionally left minimal for this skeleton.
```

### Open `task-tracker/backend/app/storage/tasks.json` and paste the following:

```json
[]
```

### Open `task-tracker/backend/requirements.txt` and paste the following:

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
pydantic==2.9.2
python-dotenv==1.0.1
```

> Note: these versions are pinned as of this writing. After installing, run `pip freeze` in your virtual environment and compare against this list to confirm the actual resolved versions, and update `requirements.txt` if they differ.

### Open `task-tracker/backend/.env.example` and paste the following:

```
PORT=8000
APP_ENV=development
```

### Open `task-tracker/backend/.gitignore` and paste the following:

```
__pycache__/
*.pyc
.env
venv/
.venv/
.pytest_cache/
*.egg-info/
dist/
build/
.DS_Store
```

### Open `task-tracker/backend/README.md` and paste the following:

```markdown
# Task Tracker API — Module 1

A minimal FastAPI backend for the Module 1 Task Tracker learning project.

## Description

This is a learning-focused REST API built with FastAPI and Pydantic. It uses local
JSON file storage instead of a database, per the project's Module 1 architecture
decision (see ADR-001). The current scope of this skeleton is limited to a basic
application setup and a health check endpoint. CRUD endpoints, authentication,
and database integration are intentionally out of scope for this step.

## Requirements

- Python 3.10+
- pip

## Setup

1. Navigate into the backend folder:
   ```
   cd task-tracker/backend
   ```

2. Create and activate a virtual environment:

   **Linux/macOS:**
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

   **Windows (PowerShell):**
   ```
   python -m venv venv
   venv\Scripts\Activate.ps1
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Copy the example environment file:

   **Linux/macOS:**
   ```
   cp .env.example .env
   ```

   **Windows (PowerShell):**
   ```
   Copy-Item .env.example .env
   ```

## Run the server

```
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

## Test the health endpoint

```
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2026-07-21T12:00:00.000000+00:00"
}
```

## API documentation (Swagger)

Once the server is running, open your browser to:

```
http://127.0.0.1:8000/docs
```

## Project structure

```
backend/
├── app/
│   ├── main.py
│   ├── schemas.py
│   ├── routes/
│   │   └── tasks.py
│   ├── services/
│   │   └── task_service.py
│   └── storage/
│       └── tasks.json
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Out of scope for this skeleton

- CRUD endpoints for tasks
- Authentication / user accounts
- Database implementation
- Docker / cloud deployment
- Frontend files
- Notifications / real-time updates
```

---

## Step 3: Create virtual environment, install dependencies, start server

**Linux/macOS:**
```bash
cd task-tracker/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

**Windows (PowerShell):**
```powershell
cd task-tracker\backend
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

---

## Step 4: Test /health

```bash
curl http://127.0.0.1:8000/health
```

Expected response shape:
```json
{
  "status": "ok",
  "timestamp": "2026-07-21T12:00:00.000000+00:00"
}
```

---

## Step 5: Swagger UI

Open in your browser:
```
http://127.0.0.1:8000/docs
```