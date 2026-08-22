import { apiClient } from './client';

const json = (method, body) => ({ method, body: JSON.stringify(body) });
const query = (path, key, value) => `${path}?${key}=${encodeURIComponent(value)}`;

export const listCities = () => apiClient('/api/cities');
export const listActivities = (cityId) => apiClient(cityId ? query('/api/activities', 'city_id', cityId) : '/api/activities');

export const createTrip = (data) => apiClient('/api/trips', json('POST', data));
export const listTrips = (ownerId) => apiClient(query('/api/trips', 'owner_id', ownerId));
export const getTrip = (tripId) => apiClient(`/api/trips/${tripId}`);
export const updateTrip = (tripId, data) => apiClient(`/api/trips/${tripId}`, json('PATCH', data));
export const deleteTrip = (tripId) => apiClient(`/api/trips/${tripId}`, { method: 'DELETE' });

export const createStop = (tripId, data) => apiClient(`/api/trips/${tripId}/stops`, json('POST', data));
export const listStops = (tripId) => apiClient(`/api/trips/${tripId}/stops`);
export const updateStop = (tripId, stopId, data) => apiClient(`/api/trips/${tripId}/stops/${stopId}`, json('PATCH', data));
export const deleteStop = (tripId, stopId) => apiClient(`/api/trips/${tripId}/stops/${stopId}`, { method: 'DELETE' });

export const createItem = (tripId, stopId, data) => apiClient(`/api/trips/${tripId}/stops/${stopId}/items`, json('POST', data));
export const listItems = (tripId, stopId) => apiClient(`/api/trips/${tripId}/stops/${stopId}/items`);
export const updateItem = (tripId, stopId, itemId, data) => apiClient(`/api/trips/${tripId}/stops/${stopId}/items/${itemId}`, json('PATCH', data));
export const deleteItem = (tripId, stopId, itemId) => apiClient(`/api/trips/${tripId}/stops/${stopId}/items/${itemId}`, { method: 'DELETE' });

export const getBudget = (tripId) => apiClient(`/api/trips/${tripId}/budget`);
export const shareTrip = (tripId) => apiClient(`/api/trips/${tripId}/share`, { method: 'POST' });
