import os
import secrets
from typing import Any

import httpx
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

MODEL = os.getenv("DYBRAIN_MODEL", "qwen2.5vl:3b")
OLLAMA_URL = os.getenv("OLLAMA_INTERNAL_URL", "http://127.0.0.1:11434").rstrip("/")

app = FastAPI(title="DyBrain", version="1.0.0")


class ChatRequest(BaseModel):
    model: str = MODEL
    messages: list[dict[str, Any]] = Field(default_factory=list)
    stream: bool = False
    options: dict[str, Any] = Field(default_factory=dict)


class GenerateRequest(BaseModel):
    model: str = MODEL
    prompt: str
    images: list[str] = Field(default_factory=list)
    stream: bool = False
    format: str | dict[str, Any] | None = None
    options: dict[str, Any] = Field(default_factory=dict)


def authorize(value: str) -> None:
    keys = [key.strip() for key in os.getenv("DYBRAIN_API_KEYS", "").split(",") if key.strip()]
    supplied = value.removeprefix("Bearer ").strip()
    if not keys:
        raise HTTPException(503, "DyBrain API keys are not configured.")
    if not any(secrets.compare_digest(supplied, key) for key in keys):
        raise HTTPException(401, "Invalid DyBrain project token.")


def validate_model(model: str) -> None:
    if model != MODEL:
        raise HTTPException(400, f"Only {MODEL} is available.")


async def ollama(method: str, path: str, **kwargs: Any) -> httpx.Response:
    try:
        async with httpx.AsyncClient(timeout=300) as client:
            response = await client.request(method, f"{OLLAMA_URL}{path}", **kwargs)
    except httpx.RequestError as exc:
        raise HTTPException(503, "The model is starting. Please try again shortly.") from exc
    if not response.is_success:
        raise HTTPException(response.status_code, "The shared model request failed.")
    return response


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": "DyBrain", "status": "ready", "model": MODEL}


@app.get("/api/dybrain/health")
async def health() -> dict[str, str]:
    try:
        response = await ollama("GET", "/api/tags")
        models = [item.get("name") or item.get("model") for item in response.json().get("models", [])]
        return {"status": "ready" if MODEL in models else "starting", "model": MODEL}
    except HTTPException:
        return {"status": "starting", "model": MODEL}


@app.get("/api/tags")
async def tags(authorization: str = Header(default="")) -> Any:
    authorize(authorization)
    return (await ollama("GET", "/api/tags")).json()


@app.get("/api/ps")
async def running_models(authorization: str = Header(default="")) -> Any:
    authorize(authorization)
    return (await ollama("GET", "/api/ps")).json()


@app.post("/api/chat")
async def chat(payload: ChatRequest, authorization: str = Header(default="")) -> Any:
    authorize(authorization)
    validate_model(payload.model)
    body = payload.model_dump()
    body["stream"] = False
    return (await ollama("POST", "/api/chat", json=body)).json()


@app.post("/api/generate")
async def generate(payload: GenerateRequest, authorization: str = Header(default="")) -> Any:
    authorize(authorization)
    validate_model(payload.model)
    body = payload.model_dump(exclude_none=True)
    body["stream"] = False
    return (await ollama("POST", "/api/generate", json=body)).json()
