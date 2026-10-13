from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.router import api_router
from app.api.auth import router as auth_router
from app.api.learning import router as learning_router
from app.api.progress import router as progress_router
from app.api.dybrain import router as dybrain_router
from app.config import get_settings
from app.database import Base, engine, get_db
from app.models import Flashcard, User
from app.schemas import (
    FlashcardCreate,
    FlashcardRead,
    FlashcardUpdate,
    LoginRequest,
    LoginResponse,
    MessageResponse,
)
from app.seed import seed_database

settings = get_settings()

app = FastAPI(title="LearnWithMe Backend", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(dybrain_router)
app.include_router(auth_router)
app.include_router(learning_router)
app.include_router(progress_router)


@app.on_event("startup")
def on_startup() -> None:
    # Local SQLite is initialized here; remote database failures do not block
    # deterministic lessons or the health endpoint.
    if settings.sqlalchemy_database_url.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)
    print("LearnWithMe backend started.")


@app.get("/")
def home() -> str:
    return "Welcome to LearnWithMe!"


@app.get("/health")
def health_check() -> str:
    return "Server is running!"


@app.get("/api/test/db")
def test_db_connection(db: Session = Depends(get_db)) -> str:
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection failed: {exc}",
        ) from exc
    return "Database connection successful!"




@app.post("/api/flashcards", response_model=FlashcardRead)
def create_flashcard(
    payload: FlashcardCreate,
    db: Session = Depends(get_db),
) -> Flashcard:
    flashcard = Flashcard(
        term=payload.term,
        definition=payload.definition,
        score=payload.score or 0,
    )
    db.add(flashcard)
    db.commit()
    db.refresh(flashcard)
    return flashcard


@app.get("/api/flashcards", response_model=list[FlashcardRead])
def get_all_flashcards(db: Session = Depends(get_db)) -> List[Flashcard]:
    return db.query(Flashcard).order_by(Flashcard.id.asc()).all()


@app.put("/api/flashcards/{flashcard_id}", response_model=FlashcardRead)
def update_flashcard(
    flashcard_id: int,
    payload: FlashcardUpdate,
    db: Session = Depends(get_db),
) -> Flashcard:
    flashcard = db.get(Flashcard, flashcard_id)
    if flashcard is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flashcard not found")

    flashcard.term = payload.term
    flashcard.definition = payload.definition
    flashcard.score = payload.score or 0
    db.commit()
    db.refresh(flashcard)
    return flashcard


@app.delete("/api/flashcards/{flashcard_id}")
def delete_flashcard(flashcard_id: int, db: Session = Depends(get_db)) -> str:
    flashcard = db.get(Flashcard, flashcard_id)
    if flashcard is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Flashcard not found")

    db.delete(flashcard)
    db.commit()
    return "Flashcard deleted successfully!"
