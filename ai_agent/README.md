# GlobeTrotter AI Agent

The AI agent is a Python package imported by the main FastAPI backend. It does
not run a second web server and never writes to the database directly.

## Configuration

Copy `.env.example` to `.env` in the `globetrotter` directory and set:

```env
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-3.5-flash-lite
AI_ENABLED=true
```

When the key is absent, AI is disabled, Gemini times out, or output fails
validation, the package automatically uses its deterministic rule planner.

## Responsibilities

- Rank catalog activities for each existing trip stop.
- Generate structured suggestions with Gemini when enabled.
- Validate activity IDs, stop IDs, day indexes, durations, duplicates, and cost.
- Estimate activity-only itinerary budgets.

HTTP routing, proposal persistence, and application transactions belong to the
backend package.
