# DyslexiaLearn 3D Learning Companion: Phase 1 Static Character

## Summary

Phase 1 replaces the Phase 0 visual placeholder with a static 3D character prototype. The companion now uses React Three Fiber to render one GLB model in the authenticated student layout, plays the available idle animation, and falls back safely when WebGL, loading, or runtime failures occur.

```text
CompanionShell
      ↓
WebGL capability check
      ↓
CompanionCanvas
      ↓
CharacterModel
      ↓
GLB asset + Idle animation
```

## Character Asset

- Character: RobotExpressive
- Local model path: `frontend/public/characters/default-companion.glb`
- Static fallback path: `frontend/public/characters/default-companion-fallback.svg`
- Source: Three.js example assets, `examples/models/gltf/RobotExpressive`
- Creator: Tomás Laulhé
- Modifications: Don McCurdy
- Licence: CC0 1.0 Universal
- Production status: legal development asset; may still be replaced by a custom branded character later

Detailed asset metadata is recorded in `docs/3d-companion/assets.md`.

## Model Measurements

- File size: 463,988 bytes, approximately 453 KB
- Triangles: 3,237
- Meshes: 14
- Materials: 3
- Textures: 0
- Skins: 2
- Animation clips: 14
- Animation clip names: `Dance`, `Death`, `Idle`, `Jump`, `No`, `Punch`, `Running`, `Sitting`, `Standing`, `ThumbsUp`, `Walking`, `WalkJump`, `Wave`, `Yes`

## Idle Animation

The model contains a named `Idle` clip. Phase 1 plays `Idle` continuously. Phase 2 can map additional semantic states to clips such as `Wave`, `Walking`, `ThumbsUp`, `Yes`, and `No`.

## Camera and Lighting

Configuration lives in `frontend/src/config/companionConfig.js`.

Camera:

```text
position: [0, 1.15, 4.8]
fov: 32
```

Character:

```text
scale: 0.3
position: [0, -0.55, 0]
rotation: [0, 0.18, 0]
```

Lighting:

```text
ambientLight intensity: 1.25
directionalLight position: [3, 5, 4]
directionalLight intensity: 1.65
Environment preset: none
```

The canvas uses a transparent background, antialiasing, alpha rendering, and controlled DPR `[1, 1.5]`.

## Responsive Behavior

- Desktop: fixed companion shell on the lower-right side of the learning area with a stable canvas height.
- Tablet: reduced shell width and canvas height at widths up to `1024px`.
- Mobile: compact shell at the bottom-right, with message panel and board hidden to avoid covering lesson content.

## Accessibility and Fallbacks

- Text-only mode does not render the 3D canvas and does not initialise WebGL.
- WebGL unavailable devices show a static accessible fallback.
- Model loading timeout shows retry and continue-without-3D actions.
- Runtime/model errors set companion status to `error` and show a calm fallback.
- Canvas is decorative; essential companion status/message remains regular HTML text.
- Controls remain keyboard-accessible and labelled.

## Reduced Motion

When reduced motion is enabled, the 3D model renders as a static pose and the idle animation is not played. Placeholder transitions are already simplified by the Phase 0 reduced-motion path.

## Debug Utility

Set:

```text
REACT_APP_COMPANION_DEBUG=true
```

When enabled, the model loader logs development-only inspection details such as animation clip names, mesh names, material names, morph target names, and model bounds. These details are not shown to students.

## Verification Notes

- Unit tests mock React Three Fiber and do not require real WebGL.
- Production build succeeds with React 18-compatible React Three Fiber/Drei versions.
- Browser verification should be repeated when the final branded model replaces this temporary asset.

## Known Limitations

- The current development model is branded and temporary.
- The only animation clip is unnamed.
- No walk-in, greeting, speech, lip-sync, pointing, AI gesture, or lesson-aware behavior is implemented.
- Route download persistence should be verified in browser network tools during manual QA; the companion is mounted in the persistent `/admin/*` layout.

## Phase 2 Requirements

- Replace the temporary character or re-export with named animation clips.
- Add a controlled animation state adapter that maps companion semantic states to animation names.
- Keep Three.js objects out of global companion state.
- Continue returning semantic backend instructions only.
