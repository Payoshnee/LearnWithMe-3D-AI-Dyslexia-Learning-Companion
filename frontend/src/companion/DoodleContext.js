import { createContext, useContext } from "react";

export const DoodleContext = createContext(null);

export function useDoodle() {
  const context = useContext(DoodleContext);
  if (!context) {
    throw new Error("useDoodle must be used inside DoodleProvider");
  }
  return context;
}
