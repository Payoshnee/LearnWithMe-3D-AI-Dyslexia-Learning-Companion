import { Mic, MicOff } from "lucide-react";
import { useState } from "react";

export default function VoiceButton({
  listening,
  supported,
  transcript,
  error,
  onStart,
  onStop,
  onSubmitText,
}) {
  const [typedText, setTypedText] = useState("");

  const submitText = (event) => {
    event.preventDefault();
    const value = typedText.trim();
    if (!value) {
      return;
    }
    setTypedText("");
    onSubmitText?.(value);
  };

  return (
    <div className="voice-console">
      <button
        className={`voice-button ${listening ? "is-listening" : ""}`}
        type="button"
        onClick={listening ? onStop : onStart}
      >
        {listening ? <MicOff size={24} /> : <Mic size={24} />}
        <span>{listening ? "Stop listening" : "Speak to Doodle"}</span>
      </button>
      <p>
        {transcript ||
          error ||
          (supported ? "Press the mic and ask for help." : "Type below or allow microphone access.")}
      </p>
      <form className="voice-fallback-form" onSubmit={submitText}>
        <input
          value={typedText}
          onChange={(event) => setTypedText(event.target.value)}
          placeholder="Type what you would say..."
          aria-label="Type to Doodle"
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}
