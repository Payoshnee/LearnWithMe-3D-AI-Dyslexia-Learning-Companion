
import robotFallbackUrl from "../assets/doodles/robot-fallback.svg";
import wendyModelUrl from "../assets/doodles/wendy.glb";
import bobModelUrl from "../assets/doodles/mira.glb";

export const doodleCatalog = [
  {
    id: "wendy",
    name: "Wendy",
    role: "Learning Buddy",
    description:
      "Hi! I'm Wendy, your Learning Buddy! We'll learn letters, sounds and stories together. Take your time — every small step matters!",
    color: "#8b5cf6",
    modelPath: wendyModelUrl,
    fallbackImagePath: robotFallbackUrl,
    scale: 0.82,
    position: [0, -1.18, 0],
    camera: { position: [0, 1.25, 5.4], fov: 36 },
    shadowPosition: [0, -1.18, 0],
    sourceName: "Wendy by Quaternius",
    modelStatus: "ready",
    voice: {
      gender: "female",
      rate: 0.82,
      pitch: 1.14,
      ttsVoice: "en_US-amy-medium.onnx",
      preferredNames: [
        "Samantha",
        "Google UK English Female",
        "Victoria",
      ],
      preview:
        "Hello! I am Wendy, your learning teacher. Let's learn something wonderful together!",
    },
  },
  {
    id: "bob",
    name: "Bob",
    role: "Practice Buddy",
    description:
      "Hey! I'm Bob, your Practice Buddy! Let's try fun challenges, play word games and celebrate every little success!",
    color: "#f97316",
    modelPath: bobModelUrl,
    fallbackImagePath: robotFallbackUrl,
    scale: 0.82,
    position: [0, -1.18, 0],
    camera: { position: [0, 1.25, 5.4], fov: 36 },
    shadowPosition: [0, -1.18, 0],
    sourceName: "Cube Guy Character by Quaternius",
    modelStatus: "ready",
    voice: {
      gender: "male",
      rate: 0.9,
      pitch: 0.96,
      ttsVoice: "en_US-ryan-medium.onnx",
      preferredNames: [
        "Alex",
        "Daniel",
        "Google US English",
      ],
      preview:
        "Hey! I am Bob. Ready to practice some words and play fun learning games?",
    },
  },
];
