
import ipaddress
import shutil

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Request,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.auth import COOKIE_NAME
from app.config import get_settings
from app.database import get_db
from app.models import User
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
from app.services.auth_service import validate_token
from app.services.local_ai_service import (
    get_ollama_status,
    sleep_ollama,
    test_brain_connection,
    wake_ollama,
)
from app.services.tts_service import (
    TextToSpeechError,
    synthesize_speech,
)


router = APIRouter(
    prefix="/companion",
    tags=["companion"],
)

settings = get_settings()

MAX_TRANSCRIPT_LENGTH = 1000
MAX_SPEECH_TEXT_LENGTH = 1000


def ensure_companion_enabled() -> None:
    if not settings.companion_enabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Companion feature is disabled.",
        )


def require_parent(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """
    Require a valid parent account session.

    The same cookie is used by the existing
    authentication and progress endpoints.
    """
    ensure_companion_enabled()

    token = request.cookies.get(COOKIE_NAME)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please sign in to use the learning companion.",
        )

    user_id = validate_token(token)
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This account is no longer available.",
        )

    return user


def require_local_admin(
    request: Request,
    parent: User = Depends(require_parent),
) -> User:
    """
    Dangerous AI administration operations
    are allowed only in local HTTP development.

    On Render, COOKIE_SECURE=true disables them.

    A local loopback check supplies an additional
    restriction, but this is not a replacement
    for production administrator roles.
    """
    client_host = (
        request.client.host
        if request.client is not None
        else ""
    )

    try:
        is_local = ipaddress.ip_address(
            client_host
        ).is_loopback
    except ValueError:
        is_local = False

    if settings.cookie_secure or not is_local:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI administration is disabled on this server.",
        )

    return parent


@router.get(
    "/preferences",
    response_model=CompanionPreferences,
)
def get_preferences(
    parent: User = Depends(require_parent),
) -> CompanionPreferences:
    return companion_service.get_preferences()


@router.put(
    "/preferences",
    response_model=CompanionPreferences,
)
def update_preferences(
    payload: CompanionPreferences,
    parent: User = Depends(require_parent),
) -> CompanionPreferences:
    # Current preferences are stored globally in memory.
    # For public use, do not allow one user to
    # change settings for every other user.
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Shared companion preferences cannot be changed.",
    )


@router.post(
    "/sessions",
    response_model=CompanionResponse,
)
def start_session(
    payload: CompanionSessionRequest,
    parent: User = Depends(require_parent),
) -> CompanionResponse:
    return companion_service.start_session(payload)


@router.post(
    "/sessions/end",
    response_model=CompanionResponse,
)
def end_session(
    payload: CompanionEndSessionRequest,
    parent: User = Depends(require_parent),
) -> CompanionResponse:
    return companion_service.end_session()


@router.post(
    "/respond",
    response_model=CompanionResponse,
)
def respond(
    payload: CompanionRespondRequest,
    parent: User = Depends(require_parent),
) -> CompanionResponse:
    return companion_service.respond(payload)


@router.post(
    "/voice-turn",
    response_model=CompanionVoiceTurnResponse,
)
def voice_turn(
    payload: CompanionVoiceTurnRequest,
    parent: User = Depends(require_parent),
) -> CompanionVoiceTurnResponse:
    transcript = payload.transcript.strip()

    if not transcript:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Please say or type something first.",
        )

    if len(transcript) > MAX_TRANSCRIPT_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="The message is too long.",
        )

    # Keep existing working conversation behavior.
    #
    # Database-backed child conversation history is
    # intentionally not enabled until learner records
    # are properly isolated by account.
    return companion_service.handle_voice_turn(
        payload,
        db=None,
    )


@router.get(
    "/system",
    response_model=CompanionSystemStatus,
)
def system_status(
    parent: User = Depends(require_parent),
) -> CompanionSystemStatus:
    return get_ollama_status()


@router.post(
    "/system/wake",
    response_model=CompanionSystemStatus,
)
def wake_system(
    admin: User = Depends(require_local_admin),
) -> CompanionSystemStatus:
    return wake_ollama()


@router.post(
    "/system/sleep",
    response_model=CompanionSystemStatus,
)
def sleep_system(
    admin: User = Depends(require_local_admin),
) -> CompanionSystemStatus:
    return sleep_ollama()


@router.post(
    "/system/test-connection",
    response_model=BrainConnectionTestResponse,
)
def test_connection(
    payload: BrainConnectionTestRequest,
    admin: User = Depends(require_local_admin),
) -> BrainConnectionTestResponse:
    # This operation may contact a user-supplied URL.
    # Never expose it to public visitors.
    return test_brain_connection(payload)


@router.post("/speech")
def create_speech(
    payload: CompanionSpeechRequest,
    background_tasks: BackgroundTasks,
    parent: User = Depends(require_parent),
) -> FileResponse:
    if len(payload.text) > MAX_SPEECH_TEXT_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Speech text is too long.",
        )

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
            detail="Server-generated speech is unavailable.",
        ) from exc

    background_tasks.add_task(
        shutil.rmtree,
        audio_path.parent,
        ignore_errors=True,
    )

    return FileResponse(
        audio_path,
        media_type="audio/wav",
        filename=f"{payload.doodle_id}-speech.wav",
        background=background_tasks,
    )
