"""Minimal, dependency-free parent account authentication.

Passwords use PBKDF2-HMAC-SHA256 with a per-account salt.  For production,
set SESSION_SECRET and use HTTPS; a managed Postgres DATABASE_URL is supported.
"""
import base64, hashlib, hmac, os, time
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.config import get_settings
from app.models import User

ITERATIONS = 310_000

def hash_password(password: str) -> str:
    if len(password) < 8: raise ValueError("Password must be at least 8 characters.")
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return f"pbkdf2_sha256${ITERATIONS}${base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"

def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, rounds, salt, digest = stored.split("$")
        if algorithm != "pbkdf2_sha256": return False
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), base64.b64decode(salt), int(rounds))
        return hmac.compare_digest(actual, base64.b64decode(digest))
    except (ValueError, TypeError): return False

def issue_token(user: User) -> str:
    settings = get_settings(); expires = int(time.time()) + settings.session_hours * 3600
    body = f"{user.id}:{expires}"; signature = hmac.new(settings.session_secret.encode(), body.encode(), hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(f"{body}:{signature}".encode()).decode()

def validate_token(token: str) -> int:
    """Return the account id only for an untampered, unexpired session token."""
    try:
        raw = base64.urlsafe_b64decode(token.encode()).decode()
        user_id, expires, signature = raw.split(":")
        body = f"{user_id}:{expires}"
        expected = hmac.new(get_settings().session_secret.encode(), body.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected) or int(expires) < int(time.time()):
            raise ValueError
        return int(user_id)
    except (ValueError, TypeError, UnicodeDecodeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session is invalid or expired.")

def register(db: Session, name: str, email: str, password: str) -> User:
    if db.query(User).filter(User.email == email.lower()).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with that email already exists.")
    try: password_hash = hash_password(password)
    except ValueError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc
    user = User(name=name.strip(), email=email.lower(), password_hash=password_hash)
    db.add(user); db.commit(); db.refresh(user)
    return user

def authenticate(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email.lower()).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return user
