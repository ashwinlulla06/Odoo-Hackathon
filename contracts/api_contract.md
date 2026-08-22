# GlobeTrotter AI Planner API

All endpoints return JSON and are served by the main FastAPI application.

## Create a proposal

`POST /api/v1/trips/{trip_id}/planner/proposals`

Body fields: `goal` (string), `preferences` (string array), `daily_budget`
(optional non-negative number), `notes` (optional string), and `use_llm`
(boolean, default `true`). The trip must already have at least one stop.

Success: `201` with a stored proposal in `ready` state. `source` is either
`gemini` or `rules`. The call does not change itinerary items.

## Read a proposal

`GET /api/v1/trips/{trip_id}/planner/proposals/{proposal_id}`

Success: `200` with the same proposal contract and its current status.

## Apply a proposal

`POST /api/v1/trips/{trip_id}/planner/proposals/{proposal_id}/apply`

Success: `200` after all proposed itinerary items are inserted and trip/stop
budgets are recalculated in one transaction. Reapplying returns `409`.

## Errors

- `404`: trip or proposal does not exist, or proposal belongs to another trip.
- `409`: proposal was already applied.
- `422`: trip has no stops, catalog has no usable activities, or proposal fails validation.
- `500`: an unexpected persistence failure; the apply transaction is rolled back.

Example bodies are in `ai_input.json` and `ai_output.json`.
