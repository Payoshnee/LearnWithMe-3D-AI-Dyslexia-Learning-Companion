from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(LoginRequest):
    name: str = Field(..., min_length=1, max_length=80)


class LoginResponse(BaseModel):
    message: str
    name: str
    email: EmailStr
    token: str = ""


class MessageResponse(BaseModel):
    message: str


class FlashcardBase(BaseModel):
    term: str = Field(..., min_length=1, max_length=100)
    definition: str = Field(..., min_length=1, max_length=255)
    score: int = Field(default=0, ge=0)


class FlashcardCreate(FlashcardBase):
    pass


class FlashcardUpdate(FlashcardBase):
    pass


class FlashcardRead(FlashcardBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class RAGRequest(BaseModel):
    question: str
    model: Optional[str] = None


class SynonymRequest(BaseModel):
    word: str
    sentence: str
    model: Optional[str] = None


class SocraticRequest(BaseModel):
    question: str
    context: str
    model: Optional[str] = None


class AIResponse(BaseModel):
    response: Optional[str] = None
    answer: Optional[str] = None
