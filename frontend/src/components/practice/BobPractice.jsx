
import { useEffect, useMemo, useRef, useState } from "react";
import { Headphones, Mic, RotateCcw, Volume2 } from "lucide-react";

import DoodleCanvas from "../companion/DoodleCanvas.jsx";
import { doodleCatalog } from "../../companion/doodleCatalog.js";
import { COMPANION_STATES } from "../../companion/companionStates.js";

import {
  speakLearningText,
  stopLearningAudio,
  warmVoices,
} from "../../audio/learningAudio.js";

import {
  getWordsForLevel,
  practiceTypes,
  getPracticeQuestion,
  checkPracticeAnswer,
} from "../../data/practiceWords.js";

const STORAGE_KEY = "learnwithme_bob_practice_v1";

function loadProgress() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
    return {
      level: saved?.level || 1,
      wordIndex: saved?.wordIndex || 0,
      typeIndex: saved?.typeIndex || 0,
      stars: saved?.stars || 0,
    };
  } catch {
    return {
      level: 1,
      wordIndex: 0,
      typeIndex: 0,
      stars: 0,
    };
  }
}

export default function BobPractice() {
  const bob = doodleCatalog.find((item) => item.id === "bob");

  const [progress, setProgress] = useState(loadProgress);
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState("");
  const [audioEnabled, setAudioEnabled] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [listening, setListening] = useState(false);
  const [busy, setBusy] = useState(false);
  const [correct, setCorrect] = useState(false);
  const [error, setError] = useState("");

  const recognitionRef = useRef(null);
  const latestSubmitRef = useRef(null);
  const completedRef = useRef(false);
  const mountedRef = useRef(true);
  const audioKeyRef = useRef("");

  const words = useMemo(
    () => getWordsForLevel(progress.level),
    [progress.level]
  );

  const currentWord = words[progress.wordIndex] || words[0];
  const currentType =
    practiceTypes[progress.typeIndex] || practiceTypes[0];

  const question = currentWord
    ? getPracticeQuestion(currentWord, currentType.id)
    : null;

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
  }, [progress]);

  useEffect(() => {
    mountedRef.current = true;

    return () => {
      mountedRef.current = false;
      recognitionRef.current?.abort();
      recognitionRef.current = null;
      stopLearningAudio();
    };
  }, []);

  async function speak(text) {
    if (!text) return;

    stopLearningAudio();
    setSpeaking(true);
    setError("");

    try {
      await speakLearningText(text, "bob");
    } catch (err) {
      if (mountedRef.current) {
        setError(err.message || "Audio playback failed.");
      }
    } finally {
      if (mountedRef.current) setSpeaking(false);
    }
  }

  async function enableAudio() {
    warmVoices();
    setAudioEnabled(true);
    setError("");
    await speak(
      "Hey! I'm Bob, your Practice Buddy. " +
      "Let's practice together. " +
      question.question
    );
  }

  // Speak new questions automatically once audio is enabled.
  useEffect(() => {
    if (!audioEnabled || !question) return;

    const key = [
      progress.level,
      progress.wordIndex,
      progress.typeIndex,
    ].join("-");

    if (audioKeyRef.current === key) return;
    audioKeyRef.current = key;

    speak(question.question);
  }, [
    audioEnabled,
    progress.level,
    progress.wordIndex,
    progress.typeIndex,
  ]);

  function updateProgress(patch) {
    setProgress((previous) => ({
      ...previous,
      ...patch,
    }));
  }

  async function submitAnswer(value) {
    const response = String(value ?? answer).trim();

    if (!response || busy || correct || !question) return;

    setBusy(true);
    setError("");
    stopLearningAudio();

    const isCorrect = checkPracticeAnswer(
      response,
      question.answer
    );

    const message = isCorrect
      ? "Wonderful effort! You got it! Ready for another challenge?"
      : "Good try! Let's look at it together. " + question.hint;

    if (isCorrect) {
      setCorrect(true);
      completedRef.current = true;

      updateProgress({
        stars: progress.stars + 1,
      });
    }

    setFeedback(message);

    // Text matching cannot verify pronunciation quality.
    if (isCorrect && currentType.id === "read") {
      setFeedback(
        "I heard the expected word! Great effort. " +
        "This checks speech recognition, not pronunciation accuracy."
      );
    }

    if (audioEnabled) {
      await speak(message);
    }

    setAnswer("");
    setBusy(false);
  }

  latestSubmitRef.current = submitAnswer;

  function stopListening() {
    recognitionRef.current?.stop();
  }

  function startListening() {
    if (recognitionRef.current) {
      stopListening();
      return;
    }

    if (busy) return;

    const Engine =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition;

    if (!Engine) {
      setError(
        "Speech recognition isn't supported. You can type your answer."
      );
      return;
    }

    stopLearningAudio();
    setSpeaking(false);
    setError("");

    const recognition = new Engine();

    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    let finalText = "";
    let interimText = "";
    let hadError = false;
    let finished = false;

    const finish = () => {
      if (finished) return;
      finished = true;

      recognitionRef.current = null;

      if (!mountedRef.current) return;

      setListening(false);

      const recognized = finalText.trim();

      if (recognized && !hadError) {
        setAnswer(recognized);
        latestSubmitRef.current?.(recognized);
      } else if (!hadError) {
        setFeedback(
          "I didn't catch that. Please try again."
        );
      }
    };

    recognition.onstart = () => {
      console.log("[Bob Mic] Started");
      setListening(true);
      setFeedback("I'm listening...");
    };

    recognition.onspeechstart = () => {
      console.log("[Bob Mic] Speech detected");
    };

    recognition.onresult = (event) => {
      const finals = [];
      const interims = [];

      for (let i = 0; i < event.results.length; i++) {
        const result = event.results[i];
        const text = result[0]?.transcript || "";

        if (result.isFinal) {
          finals.push(text);
        } else {
          interims.push(text);
        }
      }

      finalText = finals.join(" ").trim();
      interimText = interims.join(" ").trim();

      const combined = [finalText, interimText]
        .filter(Boolean)
        .join(" ");

      setAnswer(combined);
      console.log("[Bob Mic] Heard:", combined);

      if (finalText) {
        recognition.stop();
      }
    };

    recognition.onerror = (event) => {
      if (event.error === "aborted") return;

      console.error("[Bob Mic] Error:", event.error);
      hadError = true;

      const messages = {
        "not-allowed":
          "Microphone access was blocked. Please allow it in Chrome.",
        "no-speech":
          "I didn't hear anything. Try speaking again.",
        network:
          "Chrome could not connect to its speech recognition service.",
        "audio-capture":
          "No working microphone was found.",
      };

      setError(
        messages[event.error] ||
        `Speech recognition error: ${event.error}`
      );
    };

    recognition.onend = finish;

    recognitionRef.current = recognition;

    try {
      recognition.start();
    } catch (err) {
      recognitionRef.current = null;
      setListening(false);
      setError("Could not start the microphone.");
    }
  }

  function nextQuestion() {
    recognitionRef.current?.abort();
    recognitionRef.current = null;
    stopLearningAudio();
    setListening(false);

    const nextType = progress.typeIndex + 1;

    if (nextType < practiceTypes.length) {
      updateProgress({ typeIndex: nextType });
    } else {
      const nextWord = progress.wordIndex + 1;

      if (nextWord < words.length) {
        updateProgress({
          wordIndex: nextWord,
          typeIndex: 0,
        });
      } else {
        const nextLevel =
          progress.level < 3 ? progress.level + 1 : 1;

        updateProgress({
          level: nextLevel,
          wordIndex: 0,
          typeIndex: 0,
        });
      }
    }

    setAnswer("");
    setFeedback("");
    setCorrect(false);
    completedRef.current = false;
    audioKeyRef.current = "";
  }

  function restartPractice() {
    recognitionRef.current?.abort();
    recognitionRef.current = null;
    stopLearningAudio();
    setListening(false);

    const reset = {
      level: 1,
      wordIndex: 0,
      typeIndex: 0,
      stars: 0,
    };

    setProgress(reset);
    setAnswer("");
    setFeedback("Let's start fresh!");
    setCorrect(false);
    completedRef.current = false;
    audioKeyRef.current = "";
  }

  if (!bob || !question) {
    return <p>Bob's practice activities are unavailable.</p>;
  }

  return (
    <div className="bob-practice">
      <section className="hub-card">
        <p className="eyebrow">Bob — Practice Buddy</p>
        <h1>Practice without pressure</h1>
        <p>
          Let's build confidence with fun speaking,
          spelling and reading challenges!
        </p>
        <p>
          Level {progress.level} · Word{" "}
          {progress.wordIndex + 1} of {words.length} ·{" "}
          ⭐ {progress.stars} stars
        </p>
      </section>

      <section className="stage-shell">
        <div className="stage-character">
          <DoodleCanvas
            doodle={bob}
            state={
              speaking
                ? COMPANION_STATES.SPEAKING
                : listening
                ? COMPANION_STATES.LISTENING
                : correct
                ? COMPANION_STATES.GREETING
                : COMPANION_STATES.IDLE
            }
          />
        </div>

        <div className="lesson-board">
          <p className="eyebrow">
            {currentType.title}
          </p>

          <h1>{currentWord.word}</h1>

          <p>{question.question}</p>

          {!audioEnabled && (
            <button
              className="start-audio"
              onClick={enableAudio}
            >
              <Headphones size={18} />
              Start Practice
            </button>
          )}

          <div className="lesson-input">
            <input
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") submitAnswer();
              }}
              placeholder="Type or say your answer"
              aria-label="Practice answer"
              disabled={busy || correct}
            />

            <button
              onClick={() => submitAnswer()}
              disabled={busy || correct || listening}
            >
              Check
            </button>

            <button
              onClick={startListening}
              disabled={busy || correct}
            >
              <Mic size={18} />
              {listening ? "Stop" : "Tap to talk"}
            </button>
          </div>

          <div className="lesson-tools">
            <button
              onClick={() => speak(question.question)}
              disabled={speaking}
            >
              <Volume2 size={17} />
              Hear Bob
            </button>

            <button
              onClick={() => {
                setFeedback(question.hint);
                if (audioEnabled) speak(question.hint);
              }}
            >
              Help
            </button>

            <button onClick={restartPractice}>
              <RotateCcw size={17} />
              Restart
            </button>

            {correct && (
              <button onClick={nextQuestion}>
                Next Challenge →
              </button>
            )}
          </div>

          {feedback && (
            <p className="lesson-feedback" role="status">
              {feedback}
            </p>
          )}

          {error && (
            <p className="audio-error" role="alert">
              {error}
            </p>
          )}
        </div>
      </section>
    </div>
  );
}
