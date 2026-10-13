# DyslexiaLearn 3D Learning Companion: Phase 2 Animation Controller

## Overview

Phase 2 adds a semantic animation-control layer. Pages and lesson code request companion states such as `thinking`, `speaking`, or `encouraging`; only the 3D companion module resolves those states to Three.js `AnimationAction` objects.

```text
Page or lesson event
        ↓
Companion semantic state
        ↓
Animation definition lookup
        ↓
Clip resolution
        ↓
Crossfade controller
        ↓
Three.js AnimationAction
        ↓
Completion or next state
```

## Semantic States

Supported states remain central in `frontend/src/companion/companionConstants.js`:

```text
hidden, loading, entering, greeting, idle, listening, thinking, speaking,
explaining, encouraging, celebrating, error
```

## Mapping

Definitions live in `frontend/src/companion/animationDefinitions.js`.

| Semantic State | Clip | Loop | Speed | Fade In | Fade Out |
| --- | --- | --- | ---: | ---: | ---: |
| `idle` | `Idle` | Yes | 0.9 | 0.3 | 0.25 |
| `entering` | `Walking` | Yes | 0.9 | 0.25 | 0.3 |
| `greeting` | `Wave` | No | 0.9 | 0.25 | 0.25 |
| `listening` | `Idle` | Yes | 0.75 | 0.25 | 0.25 |
| `thinking` | `No` | Yes | 0.65 | 0.3 | 0.25 |
| `speaking` | `Yes` | Yes | 0.9 | 0.2 | 0.2 |
| `explaining` | `Punch` | No | 0.8 | 0.25 | 0.25 |
| `encouraging` | `ThumbsUp` | No | 0.85 | 0.25 | 0.25 |
| `celebrating` | `Dance` | No | 0.75 | 0.2 | 0.3 |

## Alias Resolution

`resolveAnimationClip()` tries:

1. Exact clip match
2. Case-insensitive match
3. Configured aliases
4. Safe partial match
5. `null` when no safe match exists

Aliases live in `frontend/src/companion/animationAliases.js`. Missing optional clips fall back calmly, usually to `idle`.

## Controller

The raw Three.js action ownership lives in `frontend/src/hooks/useCharacterAnimationController.js`.

The controller exposes:

- `playState`
- `playClip`
- `stopCurrent`
- `returnToIdle`
- `playSequence`
- `cancelAnimationSequence`
- `currentState`
- `currentClip`
- `isTransitioning`
- `availableAnimations`

Global companion helpers in `CompanionProvider` expose semantic methods:

- `playAnimationState`
- `playAnimationSequence`
- `cancelAnimationSequence`
- `returnToIdle`

Pages should use these semantic helpers and must not call `actions["ClipName"]` directly.

## Looping and One-Shot Behavior

Looping states use `LoopRepeat` and continue until another semantic state interrupts them.

One-shot states use `LoopOnce` and `clampWhenFinished`. The controller listens to the mixer `finished` event and returns to idle or a configured `returnTo` state.

Stale completion events are ignored using transition IDs and cancelled completion resolvers.

## Queue Behavior

`playSequence()` executes a small list of semantic commands sequentially. It supports state commands and simple delays. `cancelAnimationSequence()` cancels pending sequence work and clears queue metadata.

This is intentionally not a cinematic timeline engine.

## Priorities

Priorities live in `frontend/src/companion/animationPriorities.js`.

`error` has the highest priority. `idle` is lowest and should not unexpectedly interrupt meaningful one-shot gestures. When a sequence is running, a higher-priority semantic state cancels the queued behavior before playing.

## Reduced Motion

Reduced motion maps dramatic states to calmer states:

- `entering`, `greeting`, `thinking`, `speaking`, `explaining` -> `idle`
- `celebrating` -> `encouraging`

Crossfade durations are reduced to zero when reduced motion is active.

## Text-Only, Hidden, Minimized

Text-only mode resolves animation promises immediately and does not invoke Three.js actions.

Hidden/error states stop current animation work. Minimized mode pauses the 3D controller through the `paused` prop so decorative animation does not continue unnecessarily.

The Page Visibility API pauses the active action while the browser tab is hidden and resumes it when visible.

## Debug Tools

When `REACT_APP_COMPANION_DEBUG=true` and the app is not in production, the shell shows a debug panel with:

- Requested state
- Resolved clip
- Current clip
- Loop mode
- Speed
- Transition status
- Queue length
- Buttons for semantic states
- `Run demo`
- `Cancel`

## Root Motion Handling

The character is kept inside a fixed parent transform. Phase 2 does not author or strip root motion. Clips with movement risk are documented in `animation-clips.md`; future entrance work should neutralise root motion before relying on movement-heavy clips.

## Known Limitations

- `speaking` uses the `Yes` clip as a temporary loop; no audio or lip-sync exists yet.
- `explaining` uses `Punch` as a temporary pointing stand-in.
- `thinking` uses `No` as a temporary thoughtful loop.
- Debug sequence timings are simple and development-only.
- FastAPI still returns semantic placeholders and does not control animation timelines in this phase.
