# LearnWithMe: setup and deployment

## Windows PowerShell

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

In another window:

```powershell
cd backend
Copy-Item .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

Open `http://localhost:5173`.

## Environment

`frontend/.env`:

```dotenv
VITE_API_BASE_URL=http://localhost:8080
```

`backend/.env`:

```dotenv
DATABASE_URL=sqlite:///./learnwithme.db
SESSION_SECRET=replace-with-a-long-random-value
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=llama3.2:1b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

The app starts locally using SQLite; use a managed PostgreSQL `DATABASE_URL` for production. Set a unique `SESSION_SECRET` before deploying.

## Ollama and speech

Install Ollama, then run `ollama pull llama3.2:1b`, `ollama pull nomic-embed-text`, and `ollama serve`. Core lessons and games work without it. Read-aloud uses browser SpeechSynthesis as a stable fallback; Piper remains optional and needs its executable configured.

## Vercel + Modal

Deploy `frontend` to Vercel with build command `npm run build`, output directory `dist`, and `VITE_API_BASE_URL` set to the backend HTTPS endpoint. Modal deployment is optional; do not activate it for local use. Modal cannot reach a developer's local Ollama, so optional chat needs a separately configured provider. Use scale-to-zero and expect cold starts. Do not commit `.env` files or enable paid inference without monitoring its budget.

## Current limitations

Browser recognition needs permission and browser support; typing is always available. A transcript does not prove pronunciation. The supplied archive contained compiled frontend output and assets, not original `src` files, so this release recreates the editable React source while preserving the supplied character GLBs.
