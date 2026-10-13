from __future__ import annotations

from typing import Any, Optional

import requests

from app.config import get_settings
from app.schemas.companion import BrainConnectionTestRequest, BrainConnectionTestResponse, CompanionSystemStatus

settings = get_settings()


class LocalAIUnavailable(RuntimeError):
    pass


def _ollama_headers() -> dict[str, str]:
    if not settings.ollama_api_key:
        return {}
    return {"Authorization": f"Bearer {settings.ollama_api_key}"}


def _brain_connection_message(exc: requests.RequestException) -> str:
    status_code = getattr(getattr(exc, "response", None), "status_code", None)
    if status_code == 401:
        return "My firmware is connected, but the brain token was rejected. Check OLLAMA_API_KEY in Render."
    if status_code == 503:
        return "My firmware is connected, but DyBrain is not configured or is still starting."
    return "My firmware is connected, but I could not reach my brain."


def ollama_embed(text: str) -> list[float]:
    try:
      response = requests.post(
          f"{settings.ollama_base_url}/api/embeddings",
          headers=_ollama_headers(),
          json={"model": settings.ollama_embedding_model, "prompt": text},
          timeout=30,
      )
      response.raise_for_status()
      data = response.json()
      embedding = data.get("embedding")
      if not isinstance(embedding, list):
          raise LocalAIUnavailable("Ollama did not return an embedding.")
      return [float(value) for value in embedding]
    except requests.RequestException as exc:
      raise LocalAIUnavailable(str(exc)) from exc


def ollama_chat(messages: list[dict[str, str]], brain: Optional[dict[str, Any]] = None) -> str:
    try:
      provider = str((brain or {}).get("provider") or "ollama").lower()
      endpoint = str((brain or {}).get("endpoint") or "").rstrip("/")
      model = str((brain or {}).get("model") or settings.ollama_chat_model)
      if provider in {"lmstudio", "other", "custom"} and endpoint:
          chat_url = endpoint if endpoint.endswith("/chat/completions") else f"{endpoint}/chat/completions"
          response = requests.post(
              chat_url,
              json={"model": model, "messages": messages, "stream": False, "temperature": 0.35, "max_tokens": 180},
              timeout=60,
          )
          response.raise_for_status()
          content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
          if not content:
              raise LocalAIUnavailable("The selected local brain did not return chat content.")
          return content.strip()

      response = requests.post(
          f"{settings.ollama_base_url}/api/chat",
          headers=_ollama_headers(),
          json={
              "model": model,
              "messages": messages,
              "stream": False,
              "options": {
                  "temperature": 0.35,
                  "num_predict": 180,
              },
          },
          timeout=60,
      )
      response.raise_for_status()
      data: dict[str, Any] = response.json()
      content = data.get("message", {}).get("content", "")
      if not content:
          raise LocalAIUnavailable("Ollama did not return chat content.")
      return content.strip()
    except requests.RequestException as exc:
      raise LocalAIUnavailable(str(exc)) from exc


def _loaded_ollama_models() -> list[str]:
    response = requests.get(
        f"{settings.ollama_base_url}/api/tags",
        headers=_ollama_headers(),
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()
    models = data.get("models", [])
    return [
        str(model.get("name") or model.get("model"))
        for model in models
        if model.get("name") or model.get("model")
    ]


def get_ollama_status() -> CompanionSystemStatus:
    try:
        loaded_models = _loaded_ollama_models()
    except requests.RequestException as exc:
        return CompanionSystemStatus(
            status="brain-error",
            ollama_reachable=False,
            chat_model=settings.ollama_chat_model,
            embedding_model=settings.ollama_embedding_model,
            loaded_models=[],
            message=_brain_connection_message(exc),
        )

    chat_loaded = any(
        model == settings.ollama_chat_model or model.startswith(f"{settings.ollama_chat_model}:")
        for model in loaded_models
    )
    return CompanionSystemStatus(
        status="up" if chat_loaded else "idle",
        ollama_reachable=True,
        chat_model=settings.ollama_chat_model,
        embedding_model=settings.ollama_embedding_model,
        loaded_models=loaded_models,
        message="My brain is connected and ready." if chat_loaded else "My brain is idle. Use Connect brain to wake it up.",
    )


def wake_ollama() -> CompanionSystemStatus:
    try:
        requests.post(
            f"{settings.ollama_base_url}/api/chat",
            headers=_ollama_headers(),
            json={
                "model": settings.ollama_chat_model,
                "messages": [{"role": "user", "content": "ready"}],
                "stream": False,
                "keep_alive": settings.ollama_keep_alive,
                "options": {"num_predict": 1, "temperature": 0},
            },
            timeout=120,
        ).raise_for_status()
    except requests.RequestException as exc:
        return CompanionSystemStatus(
            status="brain-error",
            ollama_reachable=False,
            chat_model=settings.ollama_chat_model,
            embedding_model=settings.ollama_embedding_model,
            loaded_models=[],
            message=_brain_connection_message(exc),
        )

    return get_ollama_status()


def sleep_ollama() -> CompanionSystemStatus:
    try:
        requests.post(
            f"{settings.ollama_base_url}/api/generate",
            headers=_ollama_headers(),
            json={
                "model": settings.ollama_chat_model,
                "prompt": "",
                "stream": False,
                "keep_alive": 0,
            },
            timeout=30,
        ).raise_for_status()
    except requests.RequestException as exc:
        return CompanionSystemStatus(
            status="error",
            ollama_reachable=False,
            chat_model=settings.ollama_chat_model,
            embedding_model=settings.ollama_embedding_model,
            loaded_models=[],
            message=f"Could not release the LLM: {exc}",
        )

    return get_ollama_status()


def test_brain_connection(payload: BrainConnectionTestRequest) -> BrainConnectionTestResponse:
    provider = payload.provider.lower()
    endpoint = payload.endpoint.rstrip("/")
    headers: dict[str, str] = {"Accept": "application/json"}

    if payload.api_key:
        if provider == "azure":
            headers["api-key"] = payload.api_key
        elif provider == "google":
            headers["x-goog-api-key"] = payload.api_key
        elif provider == "claude":
            headers.update({"x-api-key": payload.api_key, "anthropic-version": "2023-06-01"})
        else:
            headers["Authorization"] = f"Bearer {payload.api_key}"

    if payload.brain_type == "dybrain":
        endpoint = settings.ollama_base_url.rstrip("/")
        provider = "ollama"

    try:
        if provider == "ollama":
            response = requests.get(f"{endpoint}/api/tags", headers=headers, timeout=12)
        elif provider == "google":
            response = requests.get(endpoint or "https://generativelanguage.googleapis.com/v1beta/models", headers=headers, timeout=12)
        elif provider == "claude":
            response = requests.get(endpoint or "https://api.anthropic.com/v1/models", headers=headers, timeout=12)
        elif provider == "azure":
            separator = "&" if "?" in endpoint else "?"
            response = requests.get(f"{endpoint}{separator}api-version={payload.api_version}", headers=headers, timeout=12)
        else:
            models_url = endpoint if endpoint.endswith("/models") else f"{endpoint}/models"
            response = requests.get(models_url, headers=headers, timeout=12)
        response.raise_for_status()
        data = response.json() if response.content else {}
        raw_models = data.get("models") or data.get("data") or []
        models = [str(item.get("name") or item.get("model") or item.get("id")) for item in raw_models if isinstance(item, dict)]
        model_ready = not payload.model or any(payload.model in item for item in models)
        if not models and provider != "ollama":
            model_ready = True
        message = "Connection successful." if model_ready else f"Connected, but model '{payload.model}' was not found."
        return BrainConnectionTestResponse(connected=model_ready, message=message, models=models[:30])
    except (requests.RequestException, ValueError) as exc:
        status_code = getattr(getattr(exc, "response", None), "status_code", None)
        detail = f" (HTTP {status_code})" if status_code else ""
        return BrainConnectionTestResponse(connected=False, message=f"Connection failed{detail}. Check the URL, credentials, model, and server access.")
