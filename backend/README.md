# DyslexiLearn FastAPI Backend

This backend replaces the previous Spring Boot service while keeping the same frontend-facing API paths.

## Run Locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

The backend expects PostgreSQL to be available at `DATABASE_URL`. If `DATABASE_URL` is not set, it uses:

```text
postgresql+psycopg://admin:password123@localhost:5432/dyslexialearn
```

## Main Routes

- `POST /api/auth/login`
- `GET /api/flashcards`
- `POST /api/flashcards`
- `PUT /api/flashcards/{id}`
- `DELETE /api/flashcards/{id}`
- `POST /api/ai/rag/ask`
- `POST /api/ai/synonym`
- `POST /api/ai/socratic`
- `GET /api/v1/companion/preferences`
- `PUT /api/v1/companion/preferences`
- `POST /api/v1/companion/sessions`
- `POST /api/v1/companion/respond`
- `GET /health`
