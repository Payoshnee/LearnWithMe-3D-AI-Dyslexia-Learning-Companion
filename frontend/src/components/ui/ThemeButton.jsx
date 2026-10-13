import { Moon, Sun } from "lucide-react";

export default function ThemeButton({ theme, onToggle }) {
  return (
    <button className="theme-button" type="button" onClick={onToggle}>
      {theme === "day" ? <Moon size={20} /> : <Sun size={20} />}
      <span>{theme === "day" ? "Night theme" : "Day theme"}</span>
    </button>
  );
}
