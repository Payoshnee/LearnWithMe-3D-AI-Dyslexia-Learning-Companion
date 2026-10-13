from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_preferences_endpoint_returns_defaults():
    response = client.get("/api/v1/companion/preferences")

    assert response.status_code == 200
    data = response.json()
    assert data["character_id"] == "default"
    assert data["muted"] is False
    assert data["text_only"] is False
    assert data["reduced_motion"] is False
    assert data["speech_rate"] == 0.85


def test_companion_session_response_matches_schema():
    response = client.post(
        "/api/v1/companion/sessions",
        json={"lesson_type": "pronunciation", "lesson_id": "demo"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Your learning companion is ready for this pronunciation."
    assert data["character"] == {
        "state": "idle",
        "animation": "Idle",
        "emotion": "friendly",
    }
    assert data["board"]["visible"] is False
    assert data["board"]["mode"] == "none"
    assert data["next_action"] == "wait"
    assert data["session_id"]


def test_invalid_preferences_are_rejected():
    response = client.put(
        "/api/v1/companion/preferences",
        json={
            "character_id": "default",
            "muted": False,
            "text_only": False,
            "reduced_motion": False,
            "speech_rate": 5,
        },
    )

    assert response.status_code == 422


def test_companion_routes_follow_current_no_auth_convention():
    response = client.post("/api/v1/companion/respond", json={"message": "hello"})

    assert response.status_code == 200
    assert response.json()["character"]["state"] == "encouraging"


def test_voice_turn_returns_rag_ready_payload():
    response = client.post(
        "/api/v1/companion/voice-turn",
        json={
            "transcript": "help me say pronunciation",
            "learnerName": "Demo",
            "learnerAge": 8,
            "doodleId": "nova",
            "doodleName": "Nova",
            "language": "auto",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "pronunciation_help"
    assert data["teachingBoard"]["word"] == "pronunciation"
    assert data["teachingBoard"]["syllables"] == ["pruh", "nun", "see", "ay", "shun"]
    assert "great job" not in data["responseText"].lower()
    assert data["responseText"] == "Demo, start with one sound: pruh."
    assert data["stateSequence"]
    assert data["memoryUpdate"]["future_pipeline"] == "local_stt_translation_rag_tts"


def test_pronunciation_help_uses_learner_name_and_target_word():
    response = client.post(
        "/api/v1/companion/voice-turn",
        json={
            "transcript": "Help me pronounce elephant",
            "learnerName": "Himanshu",
            "learnerAge": 8,
            "doodleId": "nova",
            "doodleName": "Nova",
            "language": "auto",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "pronunciation_help"
    assert data["teachingBoard"]["word"] == "elephant"
    assert data["teachingBoard"]["syllables"] == ["el", "e", "phant"]
    assert data["teachingBoard"]["focusIndex"] == 0
    assert data["teachingBoard"]["focusSyllable"] == "el"
    assert data["responseText"] == "Himanshu, start with one sound: el."
    assert "Hey Nova" not in data["responseText"]
    assert "nice job" not in data["responseText"].lower()


def test_pronunciation_attempt_does_not_restart_lesson():
    response = client.post(
        "/api/v1/companion/voice-turn",
        json={
            "transcript": "pronunciation",
            "learnerName": "Demo",
            "learnerAge": 8,
            "doodleId": "milo",
            "doodleName": "Milo",
            "context": {
                "currentBoard": {
                    "type": "syllables",
                    "word": "pronunciation",
                    "syllables": ["pruh", "nun", "see", "ay", "shun"],
                }
            },
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "pronunciation_attempt"
    assert data["teachingBoard"]["word"] == "pronunciation"
    assert data["memoryUpdate"]["focus"] == "pronunciation_attempt_feedback"
    assert "pronunciation_score" in data["memoryUpdate"]
    assert data["teachingBoard"]["score"] >= 0


def test_pronunciation_loop_retries_advances_and_stops():
    context = {
        "currentBoard": {
            "type": "syllables",
            "word": "pronunciation",
            "syllables": ["pruh", "nun", "see", "ay", "shun"],
            "focusIndex": 0,
            "focusSyllable": "pruh",
        }
    }

    response = client.post(
        "/api/v1/companion/voice-turn",
        json={
            "transcript": "pro",
            "learnerName": "Demo",
            "learnerAge": 8,
            "doodleId": "nova",
            "doodleName": "Nova",
            "context": context,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["teachingBoard"]["focusIndex"] == 0
    assert data["teachingBoard"]["focusSyllable"] == "pruh"
    assert "try again" in data["responseText"].lower()

    response = client.post(
        "/api/v1/companion/voice-turn",
        json={
            "transcript": "pruh",
            "learnerName": "Demo",
            "learnerAge": 8,
            "doodleId": "nova",
            "doodleName": "Nova",
            "context": context,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["teachingBoard"]["focusIndex"] == 1
    assert data["teachingBoard"]["focusSyllable"] == "nun"
    assert data["responseText"] == "Good. Your next sound is: nun."

    response = client.post(
        "/api/v1/companion/voice-turn",
        json={
            "transcript": "stop",
            "learnerName": "Demo",
            "learnerAge": 8,
            "doodleId": "nova",
            "doodleName": "Nova",
            "context": context,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "stop_practice"
    assert data["teachingBoard"] is None
    assert data["stateSequence"][-1] == "idle"


def test_quiz_prompt_returns_four_options():
    response = client.post(
        "/api/v1/companion/voice-turn",
        json={
            "transcript": "quiz me",
            "learnerName": "Demo",
            "learnerAge": 8,
            "doodleId": "nova",
            "doodleName": "Nova",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "quiz"
    assert len(data["teachingBoard"]["options"]) == 4
    assert "Option four" in data["responseText"]


def test_quiz_answer_accepts_letter_number_and_full_option():
    base_payload = {
        "learnerName": "Demo",
        "learnerAge": 8,
        "doodleId": "nova",
        "doodleName": "Nova",
        "context": {
            "currentBoard": {
                "type": "quiz",
                "question": "Which strategy helps with a long word?",
                "options": [
                    "Say it faster",
                    "Break it into syllables",
                    "Skip the tricky sound",
                    "Guess and move on",
                ],
                "correctAnswer": "Break it into syllables",
            }
        },
    }

    for transcript in ["option B", "number two", "Break it into syllables"]:
        response = client.post(
            "/api/v1/companion/voice-turn",
            json={**base_payload, "transcript": transcript},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == "quiz"
        assert data["teachingBoard"]["selectedIndex"] == 1
        assert data["memoryUpdate"]["quiz_correct"] is True

    response = client.post(
        "/api/v1/companion/voice-turn",
        json={**base_payload, "transcript": "option D"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["teachingBoard"]["selectedIndex"] == 3
    assert data["memoryUpdate"]["quiz_correct"] is False


def test_speech_endpoint_returns_audio(monkeypatch, tmp_path):
    audio_path = tmp_path / "speech.wav"
    audio_path.write_bytes(b"fake audio")

    def fake_synthesize_speech(**kwargs):
        return audio_path

    monkeypatch.setattr(
        "app.api.v1.companion.synthesize_speech",
        fake_synthesize_speech,
    )

    response = client.post(
        "/api/v1/companion/speech",
        json={
            "text": "Hi, I am Leo.",
            "doodleId": "leo",
            "voiceName": "Alex",
            "rate": 0.86,
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("audio/wav")
    assert response.content == b"fake audio"


def test_stats_request_returns_progress_board():
    response = client.post(
        "/api/v1/companion/voice-turn",
        json={
            "transcript": "how am I doing show my stats",
            "learnerName": "Demo",
            "learnerAge": 8,
            "doodleId": "leo",
            "doodleName": "Leo",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "stats_request"
    assert data["teachingBoard"]["type"] == "stats"
    assert "nextPractice" in data["teachingBoard"]


def test_dybrain_health_is_public(monkeypatch):
    class Response:
        def json(self):
            return {"models": [{"name": "qwen2.5vl:3b"}]}

    monkeypatch.setattr("app.api.dybrain.requests.get", lambda *args, **kwargs: Response())
    response = client.get("/api/dybrain/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"
