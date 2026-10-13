
import { useEffect, useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { useAnimations, useGLTF } from "@react-three/drei";
import { clone } from "three/examples/jsm/utils/SkeletonUtils.js";
import * as THREE from "three";

import {
  animationMap,
  COMPANION_STATES,
} from "../../companion/companionStates.js";

function resolveClip(names, state) {
  const aliases =
    animationMap[state] || animationMap[COMPANION_STATES.IDLE];

  return (
    aliases.find((alias) => names.includes(alias)) ||
    aliases
      .map((alias) =>
        names.find((name) =>
          name.toLowerCase().endsWith(`|${alias.toLowerCase()}`)
        )
      )
      .find(Boolean) ||
    aliases
      .map((alias) =>
        names.find((name) =>
          name.toLowerCase().includes(alias.toLowerCase())
        )
      )
      .find(Boolean) ||
    names[0]
  );
}

export default function DoodleModel({ doodle, state }) {
  const groupRef = useRef(null);
  const activeActionRef = useRef(null);

  // Load the character's 3D model.
  const { scene, animations } = useGLTF(doodle.modelPath);

  // Clone so multiple instances can animate independently.
  const copiedScene = useMemo(() => clone(scene), [scene]);

  // Load animations for the cloned character.
  const { actions, names } = useAnimations(
    animations,
    groupRef
  );

  // Smooth character movements.
  useFrame(({ clock }) => {
    if (!groupRef.current) return;

    const time = clock.getElapsedTime();

    const targetY =
      state === COMPANION_STATES.HEARING ? -0.36 : 0.16;

    const targetX =
      state === COMPANION_STATES.PROCESSING
        ? Math.sin(time * 2.6) * 0.04
        : 0;

    const targetZ =
      state === COMPANION_STATES.LISTENING
        ? Math.sin(time * 3.2) * 0.025
        : 0;

    groupRef.current.rotation.y +=
      (targetY - groupRef.current.rotation.y) * 0.08;

    groupRef.current.rotation.x +=
      (targetX - groupRef.current.rotation.x) * 0.08;

    groupRef.current.rotation.z +=
      (targetZ - groupRef.current.rotation.z) * 0.08;
  });

  // Play the correct animation for the current state.
  useEffect(() => {
    if (!actions || names.length === 0) return;

    const clip = resolveClip(names, state);
    const action = actions[clip];

    if (!action) {
      console.warn(
        `Animation not found for ${doodle.name}:`,
        state
      );
      return;
    }

    console.log(
      `${doodle.name} playing animation:`,
      clip
    );

    const previousAction = activeActionRef.current;

    // Stop a different animation before starting this one.
    if (previousAction && previousAction !== action) {
      previousAction.fadeOut(0.2);
    }

    action.reset();
    action.enabled = true;
    action.paused = false;
    action.clampWhenFinished = false;

    action.setEffectiveTimeScale(1);
    action.setEffectiveWeight(1);

    // Repeat greeting animation for testing.
    action.setLoop(THREE.LoopRepeat, Infinity);

    action.fadeIn(0.2);
    action.play();

    activeActionRef.current = action;

    return () => {
      action.fadeOut(0.2);
    };
  }, [actions, names, state, doodle.name]);

  const scale = doodle.scale || 0.42;
  const position = doodle.position || [0, -1.2, 0];

  return (
    <group
      ref={groupRef}
      position={position}
      rotation={[0, 0.16, 0]}
      scale={scale}
    >
      <primitive object={copiedScene} />
    </group>
  );
}
