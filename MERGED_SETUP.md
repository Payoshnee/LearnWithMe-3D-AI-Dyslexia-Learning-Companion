# LearnWithMe-Merged

This merge keeps the original dark blue/teal robot-city interface, original React Three Fiber scene, Wendy (`wendy.glb`), Bob (`mira.glb`), voice previews, and day/night learning stage. Authentication, structured CAT/SUN lessons, four multi-level phonics games, reading, automatic learner-enabled speech, progress persistence and deployment files are integrated into that design.

For the current validation record and exact third-party rights, also read `UPDATED_SETUP_AND_TESTS.md` and `ATTRIBUTIONS_AND_LICENSES.md`.

## Windows PowerShell

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

In a second PowerShell window:

```powershell
cd backend
Copy-Item .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

Open `http://localhost:5173`. Local development uses SQLite and creates `backend/learnwithme.db`. Passwords use salted PBKDF2 hashing. Authentication uses an HttpOnly session cookie, never localStorage. For HTTPS production set `COOKIE_SECURE=true`, use a long random `SESSION_SECRET`, and point `DATABASE_URL` at persistent managed PostgreSQL.

## Ollama

```powershell
ollama pull llama3.2:1b
ollama pull nomic-embed-text
ollama serve
```

Defaults are FastAPI `http://127.0.0.1:8080` and Ollama `http://127.0.0.1:11434`. Deterministic lessons and games work without Ollama.

## Vercel and Modal

Deploy `frontend` to Vercel. Set `VITE_API_BASE_URL` to the backend HTTPS URL. `vercel.json` preserves client-side routes.

From `backend`, install Modal and run `modal setup`, create the documented `learnwithme-secrets`, then run `modal deploy modal_app.py`. The function scales to zero. Modal cannot access local Ollama; configure a remote provider separately if needed. Free credits, pricing and cold-start behavior can change—set spending limits and inspect current Modal usage before enabling external inference. No deployment or billing was activated by this project.

## Limitations

Browser speech recognition requires a supporting browser, microphone permission and a secure context outside localhost. Piper requires its executable and voice files; browser SpeechSynthesis is the fallback. Speech-recognition text is not a pronunciation-quality score. A persistent production database is required because Modal container-local SQLite does not survive all scale-to-zero lifecycle events.
