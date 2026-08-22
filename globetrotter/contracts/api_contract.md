# GlobeTrotter API Contract

**Status**: Reflects the ACTUAL, tested backend as of Chunk 7 (not the original plan — this supersedes any earlier draft).
**Owner**: M1 (Backend). Do not edit unilaterally — if a change is needed, flag it to the team first (per hackathon rules).
**Base URL (local dev)**: `http://127.0.0.1:8000`
**Format**: All requests/responses are JSON. Dates are `YYYY-MM-DD` strings.

---

## 1. Catalog (Read-Only)

### `GET /api/cities`
Returns all cities.

**Response 200**
```json
[
  {
    "id": "city-paris",
    "name": "Paris",
    "country": "France",
    "cost_index": 85,
    "popularity": 100,
    "image_url": "https://..."
  }
]
```

### `GET /api/activities`
### `GET /api/activities?city_id={city_id}`
Returns all activities, optionally filtered by city.

**Response 200**
```json
[
  {
    "id": "act-eiffel-tour",
    "city_id": "city-paris",
    "name": "Eiffel Tower Tour",
    "category": "sightseeing",
    "cost": 25.0,
    "duration_hours": 2.0,
    "description": "...",
    "image_url": "https://..."
  }
]
```

---

## 2. Trips

### `POST /api/trips`
**Request body**
```json
{
  "name": "Europe Trip",
  "owner_id": "user1",
  "start_date": "2026-09-01",
  "end_date": "2026-09-10",
  "description": null,
  "cover_image_url": null
}
```
Required: `name`, `owner_id`, `start_date`, `end_date`. Optional: `description`, `cover_image_url`.

**Response 201/200**
```json
{
  "id": "bead7e7f-...",
  "name": "Europe Trip",
  "owner_id": "user1",
  "start_date": "2026-09-01",
  "end_date": "2026-09-10",
  "description": null,
  "cover_image_url": null,
  "is_public": false,
  "share_token": null,
  "total_budget": 0.0
}
```

### `GET /api/trips?owner_id={owner_id}`
Returns list of `TripOut` for that owner. **`owner_id` is required** — no auth yet, so this must be passed explicitly by the frontend.

### `GET /api/trips/{trip_id}`
Returns single `TripOut`. 404 if not found.

### `PATCH /api/trips/{trip_id}`
**Request body** (all fields optional, only send what changes)
```json
{ "description": "Backpacking through 5 countries" }
```
Accepts any subset of: `name`, `start_date`, `end_date`, `description`, `cover_image_url`, `is_public`.

### `DELETE /api/trips/{trip_id}`
**Response 200**
```json
{ "deleted": true }
```

---

## 3. Trip Stops

Base path: `/api/trips/{trip_id}/stops`

### `POST /api/trips/{trip_id}/stops`
**Request body**
```json
{
  "city_id": "city-paris",
  "sequence": 10,
  "start_date": "2026-09-01",
  "end_date": "2026-09-04",
  "description": null,
  "budget_estimate": 0.0
}
```
Required: `city_id`, `sequence`, `start_date`, `end_date`. Optional: `description`, `budget_estimate` (defaults to `0.0`).

**Response**
```json
{
  "id": "stop-uuid",
  "trip_id": "trip-uuid",
  "city_id": "city-paris",
  "sequence": 10,
  "start_date": "2026-09-01",
  "end_date": "2026-09-04",
  "description": null,
  "budget_estimate": 0.0
}
```

### `GET /api/trips/{trip_id}/stops`
Returns list of `TripStopOut`, ordered by `sequence`.

### `PATCH /api/trips/{trip_id}/stops/{stop_id}`
Partial update — any subset of: `city_id`, `sequence`, `start_date`, `end_date`, `description`, `budget_estimate`.

### `DELETE /api/trips/{trip_id}/stops/{stop_id}`
Deletes the stop (cascades to its itinerary items).

---

## 4. Itinerary Items

Base path: `/api/trips/{trip_id}/stops/{stop_id}/items`

### `POST /.../items`
**Request body**
```json
{
  "activity_id": "act-eiffel-tour",
  "name": "Eiffel Tower Visit",
  "day_index": 1,
  "sequence": 10,
  "time_slot": "9:00 AM",
  "cost": 25.0,
  "notes": null
}
```
Required: `name`, `day_index`, `sequence`. Optional: `activity_id` (link to catalog, or omit for a freeform item), `time_slot`, `cost` (defaults `0.0`), `notes`.

**Response**
```json
{
  "id": "item-uuid",
  "stop_id": "stop-uuid",
  "activity_id": "act-eiffel-tour",
  "name": "Eiffel Tower Visit",
  "day_index": 1,
  "sequence": 10,
  "time_slot": "9:00 AM",
  "cost": 25.0,
  "notes": null
}
```

### `GET /.../items`
Returns list of `ItineraryItemOut`, ordered by `day_index` then `sequence`.

### `PATCH /.../items/{item_id}`
Partial update — any subset of: `activity_id`, `name`, `day_index`, `sequence`, `time_slot`, `cost`, `notes`.

### `DELETE /.../items/{item_id}`
Deletes the item.

---

## 5. Not Yet Built (do not build against these paths yet)

- `GET /api/trips/{trip_id}/budget` — budget breakdown endpoint (**Chunk 8, in progress**)
- `POST /api/trips/{trip_id}/share` — generate public share link
- `GET /api/public/trips/{share_token}` — public read-only view
- Auth endpoints (`/api/auth/...`) — no login/JWT yet; all endpoints currently take `owner_id` as a plain string with no verification
- AI agent endpoints (`/api/agent/...`) — recommend/budget-optimize/proposal apply-discard flow

## 6. Known Gaps / Notes for Frontend (M2)

- **No authentication yet.** Every request that needs a user must pass `owner_id` as a plain string. This will change once auth is built — expect a breaking change later, don't hardcode assumptions about this being permanent.
- **`total_budget` on `Trip` is not yet auto-calculated** — currently just a stored float, defaults to `0.0`, not updated automatically when stops/items change. This is what Chunk 8 (Budget Service) is fixing right now.
- IDs are UUID strings, not integers.
- Dates are plain `YYYY-MM-DD`, no time component.