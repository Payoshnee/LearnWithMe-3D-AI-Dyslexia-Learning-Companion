import { loggedFetch } from "./developerLogger.js";

// One public frontend setting for authentication, lessons, speech and chat.
const API_BASE_URL = import.meta.env?.VITE_API_BASE_URL || "http://localhost:8080";

export async function requestVoiceTurn(payload) {
  const response = await loggedFetch(`${API_BASE_URL}/api/v1/companion/voice-turn`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  }, "backend");

  if (!response.ok) {
    throw new Error(`Voice turn failed with status ${response.status}`);
  }

  return response.json();
}

export async function requestSpeechAudio(payload, { signal } = {}) {
  const response = await loggedFetch(`${API_BASE_URL}/api/v1/companion/speech`, {
    method: "POST",
    credentials: "include",
    signal,
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  }, "backend");

  if (!response.ok) {
    throw new Error(`Speech audio failed with status ${response.status}`);
  }

  return response.blob();
}

export async function requestSystemStatus() {
  const response = await loggedFetch(`${API_BASE_URL}/api/v1/companion/system`, {}, "api");

  if (!response.ok) {
    throw new Error(`System check failed with status ${response.status}`);
  }

  return response.json();
}

export async function requestSystemWake() {
  const response = await loggedFetch(`${API_BASE_URL}/api/v1/companion/system/wake`, {
    method: "POST",
  }, "api");

  if (!response.ok) {
    throw new Error(`System wake failed with status ${response.status}`);
  }

  return response.json();
}

export async function testBrainConnection(payload) {
  const response = await loggedFetch(`${API_BASE_URL}/api/v1/companion/system/test-connection`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }, "custom");
  if (!response.ok) throw new Error(`Connection test failed with status ${response.status}`);
  return response.json();
}

export function sendSystemSleep() {
  const url = `${API_BASE_URL}/api/v1/companion/system/sleep`;
  if (navigator.sendBeacon) {
    return navigator.sendBeacon(url);
  }
  fetch(url, { method: "POST", keepalive: true }).catch(() => {});
  return true;
}
