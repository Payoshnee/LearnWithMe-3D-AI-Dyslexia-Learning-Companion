
"""
LearnWithMe — Wendy's Structured Teaching Engine

Supports 22 beginner words across three levels.
Deterministic answer checking — no Ollama required.

Existing API:
    advance_lesson(lesson_id, step, response)

Returns:
    complete, step, correct, message

The four-step structure is retained for compatibility
with the existing learning API and frontend.
"""

import re


# LEVEL 1 — Beginner words
# LEVEL 2 — Additional short-vowel words
# LEVEL 3 — Digraphs

TEACHING_WORDS = {
    "cat": (1, ["c", "a", "t"]),
    "sun": (1, ["s", "u", "n"]),
    "mat": (1, ["m", "a", "t"]),
    "sat": (1, ["s", "a", "t"]),
    "pin": (1, ["p", "i", "n"]),
    "tin": (1, ["t", "i", "n"]),
    "pan": (1, ["p", "a", "n"]),
    "bat": (1, ["b", "a", "t"]),

    "dog": (2, ["d", "o", "g"]),
    "pig": (2, ["p", "i", "g"]),
    "hen": (2, ["h", "e", "n"]),
    "pen": (2, ["p", "e", "n"]),
    "bed": (2, ["b", "e", "d"]),
    "red": (2, ["r", "e", "d"]),
    "cup": (2, ["c", "u", "p"]),
    "bus": (2, ["b", "u", "s"]),

    "ship": (3, ["sh", "i", "p"]),
    "shop": (3, ["sh", "o", "p"]),
    "fish": (3, ["f", "i", "sh"]),
    "chip": (3, ["ch", "i", "p"]),
    "chat": (3, ["ch", "a", "t"]),
    "thin": (3, ["th", "i", "n"]),
}


# Common names spoken by a learner or produced by
# Chrome speech recognition.
LETTER_NAMES = {
    "a": {"a", "ay", "aye"},
    "b": {"b", "bee", "be"},
    "c": {"c", "see", "cee"},
    "d": {"d", "dee"},
    "e": {"e", "ee"},
    "f": {"f", "ef", "eff"},
    "g": {"g", "gee"},
    "h": {"h", "aitch"},
    "i": {"i", "eye"},
    "j": {"j", "jay"},
    "k": {"k", "kay"},
    "l": {"l", "el"},
    "m": {"m", "em"},
    "n": {"n", "en"},
    "o": {"o", "oh"},
    "p": {"p", "pee"},
    "q": {"q", "cue"},
    "r": {"r", "ar"},
    "s": {"s", "ess"},
    "t": {"t", "tee"},
    "u": {"u", "you"},
}


SOUND_NAMES = {
    "c": {"k", "kuh", "c", "ck"},
    "a": {"a", "ah", "æ"},
    "s": {"s", "sss", "ss"},
    "m": {"m", "mmm", "mm"},
    "p": {"p", "puh"},
    "t": {"t", "tuh"},
    "b": {"b", "buh"},
    "d": {"d", "duh"},
    "i": {"i", "ih"},
    "n": {"n", "nnn"},
    "o": {"o", "ah"},
    "g": {"g", "guh"},
    "h": {"h", "hhh"},
    "e": {"e", "eh"},
    "r": {"r", "rrr"},
    "u": {"u", "uh"},
    "f": {"f", "fff"},
    "sh": {"sh", "shh", "shhh"},
    "ch": {"ch", "chuh"},
    "th": {"th", "thh"},
}


def normalize_answer(value: str) -> str:
    """Normalize text, including basic speech transcriptions."""
    text = str(value or "").lower().strip()

    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(text.split())


def compact_answer(value: str) -> str:
    return normalize_answer(value).replace(" ", "")


def make_steps(word: str, sounds: list[str]) -> list:
    """Build four compatible lesson steps."""

    first_letter = word[0].upper()
    first_sound = sounds[0]

    letter_answers = LETTER_NAMES.get(
        word[0],
        {word[0]},
    )

    sound_answers = SOUND_NAMES.get(
        first_sound,
        {first_sound},
    )

    first_sound_label = (
        "k" if first_sound == "c" else first_sound
    )

    return [
        (
            f"Find the letter {first_letter} in {word.upper()}",
            letter_answers,
        ),
        (
            f"Say the /{first_sound_label}/ sound",
            sound_answers,
        ),
        (
            f"Blend the sounds to make {word.upper()}",
            {word},
        ),
        (
            f"Read the word {word.upper()}",
            {word},
        ),
    ]


# Generate all lessons.
BEGINNER_LESSONS = {
    word: make_steps(word, sounds)
    for word, (_, sounds) in TEACHING_WORDS.items()
}


# Legacy CAT structure retained for compatibility.
CAT_LESSON = {
    "word": "CAT",
    "steps": [
        {
            "id": "recognize",
            "instruction": "Look at CAT. Find the letter C.",
        },
        {
            "id": "sound_c",
            "instruction": "The letter C makes the /k/ sound in CAT.",
        },
        {
            "id": "blend",
            "instruction": "Blend the sounds to make CAT.",
        },
        {
            "id": "read",
            "instruction": "Read the whole word CAT.",
        },
        {
            "id": "complete",
            "instruction": "Great effort! You finished CAT!",
        },
    ],
}


def get_lesson_step(step_index: int):
    """Backward-compatible CAT lesson helper."""
    steps = CAT_LESSON["steps"]

    if not 0 <= step_index < len(steps):
        return None

    return steps[step_index]


def get_available_lessons(level=None):
    """Return the words available at a given level."""
    result = []

    for word, (word_level, sounds) in TEACHING_WORDS.items():
        if level is None or int(level) == word_level:
            result.append({
                "id": word,
                "word": word.upper(),
                "level": word_level,
                "sounds": sounds,
                "step_count": len(BEGINNER_LESSONS[word]),
            })

    return result


def _answer_matches(response: str, accepted: set[str]) -> bool:
    """Use exact normalized matching, not substrings."""
    value = compact_answer(response)

    if not value:
        return False

    return any(
        value == compact_answer(answer)
        for answer in accepted
    )


def advance_lesson(
    lesson_id: str,
    step: int,
    response: str,
) -> dict:
    """
    Check the learner's answer and advance when appropriate.

    Each call is independent of chat history.
    The caller stores the current step.
    """

    lesson_id = normalize_answer(lesson_id)

    if lesson_id not in BEGINNER_LESSONS:
        return {
            "complete": False,
            "step": 0,
            "correct": False,
            "message": "This lesson is not available yet.",
        }

    steps = BEGINNER_LESSONS[lesson_id]

    step = max(0, int(step))

    if step >= len(steps):
        return {
            "complete": True,
            "step": len(steps),
            "correct": True,
            "message": (
                f"You have already completed "
                f"{lesson_id.upper()}! Well done!"
            ),
        }

    answer = normalize_answer(response)

    if not answer:
        return {
            "complete": False,
            "step": step,
            "correct": False,
            "message": (
                "Take your time. You can try again "
                "or ask Wendy for help."
            ),
        }

    if answer in {"hint", "help", "help me"}:
        instruction = steps[step][0]

        return {
            "complete": False,
            "step": step,
            "correct": False,
            "message": (
                f"Let's try together. {instruction}. "
                "Take your time!"
            ),
        }

    if answer in {"repeat", "again", "say again"}:
        return {
            "complete": False,
            "step": step,
            "correct": False,
            "message": f"Of course! {steps[step][0]}.",
        }

    if answer in {"skip", "next"}:
        next_step = step + 1

        if next_step >= len(steps):
            return {
                "complete": True,
                "step": len(steps),
                "correct": False,
                "message": (
                    f"We reached the end of {lesson_id.upper()}. "
                    "You can practice it again anytime!"
                ),
            }

        return {
            "complete": False,
            "step": next_step,
            "correct": False,
            "message": (
                f"Let's move on. {steps[next_step][0]}."
            ),
        }

    expected_answers = steps[step][1]

    if not _answer_matches(answer, expected_answers):
        return {
            "complete": False,
            "step": step,
            "correct": False,
            "message": (
                "Good try! Let's try that once more. "
                "You can ask for a hint whenever you need."
            ),
        }

    next_step = step + 1

    if next_step >= len(steps):
        return {
            "complete": True,
            "step": len(steps),
            "correct": True,
            "message": (
                f"Wonderful! You finished learning "
                f"{lesson_id.upper()}! "
                "Every small step matters!"
            ),
        }

    return {
        "complete": False,
        "step": next_step,
        "correct": True,
        "message": (
            f"Great work! {steps[next_step][0]}."
        ),
    }
