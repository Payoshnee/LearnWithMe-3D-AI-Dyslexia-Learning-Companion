# Production deployment

## Service layout

- Vercel: React/Vite frontend from `frontend/`.
- Render: FastAPI application from `backend/` using `render.yaml`.
- PostgreSQL: any reachable managed PostgreSQL database.
- Hugging Face: the standalone `dybrain-huggingface/` Docker Space containing Ollama and `qwen2.5vl:3b`.

The browser must never receive the DyBrain API token or database URL.

## 1. Hugging Face DyBrain

The Space URL is `https://payoshneejoshi-dyslexialearn.hf.space`.

Set one Space secret:

```text
DYBRAIN_API_KEYS=DYSLEXIA_TOKEN,CLOSIRA_TOKEN,AROGYA_TOKEN
```

Use newly generated values and never commit them.

## 2. FastAPI backend on Render

Create a Render Blueprint from this GitHub repository. Render reads `render.yaml` and deploys the `backend/` Dockerfile.

Supply these secret values when Render asks:

```text
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
OLLAMA_API_KEY=DYSLEXIA_TOKEN
```

`OLLAMA_API_KEY` must exactly match the DyslexiaLearn token included in the Hugging Face `DYBRAIN_API_KEYS` secret.

After deployment, verify:

```text
https://YOUR-RENDER-SERVICE.onrender.com/health
https://YOUR-RENDER-SERVICE.onrender.com/api/v1/companion/system
```

## 3. Frontend on Vercel

Configure the Vercel project with:

- Root Directory: `frontend`
- Framework Preset: Vite
- Build Command: `pnpm build`
- Output Directory: `dist`

Add this Vercel environment variable for Production, Preview, and Development:

```text
VITE_API_BASE_URL=https://YOUR-RENDER-SERVICE.onrender.com
```

Redeploy Vercel after changing the environment variable. Vite embeds `VITE_*` values at build time.

## Request path

```text
Chrome SpeechRecognition
  -> Vercel React frontend
  -> Render FastAPI backend
  -> Hugging Face DyBrain Ollama service
  -> Render FastAPI response/TTS
  -> Vercel frontend
```

Chrome speech recognition requires HTTPS and microphone permission. Both Vercel and Hugging Face provide HTTPS.
