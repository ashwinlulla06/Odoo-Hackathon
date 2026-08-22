const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8001").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(message, status, details) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

export async function apiRequest(path, options = {}) {
  const token = localStorage.getItem("gt-token");
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      credentials: "include",
      ...options,
      headers: {
        Accept: "application/json",
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
    });
  } catch (error) {
    throw new ApiError("GlobeTrotter API is offline. Start the app with npm run dev, then retry.", 0, error);
  }

  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    if (response.status === 401 && token) {
      localStorage.removeItem("gt-token");
      localStorage.removeItem("gt-user");
      window.dispatchEvent(new Event("globetrotter:unauthorized"));
    }
    const serverMessage = typeof payload === "object" && (payload.detail || payload.message);
    const message = typeof serverMessage === "string"
      ? serverMessage
      : serverMessage
        ? JSON.stringify(serverMessage)
        : `Request failed with status ${response.status}`;
    throw new ApiError(message, response.status, payload);
  }

  return payload;
}

export function setAccessToken(token) {
  if (token) localStorage.setItem("gt-token", token);
  else localStorage.removeItem("gt-token");
}
