# Task-Tracker

A FastAPI + vanilla JS Kanban task tracker, built across Modules 1-3 and extended with a
mid-course checkpoint (due dates/overdue filtering and tags/labels — see
[docs/midcourse/](docs/midcourse/)).

## Run the backend

```bash
cd task-tracker/backend
python -m venv venv        # first time only
venv\Scripts\Activate.ps1  # Windows PowerShell; use `source venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- Health check: `curl http://localhost:8000/health`

Storage is in-memory only — restarting the backend clears all tasks.

## Open the frontend

The frontend is a static `index.html` that calls the backend at `http://localhost:8000`, so it
must be served (not opened via `file://`) from an origin the backend's CORS config allows
(`http://localhost:5500`, `http://127.0.0.1:5500`, or `http://localhost:5173`):

```bash
cd task-tracker/frontend
python -m http.server 5500
```

Then open http://localhost:5500/index.html in a browser, with the backend already running.

## Run the tests

```bash
cd task-tracker/backend
venv\Scripts\python.exe -m pytest tests/ -v
```

## Project docs

- [task-tracker/backend/README.md](task-tracker/backend/README.md) — backend-specific setup notes
- [docs/midcourse/](docs/midcourse/) — mid-course checkpoint deliverables: user stories,
  mini-ADR, prompt log, verification log, and reflection for the due-dates/overdue and
  tags/labels features
