# DyslexiaLearn 3D Companion: Phase 3 Entrance and Greeting

## Flow

```text
Student layout ready
        ↓
Eligibility check
        ↓
Walk entrance
        ↓
Wave
        ↓
Speech bubble
        ↓
Browser speech
        ↓
Talk animation
        ↓
Idle
```

## Character Movement

The default character remains `frontend/public/characters/default-companion.glb`.

- Entrance position: `[1.8, -0.55, 0]`
- Resting position: `[0, -0.55, 0]`
- Rotation: `[0, 0.18, 0]`
- Scale: `0.3`

`CompanionCanvas` wraps `CharacterModel` in an outer root group. The outer group owns entrance position, resting position, rotation, and scale. The inner model still owns skeleton animation through the Phase 2 animation controller.

`useCharacterEntrance` uses `useFrame`, `MathUtils.damp`, and a `0.01` arrival threshold. On arrival, the root snaps to the exact resting position.

## Animation Clips

- Walk: `Walking`
- Wave: `Wave`
- Talk: `Yes`
- Idle: `Idle`

The walk state loops during entrance movement. `Wave` remains a one-shot. `Yes` is a temporary talking loop until a better talk/lip-sync asset exists.

## Root Motion

The RobotExpressive `Walking` clip has root/body motion risk. Phase 3 keeps global screen movement on the outer root group and snaps that root back to the resting position after arrival. A future production walk-in should use an in-place walk clip or strip horizontal root translation.

## Greeting

Default text:

```text
Hi! I'm your learning companion. I'm here to help you learn at your own pace.
```

Speech configuration:

- Language: `en-US`
- Rate: `0.82`
- Pitch: `1`
- Volume: `1`

Optional name personalisation is supported only from an already available display name. The name is trimmed, length-limited, and stripped of unsafe characters.

## Browser Speech

`useCompanionSpeech` uses `window.speechSynthesis` and `SpeechSynthesisUtterance`.

Voice selection priority:

1. Preferred names: `Google US English`, `Microsoft Aria`, `Samantha`
2. Exact requested language
3. Same language family
4. Default browser voice
5. First available voice

Speech requests use monotonically increasing request IDs so stale callbacks cannot change the current companion state.

## Session Behavior

The automatic entrance greeting runs once per browser session using:

```text
dyslexialearn_companion_greeted
```

Route navigation in the Admin layout does not replay the full entrance. Manual replay is available from the speech bubble and replays the wave/speech greeting without the walking entrance.

## Reduced Motion and Text Only

Reduced motion skips walking and large gesture changes, places the character at the resting position, shows the speech bubble, and plays speech when possible.

Text-only mode does not wait for the GLB model. It shows the HTML speech bubble and uses browser speech when available and unmuted.

## Mute and Failure Behavior

Muted mode skips browser speech, keeps the greeting readable, waits briefly, then returns to idle.

If speech is unsupported or fails, the bubble remains visible with:

```text
Audio is unavailable. You can read the message instead.
```

Entrance failure is non-fatal: the character is placed at the resting position and the greeting continues.

Hidden, minimized, and hidden-tab states cancel active speech, cancel entrance movement, and return the companion to idle.

## Known Limitations

- The talk animation uses `Yes`; there is no phoneme-level lip-sync yet.
- The entrance uses damped movement rather than an authored cinematic path.
- Browser autoplay rules may prevent automatic speech until the learner interacts with the page.
- Mobile speech bubble is compact and anchored above the companion controls.
