# LearnWithMe updated setup and validation

## Local setup (no paid services)

Prerequisites: Node.js 20+, Python 3.11+, and a modern Chromium browser. Ollama and Piper are optional. Browser speech synthesis is the fallback when Piper is unavailable. Microphone recognition depends on browser Web Speech support and user permission.

### Backend

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
```

The default local SQLite configuration needs no cloud account. Do not add paid provider credentials. Optional local Ollama and Piper setup remains in `MERGED_SETUP.md`; `backend/MODAL_DEPLOYMENT.md` is optional and Modal was not activated.

### Frontend

In a second PowerShell window:

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Open `http://localhost:5173`. Keep `VITE_API_BASE_URL=http://localhost:8080`. Register or sign in, then use **Start Learning** or **Start Practice** once to enable automatic audio. Browser autoplay policy requires this learner gesture.

## Validation run on 13 October 2026

- `npm run test`: 7/7 game, phonics normalization, voice selection, and browser TTS fallback tests passed.
- `npm run build`: production Vite build passed (2,206 modules). Vite reported only its advisory large-chunk warning.
- `py -m pytest -q`: 18/18 backend tests passed after the final integration test was added. Existing FastAPI/Pydantic deprecation warnings remain non-fatal.
- Authenticated integration covers registration, HttpOnly session validation, IPA-normalized lesson answers, progress PUT/GET persistence, logout, and post-logout 401.
- Browser interaction pass: login and protected dashboard passed; Start Learning enabled automatic audio; CAT advanced from step 1 to step 2; word building accepted MAT and advanced to SAT; letter catch accepted M and moved to S; memory-card reveal rendered; game tabs and level selection rendered.
- Recorded phoneme files were present and exercised from the UI. `/k/` maps to the hard-C recording and is never sent to spelling-based TTS as an isolated phoneme.
- Wendy and Bob production assets remained in the build: Wendy 519.34 KB and Bob/Mira 342.32 KB.

## Checks that could not be fully automated

- Real acoustic microphone capture and echo rejection require physical microphone input. The browser control environment cannot supply a human voice. The no-result timeout/fallback path was exercised; successful live transcription needs checking on the target device.
- Subjective pronunciation quality needs listening review by a qualified phonics educator. File mapping and playback were validated, not clinical or pedagogical accuracy.
- Touch hardware was unavailable. Pointer/touch handlers share the same implementation; desktop click, keyboard, validation logic, and responsive build were checked.
- No deployment, Modal activation, or paid service was run.

## Manual acceptance checklist

1. Select Start Learning and confirm the prompt plays once.
2. While audio plays, confirm Tap to talk is disabled; afterward allow microphone access and speak “C”.
3. Confirm the displayed `/k/` button plays the recorded hard-C phoneme, not the spoken letter name.
4. Complete one round of each game with mouse, keyboard, and touch where available.
5. Refresh after completing a lesson or game and confirm Progress retains the result.
6. Enable Reduced motion in Settings and confirm decorative motion stops.
