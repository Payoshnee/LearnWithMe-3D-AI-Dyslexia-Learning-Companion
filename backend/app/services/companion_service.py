from uuid import uuid4
from typing import Optional
from collections import defaultdict, deque
from threading import Lock

from sqlalchemy.orm import Session

from app.config import get_settings
from app.schemas.companion import (
    CompanionBoardInstruction,
    CompanionCharacterInstruction,
    CompanionPreferences,
    CompanionRespondRequest,
    CompanionResponse,
    CompanionSessionRequest,
    CompanionTeachingBoard,
    CompanionVoiceTurnRequest,
    CompanionVoiceTurnResponse,
)
from app.services.rag_service import (
    build_quiz,
    build_stats_board,
    detect_intent,
    detect_language,
    extract_pronunciation_word,
    generate_response,
    generate_pronunciation_attempt_feedback,
    remember_turn,
    retrieve_context,
    score_pronunciation_attempt,
    simple_syllables,
)

settings = get_settings()

# Development-only short-term memory. Resets when the server restarts.
# Keyed by learner name and character until unique client session IDs are added.
conversation_history = defaultdict(lambda: deque(maxlen=6))
history_lock = Lock()

_preferences = CompanionPreferences(
    character_id=settings.companion_default_character,
    muted=False,
    text_only=False,
    reduced_motion=False,
    speech_rate=0.85,
)


def get_preferences() -> CompanionPreferences:
    return _preferences


def update_preferences(preferences: CompanionPreferences) -> CompanionPreferences:
    global _preferences
    _preferences = preferences
    return _preferences


def start_session(payload: CompanionSessionRequest) -> CompanionResponse:
    session_id = str(uuid4())
    lesson_label = payload.lesson_type or "lesson"
    return CompanionResponse(
        session_id=session_id,
        message=f"Your learning companion is ready for this {lesson_label}.",
        character=CompanionCharacterInstruction(
            state="idle",
            animation="Idle",
            emotion="friendly",
        ),
        board=CompanionBoardInstruction(),
        next_action="wait",
    )


def end_session() -> CompanionResponse:
    return CompanionResponse(
        message="Companion session ended.",
        character=CompanionCharacterInstruction(
            state="idle",
            animation="Idle",
            emotion="neutral",
        ),
        board=CompanionBoardInstruction(),
        next_action="wait",
    )


def respond(payload: CompanionRespondRequest) -> CompanionResponse:
    return CompanionResponse(
        session_id=payload.session_id,
        message="I am ready to help when Phase 1 connects lesson intelligence.",
        character=CompanionCharacterInstruction(
            state="encouraging",
            animation="Encourage",
            emotion="encouraging",
        ),
        board=CompanionBoardInstruction(
            visible=False,
            mode="none",
            title=None,
            content=None,
            highlighted_index=-1,
        ),
        next_action="wait",
    )


def handle_voice_turn(
    payload: CompanionVoiceTurnRequest,
    db: Optional[Session] = None,
) -> CompanionVoiceTurnResponse:
    transcript = payload.transcript.strip()
    # A client-generated session id prevents one learner or browser tab from
    # receiving another session's short-term conversation history.
    session_key = (payload.session_id, payload.doodle_id)
    with history_lock:
        recent_history = list(conversation_history[session_key])
    intent = detect_intent(transcript)
    detected_language = detect_language(transcript)
    current_board = payload.context.get("currentBoard") or {}
    current_board_type = current_board.get("type")
    current_word = (current_board.get("word") or "").strip()
    current_syllables = current_board.get("syllables") or []
    current_focus_index = current_board.get("focusIndex")
    if current_focus_index is None:
        current_focus_index = current_board.get("focus_index")
    clean_attempt = transcript.lower().strip(" .,!?'\"")

    if intent == "stop_practice":
        pass
    elif (
        current_board_type == "syllables"
        and current_word
        and (
            clean_attempt == current_word.lower()
            or clean_attempt in [str(syllable).lower() for syllable in current_syllables]
            or len(transcript.split()) <= 3
        )
    ):
        intent = "pronunciation_attempt"
    elif current_board_type == "quiz":
        intent = "quiz"

    context_chunks = []
    retrieval_source = "local-teaching-rule"

    # Pronunciation, quizzes, commands, and stats are deterministic teaching
    # flows. Do not wake the remote embedding/chat model for these turns.
    # This keeps them usable when a free Hugging Face Space is cold.
    needs_llm_context = intent in {"general_help", "translation_help"}
    if db is not None and needs_llm_context:
        context_chunks, retrieval_source = retrieve_context(db, transcript)

    response_text = ""
    generation_source = "local-rules"

    if intent == "stop_practice":
        teaching_board = None
        state_sequence = ["processing", "speaking", "idle"]
        response_text = "Okay, I stopped that practice. Tell me what you want to do next."
        generation_source = "local-command"
        memory_update = {
            "focus": "practice_stopped",
            "last_transcript": transcript,
            "retrieved_chunks": [chunk.title for chunk in context_chunks],
        }
    elif intent == "pronunciation_attempt":
        target_word = current_word
        syllables = [str(syllable) for syllable in current_syllables] or simple_syllables(target_word)
        try:
            focus_index = int(current_focus_index)
        except (TypeError, ValueError):
            focus_index = 0
        focus_index = max(0, min(focus_index, len(syllables) - 1))
        focus_syllable = syllables[focus_index]
        score = score_pronunciation_attempt(
            transcript,
            target_word,
            syllables,
            focus_syllable=focus_syllable,
        )

        if not score["passed"]:
            response_text = f"Try again: {focus_syllable}."
            next_focus_index = focus_index
            next_focus_syllable = focus_syllable
            teaching_board = CompanionTeachingBoard(
                type="syllables",
                word=target_word,
                syllables=syllables,
                heard_text=transcript,
                score=score["score"],
                passed=False,
                weak_syllable=focus_syllable,
                focus_syllable=next_focus_syllable,
                focus_index=next_focus_index,
                prompt=f"Try again: {focus_syllable}.",
            )
        elif focus_index < len(syllables) - 1:
            next_focus_index = focus_index + 1
            next_focus_syllable = syllables[next_focus_index]
            response_text = f"Good. Your next sound is: {next_focus_syllable}."
            teaching_board = CompanionTeachingBoard(
                type="syllables",
                word=target_word,
                syllables=syllables,
                heard_text=transcript,
                score=score["score"],
                passed=False,
                weak_syllable=next_focus_syllable,
                focus_syllable=next_focus_syllable,
                focus_index=next_focus_index,
                prompt=f"Now repeat {next_focus_syllable} slowly.",
            )
        else:
            response_text = f"Great work. You completed {target_word}."
            teaching_board = None
        generation_source = "local-pronunciation-score"
        state_sequence = (
            ["processing", "speaking", "idle"]
            if teaching_board is None
            else ["processing", "speaking", "pointing", "listening"]
        )
        memory_update = {
            "last_word": target_word,
            "last_attempt": transcript,
            "pronunciation_score": score["score"],
            "passed": teaching_board is None,
            "weak_syllable": score["weak_syllable"],
            "focus_index": None if teaching_board is None else teaching_board.focus_index,
            "focus": "pronunciation_attempt_feedback",
            "retrieved_chunks": [chunk.title for chunk in context_chunks],
        }
    elif intent == "pronunciation_help":
        target_word = extract_pronunciation_word(transcript)
        syllables = simple_syllables(target_word)
        teaching_board = CompanionTeachingBoard(
            type="syllables",
            word=target_word,
            syllables=syllables,
            weak_syllable=syllables[0],
            focus_syllable=syllables[0],
            focus_index=0,
            prompt=f"Repeat just {syllables[0]} slowly.",
        )
        state_sequence = ["processing", "speaking", "pointing", "listening"]
        memory_update = {
            "last_word": target_word,
            "focus": "syllable_breakdown",
            "confidence_signal": "needs_support",
            "retrieved_chunks": [chunk.title for chunk in context_chunks],
        }
        response_text = f"{payload.learner_name}, start with one sound: {syllables[0]}."
    elif intent == "quiz":
        quiz = build_quiz(transcript, current_board)
        if quiz.get("answered"):
            teaching_board = CompanionTeachingBoard(
                type="quiz",
                question=quiz["question"],
                options=quiz["options"],
                correct_answer=quiz["correct_answer"],
                feedback=quiz["feedback"],
                selected_answer=quiz["selected_answer"],
                selected_index=quiz["selected_index"],
            )
            response_text = quiz["feedback"]
            state_sequence = ["processing", "speaking", "idle"]
            memory_update = {
                "focus": "quiz_answer",
                "quiz_correct": quiz["correct"],
                "selected_answer": quiz["selected_answer"],
                "selected_index": quiz["selected_index"],
                "retrieved_chunks": [chunk.title for chunk in context_chunks],
            }
        else:
            teaching_board = CompanionTeachingBoard(
                type="quiz",
                question=quiz["question"],
                options=quiz["options"],
                correct_answer=quiz["correct_answer"],
            )
            response_text = (
                "Quiz time. Which strategy helps with a long word? "
                "Option one: say it faster. Option two: break it into syllables. "
                "Option three: skip the tricky sound. Option four: guess and move on."
            )
            state_sequence = ["processing", "speaking", "listening"]
            memory_update = {
                "focus": "quiz_prompt",
                "retrieved_chunks": [chunk.title for chunk in context_chunks],
            }
    elif intent == "stats_request":
        stats = build_stats_board(payload, db)
        teaching_board = CompanionTeachingBoard(
            type="stats",
            accuracy=stats["accuracy"],
            tricky_words=stats["tricky_words"],
            next_practice=stats["next_practice"],
            prompt="Your learning progress",
        )
        response_text = (
            f"Here is your progress. Your quiz accuracy is {stats['accuracy']} percent. "
            f"Next, we can practice {stats['next_practice']}."
        )
        state_sequence = ["processing", "speaking", "idle"]
        memory_update = {
            "focus": "stats_review",
            "next_practice": stats["next_practice"],
            "retrieved_chunks": [chunk.title for chunk in context_chunks],
        }
    else:
        response_text, generation_source = generate_response(
            payload, intent, context_chunks, history=recent_history
        )
        teaching_board = None
        state_sequence = ["processing", "speaking", "idle"]
        memory_update = {
            "last_transcript": transcript,
            "focus": "open_voice_turn",
            "retrieved_chunks": [chunk.title for chunk in context_chunks],
        }

    memory_update = {
        **memory_update,
        "learner_age": payload.learner_age,
        "doodle_id": payload.doodle_id,
        "retrieval_source": retrieval_source,
        "generation_source": generation_source,
        "future_pipeline": "local_stt_translation_rag_tts",
    }

    if db is not None:
        remember_turn(
            db,
            payload=payload,
            intent=intent,
            detected_language=detected_language,
            response_text=response_text,
            memory_update=memory_update,
        )

    with history_lock:
        conversation_history[session_key].append({
            "user": transcript,
            "assistant": response_text,
        })

    return CompanionVoiceTurnResponse(
        transcript=transcript,
        detectedLanguage=detected_language,
        intent=intent,
        stateSequence=state_sequence,
        responseText=response_text,
        teachingBoard=teaching_board,
        memoryUpdate=memory_update,
        source=generation_source,
    )
