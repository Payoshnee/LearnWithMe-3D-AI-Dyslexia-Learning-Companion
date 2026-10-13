import { useMemo, useState } from "react";

import { doodleCatalog } from "./doodleCatalog.js";
import { COMPANION_STATES } from "./companionStates.js";
import { DoodleContext } from "./DoodleContext.js";

const savedProfile = () => {
  try {
    return JSON.parse(localStorage.getItem("dyslexialearn_profile"));
  } catch {
    return null;
  }
};

export function DoodleProvider({ children }) {
  const [profile, setProfileState] = useState(savedProfile);
  const [selectedDoodle, setSelectedDoodle] = useState(null);
  const [companionState, setCompanionState] = useState(COMPANION_STATES.IDLE);
  const [message, setMessage] = useState("");
  const [theme, setTheme] = useState("day");
  const [boardOpen, setBoardOpen] = useState(false);
  const [activeSyllable, setActiveSyllable] = useState(-1);

  const setProfile = (nextProfile) => {
    localStorage.setItem("dyslexialearn_profile", JSON.stringify(nextProfile));
    setProfileState(nextProfile);
  };

  const chooseDoodle = (id) => {
    setSelectedDoodle(doodleCatalog.find((doodle) => doodle.id === id) || doodleCatalog[0]);
  };

  const toggleTheme = () => setTheme((current) => (current === "day" ? "night" : "day"));

  const value = useMemo(
    () => ({
      profile,
      setProfile,
      doodles: doodleCatalog,
      selectedDoodle,
      chooseDoodle,
      companionState,
      setCompanionState,
      message,
      setMessage,
      theme,
      toggleTheme,
      boardOpen,
      setBoardOpen,
      activeSyllable,
      setActiveSyllable,
    }),
    [activeSyllable, boardOpen, companionState, message, profile, selectedDoodle, theme]
  );

  return <DoodleContext.Provider value={value}>{children}</DoodleContext.Provider>;
}
