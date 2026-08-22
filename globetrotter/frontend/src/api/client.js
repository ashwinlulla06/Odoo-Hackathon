const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
 
// Hardcoded until auth exists. Swap this out once a real /login or /me
// endpoint is available on the backend.
export const DEMO_OWNER_ID = "demo-owner-1";
 
class ApiError extends Error {
  constructor(message, status, detail) {
    super(message);
    this.status = status;
    this.detail = detail;
  }
}
 
async function request(path, { method = "GET", body, params } = {}) {
  let url = `${BASE_URL}${path}`;
 
  if (params) {
    const query = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== null)
    );
    const qs = query.toString();
    if (qs) url += `?${qs}`;
  }
 
  const res = await fetch(url, {
    method,
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
 
  // FastAPI returns 204/empty body on some deletes; guard against empty JSON parse
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
 
  if (!res.ok) {
    const message = data?.detail || res.statusText || "Request failed";
    throw new ApiError(message, res.status, data);
  }
 
  return data;
}
 
export const apiClient = {
  get: (path, params) => request(path, { method: "GET", params }),
  post: (path, body) => request(path, { method: "POST", body }),
  patch: (path, body) => request(path, { method: "PATCH", body }),
  delete: (path) => request(path, { method: "DELETE" }),
};
 
export { ApiError };