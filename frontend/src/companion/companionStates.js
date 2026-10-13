export const COMPANION_STATES = {
  IDLE: "idle",
  HEARING: "hearing",
  WALKING: "walking",
  GREETING: "greeting",
  PROCESSING: "processing",
  SPEAKING: "speaking",
  POINTING: "pointing",
  LISTENING: "listening",
};

export const animationMap = {
  [COMPANION_STATES.IDLE]: ["Idle", "Idle_Neutral", "Standing"],
  [COMPANION_STATES.HEARING]: ["Idle_Neutral", "Idle", "Standing"],
  [COMPANION_STATES.WALKING]: ["Walking", "Walk", "WalkJump", "Running", "Run"],
  [COMPANION_STATES.GREETING]: ["Wave"],
  [COMPANION_STATES.PROCESSING]: ["No", "Idle_Neutral", "Idle"],
  [COMPANION_STATES.SPEAKING]: ["Yes", "Interact", "Idle_Neutral"],
  [COMPANION_STATES.POINTING]: ["Punch", "Punch_Right", "Punch_Left", "Interact"],
  [COMPANION_STATES.LISTENING]: ["Idle_Neutral", "Idle", "Standing"],
};
