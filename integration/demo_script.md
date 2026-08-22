# AI Planner Demo

1. Start the API from the `globetrotter` directory with Uvicorn.
2. Confirm `GET /health` returns `{\"status\": \"ok\"}`.
3. Create or select a trip that has a Paris stop and note its trip ID.
4. Call `POST /api/v1/trips/{trip_id}/planner/proposals` using the example in
   `contracts/ai_input.json`.
5. Point out the proposal `source`, estimated total, warnings, and scheduled items.
6. Call the proposal GET endpoint to show that it was saved but not yet applied.
7. Call the apply endpoint once and display the resulting itinerary and budget.
8. Call apply a second time to demonstrate the `409` duplicate protection.
9. For the reliable fallback demonstration, set `AI_ENABLED=false` and generate
   another proposal; it should succeed with `source: rules`.
