# GlobeTrotter — Personalized Travel Planning Platform

A full-stack travel itinerary planner built for a hackathon. Users can sign up, create multi-city trips, add stops and activities, track budgets automatically, and share trips publicly.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy |
| Migrations | Alembic |
| Database | SQLite (dev) — see `alembic.ini` / `database.py` for connection config |
| Auth | JWT (access token), bcrypt password hashing |
| Frontend | React (Vite) |
| Deployment | Procfile-based (see `DEPLOYMENT.md`) |
| Package management | `pip` (backend), `npm` (frontend) |

---

## Project Structure

```
globetrotter/
├── ai_agent/                   # AI planning/recommendation helpers
├── backend/
│   ├── alembic/                 # Database migration scripts
│   ├── models/                  # SQLAlchemy models (User, Trip, TripStop, City, Activity, ItineraryItem, AIProposal)
│   ├── routers/
│   │   ├── admin_router.py       # Admin-only endpoints
│   │   ├── agent_router.py       # AI planning agent endpoints
│   │   ├── auth_router.py        # Signup, login, current user
│   │   ├── catalog_router.py     # City / activity catalog & search
│   │   ├── public_router.py      # Public shared-trip view
│   │   ├── trip_router.py        # Trip / stop / itinerary / budget CRUD
│   │   └── trip_v1_router.py     # Versioned trip API (v1)
│   ├── schemas/                  # Pydantic request/response schemas
│   ├── seed_data/                # Sample JSON data (cities, activities, demo trip)
│   ├── services/                 # Business logic (security, budget, recommendations, validation, AI)
│   ├── __init__.py
│   ├── auth.py                   # Shared auth helpers/dependencies
│   ├── database.py               # SQLAlchemy engine, session, Base
│   ├── main.py                   # FastAPI app entrypoint
│   ├── migrations.py             # Migration helper/runner
│   ├── seed.py                   # DB seeding script
│   └── requirements.txt
├── contracts/                    # API contracts and JSON schemas for AI integration
├── frontend/                     # React (Vite) app
├── integration/                  # Postman collection, demo script, test data
├── .env.example
├── .gitignore
├── alembic.ini                   # Alembic configuration
├── DEPLOYMENT.md                 # Deployment instructions
├── HACKATHON.md                  # Hackathon submission notes
├── package-lock.json
├── Procfile                      # Process definition for deployment (e.g. Heroku-style)
└── README.md
```

---

## Features

- **Authentication** — signup, login (JWT), get current user
- **Trips** — create, list, view, update, delete (v1 endpoints available under `trip_v1_router`)
- **Trip stops** — add cities/dates to a trip, reorder, edit, delete
- **Itinerary items** — activities within a stop, with cost and scheduling
- **Budget** — automatic cost breakdown, recalculated on every stop/item change
- **Public sharing** — generate a shareable public link for a trip
- **City & activity catalog** — browse and filter by country/cost/type
- **Admin dashboard endpoints** — platform usage / management (see `admin_router.py`)
- **AI planning agent** — proposal generation for itineraries (see `ai_agent/`, `agent_router.py`)

---

## Setup Instructions

### Prerequisites
- Python 3.12+ (check with `python3 --version`)
- Node.js + npm
- Git

### 1. Clone the repo
```bash
git clone https://github.com/ashwinlulla06/Odoo-Hackathon.git
cd Odoo-Hackathon/globetrotter
```

### 2. Backend setup

Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate          # Linux/Mac
# .venv\Scripts\activate           # Windows
```

Install dependencies:
```bash
pip install --upgrade pip
pip install -r backend/requirements.txt
```

Create your `.env` file:
```bash
cp .env.example backend/.env
```

Edit `backend/.env` and set:
```
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
DATABASE_URL=sqlite:///./globetrotter.db
```

### 3. Run database migrations

```bash
alembic upgrade head
```

(Uses `alembic.ini` at the project root — run this from `globetrotter/`.)

### 4. (Optional) Seed the database

```bash
python backend/seed.py
```

### 5. Run the backend

From `globetrotter/` (backend is a package, imported as `backend.main`):
```bash
uvicorn backend.main:app --reload
```

Server runs at **http://127.0.0.1:8000**
Interactive API docs at **http://127.0.0.1:8000/docs**

### 6. Frontend setup

```bash
cd frontend
npm ci
npm run dev
```

Frontend runs at **http://localhost:5173** (Vite default)

> Backend CORS must include your frontend's dev server origin — check `allow_origins` in `backend/main.py`.

---

## API Endpoints Overview

| Router | Prefix | Description |
|---|---|---|
| `auth_router` | `/auth` | Signup, login, current user |
| `trip_router` | `/api/trips` | Trip / stop / itinerary / budget / share CRUD |
| `trip_v1_router` | `/api/v1/trips` | Versioned trip API |
| `catalog_router` | — | City and activity search/catalog |
| `public_router` | — | Public read-only shared-trip view |
| `admin_router` | `/admin` | Admin-only platform management |
| `agent_router` | — | AI planning agent / proposal generation |

Full interactive reference: `/docs` (Swagger UI) once the server is running — exact paths, params, and schemas for every endpoint live there.

---

## Testing the API

### Swagger UI (recommended)
Go to `http://127.0.0.1:8000/docs`, use "Try it out" on any endpoint.

For protected routes: call `/auth/login` first, copy the `access_token`, click **Authorize** (padlock icon), paste the token, then call protected endpoints.

### curl
```bash
# Signup
curl -X POST http://127.0.0.1:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com", "password": "secret123"}'

# Login
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=secret123"

# Authenticated request
curl http://127.0.0.1:8000/auth/me \
  -H "Authorization: Bearer <token>"
```

### Postman
A ready-to-import collection is available at:
`integration/postman/globetrotter.postman_collection.json`

---

## Deployment

See `DEPLOYMENT.md` for full instructions. The `Procfile` defines the process command used by the hosting platform (e.g. Heroku-style deploys).

---

## Known Setup Gotchas

| Issue | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'email_validator'` | `pip install "pydantic[email]"` |
| `AttributeError: module 'bcrypt' has no attribute '__about__'` | `pip install "bcrypt==4.0.1"` (passlib compatibility issue with newer bcrypt) |
| Tables not created / out of sync | Run `alembic upgrade head` — don't rely solely on `create_all()` once migrations are in use |
| `ModuleNotFoundError: No module named 'backend'` | Run `uvicorn` from `globetrotter/` (the parent of `backend/`), not from inside `backend/` itself |
| Frontend requests blocked by browser (CORS) | Confirm `CORSMiddleware` in `main.py` includes your frontend's actual dev server origin |
| `{"detail": "Not Found"}` in browser | You likely visited `/` directly — there's no route at root; use `/docs` instead |

---

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `SECRET_KEY` | JWT signing secret — keep private, never commit | `<random 64-char hex string>` |
| `ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime | `1440` (1 day) |
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./globetrotter.db` |

`.env` is git-ignored — copy `.env.example` and fill in your own values, never commit real secrets.

---

## Contributors

- **AI planning agent, recommendations** — Ashwin Lulla
- **Auth, security, and DB wiring** — Manthan Khedekar
- **Trips, stops, itinerary items, budget, sharing** — Dhruv Ghosiya
- **Frontend** — Anant Khushalani

---

## License

Hackathon project — no license specified.