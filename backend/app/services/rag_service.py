from __future__ import annotations

import math
import re
from difflib import SequenceMatcher

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import ChildMemory, LessonChunk, SpeechTurn
from app.schemas.companion import CompanionVoiceTurnRequest
from app.services.local_ai_service import LocalAIUnavailable, ollama_chat, ollama_embed

settings = get_settings()


def cosine_similarity(left: list[float] | None, right: list[float] | None) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def ensure_chunk_embeddings(db: Session) -> None:
    chunks = db.query(LessonChunk).filter(LessonChunk.embedding.is_(None)).all()
    changed = False
    for chunk in chunks:
        try:
            chunk.embedding = ollama_embed(f"{chunk.title}\n{chunk.content}")
            changed = True
        except LocalAIUnavailable:
            return
    if changed:
        db.commit()


def retrieve_context(db: Session, query: str) -> tuple[list[LessonChunk], str]:
    ensure_chunk_embeddings(db)
    chunks = db.query(LessonChunk).order_by(LessonChunk.id.asc()).all()

    try:
        query_embedding = ollama_embed(query)
    except LocalAIUnavailable:
        query_embedding = None

    if query_embedding:
        ranked = sorted(
            chunks,
            key=lambda chunk: cosine_similarity(chunk.embedding, query_embedding),
            reverse=True,
        )
        return ranked[: settings.rag_top_k], "ollama-embeddings"

    tokens = {token.strip(".,?!").lower() for token in query.split() if token.strip()}
    ranked = sorted(
        chunks,
        key=lambda chunk: sum(1 for token in tokens if token in chunk.content.lower()),
        reverse=True,
    )
    return ranked[: settings.rag_top_k], "keyword-fallback"


def detect_intent(transcript: str) -> str:
    normalized = transcript.lower()
    if any(phrase in normalized for phrase in ["stop", "cancel", "done", "quit", "new command"]):
        return "stop_practice"
    if any(word in normalized for word in ["stats", "progress", "score", "how am i doing"]):
        return "stats_request"
    if any(word in normalized for word in ["quiz", "question", "test me", "option", "number"]):
        return "quiz"
    if any(
        phrase in normalized
        for phrase in [
            "pronounce",
            "pronunciation",
            "practice pronunciation",
            "pronunciation of",
            "how to say",
            "help me say",
            "say the word",
            "sound out",
            "syllable",
        ]
    ):
        return "pronunciation_help"
    if any(word in normalized for word in ["hindi", "translate", "meaning", "samajh", "समझ"]):
        return "translation_help"
    return "general_help"


def detect_language(transcript: str) -> str:
    if any("\u0900" <= character <= "\u097f" for character in transcript):
        return "hi"
    return "en"


def extract_pronunciation_word(transcript: str) -> str:
    normalized = transcript.strip().lower()
    patterns = [
        r"(?:pronounce|pronunciation of|how to say|help me say|say the word|sound out)\s+(?:the\s+word\s+)?([a-zA-Z][a-zA-Z'-]{1,30})",
        r"(?:word is|word)\s+([a-zA-Z][a-zA-Z'-]{1,30})",
    ]
    stop_words = {"please", "this", "that", "word", "pronounce", "say", "help", "me", "to", "the"}
    for pattern in patterns:
        match = re.search(pattern, normalized)
        if match:
            candidate = match.group(1).strip(" .'\"")
            if candidate and candidate not in stop_words:
                return candidate
    words = [word.strip(".,?!'\"").lower() for word in normalized.split()]
    for word in reversed(words):
        if len(word) > 2 and word not in stop_words:
            return word
    return "pronunciation"


def simple_syllables(word: str) -> list[str]:
    known = {
        "pronunciation": ["pruh", "nun", "see", "ay", "shun"],
        "celebration": ["cel", "e", "bra", "tion"],
        "imagination": ["im", "ag", "i", "na", "tion"],
        "education": ["ed", "u", "ca", "tion"],
        "beautiful": ["beau", "ti", "ful"],
        "elephant": ["el", "e", "phant"],
    }
    clean_word = word.lower().strip()
    if clean_word in known:
        return known[clean_word]
    vowels = "aeiouy"
    chunks = []
    current = ""
    for index, character in enumerate(clean_word):
        current += character
        next_character = clean_word[index + 1] if index + 1 < len(clean_word) else ""
        if character in vowels and next_character and next_character not in vowels and len(current) >= 2:
            chunks.append(current)
            current = ""
    if current:
        chunks.append(current)
    return chunks if len(chunks) > 1 else [clean_word]


LETTER_TO_INDEX = {"a": 0, "b": 1, "c": 2, "d": 3}
NUMBER_TO_INDEX = {
    "1": 0,
    "one": 0,
    "first": 0,
    "2": 1,
    "two": 1,
    "second": 1,
    "3": 2,
    "three": 2,
    "third": 2,
    "4": 3,
    "four": 3,
    "fourth": 3,
}


def normalize_answer(value: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", "", value.lower()).strip()


def parse_quiz_answer(transcript: str, options: list[str]) -> dict:
    normalized = normalize_answer(transcript)
    tokens = normalized.split()

    for token in tokens:
        if token in NUMBER_TO_INDEX and NUMBER_TO_INDEX[token] < len(options):
            selected_index = NUMBER_TO_INDEX[token]
            return {
                "answered": True,
                "selected_index": selected_index,
                "selected_answer": options[selected_index],
            }

    for index, token in enumerate(tokens):
        if token == "option" and index + 1 < len(tokens):
            next_token = tokens[index + 1]
            if next_token in LETTER_TO_INDEX and LETTER_TO_INDEX[next_token] < len(options):
                selected_index = LETTER_TO_INDEX[next_token]
                return {
                    "answered": True,
                    "selected_index": selected_index,
                    "selected_answer": options[selected_index],
                }
            if next_token in NUMBER_TO_INDEX and NUMBER_TO_INDEX[next_token] < len(options):
                selected_index = NUMBER_TO_INDEX[next_token]
                return {
                    "answered": True,
                    "selected_index": selected_index,
                    "selected_answer": options[selected_index],
                }

    normalized_options = [normalize_answer(option) for option in options]
    ranked = sorted(
        enumerate(normalized_options),
        key=lambda item: SequenceMatcher(None, normalized, item[1]).ratio(),
        reverse=True,
    )
    if ranked and ranked[0][1] and ranked[0][0] < len(options):
        score = SequenceMatcher(None, normalized, ranked[0][1]).ratio()
        if score >= 0.72 or ranked[0][1] in normalized:
            selected_index = ranked[0][0]
            return {
                "answered": True,
                "selected_index": selected_index,
                "selected_answer": options[selected_index],
            }

    return {"answered": False}


def score_pronunciation_attempt(
    transcript: str,
    word: str,
    syllables: list[str],
    focus_syllable: str | None = None,
) -> dict:
    heard = normalize_answer(transcript)
    target = normalize_answer(word)
    focus_target = normalize_answer(focus_syllable or "")
    if not heard or not target:
        return {
            "score": 0,
            "passed": False,
            "weak_syllable": focus_syllable or (syllables[0] if syllables else word),
        }

    word_score = SequenceMatcher(None, heard.replace(" ", ""), target).ratio()
    if focus_target:
        focus_score = SequenceMatcher(None, heard.replace(" ", ""), focus_target).ratio()
        if focus_target in heard:
            focus_score = 1.0
        return {
            "score": round(focus_score * 100),
            "passed": focus_score >= 0.78,
            "weak_syllable": focus_syllable,
        }

    syllable_scores = []
    for syllable in syllables:
        clean_syllable = normalize_answer(syllable)
        syllable_scores.append(
            (
                syllable,
                1.0
                if clean_syllable and clean_syllable in heard
                else SequenceMatcher(None, heard, clean_syllable).ratio(),
            )
        )
    weak_syllable = min(syllable_scores, key=lambda item: item[1])[0] if syllable_scores else word
    score = round(max(word_score, max((item[1] for item in syllable_scores), default=0)) * 100)
    return {
        "score": score,
        "passed": score >= 78,
        "weak_syllable": weak_syllable,
    }


def build_quiz(transcript: str, current_board: dict | None = None) -> dict:
    question = (current_board or {}).get("question") or "Which strategy helps with a long word?"
    options = (current_board or {}).get("options") or [
        "Say it faster",
        "Break it into syllables",
        "Skip the tricky sound",
        "Guess and move on",
    ]
    correct_answer = (current_board or {}).get("correctAnswer") or "Break it into syllables"
    parsed_answer = parse_quiz_answer(transcript, options)
    if parsed_answer["answered"]:
        selected_answer = parsed_answer["selected_answer"]
        correct = normalize_answer(selected_answer) == normalize_answer(correct_answer)
        letter = "ABCD"[parsed_answer["selected_index"]]
        if correct:
            feedback = f"I heard option {letter}: {selected_answer}. Correct."
        else:
            feedback = (
                f"I heard option {letter}: {selected_answer}. Good try. "
                f"The best answer is {correct_answer}."
            )
        return {
            "answered": True,
            "correct": correct,
            "feedback": feedback,
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "selected_answer": selected_answer,
            "selected_index": parsed_answer["selected_index"],
        }
    return {
        "answered": False,
        "question": question,
        "options": options,
        "correct_answer": correct_answer,
    }


def build_stats_board(payload: CompanionVoiceTurnRequest, db: Session | None) -> dict:
    turns = []
    if db is not None:
        turns = (
            db.query(SpeechTurn)
            .filter(SpeechTurn.learner_name == payload.learner_name)
            .order_by(SpeechTurn.id.desc())
            .limit(20)
            .all()
        )

    practiced_words = []
    correct_quiz_count = 0
    quiz_count = 0
    for turn in turns:
        update = turn.memory_update or {}
        if update.get("last_word"):
            practiced_words.append(update["last_word"])
        if "quiz_correct" in update:
            quiz_count += 1
            correct_quiz_count += 1 if update["quiz_correct"] else 0

    accuracy = round((correct_quiz_count / quiz_count) * 100) if quiz_count else 0
    tricky_words = list(dict.fromkeys(practiced_words))[:3] or ["pronunciation"]
    next_practice = tricky_words[0]
    return {
        "accuracy": accuracy,
        "tricky_words": tricky_words,
        "next_practice": next_practice,
    }


def generate_response(
    payload: CompanionVoiceTurnRequest,
    intent: str,
    context_chunks: list[LessonChunk],
    history: list[dict] | None = None,
) -> tuple[str, str]:
    context = "\n\n".join(f"{chunk.title}: {chunk.content}" for chunk in context_chunks)
    system_prompt = (
        "You are a gentle voice-first 3D doodle tutor for a child with dyslexia. "
        "Answer in short, warm sentences. Use the provided lesson context. "
        "Do not overload the child. Give one small next step. "
        "The doodle name is your name, not the learner name. "
        "Never say 'Hey' to the doodle name. Address the learner by learner name. "
        "Do not praise an action the child has not done yet."
    )
    user_prompt = (
        f"Learner name: {payload.learner_name}\n"
        f"Learner age: {payload.learner_age}\n"
        f"Doodle name: {payload.doodle_name}\n"
        f"Intent: {intent}\n"
        f"Transcript: {payload.transcript}\n\n"
        f"Retrieved context:\n{context}\n\n"
        "Return only the spoken reply."
    )

    messages = [{"role": "system", "content": system_prompt}]
    for turn in (history or [])[-6:]:
        messages.append({"role": "user", "content": turn["user"]})
        messages.append({"role": "assistant", "content": turn["assistant"]})
    messages.append({"role": "user", "content": user_prompt})

    try:
        return (
            ollama_chat(messages, payload.context.get("brain")),
            "ollama-rag",
        )
    except LocalAIUnavailable:
        if intent == "pronunciation_help":
            return (
                "Let us practice pronunciation one sound at a time: pruh, nun, see, ay, shun. Start with pruh.",
                "mock-rag",
            )
        return (
            "I heard you. Tell me the word or lesson you want to practice, and I will help one small step at a time.",
            "mock-rag",
        )


def generate_pronunciation_attempt_feedback(
    payload: CompanionVoiceTurnRequest,
    word: str,
    syllables: list[str],
    context_chunks: list[LessonChunk],
) -> tuple[str, str]:
    context = "\n\n".join(f"{chunk.title}: {chunk.content}" for chunk in context_chunks)
    prompt = (
        "A child is practicing pronunciation with a 3D doodle tutor.\n"
        f"Target word: {word}\n"
        f"Syllables: {', '.join(syllables)}\n"
        f"Child said/transcribed: {payload.transcript}\n"
        f"Context: {context}\n\n"
        "Decide if the child attempted the target word or a target syllable. "
        "Give short supportive feedback. Do not restart the full lesson. "
        "If it seems correct, praise and ask for one next small challenge. "
        "If unclear, ask them to repeat one specific syllable."
    )
    try:
        return (
            ollama_chat(
                [
                    {
                        "role": "system",
                        "content": "You are a warm dyslexia pronunciation coach. Keep replies under 35 words.",
                    },
                    {"role": "user", "content": prompt},
                ],
                payload.context.get("brain"),
            ),
            "ollama-rag",
        )
    except LocalAIUnavailable:
        if payload.transcript.lower().strip(" .,!?'\"") == word.lower():
            return (
                f"Nice try saying {word}. Now let us make the tricky part clearer: say {syllables[min(2, len(syllables) - 1)]} slowly.",
                "mock-rag",
            )
        return (
            f"Good effort. I heard your try. Let us repeat just one part: {syllables[0]}.",
            "mock-rag",
        )


def remember_turn(
    db: Session,
    payload: CompanionVoiceTurnRequest,
    intent: str,
    detected_language: str,
    response_text: str,
    memory_update: dict,
) -> None:
    db.add(
        SpeechTurn(
            learner_name=payload.learner_name,
            learner_age=payload.learner_age,
            doodle_id=payload.doodle_id,
            transcript=payload.transcript,
            response_text=response_text,
            intent=intent,
            detected_language=detected_language,
            memory_update=memory_update,
        )
    )
    db.add(
        ChildMemory(
            learner_name=payload.learner_name,
            key=f"last_{intent}",
            value=memory_update,
        )
    )
    db.commit()
