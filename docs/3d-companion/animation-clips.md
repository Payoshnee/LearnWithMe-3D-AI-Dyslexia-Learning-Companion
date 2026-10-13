# 3D Companion Animation Clips

Current model: `frontend/public/characters/default-companion.glb`

Source asset: RobotExpressive from Three.js examples.

## Clip Inventory

| Clip | Duration | Tracks | Loop Naturally | Root Movement | Neutral Return | Body Scope | Facial Animation |
| --- | ---: | ---: | --- | --- | --- | --- | --- |
| `Dance` | 3.333s | 12 | Yes, energetic | Some body translation | No, celebratory pose/motion | Full body | Morph/weights tracks present |
| `Death` | 0.958s | 18 | No | Some body translation | No | Full body | Morph/weights tracks present |
| `Idle` | 3.333s | 7 | Yes | Minimal | Yes | Full body/subtle | Morph/weights tracks present |
| `Jump` | 0.708s | 18 | No | Vertical/body translation | Mostly | Full body | Morph/weights tracks present |
| `No` | 1.667s | 7 | Yes if looped gently | Minimal | Mostly | Head/upper body | Morph/weights tracks present |
| `Punch` | 0.833s | 15 | No | Minimal | Mostly | Full/upper body | Morph/weights tracks present |
| `Running` | 0.958s | 18 | Yes | Root/body motion risk | No | Full body | Morph/weights tracks present |
| `Sitting` | 0.417s | 10 | No | Pose transition | No | Full body | Morph/weights tracks present |
| `Standing` | 0.417s | 10 | No | Pose transition | Yes | Full body | Morph/weights tracks present |
| `ThumbsUp` | 1.583s | 15 | No | Minimal | Mostly | Full/upper body | Morph/weights tracks present |
| `Walking` | 0.958s | 20 | Yes | Root/body motion risk | No | Full body | Morph/weights tracks present |
| `WalkJump` | 0.833s | 18 | No | Root/body motion risk | No | Full body | Morph/weights tracks present |
| `Wave` | 1.833s | 18 | No | Minimal | Mostly | Full/upper body | Morph/weights tracks present |
| `Yes` | 1.667s | 7 | Yes if looped gently | Minimal | Mostly | Head/upper body | Morph/weights tracks present |

## Phase 2 Usage

Looping states:

- `idle` -> `Idle`
- `listening` -> `Idle`
- `thinking` -> `No`
- `speaking` -> `Yes`

One-shot states:

- `entering` -> `Walking` looped during outer-root entrance movement
- `greeting` -> `Wave`
- `explaining` -> `Punch`
- `encouraging` -> `ThumbsUp`
- `celebrating` -> `Dance`

## Root Motion Note

`Walking`, `Running`, and `WalkJump` may contain root/body translation risk. Phase 3 keeps screen movement on the outer character root and snaps the character back to the configured resting position after arrival. A later production entrance should neutralise root motion or author a dedicated in-place walk clip.
