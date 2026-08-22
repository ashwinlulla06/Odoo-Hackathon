export const API_BASE_URL = 'http://127.0.0.1:8000';

export async function apiClient(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: { Accept: 'application/json', ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...options.headers },
  });

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const error = await response.json();
      message = error.detail || error.message || message;
    } catch {
      // The backend may send an empty/non-JSON error body.
    }
    throw new Error(typeof message === 'string' ? message : JSON.stringify(message));
  }

  if (response.status === 204) return null;
  return response.json();
}
