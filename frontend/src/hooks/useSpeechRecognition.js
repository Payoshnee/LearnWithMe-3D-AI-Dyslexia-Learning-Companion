
import { useEffect, useRef, useState } from "react";

function getSpeechRecognition() {
  return (
    window.SpeechRecognition ||
    window.webkitSpeechRecognition ||
    null
  );
}

const ERROR_MESSAGES = {
  "audio-capture": "No microphone was found. Check your microphone.",
  "not-allowed": "Microphone permission was blocked.",
  "service-not-allowed": "Speech recognition is unavailable in this browser.",
  network: "Speech recognition could not connect. Check your internet connection.",
  "no-speech": "I didn't hear anything. Please try speaking again.",
  "language-not-supported": "The selected speech language is not supported.",
};

export function useSpeechRecognition({
  onResult,
  onStart,
  onEnd,
  onError,
} = {}) {
  const recognitionRef = useRef(null);
  const callbacksRef = useRef({});
  const finalTranscriptRef = useRef("");
  const hadErrorRef = useRef(false);

  const [supported] = useState(
    () => Boolean(getSpeechRecognition())
  );

  const [listening, setListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    callbacksRef.current = {
      onResult,
      onStart,
      onEnd,
      onError,
    };
  }, [onResult, onStart, onEnd, onError]);

  useEffect(() => {
    return () => {
      const recognition = recognitionRef.current;

      if (recognition) {
        recognition.onstart = null;
        recognition.onresult = null;
        recognition.onerror = null;
        recognition.onend = null;
        recognition.abort();
        recognitionRef.current = null;
      }
    };
  }, []);

  const startListening = () => {
    if (recognitionRef.current) return;

    const SpeechRecognition = getSpeechRecognition();

    if (!SpeechRecognition) {
      const message = "Speech recognition is not supported.";
      setError(message);
      callbacksRef.current.onError?.(message);
      return;
    }

    const recognition = new SpeechRecognition();

    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    finalTranscriptRef.current = "";
    hadErrorRef.current = false;

    setTranscript("");
    setError("");

    recognition.onstart = () => {
      console.log("[Speech] Microphone started");
      setListening(true);
      callbacksRef.current.onStart?.();
    };

    recognition.onspeechstart = () => {
      console.log("[Speech] Speech detected");
    };

    recognition.onspeechend = () => {
      console.log("[Speech] Speech ended");
    };

    recognition.onresult = (event) => {
      let finalText = "";
      let interimText = "";

      // Rebuild results to prevent duplicated text.
      for (let i = 0; i < event.results.length; i++) {
        const text = event.results[i][0]?.transcript || "";

        if (event.results[i].isFinal) {
          finalText += `${text} `;
        } else {
          interimText += `${text} `;
        }
      }

      finalTranscriptRef.current = finalText.trim();

      const combined = `${finalText} ${interimText}`.trim();
      setTranscript(combined);

      console.log("[Speech] Transcript:", combined);
    };

    recognition.onerror = (event) => {
      console.error("[Speech] Recognition error:", event.error);

      if (event.error === "aborted") return;

      hadErrorRef.current = true;

      const message =
        ERROR_MESSAGES[event.error] ||
        `Speech recognition failed: ${event.error}`;

      setError(message);
      callbacksRef.current.onError?.(message);
    };

    recognition.onend = () => {
      console.log("[Speech] Recognition ended");

      recognitionRef.current = null;
      setListening(false);

      const finalText = finalTranscriptRef.current.trim();

      if (finalText && !hadErrorRef.current) {
        console.log("[Speech] Sending result:", finalText);
        setTranscript(finalText);
        callbacksRef.current.onResult?.(finalText);
      } else if (!hadErrorRef.current) {
        const message = "No speech recognized. Please try again.";
        setError(message);
        callbacksRef.current.onError?.(message);
      }

      callbacksRef.current.onEnd?.();
    };

    recognitionRef.current = recognition;

    try {
      recognition.start();
    } catch (err) {
      console.error("[Speech] Start error:", err);

      recognitionRef.current = null;
      setListening(false);

      const message = "Could not start microphone recognition.";
      setError(message);
      callbacksRef.current.onError?.(message);
    }
  };

  const stopListening = () => {
    recognitionRef.current?.stop();
  };

  return {
    supported,
    listening,
    transcript,
    error,
    startListening,
    stopListening,
  };
}
