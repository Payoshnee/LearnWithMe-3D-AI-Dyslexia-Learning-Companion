from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.lesson_service import BEGINNER_LESSONS, advance_lesson

router = APIRouter(prefix="/api/learning", tags=["learning"])
class LessonReply(BaseModel):
    lesson_id: str = "cat"
    step: int = Field(default=0, ge=0)
    response: str = Field(min_length=1, max_length=200)

@router.get("/lessons")
def lessons(): return [{"id": lesson_id, "steps": len(steps)} for lesson_id, steps in BEGINNER_LESSONS.items()]

@router.post("/answer")
def answer(payload: LessonReply): return advance_lesson(payload.lesson_id, payload.step, payload.response)
