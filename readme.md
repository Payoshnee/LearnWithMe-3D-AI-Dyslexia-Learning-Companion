# DyslexiaLearn 3D AI Doodle Companion

Voice-first dyslexia learning companion with a 3D animated doodle, Chrome speech recognition, shared Ollama/RAG reasoning, dynamic teaching boards, pronunciation scoring, voice quizzes, stats memory, and backend-generated speech.

The current MVP uses Chrome's native Web Speech API for speech recognition. The recognized text is sent to FastAPI and the shared DyBrain Ollama service, then the doodle speaks the answer using Piper TTS.

![Robot fallback visual](frontend/src/assets/doodles/robot-fallback.svg)

## Interview Summary

DyslexiaLearn is a multimodal AI tutoring system for children with dyslexia. The project moved from a regular dashboard-style learning app to a voice-first 3D companion experience:

- A child selects a 3D doodle.
- The doodle enters, greets the learner, listens, thinks, speaks, and points.
- The child can ask for pronunciation help, quizzes, stats, or general learning help.
- The backend controls the lesson state instead of letting the frontend hardcode lessons.
- The system stores learner memory and uses RAG-ready context for personalized future responses.

Resume line:

> Built a voice-first multimodal dyslexia tutor using React, Three.js, Chrome SpeechRecognition, FastAPI, a shared Ollama model, Piper TTS, RAG memory, dynamic teaching boards, and animated 3D companion state control.

## MVP Status

| Area | Status | Notes |
|---|---:|---|
| New React/Vite frontend | Done | Old dashboard frontend was replaced with a voice-first app. |
| FastAPI backend | Done | Backend handles auth legacy routes plus companion APIs. |
| 3D doodle selection | Done | Nova, Luna, Bob, Leo. |
| 3D stage | Done | Full-page stage with animated state changes. |
| Chrome speech recognition | Done | Chrome converts microphone speech to text using its native Web Speech API. |
| Backend TTS | Done | Piper TTS generates WAV audio. |
| LLM/RAG | MVP | Ollama response generation and RAG-ready memory are wired. |
| Dynamic pronunciation board | Done | Board generated from backend intent and target word. |
| Pronunciation attempt loop | Done | Starts at first syllable, retries low scores, advances on pass, stops on command. |
| Quiz board | Done | Four options; accepts option number, letter, or full option text. |
| Stats board | Done | Shows quiz accuracy and next practice from learner memory. |
| Text fallback | Done | Learners can type when Chrome speech recognition is unavailable. |

## Visual Experience

### Main Pages

| Page | Purpose |
|---|---|
| Home | Intro page with background video and Get Started flow. |
| Login/Register | Basic learner access flow with Google sign-in UI placeholder. |
| Doodle selection | Pick one of four 3D companions and preview voice. |
| Stage | Main learning page. Doodle listens, speaks, points, and shows dynamic boards. |

### Visual Assets

| Asset | Path | Purpose |
|---|---|---|
| Background video | `frontend/public/videos/robot-friendship-background.mp4` | Used on non-stage pages. |
| Nova model | `frontend/src/assets/doodles/robot.glb` | Existing project robot companion. |
| Luna model | `frontend/src/assets/doodles/luna.glb` | Female 3D companion. |
| Bob model | `frontend/src/assets/doodles/mira.glb` | Male cube-style quiz coach; source file name preserved. |
| Leo model | `frontend/src/assets/doodles/leo.glb` | Male practice buddy. |
| Robot fallback SVG | `frontend/src/assets/doodles/robot-fallback.svg` | Fallback visual if GLB cannot render. |
| Favicon | `frontend/public/favicon.svg` | App icon. |

### Doodle Catalog

| Doodle | Model | Voice | Role | Source |
|---|---|---|---|---|
| Nova | `robot.glb` | `en_US-lessac-medium.onnx` | Logical pronunciation helper | Existing project robot |
| Luna | `luna.glb` | `en_US-amy-medium.onnx` | Calm reading guide | Animated Woman 3D Model |
| Bob | `mira.glb` | `en_US-ryan-medium.onnx` | Playful quiz coach | Cube Guy Character by Quaternius |
| Leo | `leo.glb` | `en_GB-alan-medium.onnx` | Friendly practice buddy | Shaun 3D Model by Quaternius |

## Architecture

```mermaid
flowchart LR
  Child[Child Learner] --> Browser[React + Three.js Frontend]
  Browser --> ChromeSTT[Chrome SpeechRecognition]
  ChromeSTT --> Turn[FastAPI /companion/voice-turn]
  Turn --> Intent[Intent Router]
  Turn --> RAG[RAG + Learner Memory]
  Turn --> Ollama[Shared DyBrain Ollama model]
  Intent --> Board[Dynamic Teaching Board]
  Intent --> Actions[Doodle State Sequence]
  Turn --> TTS[FastAPI /companion/speech]
  TTS --> Piper[Piper TTS WAV]
  Piper --> Browser
  Board --> Browser
  Actions --> Browser
  Browser --> Doodle[Animated 3D Doodle]
```

## Data Pipeline

### Full Voice Turn

```mermaid
sequenceDiagram
  participant U as Learner
  participant F as Frontend
  participant B as FastAPI
  participant C as Chrome SpeechRecognition
  participant R as Intent/RAG
  participant L as Ollama
  participant P as Piper

  U->>F: Click Speak to Doodle
  F->>F: Stop any active doodle audio
  F->>C: Start native speech recognition
  C-->>F: transcript
  F->>B: POST /api/v1/companion/voice-turn
  B->>R: Detect intent + read board context
  alt Controlled flow
    R-->>B: pronunciation/quiz/stats result
  else Open question
    R->>L: Prompt with learner + context
    L-->>R: response
  end
  B-->>F: responseText + teachingBoard + stateSequence
  F->>B: POST /api/v1/companion/speech
  B->>P: Generate WAV audio
  P-->>B: speech.wav
  B-->>F: audio blob
  F->>F: Play one controlled audio stream
  F->>U: Doodle speaks and animates
```

## Backend API

Base URL locally:

```text
http://localhost:8080
```

Important companion endpoints:

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/v1/companion/preferences` | GET/PUT | Companion settings. |
| `/api/v1/companion/sessions` | POST | Start companion session. |
| `/api/v1/companion/voice-turn` | POST JSON | Main brain: intent, board, memory, response, actions. |
| `/api/v1/companion/speech` | POST JSON | Convert response text to WAV audio using Piper. |

Example voice-turn request:

```json
{
  "transcript": "Help me pronounce elephant",
  "learnerName": "Himanshu",
  "learnerAge": 8,
  "doodleId": "nova",
  "doodleName": "Nova",
  "language": "auto",
  "context": {
    "currentBoard": null,
    "boardOpen": false,
    "companionState": "idle"
  }
}
```

Example pronunciation response:

```json
{
  "intent": "pronunciation_help",
  "responseText": "Himanshu, let us practice elephant. Break it into: el, e, phant. Now repeat just el slowly.",
  "stateSequence": ["processing", "speaking", "pointing", "listening"],
  "teachingBoard": {
    "type": "syllables",
    "word": "elephant",
    "syllables": ["el", "e", "phant"],
    "focusSyllable": "el",
    "focusIndex": 0,
    "prompt": "Repeat just el slowly."
  }
}
```

## Learning Flows

### Pronunciation Help

User says:

```text
Help me pronounce elephant.
```

Backend:

1. Detects `pronunciation_help`.
2. Extracts target word: `elephant`.
3. Generates syllables:
   - known dictionary first
   - heuristic fallback for unknown words
4. Creates board.
5. Starts at first syllable.

Flow:

```mermaid
stateDiagram-v2
  [*] --> StartWord
  StartWord --> Syllable0: focus first syllable
  Syllable0 --> Syllable0: score below pass threshold
  Syllable0 --> Syllable1: pass
  Syllable1 --> Syllable1: score below pass threshold
  Syllable1 --> Syllable2: pass
  Syllable2 --> Complete: final pass
  Syllable0 --> Stopped: child says stop
  Syllable1 --> Stopped: child says cancel/done/quit
  Syllable2 --> Stopped: child says new command
  Complete --> [*]: board closes
  Stopped --> [*]: board closes
```

Current scoring:

- Uses backend transcript similarity.
- Scores current focus syllable first.
- Below pass threshold means retry the same syllable.
- Passing moves to the next syllable.
- Finishing the last syllable closes the board.

This is MVP scoring. Future improvement is audio-level phoneme scoring.

### Quiz Flow

User says:

```text
Quiz me.
```

Board shows four options:

```text
A. Say it faster
B. Break it into syllables
C. Skip the tricky sound
D. Guess and move on
```

The child can answer:

- `option B`
- `B`
- `number two`
- `option two`
- `break it into syllables`

Backend parses the answer and returns:

```text
I heard option B: Break it into syllables. Correct.
```

### Stats Flow

User says:

```text
How am I doing?
```

Backend reads learner memory and returns:

- quiz accuracy
- tricky words
- next practice suggestion

## Why Not Let the LLM Do Everything?

Early testing showed open LLM responses can make child-facing mistakes, such as:

- confusing the doodle name with learner name
- praising an action the child had not done yet
- restarting pronunciation instead of checking the attempt
- generating inconsistent board state

Solution:

```mermaid
flowchart TD
  Input[Transcript] --> Intent[Backend Intent Router]
  Intent --> Controlled{Controlled Learning Flow?}
  Controlled -->|Pronunciation| Template[Safe backend template + scorer]
  Controlled -->|Quiz| QuizParser[Backend option parser]
  Controlled -->|Stats| StatsCalc[Backend memory calculation]
  Controlled -->|General question| LLM[Ollama LLM + RAG]
  Template --> Response[Validated response]
  QuizParser --> Response
  StatsCalc --> Response
  LLM --> Response
```

Rule:

> Use the LLM where intelligence is needed, not where control and safety are needed.

## Local AI Stack

Shared model profile:

```env
OLLAMA_CHAT_MODEL=qwen2.5vl:3b
TTS_ENGINE=piper
```

Speech-to-text does not consume server resources because Chrome performs it in the browser.

Recommended local models:

| Purpose | Model/Tool | Why |
|---|---|---|
| STT | Chrome Web Speech API | No Whisper model or transcription server is required. |
| LLM + vision | `qwen2.5vl:3b` | One compact model supports all three projects, including Closira images. |
| Embeddings | `nomic-embed-text` | Local embedding model for RAG. |
| TTS | Piper | Cross-platform local speech generation. |

Pull Ollama models:

```bash
ollama pull qwen2.5vl:3b
ollama pull nomic-embed-text
```

Optional cleanup:

```bash
ollama list
ollama rm <unused-model-name>
```

Keep at least:

- `qwen2.5:7b-instruct`
- `nomic-embed-text`

## Setup

### Prerequisites

- Node.js 18+
- Python 3.9+
- PostgreSQL or local database configured by backend settings
- Ollama running locally
- Modern browser with microphone recording support

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Download Piper voices:

```bash
cd ..
backend/scripts/download_piper_voices.sh backend/tts/voices
```

Run backend:

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8080
```

### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

Frontend local URL is usually:

```text
http://localhost:5173
```

## Environment Variables

Backend example:

```env
DATABASE_URL=postgresql+psycopg://admin:password123@localhost:5432/dyslexialearn
FRONTEND_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174
COMPANION_ENABLED=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_API_KEY=
OLLAMA_CHAT_MODEL=qwen2.5vl:3b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text:latest
RAG_TOP_K=4
TTS_ENGINE=piper
PIPER_BINARY_PATH=piper
PIPER_VOICE_DIR=tts/voices
```

Frontend example:

```env
VITE_API_BASE_URL=http://localhost:8080
```

## Performance Improvements

The MVP moved through several audio/AI designs.

```mermaid
xychart-beta
  title "Expected Local Voice Turn Latency Improvement"
  x-axis ["Chrome STT", "Shared model call", "Controlled intent fast-path"]
  y-axis "Approx. response delay seconds" 0 --> 8
  bar [1.0, 3.5, 2.0]
```

What improved:

| Problem | Fix |
|---|---|
| Whisper required extra server memory | Switched to Chrome-native SpeechRecognition with typed fallback. |
| macOS-only audio | Replaced `say` with Piper TTS. |
| Silent audio | Installed Piper, downloaded voices, fixed voice directory. |
| Doodle talked over new audio | Added one global audio controller and stop-on-new-speech. |
| Mic started while doodle spoke | Mic click now stops active doodle audio first. |
| LLM confused learner/doodle names | Backend templates + stricter prompt rules. |
| Pronunciation restarted after attempts | Added active board context and attempt detection. |
| Pronunciation skipped to wrong syllable | Added `focusIndex`/`focusSyllable` loop. |
| Quiz accepted only fixed words | Added number/letter/full-option parser. |

### Current Bottleneck

Current STT is still not true streaming:

```text
record short audio -> upload blob -> Whisper transcribes -> backend responds
```

True real-time would use:

```text
audio chunks -> WebSocket -> streaming STT -> partial transcript -> early intent
```

This is a future improvement, not required for the MVP.

## Testing

Backend:

```bash
cd backend
source venv/bin/activate
pytest
```

Current backend suite covers:

- companion defaults
- session response schema
- voice-turn pronunciation request
- learner-name correctness
- pronunciation attempt scoring
- pronunciation loop retry/advance/stop
- speech endpoint
- stats board
- transcription endpoint
- quiz prompt and answer parsing

Frontend:

```bash
cd frontend
pnpm build
```

Latest verification:

```text
Backend tests: 13 passed
Frontend build: passed
```

## Problems Faced And Solutions

### 1. 3D models not visible or badly scaled

Problem:

- GLB paths returned 404.
- Models had different raw units.
- Luna, Bob, and Leo were too small or too large.

Solution:

- Moved models into `frontend/src/assets/doodles`.
- Imported GLBs through Vite.
- Added per-doodle scale, camera, position, and shadow settings.

### 2. Browser speech was unreliable

Problem:

- Arc/Chrome extension behavior caused speech recognition or speech synthesis issues.
- Browser voices loaded inconsistently.

Solution:

- Replaced browser speech recognition with backend STT.
- Replaced browser speech synthesis with backend Piper TTS.

### 3. LLM hallucinated child-facing feedback

Problem:

- LLM said “Hey Nova” because it confused doodle name with learner name.
- LLM praised the child before the child had spoken.

Solution:

- Backend now owns controlled learning flows.
- LLM is used for open-ended help, not for deterministic pronunciation/quiz/state transitions.

### 4. Pronunciation practice did not behave like a lesson

Problem:

- Board was static.
- Attempts restarted the lesson.
- Weak attempts advanced to the wrong syllable.
- Board stayed open after completion.

Solution:

- Added `focusIndex`, `focusSyllable`, score, pass/fail, weak syllable.
- Added stop commands.
- Added board close on completion.

### 5. Quiz answer handling was too narrow

Problem:

- The child might say “B”, “option B”, “number two”, or the full answer.

Solution:

- Added robust quiz parsing with number, letter, and fuzzy full-text matching.
- Board highlights selected answer.

## File Map

```text
backend/
  app/api/v1/companion.py          # Companion API routes
  app/services/companion_service.py# Main voice-turn orchestration
  app/services/rag_service.py      # Intent, scoring, quiz parsing, RAG helpers
  app/services/tts_service.py      # Piper speech synthesis
  app/services/local_ai_service.py # Ollama chat/embedding calls
  app/schemas/companion.py         # API schemas
  scripts/download_piper_voices.sh # Voice model downloader
  tests/test_companion.py          # Companion behavior tests

frontend/
  src/pages/CompanionStagePage.jsx       # Main voice-first stage
  src/pages/DoodleSelectPage.jsx         # Doodle carousel/selection
  src/components/companion/DoodleCanvas.jsx
  src/components/companion/DoodleModel.jsx
  src/components/companion/TeachingBoard.jsx
  src/components/companion/VoiceButton.jsx
  src/hooks/useSpeechRecognition.js      # Chrome-native Web Speech API
  src/utils/doodleVoice.js               # Single audio controller + backend TTS
  src/companion/doodleCatalog.js         # Doodle model/voice/camera config
```

## Interview Talking Points

1. **Why voice-first?**  
   Dyslexia support benefits from auditory, step-by-step interaction instead of dense text dashboards.

2. **Why a 3D doodle?**  
   The companion gives visible state feedback: hearing, thinking, speaking, pointing, idle.

3. **Why controlled backend flows?**  
   Child-facing education needs predictable safety. LLMs can help, but deterministic state handling prevents hallucinated lesson behavior.

4. **Why local AI?**  
   Privacy, offline capability, and strong full-stack AI engineering story.

5. **What is novel?**  
   A voice memory RAG tutor that remembers practiced words, checks attempts, adapts syllable practice, and controls a 3D animated companion.

## Next Improvements

- WebSocket streaming STT for lower-latency partial transcription.
- Audio-level phoneme scoring using forced alignment or wav2vec/phoneme models.
- Parent insight dashboard.
- More lesson types: spelling, reading fluency, story comprehension.
- Better multilingual Hindi/English support.
- Deployment profile with lighter hosted models.
- End-to-end Playwright tests for the stage and board behavior.

## License And Asset Notes

This repository includes downloaded 3D assets under `frontend/src/assets/downloaded assets` and copied runtime GLBs under `frontend/src/assets/doodles`. Before public release or commercial use, verify the license for each downloaded model source.

Piper voices are downloaded from the public Piper voice repository through `backend/scripts/download_piper_voices.sh`. Voice model files are large and may be excluded from version control depending on repository policy.
