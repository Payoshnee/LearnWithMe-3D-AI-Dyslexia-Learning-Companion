const MAX_LOGS = 300;
const listeners = new Set();
let entries = [];
let installed = false;

function notify() {
  const snapshot = [...entries];
  listeners.forEach((listener) => listener(snapshot));
}

export function logEvent(service, level, message, details = "") {
  const entry = {
    id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    time: new Date().toISOString(),
    service,
    level,
    message,
    details: typeof details === "string" ? details : JSON.stringify(details),
  };
  entries = [...entries.slice(-(MAX_LOGS - 1)), entry];
  notify();
  return entry;
}

export function subscribeToLogs(listener) {
  listeners.add(listener);
  listener([...entries]);
  return () => listeners.delete(listener);
}

export function clearLogs() {
  entries = [];
  notify();
}

export function installBrowserLogging() {
  if (installed) return;
  installed = true;
  logEvent("frontend", "info", "Frontend developer logger started");

  window.addEventListener("error", (event) => {
    logEvent("frontend", "error", event.message || "Unknown browser error", `${event.filename || ""}:${event.lineno || ""}`);
  });
  window.addEventListener("unhandledrejection", (event) => {
    logEvent("frontend", "error", "Unhandled promise rejection", String(event.reason || "Unknown reason"));
  });
}

export async function loggedFetch(url, options = {}, service = "api") {
  const method = options.method || "GET";
  const startedAt = performance.now();
  logEvent(service, "info", `${method} ${url}`);
  try {
    const response = await fetch(url, options);
    const duration = Math.round(performance.now() - startedAt);
    logEvent(
      service,
      response.ok ? "success" : "error",
      `${method} ${url} → ${response.status}`,
      `${duration}ms`,
    );
    return response;
  } catch (error) {
    logEvent(service, "error", `${method} ${url} failed`, error.message);
    throw error;
  }
}
