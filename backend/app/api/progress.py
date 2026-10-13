
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.api.auth import COOKIE_NAME
from app.database import get_db
from app.models import LearningProgress
from app.services.auth_service import validate_token


router = APIRouter(
    prefix="/api/progress",
    tags=["progress"],
)


class ProgressData(BaseModel):
    stars: int = Field(default=0, ge=0)
    completedLessons: list[str] = Field(default_factory=list)
    completedGames: list[str] = Field(default_factory=list)
    level: int = Field(default=1, ge=1, le=10)
    wordsLearned: list[str] = Field(default_factory=list)
    letterMastery: dict[str, int] = Field(default_factory=dict)


def user_id(request: Request):
    token = request.cookies.get(COOKIE_NAME)

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Sign in required",
        )

    return validate_token(token)


@router.get("")
def get_progress(
    request: Request,
    db: Session = Depends(get_db),
):
    uid = user_id(request)

    row = (
        db.query(LearningProgress)
        .filter_by(user_id=uid)
        .first()
    )

    if row is None:
        return ProgressData().model_dump()

    return ProgressData.model_validate(row.data or {}).model_dump()


@router.put("")
def put_progress(
    payload: ProgressData,
    request: Request,
    db: Session = Depends(get_db),
):
    uid = user_id(request)
    new_data = payload.model_dump()

    row = (
        db.query(LearningProgress)
        .filter_by(user_id=uid)
        .first()
    )

    if row is None:
        row = LearningProgress(
            user_id=uid,
            data=new_data,
        )
        db.add(row)
    else:
        row.data = new_data
        flag_modified(row, "data")

    db.commit()

    return new_data
