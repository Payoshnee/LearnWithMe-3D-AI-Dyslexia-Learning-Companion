export default function SpeechBubble({ message }) {
  if (!message) {
    return null;
  }

  return (
    <div className="speech-bubble" aria-live="polite">
      {message}
    </div>
  );
}
