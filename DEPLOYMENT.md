# GlobeTrotter deployment

GlobeTrotter has two deployable parts: the FastAPI backend and the static React
frontend. Docker and Odoo are not used.

## Backend

Use Python 3.12, install `backend/requirements.txt`, run
`python -m alembic upgrade head`, then start:

```text
uvicorn backend.main:app --host 0.0.0.0 --port <platform-port>
```

Required production variables:

```text
ENVIRONMENT=production
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
JWT_SECRET=<unique random value with at least 32 characters>
JWT_EXPIRE_MINUTES=10080
CORS_ORIGINS=https://your-frontend.example
CORS_ORIGIN_REGEX=^https://your-frontend\.example$
ADMIN_EMAILS=admin@example.com
AI_ENABLED=true
GEMINI_API_KEY=<server-side key>
GEMINI_MODEL=gemini-3.5-flash-lite
```

SQLite is suitable for a single-instance demo. Use PostgreSQL for a hosted,
multi-instance deployment. Keep the Gemini key on the backend only.

Health check: `GET /health`. API documentation: `GET /docs`.

## Frontend

From `frontend`, run `npm ci` and `npm run build`. Set
`VITE_API_BASE_URL=https://your-api.example` at build time and publish
`frontend/dist`. Configure the host to rewrite unknown paths to `/index.html`
so React Router URLs work after refresh.

## Release checks

From the project root:

```text
..\.venv\Scripts\python.exe -m pytest -q
..\.venv\Scripts\python.exe -m compileall backend ai_agent -q
```

From `frontend`:

```text
npm audit
npm test
npm run build
```

After deployment, verify signup, login, city discovery, trip creation, adding a
stop, AI proposal generation and apply, budget display, and publishing.
