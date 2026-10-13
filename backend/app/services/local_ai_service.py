
from __future__ import annotations

from typing import Any, Optional

import requests

from app.config import get_settings
from app.schemas.companion import (
    BrainConnectionTestRequest,
    BrainConnectionTestResponse,
    CompanionSystemStatus,
)


settings = get_settings()

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
FREE_MODEL = "openrouter/free"


class LocalAIUnavailable(RuntimeError):
    pass


def _use_openrouter() -> bool:
    return settings.ai_provider.strip().lower() == "openrouter"


def _ollama_headers() -> dict[str, str]:
    if not settings.ollama_api_key:
        return {}
    return {
        "Authorization": f"Bearer {settings.ollama_api_key}"
    }


def _brain_connection_message(
    exc: requests.RequestException,
) -> str:
    status_code = getattr(
        getattr(exc, "response", None),
        "status_code",
        None,
    )

    if status_code == 401:
        return "The AI service rejected its API credentials."

    if status_code == 429:
        return "The free AI request limit has been reached. Please try again later."

    if status_code == 503:
        return "The AI service is temporarily unavailable."

    return "The AI service could not be reached."


def ollama_embed(text: str) -> list[float]:
    # OpenRouter chat does not provide the local Ollama
    # embedding model. The RAG service will use its
    # existing keyword-based fallback instead.
    if _use_openrouter():
        raise LocalAIUnavailable(
            "Embeddings are unavailable in hosted AI mode."
        )

    try:
        response = requests.post(
            f"{settings.ollama_base_url.rstrip('/')}/api/embeddings",
            headers=_ollama_headers(),
            json={
                "model": settings.ollama_embedding_model,
                "prompt": text,
            },
            timeout=30,
        )

        response.raise_for_status()
        data = response.json()

        embedding = data.get("embedding")

        if not isinstance(embedding, list):
            raise LocalAIUnavailable(
                "Ollama did not return an embedding."
            )

        return [float(value) for value in embedding]

    except (requests.RequestException, ValueError, TypeError) as exc:
        raise LocalAIUnavailable(
            "Ollama embedding generation failed."
        ) from exc


def _openrouter_chat(
    messages: list[dict[str, str]],
) -> str:
    if not settings.openrouter_api_key.strip():
        raise LocalAIUnavailable(
            "OpenRouter API key is not configured."
        )

    # Security: deliberately use the fixed, free-only
    # model router. Do not accept a model or endpoint
    # supplied by a browser request.
    #
    # This prevents client-provided brain settings
    # from selecting a paid model.
    try:
        response = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": (
                    f"Bearer {settings.openrouter_api_key}"
                ),
                "Content-Type": "application/json",
                "X-Title": "LearnWithMe",
            },
            json={
                "model": FREE_MODEL,
                "messages": messages,
                "stream": False,
                "temperature": 0.35,
                "max_tokens": 180,
            },
            timeout=55,
        )

        response.raise_for_status()
        data = response.json()

        choices = data.get("choices") or []
        if not choices:
            raise LocalAIUnavailable(
                "The hosted model returned no response."
            )

        content = (
            choices[0].get("message") or {}
        ).get("content", "")

        if isinstance(content, list):
            content = " ".join(
                part.get("text", "")
                for part in content
                if isinstance(part, dict)
                and part.get("type") == "text"
            )

        if not isinstance(content, str) or not content.strip():
            raise LocalAIUnavailable(
                "The hosted model returned no spoken text."
            )

        return content.strip()

    except requests.HTTPError as exc:
        status_code = getattr(
            exc.response,
            "status_code",
            None,
        )

        if status_code == 429:
            raise LocalAIUnavailable(
                "The free AI request limit has been reached."
            ) from exc

        if status_code in (401, 403):
            raise LocalAIUnavailable(
                "The hosted AI key was rejected or restricted."
            ) from exc

        raise LocalAIUnavailable(
            f"Hosted AI request failed (HTTP {status_code})."
        ) from exc

    except (requests.RequestException, ValueError, TypeError) as exc:
        raise LocalAIUnavailable(
            "The hosted AI service is temporarily unavailable."
        ) from exc


def ollama_chat(
    messages: list[dict[str, str]],
    brain: Optional[dict[str, Any]] = None,
) -> str:
    # Production always uses the configured free router.
    # Ignore client-controlled provider, model, endpoint,
    # or API key in hosted mode.
    if _use_openrouter():
        return _openrouter_chat(messages)

    # Preserve existing local Ollama and local custom
    # provider behavior for development.
    try:
        provider = str(
            (brain or {}).get("provider") or "ollama"
        ).lower()

        endpoint = str(
            (brain or {}).get("endpoint") or ""
        ).rstrip("/")

        model = str(
            (brain or {}).get("model")
            or settings.ollama_chat_model
        )

        if provider in {"lmstudio", "other", "custom"} and endpoint:
            chat_url = (
                endpoint
                if endpoint.endswith("/chat/completions")
                else f"{endpoint}/chat/completions"
            )

            response = requests.post(
                chat_url,
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "temperature": 0.35,
                    "max_tokens": 180,
                },
                timeout=60,
            )

            response.raise_for_status()

            content = (
                response.json()
                .get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )

            if not isinstance(content, str) or not content.strip():
                raise LocalAIUnavailable(
                    "The selected local model returned no content."
                )

            return content.strip()

        response = requests.post(
            f"{settings.ollama_base_url.rstrip('/')}/api/chat",
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
        data = response.json()

        content = data.get("message", {}).get("content", "")

        if not isinstance(content, str) or not content.strip():
            raise LocalAIUnavailable(
                "Ollama did not return chat content."
            )

        return content.strip()

    except (requests.RequestException, ValueError, TypeError) as exc:
        raise LocalAIUnavailable(
            "The local AI service is unavailable."
        ) from exc


def _loaded_ollama_models() -> list[str]:
    response = requests.get(
        f"{settings.ollama_base_url.rstrip('/')}/api/tags",
        headers=_ollama_headers(),
        timeout=20,
    )

    response.raise_for_status()
    data = response.json()

    return [
        str(model.get("name") or model.get("model"))
        for model in data.get("models", [])
        if model.get("name") or model.get("model")
    ]


def get_ollama_status() -> CompanionSystemStatus:
    if _use_openrouter():
        configured = bool(settings.openrouter_api_key.strip())

        return CompanionSystemStatus(
            status="idle" if configured else "brain-error",
            ollama_reachable=False,
            chat_model=FREE_MODEL,
            embedding_model="keyword-fallback",
            loaded_models=[],
            message=(
                "Hosted free AI is configured. "
                "A chat request is needed to verify availability."
                if configured
                else "The hosted AI key is not configured."
            ),
        )

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
        model == settings.ollama_chat_model
        or model.startswith(f"{settings.ollama_chat_model}:")
        for model in loaded_models
    )

    return CompanionSystemStatus(
        status="up" if chat_loaded else "idle",
        ollama_reachable=True,
        chat_model=settings.ollama_chat_model,
        embedding_model=settings.ollama_embedding_model,
        loaded_models=loaded_models,
        message=(
            "My brain is connected and ready."
            if chat_loaded
            else "My brain is idle. Use Connect brain to wake it up."
        ),
    )


def wake_ollama() -> CompanionSystemStatus:
    if _use_openrouter():
        return get_ollama_status()

    try:
        requests.post(
            f"{settings.ollama_base_url.rstrip('/')}/api/chat",
            headers=_ollama_headers(),
            json={
                "model": settings.ollama_chat_model,
                "messages": [
                    {"role": "user", "content": "ready"}
                ],
                "stream": False,
                "keep_alive": settings.ollama_keep_alive,
                "options": {
                    "num_predict": 1,
                    "temperature": 0,
                },
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
    if _use_openrouter():
        return get_ollama_status()

    try:
        requests.post(
            f"{settings.ollama_base_url.rstrip('/')}/api/generate",
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
            message=_brain_connection_message(exc),
        )

    return get_ollama_status()


def test_brain_connection(
    payload: BrainConnectionTestRequest,
) -> BrainConnectionTestResponse:
    # This endpoint is restricted to local development
    # in companion.py. Never let its input choose a
    # provider or URL on the deployed backend.
    if _use_openrouter():
        return BrainConnectionTestResponse(
            connected=False,
            message=(
                "Manual provider connection testing "
                "is disabled in hosted mode."
            ),
            models=[],
        )

    provider = payload.provider.lower()
    endpoint = payload.endpoint.rstrip("/")

    headers: dict[str, str] = {
        "Accept": "application/json"
    }

    if payload.api_key:
        if provider == "azure":
            headers["api-key"] = payload.api_key
        elif provider == "google":
            headers["x-goog-api-key"] = payload.api_key
        elif provider == "claude":
            headers.update({
                "x-api-key": payload.api_key,
                "anthropic-version": "2023-06-01",
            })
        else:
            headers["Authorization"] = (
                f"Bearer {payload.api_key}"
            )

    if payload.brain_type == "dybrain":
        endpoint = settings.ollama_base_url.rstrip("/")
        provider = "ollama"

    try:
        if provider == "ollama":
            response = requests.get(
                f"{endpoint}/api/tags",
                headers=headers,
                timeout=12,
            )

        elif provider == "google":
            response = requests.get(
                endpoint or (
                    "https://generativelanguage.googleapis.com"
                    "/v1beta/models"
                ),
                headers=headers,
                timeout=12,
            )

        elif provider == "claude":
            response = requests.get(
                endpoint or "https://api.anthropic.com/v1/models",
                headers=headers,
                timeout=12,
            )

        elif provider == "azure":
            separator = "&" if "?" in endpoint else "?"
            response = requests.get(
                f"{endpoint}{separator}api-version={payload.api_version}",
                headers=headers,
                timeout=12,
            )

        else:
            models_url = (
                endpoint
                if endpoint.endswith("/models")
                else f"{endpoint}/models"
            )
            response = requests.get(
                models_url,
                headers=headers,
                timeout=12,
            )

        response.raise_for_status()
        data = response.json() if response.content else {}

        raw_models = (
            data.get("models")
            or data.get("data")
            or []
        )

        models = [
            str(
                item.get("name")
                or item.get("model")
                or item.get("id")
            )
            for item in raw_models
            if isinstance(item, dict)
        ]

        model_ready = (
            not payload.model
            or any(payload.model in item for item in models)
        )

        if not models and provider != "ollama":
            model_ready = True

        return BrainConnectionTestResponse(
            connected=model_ready,
            message=(
                "Connection successful."
                if model_ready
                else "Connected, but the model was not found."
            ),
            models=models[:30],
        )

    except (requests.RequestException, ValueError):
        return BrainConnectionTestResponse(
            connected=False,
            message=(
                "Connection failed. Check the URL, "
                "credentials, model, and server access."
            ),
            models=[],
        )
