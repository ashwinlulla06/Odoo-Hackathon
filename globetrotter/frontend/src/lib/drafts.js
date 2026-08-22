const key = (id) => `globetrotter-trip-draft:${id}`;
export function getDraft(id) { try { return JSON.parse(localStorage.getItem(key(id))) || { stops: [], notes: "" }; } catch { return { stops: [], notes: "" }; } }
export function saveDraft(id, value) { localStorage.setItem(key(id), JSON.stringify(value)); }
