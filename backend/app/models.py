from typing import Dict, List, Optional

from sqlalchemy import Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)


class Flashcard(Base):
    __tablename__ = "flashcard"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    term: Mapped[str] = mapped_column(String(100), nullable=False)
    definition: Mapped[str] = mapped_column(String(255), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class LessonChunk(Base):
    __tablename__ = "lesson_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    topic: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    language: Mapped[str] = mapped_column(String(12), nullable=False, default="en")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)


class SpeechTurn(Base):
    __tablename__ = "speech_turns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    learner_name: Mapped[str] = mapped_column(String(120), nullable=False)
    learner_age: Mapped[int] = mapped_column(Integer, nullable=False)
    doodle_id: Mapped[str] = mapped_column(String(80), nullable=False)
    transcript: Mapped[str] = mapped_column(Text, nullable=False)
    response_text: Mapped[str] = mapped_column(Text, nullable=False)
    intent: Mapped[str] = mapped_column(String(80), nullable=False)
    detected_language: Mapped[str] = mapped_column(String(12), nullable=False, default="en")
    memory_update: Mapped[Dict] = mapped_column(JSON, nullable=False, default=dict)


class ChildMemory(Base):
    __tablename__ = "child_memory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    learner_name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    key: Mapped[str] = mapped_column(String(120), nullable=False)
    value: Mapped[Dict] = mapped_column(JSON, nullable=False, default=dict)

class LearningProgress(Base):
    __tablename__ = "learning_progress"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    data: Mapped[Dict] = mapped_column(JSON, nullable=False, default=dict)
