import shutil

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.schemas.companion import (
    BrainConnectionTestRequest,
    BrainConnectionTestResponse,
    CompanionEndSessionRequest,
    CompanionPreferences,
    CompanionRespondRequest,
    CompanionResponse,
    CompanionSessionRequest,
    CompanionSpeechRequest,
    CompanionSystemStatus,
    CompanionVoiceTurnRequest,
    CompanionVoiceTurnResponse,
)
from app.services import companion_service
from app.services.local_ai_service import get_ollama_status, sleep_ollama, test_brain_connection, wake_ollama
from app.services.tts_service import TextToSpeechError, synthesize_speech

router = APIRouter(prefix="/companion", tags=["companion"])
settings = get_settings()


def ensure_companion_enabled() -> None:
    if not settings.companion_enabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Companion feature is disabled.",
        )


@router.get("/preferences", response_model=CompanionPreferences)
def get_preferences() -> CompanionPreferences:
    ensure_companion_enabled()
    return companion_service.get_preferences()


@router.put("/preferences", response_model=CompanionPreferences)
def update_preferences(payload: CompanionPreferences) -> CompanionPreferences:
    ensure_companion_enabled()
    return companion_service.update_preferences(payload)


@router.post("/sessions", response_model=CompanionResponse)
def start_session(payload: CompanionSessionRequest) -> CompanionResponse:
    ensure_companion_enabled()
    return companion_service.start_session(payload)


@router.post("/sessions/end", response_model=CompanionResponse)
def end_session(payload: CompanionEndSessionRequest) -> CompanionResponse:
    ensure_companion_enabled()
    return companion_service.end_session()


@router.post("/respond", response_model=CompanionResponse)
def respond(payload: CompanionRespondRequest) -> CompanionResponse:
    ensure_companion_enabled()
    return companion_service.respond(payload)



@router.post("/voice-turn", response_model=CompanionVoiceTurnResponse)
def voice_turn(
    payload: CompanionVoiceTurnRequest,
) -> CompanionVoiceTurnResponse:
    ensure_companion_enabled()

    # Temporary development mode:
    # Run conversation without PostgreSQL or database memory.
    return companion_service.handle_voice_turn(
        payload,
        db=None,
    )



@router.get("/system", response_model=CompanionSystemStatus)
def system_status() -> CompanionSystemStatus:
    ensure_companion_enabled()
    return get_ollama_status()


@router.post("/system/wake", response_model=CompanionSystemStatus)
def wake_system() -> CompanionSystemStatus:
    ensure_companion_enabled()
    return wake_ollama()


@router.post("/system/sleep", response_model=CompanionSystemStatus)
def sleep_system() -> CompanionSystemStatus:
    ensure_companion_enabled()
    return sleep_ollama()


@router.post("/system/test-connection", response_model=BrainConnectionTestResponse)
def test_connection(payload: BrainConnectionTestRequest) -> BrainConnectionTestResponse:
    ensure_companion_enabled()
    return test_brain_connection(payload)


@router.post("/speech")
def create_speech(
    payload: CompanionSpeechRequest,
    background_tasks: BackgroundTasks,
) -> FileResponse:
    ensure_companion_enabled()
    try:
        audio_path = synthesize_speech(
            text=payload.text,
            doodle_id=payload.doodle_id,
            voice_name=payload.voice_name,
            rate=payload.rate,
        )
    except TextToSpeechError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    background_tasks.add_task(shutil.rmtree, audio_path.parent, ignore_errors=True)
    return FileResponse(
        audio_path,
        media_type="audio/wav",
        filename=f"{payload.doodle_id}-speech.wav",
        background=background_tasks,
    )
