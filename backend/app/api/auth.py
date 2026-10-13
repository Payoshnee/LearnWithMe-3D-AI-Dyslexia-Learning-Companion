from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.base import LoginRequest, LoginResponse, RegisterRequest
from app.services.auth_service import authenticate, issue_token, register, validate_token

router = APIRouter(prefix="/api/auth", tags=["authentication"])
COOKIE_NAME = "learnwithme_session"
def account(user): return LoginResponse(message="Welcome to LearnWithMe", name=user.name, email=user.email)
def set_session(response: Response, user):
    from app.config import get_settings
    settings=get_settings()
    response.set_cookie(COOKIE_NAME,issue_token(user),max_age=settings.session_hours*3600,httponly=True,samesite="lax",secure=settings.cookie_secure,path="/")

@router.post("/register", response_model=LoginResponse, status_code=201)
def register_account(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    user=register(db,payload.name,payload.email,payload.password);set_session(response,user);return account(user)

@router.post("/login", response_model=LoginResponse)
def login_account(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user=authenticate(db,payload.email,payload.password);set_session(response,user);return account(user)

@router.get("/session", response_model=LoginResponse)
def validate_session(request: Request, db: Session = Depends(get_db)):
    token=request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="A session token is required.")
    user_id = validate_token(token)
    from app.models import User
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session account no longer exists.")
    return account(user)

@router.post("/logout")
def logout_account(response: Response):
    response.delete_cookie(COOKIE_NAME,path="/")
    return {"message":"Signed out"}
