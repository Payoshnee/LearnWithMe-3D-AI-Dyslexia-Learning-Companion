# DyslexiaLearn 3D Learning Companion: Phase 0 Foundation

## Architecture Overview

Phase 0 prepares DyslexiaLearn for a persistent 3D learning companion without implementing the final character, 3D canvas, animation system, lip-sync, speech analysis, or AI gesture logic.

The current project uses:

- React with Create React App
- JavaScript components
- React Router v6
- React Context and `useReducer` for companion state
- Framer Motion for lightweight placeholder transitions
- FastAPI backend
- PostgreSQL through SQLAlchemy for existing backend data

## Frontend State Ownership

The frontend owns visual companion behavior:

- Rendering and future Three.js canvas lifecycle
- Animation playback and transitions
- Speech bubble text
- Companion visibility, minimise, restore, mute, and text-only controls
- Reduced-motion behavior
- Learning-board display and highlighted item state

Global companion state is serialisable and lives in `frontend/src/companion`. Future Three.js objects, animation mixers, audio nodes, browser speech objects, and model refs must stay inside dedicated rendering or speech controllers, not inside reducer state.

## Backend Responsibility

FastAPI returns semantic companion instructions only. It must not return mesh names, animation frames, rotations, scene objects, or renderer commands.

Example semantic response:

```json
{
  "message": "Your learning companion is ready.",
  "character": {
    "state": "idle",
    "animation": "Idle",
    "emotion": "friendly"
  },
  "board": {
    "visible": false,
    "mode": "none",
    "title": null,
    "content": null,
    "highlighted_index": -1
  },
  "next_action": "wait"
}
```

## Folder Structure

Frontend foundation:

```text
frontend/src/components/companion/
frontend/src/companion/
frontend/src/hooks/
frontend/src/services/
frontend/src/config/
```

Backend foundation:

```text
backend/app/api/v1/companion.py
backend/app/api/v1/router.py
backend/app/schemas/companion.py
backend/app/services/companion_service.py
```

## Companion State Definitions

Allowed statuses:

```text
hidden, loading, entering, greeting, idle, listening, thinking, speaking,
explaining, encouraging, celebrating, error
```

Allowed emotions:

```text
neutral, friendly, happy, encouraging, curious, concerned
```

Allowed board modes:

```text
none, pronunciation, reading, topic, quiz_hint, vocabulary, step_by_step
```

## API Endpoints

Phase 0 adds:

```text
GET  /api/v1/companion/preferences
PUT  /api/v1/companion/preferences
POST /api/v1/companion/sessions
POST /api/v1/companion/sessions/end
POST /api/v1/companion/respond
```

Preferences use in-memory placeholder storage in Phase 0. This is intentional because the current app does not yet have durable user preferences. A future phase should persist preferences by student/user once authenticated user identity is formalized across the FastAPI backend.

## Environment Variables

Frontend:

```text
REACT_APP_COMPANION_ENABLED=true
REACT_APP_COMPANION_DEFAULT_CHARACTER=default
```

Backend:

```text
COMPANION_ENABLED=true
COMPANION_DEFAULT_CHARACTER=default
```

## Feature Flag Behavior

When `REACT_APP_COMPANION_ENABLED` is not `true`:

- The companion shell does not render
- Placeholder board does not render
- Companion API service returns without calling backend endpoints
- Future 3D dependencies should not be imported by the shell

When `COMPANION_ENABLED` is false:

- FastAPI companion endpoints return `404`

## Data Flow

```text
Student interaction
        ↓
React companion controller
        ↓
Frontend API service
        ↓
FastAPI companion endpoint
        ↓
Semantic response
        ↓
React updates character and board state
```

## Future Integration Notes

Phase 1 should start by replacing `CompanionPlaceholder` with a rendering adapter that mounts a lightweight Three.js scene behind the same `CompanionShell` boundary. Keep model loading, animation mixers, refs, and browser APIs local to rendering/speech modules.

Future lesson-aware behavior should use `companionApi.respond(payload)` and convert backend semantic instructions into reducer actions. Visual components should never call `fetch()` directly.

## Not Included In Phase 0

Phase 0 intentionally does not include:

- Final GLB model
- Blender work
- Real animations
- Walk-in or wave sequences
- Lip-sync
- Facial morph targets
- Speech recognition
- Pronunciation scoring
- AI-generated gestures
- WebSockets
- Advanced character selection
- Full learning-board modes
- Topic diagrams
- Reading highlighting
- Production voice generation
