
/**
 * LearnWithMe — Authentication API
 *
 * Handles parent registration, login, session checks
 * and logout using cookie-based authentication.
 */

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ||
  "http://localhost:8080"
).replace(/\/+$/, "");

async function call(path, options = {}) {
  const {
    headers: customHeaders = {},
    ...fetchOptions
  } = options;

  let response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...fetchOptions,
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        ...customHeaders,
      },
    });
  } catch (error) {
    console.error("[LearnWithMe Auth] Network error:", error);
    throw new Error(
      "Cannot connect to the authentication server."
    );
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message =
      typeof data.detail === "string"
        ? data.detail
        : data.message || `Request failed (${response.status}).`;

    if (response.status !== 401 || path !== "/api/auth/session") {
      console.error(
        `[LearnWithMe Auth] ${path} failed:`,
        response.status,
        message
      );
    }

    throw new Error(message);
  }

  return data;
}

export function login(body) {
  return call("/api/auth/login", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function register(body) {
  return call("/api/auth/register", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function session() {
  return call("/api/auth/session", {
    method: "GET",
  });
}

export function logout() {
  return call("/api/auth/logout", {
    method: "POST",
  });
}

export { API_BASE_URL };
