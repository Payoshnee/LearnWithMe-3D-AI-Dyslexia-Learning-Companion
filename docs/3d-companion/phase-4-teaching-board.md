# DyslexiaLearn 3D Companion: Phase 4 Teaching Board

## Flow

```text
Learner starts lesson
        ↓
Board opens
        ↓
Companion points
        ↓
Word appears
        ↓
Syllables appear
        ↓
Syllables highlight and speak
        ↓
Full word is spoken
        ↓
Learner is asked to repeat
        ↓
Listening-ready state
```

## Board Architecture

The board is normal accessible HTML rendered outside the Three.js canvas.

- `LearningBoard` chooses the board mode.
- `PronunciationBoard` renders the Phase 4 pronunciation content.
- `SyllableDisplay` renders syllables and the active syllable state.
- `ListeningPlaceholder` shows the non-recording “Your turn” state.
- `usePronunciationDemoSequence` coordinates board state, speech, companion animation, repeat, and cancellation.

Board state remains serializable in the companion reducer: `open`, `mode`, `title`, `word`, `syllables`, `highlightedIndex`, `instruction`, `showRepeat`, `showMicrophonePlaceholder`, and `progressLabel`.

## Demo Data

The fixed Phase 4 lesson lives in `frontend/src/companion/pronunciationDemoData.js`.

- Word: `pronunciation`
- Syllables: `pro · nun · ci · a · tion`
- Introduction: `Let us say this word slowly.`
- Final prompt: `Now try saying the complete word.`

FastAPI is not required for this phase.

## Animation

- Pointing state: `explaining`
- Current pointing clip: `Punch`, via the Phase 2 alias/fallback map
- Talk state: `speaking`
- Current talk clip: `Yes`
- Listening-ready state: `listening`
- Current listening clip: `Idle`

If the pointing clip is missing, the resolver falls back safely and the board sequence continues.

## Motion

The board slides from the right toward the companion panel:

```text
opacity 0 -> 1
x 90 -> 0
scale 0.98 -> 1
```

Reduced-motion mode renders the board immediately with no slide or scale transition.

## Speech

Speech uses the existing browser speech synthesis hook.

Rates:

- Instruction: `0.82`
- Syllable: `0.62`
- Full word: `0.72`

During syllable demonstration, the companion stays in `speaking` for the grouped sequence to avoid Talk -> Idle flicker between short syllables.

## Repeat And Close

Repeat uses replace-current behavior:

1. Cancel any active sequence.
2. Stop active speech.
3. Clear the highlight.
4. Restart the deterministic pronunciation sequence.

Close cancels speech and animation, clears the highlight, hides the listening placeholder, closes the board, and returns the companion to `idle`.

## Listening Ready

After the final prompt:

- Companion state becomes `listening`
- Repeat control is shown
- Microphone placeholder is shown
- No microphone permission is requested

Placeholder text:

```text
Your turn. Microphone practice will be added next.
```

## Accessibility

- Board uses an `aside` labelled by its heading.
- Instruction changes use polite live text.
- Active syllable uses colour, border, underline, font weight, and `aria-current`.
- Repeat and close controls are keyboard accessible.
- Full word and syllables remain visible as text.
- No essential content is only inside Three.js or audio.

## Mobile Layout

On mobile, the board becomes a compact fixed bottom sheet above the companion controls. The 3D companion remains small, and the word/syllables remain readable.

## Failure Behavior

Speech failure is non-fatal. The board remains open and displays:

```text
Audio is unavailable. Read the syllables slowly.
```

Muted mode skips speech synthesis and uses visual timing for syllable highlights.

Tab-hidden cleanup cancels active sequence work, stops speech, clears the highlight, and leaves a repeatable instruction.

## Known Limitations

- `Punch` is a temporary pointing stand-in because the current model does not include a dedicated `PointLeft` clip.
- `Yes` is a temporary talk loop; there is no lip-sync yet.
- Microphone practice is a placeholder only.
- The demo uses fixed data and does not store pronunciation attempts.
