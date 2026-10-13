import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from app.config import get_settings


class TextToSpeechError(RuntimeError):
    pass


def _resolve_voice_path(doodle_id: str, voice_name: Optional[str]) -> Path:
    settings = get_settings()
    voice_dir = Path(settings.piper_voice_dir)
    voice_map = {
        "nova": settings.piper_voice_nova,
        "luna": settings.piper_voice_luna,
        "bob": settings.piper_voice_bob,
        "leo": settings.piper_voice_leo,
    }
    voice_file = voice_name or voice_map.get(doodle_id, settings.piper_voice_nova)
    voice_path = Path(voice_file)
    if not voice_path.is_absolute():
        voice_path = voice_dir / voice_path
    return voice_path


def synthesize_speech(
    text: str,
    doodle_id: str = "nova",
    voice_name: Optional[str] = None,
    rate: float = 0.86,
) -> Path:
    settings = get_settings()
    if settings.tts_engine.lower() != "piper":
        raise TextToSpeechError("Only Piper TTS is configured for deployable local audio.")

    piper_binary = shutil.which(settings.piper_binary_path) or settings.piper_binary_path
    if not piper_binary:
        raise TextToSpeechError("Piper binary is not configured.")

    voice_path = _resolve_voice_path(doodle_id, voice_name)
    if not voice_path.exists():
        raise TextToSpeechError(f"Piper voice model not found: {voice_path}")

    temp_dir = Path(tempfile.mkdtemp(prefix="dyslexialearn-tts-"))
    audio_path = temp_dir / "speech.wav"
    length_scale = max(0.65, min(1.8, 1.0 / rate))

    try:
        subprocess.run(
            [
                piper_binary,
                "--model",
                str(voice_path),
                "--output_file",
                str(audio_path),
                "--length_scale",
                str(length_scale),
            ],
            input=text,
            check=True,
            capture_output=True,
            text=True,
            timeout=45,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise TextToSpeechError(f"Could not create Piper speech audio: {exc}") from exc

    return audio_path
