# GlobeTrotter

FastAPI + SQLAlchemy travel planner with an optional Gemini itinerary agent and
a deterministic fallback. Odoo and Docker are not required.

## Run the backend (Windows PowerShell)

From `Odoo-Hackathon-Ashwin`:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r globetrotter\backend\requirements.txt
Copy-Item globetrotter\.env.example globetrotter\.env
Set-Location globetrotter
..\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

Put the Gemini key in `globetrotter/.env`. Without it, the planner still works
and returns a proposal with `source: rules`.

Open `http://127.0.0.1:8001/docs` for the interactive API documentation during local development.

## Validate the AI feature

```powershell
Set-Location globetrotter
..\.venv\Scripts\python.exe -m pytest ai_agent\tests integration\tests -q
```

The suite covers recommendation filtering, budgets, schedule validation,
Gemini failure fallback, proposal persistence, transactional apply, 404/422
responses, and duplicate-apply protection.

## AI endpoints

- `POST /api/v1/trips/{trip_id}/planner/proposals`
- `GET /api/v1/trips/{trip_id}/planner/proposals/{proposal_id}`
- `POST /api/v1/trips/{trip_id}/planner/proposals/{proposal_id}/apply`

The trip must already contain at least one stop. The agent uses only activities
from the catalog for each stop's city and does not alter the itinerary until the
apply endpoint is called.

## Run the complete application

The development command starts FastAPI and React together. If a healthy
GlobeTrotter API or frontend is already using its normal port, the launcher
reuses it instead of failing with "Port 5173 is already in use":

```powershell
Set-Location globetrotter\frontend
Copy-Item .env.example .env
npm install
npm run dev
```

Open `http://localhost:5173`. Create an account through the real signup screen.
To give that account admin access, add its email to `ADMIN_EMAILS` in the backend
`.env` before signup. The frontend reads its backend URL from
`VITE_API_BASE_URL`.

## Full feature set

- JWT signup, login, session restoration, profile editing, and admin guards.
- Trip CRUD, multi-city stops, catalog activities, itinerary timeline/calendar,
  reorder-ready APIs, expense tracking, and category/day budget analytics.
- Gemini proposal generation with deterministic validation and fallback, plus
  explicit review-before-apply.
- City/activity discovery, saved cities, public trip publishing, community
  browsing, share links, and private trip copying.
- Persistent light/dark travel-journal theme and responsive mobile navigation.

## Validate everything

```powershell
# Backend and AI tests (13 tests)
..\.venv\Scripts\python.exe -m pytest -q

# Frontend tests and production build
Set-Location frontend
npm test
npm run build
```

For schema upgrades, install the backend requirements and run
`..\.venv\Scripts\python.exe -m alembic upgrade head`. SQLite is the local
default; set `DATABASE_URL` to a PostgreSQL SQLAlchemy URL when deploying.
See [DEPLOYMENT.md](DEPLOYMENT.md) for production variables and release steps.
