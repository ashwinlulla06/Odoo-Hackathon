import { apiRequest } from "./client";

const json = (method, body) => ({ method, ...(body !== undefined ? { body: JSON.stringify(body) } : {}) });
const qs = (params = {}) => {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => value !== undefined && value !== null && value !== "" && search.set(key, value));
  return search.toString() ? `?${search}` : "";
};

export const authApi = {
  signup: (body) => apiRequest("/api/v1/auth/signup", json("POST", body)),
  login: (body) => apiRequest("/api/v1/auth/login", json("POST", body)),
  me: () => apiRequest("/api/v1/me"),
  update: (body) => apiRequest("/api/v1/me", json("PATCH", body)),
};

export const tripsApi = {
  list: () => apiRequest("/api/v1/trips"),
  get: (id) => apiRequest(`/api/v1/trips/${id}`),
  create: (body) => apiRequest("/api/v1/trips", json("POST", body)),
  update: (id, body) => apiRequest(`/api/v1/trips/${id}`, json("PATCH", body)),
  remove: (id) => apiRequest(`/api/v1/trips/${id}`, { method: "DELETE" }),
  addStop: (id, body) => apiRequest(`/api/v1/trips/${id}/stops`, json("POST", body)),
  updateStop: (id, stopId, body) => apiRequest(`/api/v1/trips/${id}/stops/${stopId}`, json("PATCH", body)),
  removeStop: (id, stopId) => apiRequest(`/api/v1/trips/${id}/stops/${stopId}`, { method: "DELETE" }),
  reorderStops: (id, orderedIds) => apiRequest(`/api/v1/trips/${id}/stops/reorder`, json("POST", { ordered_ids: orderedIds })),
  addItem: (id, stopId, body) => apiRequest(`/api/v1/trips/${id}/stops/${stopId}/items`, json("POST", body)),
  updateItem: (id, stopId, itemId, body) => apiRequest(`/api/v1/trips/${id}/stops/${stopId}/items/${itemId}`, json("PATCH", body)),
  removeItem: (id, stopId, itemId) => apiRequest(`/api/v1/trips/${id}/stops/${stopId}/items/${itemId}`, { method: "DELETE" }),
  budget: (id) => apiRequest(`/api/v1/trips/${id}/budget`),
  addExpense: (id, body) => apiRequest(`/api/v1/trips/${id}/expenses`, json("POST", body)),
  removeExpense: (id, expenseId) => apiRequest(`/api/v1/trips/${id}/expenses/${expenseId}`, { method: "DELETE" }),
  publish: (id) => apiRequest(`/api/v1/trips/${id}/publish`, { method: "POST" }),
  unpublish: (id) => apiRequest(`/api/v1/trips/${id}/unpublish`, { method: "POST" }),
};

export const catalogApi = {
  cities: (params) => apiRequest(`/api/v1/cities${qs(params)}`),
  activities: (params) => apiRequest(`/api/v1/activities${qs(params)}`),
  saved: () => apiRequest("/api/v1/me/saved-cities"),
  save: (id) => apiRequest(`/api/v1/me/saved-cities/${id}`, { method: "POST" }),
  unsave: (id) => apiRequest(`/api/v1/me/saved-cities/${id}`, { method: "DELETE" }),
};

export const publicApi = {
  list: (params) => apiRequest(`/api/v1/public/trips${qs(params)}`),
  get: (slug) => apiRequest(`/api/v1/public/trips/${slug}`),
  copy: (slug) => apiRequest(`/api/v1/public/trips/${slug}/copy`, { method: "POST" }),
};

export const adminApi = {
  analytics: () => apiRequest("/api/v1/admin/analytics"),
  users: (params) => apiRequest(`/api/v1/admin/users${qs(params)}`),
  updateUser: (id, body) => apiRequest(`/api/v1/admin/users/${id}`, json("PATCH", body)),
};

export const agentApi = {
  status: () => apiRequest("/api/v1/ai/status"),
  create: (tripId, body) => apiRequest(`/api/v1/trips/${tripId}/planner/proposals`, json("POST", body)),
  get: (tripId, proposalId) => apiRequest(`/api/v1/trips/${tripId}/planner/proposals/${proposalId}`),
  apply: (tripId, proposalId) => apiRequest(`/api/v1/trips/${tripId}/planner/proposals/${proposalId}/apply`, { method: "POST" }),
};
