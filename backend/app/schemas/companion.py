from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


def to_camel(value: str) -> str:
    head, *tail = value.split("_")
    return head + "".join(part.capitalize() for part in tail)


class CompanionPreferences(BaseModel):
    character_id: Optional[str] = None
    muted: bool = False
    text_only: bool = False
    reduced_motion: bool = False
    speech_rate: float = Field(default=0.85, ge=0.5, le=1.5)


class CompanionSessionRequest(BaseModel):
    lesson_type: Optional[str] = None
    lesson_id: Optional[str] = None


class CompanionRespondRequest(BaseModel):
    session_id: Optional[str] = None
    message: str = ""
    lesson_type: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class CompanionEndSessionRequest(BaseModel):
    session_id: Optional[str] = None


class CompanionCharacterInstruction(BaseModel):
    state: str
    animation: Optional[str] = None
    emotion: str = "neutral"


class CompanionBoardInstruction(BaseModel):
    visible: bool = False
    mode: str = "none"
    title: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    highlighted_index: int = -1


class CompanionResponse(BaseModel):
    message: str
    character: CompanionCharacterInstruction
    board: CompanionBoardInstruction
    next_action: Optional[str] = None
    session_id: Optional[str] = None


class CompanionVoiceTurnRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    transcript: str
    session_id: str = "default"
    learner_name: str = "Learner"
    learner_age: int = Field(default=8, ge=4, le=18)
    doodle_id: str = "nova"
    doodle_name: str = "Nova"
    language: str = "auto"
    context: Dict[str, Any] = Field(default_factory=dict)


class CompanionTeachingBoard(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    type: str = "syllables"
    word: Optional[str] = None
    syllables: List[str] = Field(default_factory=list)
    question: Optional[str] = None
    options: List[str] = Field(default_factory=list)
    correct_answer: Optional[str] = None
    feedback: Optional[str] = None
    accuracy: Optional[int] = None
    tricky_words: List[str] = Field(default_factory=list)
    next_practice: Optional[str] = None
    prompt: Optional[str] = None
    heard_text: Optional[str] = None
    score: Optional[int] = None
    passed: Optional[bool] = None
    weak_syllable: Optional[str] = None
    focus_syllable: Optional[str] = None
    focus_index: Optional[int] = None
    selected_answer: Optional[str] = None
    selected_index: Optional[int] = None


class CompanionVoiceTurnResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    transcript: str
    detected_language: str
    intent: str
    state_sequence: List[str]
    response_text: str
    teaching_board: Optional[CompanionTeachingBoard] = None
    memory_update: Dict[str, Any] = Field(default_factory=dict)
    source: str = "mock-rag"


class CompanionSpeechRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    text: str = Field(min_length=1, max_length=1200)
    doodle_id: str = "nova"
    voice_name: Optional[str] = None
    rate: float = Field(default=0.86, ge=0.5, le=1.5)


class CompanionSystemStatus(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    status: str
    ollama_reachable: bool = False
    chat_model: str
    embedding_model: str
    loaded_models: List[str] = Field(default_factory=list)
    message: str


class BrainConnectionTestRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    brain_type: str
    provider: str
    endpoint: str = ""
    model: str = ""
    api_key: str = ""
    api_version: str = "2024-10-21"
    deployment: str = ""
    project_id: str = ""
    location: str = ""


class BrainConnectionTestResponse(BaseModel):
    connected: bool
    message: str
    models: List[str] = Field(default_factory=list)
