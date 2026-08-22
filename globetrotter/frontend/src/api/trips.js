import { apiClient, DEMO_OWNER_ID } from "./client";
 
const BASE = "/api/trips";
 
// Matches TripCreate schema: name, owner_id, start_date, end_date,
// description?, cover_image_url?
export function createTrip({ name, startDate, endDate, description, coverImageUrl }) {
  return apiClient.post(BASE, {
    name,
    owner_id: DEMO_OWNER_ID,
    start_date: startDate,
    end_date: endDate,
    description: description || undefined,
    cover_image_url: coverImageUrl || undefined,
  });
}
 
// Backend requires owner_id as a query param on list
export function listTrips() {
  return apiClient.get(BASE, { owner_id: DEMO_OWNER_ID });
}
 
export function getTrip(tripId) {
  return apiClient.get(`${BASE}/${tripId}`);
}
 
// Matches TripUpdate schema: any subset of fields
export function updateTrip(tripId, updates) {
  return apiClient.patch(`${BASE}/${tripId}`, updates);
}
 
export function deleteTrip(tripId) {
  return apiClient.delete(`${BASE}/${tripId}`);
}