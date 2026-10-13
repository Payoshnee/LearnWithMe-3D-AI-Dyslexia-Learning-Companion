# 3D Companion Assets

## default-companion.glb

- Asset filename: `frontend/public/characters/default-companion.glb`
- Fallback filename: `frontend/public/characters/default-companion-fallback.svg`
- Source model: RobotExpressive from the Three.js example assets
- Source URL: https://github.com/mrdoob/three.js/tree/dev/examples/models/gltf/RobotExpressive
- Download URL: https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/models/gltf/RobotExpressive/RobotExpressive.glb
- Creator: Tomás Laulhé
- Modifications: Don McCurdy
- Licence: CC0 1.0 Universal, as documented by the source model README
- Attribution required: no legal attribution required by CC0, but source credit is retained in documentation
- Original download date: 2026-07-26
- Modifications made: renamed locally to `default-companion.glb`; no mesh, texture, rig, or animation edits
- Phase status: temporary development asset for validating the 3D companion pipeline

## Measured Phase 1 Stats

- File size: 463,988 bytes, approximately 453 KB
- Mesh count: 14
- Primitive count: 19
- Triangle count: 3,237
- Material count: 3
- Texture count: 0
- Image count: 0
- Skin count: 2
- Animation clip count: 14
- Animation clip names: `Dance`, `Death`, `Idle`, `Jump`, `No`, `Punch`, `Running`, `Sitting`, `Standing`, `ThumbsUp`, `Walking`, `WalkJump`, `Wave`, `Yes`
- Mesh names: `Foot.L`, `Torso`, `Head`, `Foot.R`, `Shoulder.L`, `Arm.L`, `Shoulder.R`, `Arm.R`, `Leg.L`, `LowerLeg.L`, `Leg.R`, `LowerLeg.R`, `Hand.R`, `Hand.L`
- Material names: `Grey`, `Main`, `Black`

## Replacement Requirement

This model is acceptable for Phase 1 because it is small, rigged, skinned, animated, robot-like, and legally documented. It is not necessarily the final DyslexiaLearn companion identity. A later design-focused asset phase may replace it with a custom branded character while preserving the same loader/config architecture.
