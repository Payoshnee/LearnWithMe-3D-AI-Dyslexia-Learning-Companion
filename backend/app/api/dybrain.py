import os
import secrets
from typing import Any

import requests
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(tags=["dybrain"])
OLLAMA_URL = os.getenv("OLLAMA_INTERNAL_URL", "http://127.0.0.1:11434").rstrip("/")
MODEL = os.getenv("DYBRAIN_MODEL", "qwen2.5vl:3b")


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
    format: str = ""
    options: dict[str, Any] = Field(default_factory=dict)


def authorize(value: str) -> None:
    keys = [key.strip() for key in os.getenv("DYBRAIN_API_KEYS", "").split(",") if key.strip()]
    supplied = value.removeprefix("Bearer ").strip()
    if not keys:
        raise HTTPException(503, "DyBrain API keys are not configured.")
    if not any(secrets.compare_digest(supplied, key) for key in keys):
        raise HTTPException(401, "Invalid DyBrain project token.")


@router.get("/api/dybrain/health")
def health() -> dict[str, Any]:
    try:
        data = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5).json()
        models = [item.get("name") or item.get("model") for item in data.get("models", [])]
        return {"status": "ready" if MODEL in models else "starting", "model": MODEL}
    except requests.RequestException:
        return {"status": "starting", "model": MODEL}


@router.get("/api/tags")
def models(authorization: str = Header(default="")) -> dict[str, Any]:
    authorize(authorization)
    response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=10)
    response.raise_for_status()
    return response.json()


@router.post("/api/chat")
def chat(payload: ChatRequest, authorization: str = Header(default="")) -> dict[str, Any]:
    authorize(authorization)
    if payload.model != MODEL:
        raise HTTPException(400, f"Only {MODEL} is available.")
    response = requests.post(f"{OLLAMA_URL}/api/chat", json={**payload.model_dump(), "stream": False}, timeout=180)
    if not response.ok:
        raise HTTPException(response.status_code, "The shared model request failed.")
    return response.json()


@router.post("/api/generate")
def generate(payload: GenerateRequest, authorization: str = Header(default="")) -> dict[str, Any]:
    authorize(authorization)
    if payload.model != MODEL:
        raise HTTPException(400, f"Only {MODEL} is available.")
    body = payload.model_dump(exclude_none=True)
    if not body.get("format"):
        body.pop("format", None)
    response = requests.post(f"{OLLAMA_URL}/api/generate", json={**body, "stream": False}, timeout=180)
    if not response.ok:
        raise HTTPException(response.status_code, "The shared model request failed.")
    return response.json()
