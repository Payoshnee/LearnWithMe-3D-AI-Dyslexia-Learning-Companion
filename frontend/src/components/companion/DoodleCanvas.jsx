
import { Suspense, useMemo } from "react";
import { Canvas } from "@react-three/fiber";
import {
  Html,
  OrbitControls,
  PerspectiveCamera,
} from "@react-three/drei";

import DoodleModel from "./DoodleModel.jsx";

function LoadingCharacter() {
  return (
    <Html center>
      <span className="loader">
        Loading character...
      </span>
    </Html>
  );
}

export default function DoodleCanvas({ doodle, state }) {
  const camera = doodle?.camera || {
    position: [0, 1.25, 5],
    fov: 35,
  };

  const shadowPosition = doodle?.shadowPosition || [
    0,
    -1.24,
    0,
  ];

  const canvasOptions = useMemo(
    () => ({
      antialias: true,
      alpha: true,
      powerPreference: "low-power",
    }),
    []
  );

  if (!doodle) {
    return (
      <div className="loader">
        Character unavailable.
      </div>
    );
  }

  return (
    <Canvas
      className="doodle-canvas"
      dpr={[1, 1.25]}
      gl={canvasOptions}
      frameloop="always"
      shadows={false}
      onCreated={({ gl }) => {
        gl.setClearAlpha(0);
      }}
    >
      <PerspectiveCamera
        makeDefault
        position={camera.position}
        fov={camera.fov}
        near={0.1}
        far={100}
      />

      <ambientLight intensity={1.8} />

      <directionalLight
        position={[4, 6, 4]}
        intensity={2.4}
      />

      <Suspense fallback={<LoadingCharacter />}>
        <DoodleModel
          doodle={doodle}
          state={state}
        />

        {/* Lightweight static floor shadow */}
        <mesh
          position={shadowPosition}
          rotation={[-Math.PI / 2, 0, 0]}
        >
          <circleGeometry args={[0.8, 32]} />
          <meshBasicMaterial
            color="#000000"
            transparent
            opacity={0.08}
            depthWrite={false}
          />
        </mesh>
      </Suspense>

      <OrbitControls
        enablePan={false}
        enableZoom={false}
        enableDamping={false}
        minPolarAngle={1.2}
        maxPolarAngle={1.8}
      />
    </Canvas>
  );
}
