import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const frontendDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const projectDir = path.resolve(frontendDir, "..");
const python = path.resolve(projectDir, "..", ".venv", "Scripts", "python.exe");
const vite = path.resolve(frontendDir, "node_modules", "vite", "bin", "vite.js");
const children = [];

async function probe(url, expectedText) {
  try {
    const response = await fetch(url, { signal: AbortSignal.timeout(1200) });
    const body = await response.text();
    return { reachable: true, healthy: response.ok && body.includes(expectedText) };
  } catch {
    return { reachable: false, healthy: false };
  }
}

const api = await probe("http://127.0.0.1:8001/health", '"status":"ok"');
const web = await probe("http://localhost:5173/", "GlobeTrotter");

if (api.reachable && !api.healthy) {
  console.error("[API] Port 8001 is occupied by another application. Stop it, then retry.");
  process.exit(1);
}
if (web.reachable && !web.healthy) {
  console.error("[WEB] Port 5173 is occupied by another application. Stop it, then retry.");
  process.exit(1);
}

if (api.healthy) {
  console.log("[API] GlobeTrotter API is already healthy on http://127.0.0.1:8001 — reusing it.");
} else {
  if (!existsSync(python)) {
    console.error(`[API] Python environment not found at ${python}`);
    console.error("Create the project virtual environment and install backend/requirements.txt first.");
    process.exit(1);
  }

  const apiProcess = spawn(
    python,
    ["-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8001"],
    { cwd: projectDir, stdio: "inherit" },
  );
  children.push(apiProcess);
  apiProcess.on("exit", (code) => {
    if (code && code !== 0) console.error(`[API] stopped with exit code ${code}`);
  });
}

if (web.healthy) {
  console.log("[WEB] GlobeTrotter frontend is already running on http://localhost:5173 — reusing it.");
} else {
  if (!existsSync(vite)) {
    console.error("[WEB] Vite is not installed. Run npm install inside the frontend folder.");
    process.exit(1);
  }

  const webProcess = spawn(
    process.execPath,
    [vite, "--host", "localhost", "--port", "5173", "--strictPort"],
    { cwd: frontendDir, stdio: "inherit", env: { ...process.env, VITE_API_BASE_URL: "http://127.0.0.1:8001" } },
  );
  children.push(webProcess);
  webProcess.on("exit", (code) => {
    if (code && code !== 0) console.error(`[WEB] stopped with exit code ${code}`);
  });
}

console.log("GlobeTrotter is starting. Open http://localhost:5173");

const keepAlive = setInterval(() => {}, 60_000);

function shutdown() {
  clearInterval(keepAlive);
  for (const child of children) {
    if (!child.killed) child.kill("SIGTERM");
  }
  setTimeout(() => process.exit(0), 250);
}

process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);
