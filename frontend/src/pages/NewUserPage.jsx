import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { useDoodle } from "../companion/DoodleContext.js";
import VideoPage from "../components/ui/VideoPage.jsx";

export default function NewUserPage() {
  const navigate = useNavigate();
  const { setProfile } = useDoodle();
  const [name, setName] = useState("");
  const [age, setAge] = useState("");

  const saveProfile = (event) => {
    event.preventDefault();
    setProfile({ name: name.trim() || "Learner", age: Number(age) || 7 });
    navigate("/choose-doodle");
  };

  return (
    <VideoPage className="auth-page">
      <form className="auth-panel" onSubmit={saveProfile}>
        <p className="eyebrow">New learner</p>
        <h1>Tell us who is learning</h1>
        <label>
          Name
          <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Aarav" />
        </label>
        <label>
          Age
          <input value={age} onChange={(event) => setAge(event.target.value)} min="4" max="14" type="number" />
        </label>
        <button type="submit">Choose a doodle</button>
      </form>
    </VideoPage>
  );
}
