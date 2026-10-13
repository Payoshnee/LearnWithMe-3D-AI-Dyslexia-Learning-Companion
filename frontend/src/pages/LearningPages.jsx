
import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Headphones, Mic, RotateCcw, Volume2 } from "lucide-react";

import AppNav from "../components/ui/AppNav.jsx";
import VideoPage from "../components/ui/VideoPage.jsx";
import DoodleCanvas from "../components/companion/DoodleCanvas.jsx";
import PhonicsGameSuite from "../components/games/PhonicsGameSuite.jsx";
import BobPractice from "../components/practice/BobPractice.jsx";

import { doodleCatalog } from "../companion/doodleCatalog.js";
import { COMPANION_STATES } from "../companion/companionStates.js";

import {
  teachingLevels,
  getTeachingWords,
  getTeachingWord,
  createTeachingLesson,
} from "../data/teachingLessons.js";

import {
  playPhoneme,
  speakLearningText,
  stopLearningAudio,
  warmVoices,
} from "../audio/learningAudio.js";

import {
  answerLesson,
  getProgress,
  saveProgress,
} from "../services/learningApi.js";

const EMPTY_PROGRESS = {
  stars: 0,
  completedLessons: [],
  completedGames: [],
  level: 1,
  wordsLearned: [],
  letterMastery: {},
};

const STORAGE_PREFIX = "learnwithme_lesson_";

// The backend currently supports four steps.
// The fifth sentence activity will be added later.
const SUPPORTED_STEPS = 4;

function Shell({ children }) {
  return (
    <VideoPage className="learning-hub">
      <AppNav />
      <div className="hub-content">{children}</div>
    </VideoPage>
  );
}

function useProgress() {
  const [progress, setProgress] = useState(EMPTY_PROGRESS);

  useEffect(() => {
    getProgress()
      .then((data) => {
        setProgress({ ...EMPTY_PROGRESS, ...data });
      })
      .catch((error) => {
        console.warn("Progress unavailable:", error);
      });
  }, []);

  const update = useCallback((patch) => {
    setProgress((current) => {
      const next = { ...current, ...patch };
      saveProgress(next).catch(console.error);
      return next;
    });
  }, []);

  return [progress, update];
}

export function DashboardPage() {
  return (
    <Shell>
      <section className="hub-card hero-card">
        <p className="eyebrow">Your learning home</p>
        <h1>What shall we explore today?</h1>
        <p>
          Choose a calm lesson with Wendy, a playful challenge
          with Bob, or a story to read aloud.
        </p>
        <div className="hub-actions">
          <Link to="/learn">Learn with Wendy</Link>
          <Link to="/practice">Practice with Bob</Link>
          <Link to="/games">Play phonics games</Link>
        </div>
      </section>

      <section className="hub-grid">
        <article>
          <h2>Letters &amp; sounds</h2>
          <p>22 structured beginner word lessons.</p>
        </article>
        <article>
          <h2>Reading</h2>
          <p>Short sentences with read-aloud support.</p>
        </article>
        <article>
          <h2>Progress</h2>
          <p>Every effort and completed activity counts.</p>
        </article>
      </section>
    </Shell>
  );
}

function readStoredLesson(id) {
  try {
    const saved = JSON.parse(
      localStorage.getItem(STORAGE_PREFIX + id) || "null"
    );

    const step = Number(saved?.step) || 0;

    return {
      step: Math.max(0, Math.min(step, SUPPORTED_STEPS)),
      complete: Boolean(saved?.complete),
    };
  } catch {
    return { step: 0, complete: false };
  }
}

function WendyLesson({ wordId }) {
  const item = getTeachingWord(wordId);
  const lesson = createTeachingLesson(item);

  const wendy = doodleCatalog.find(
    (character) => character.id === "wendy"
  );

  const [state, setState] = useState(() =>
    readStoredLesson(wordId)
  );

  const [input, setInput] = useState("");
  const [feedback, setFeedback] = useState("");
  const [busy, setBusy] = useState(false);
  const [listening, setListening] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [audioEnabled, setAudioEnabled] = useState(false);
  const [audioError, setAudioError] = useState("");
  const [micError, setMicError] = useState("");
  const [heardText, setHeardText] = useState("");

  const recognitionRef = useRef(null);
  const timerRef = useRef(null);
  const submittingRef = useRef(false);
  const submitRef = useRef(null);
  const spokenKeyRef = useRef("");
  const mountedRef = useRef(true);
  const audioRunRef = useRef(0);

  const currentStep = Math.min(
    state.step,
    SUPPORTED_STEPS - 1
  );

  const prompt = lesson?.steps[currentStep];

  useEffect(() => {
    mountedRef.current = true;

    return () => {
      mountedRef.current = false;
      audioRunRef.current += 1;

      clearTimeout(timerRef.current);

      const recognition = recognitionRef.current;
      recognitionRef.current = null;

      if (recognition) {
        recognition.onresult = null;
        recognition.onerror = null;
        recognition.onend = null;
        recognition.abort();
      }

      stopLearningAudio();
    };
  }, []);

  const speakPrompt = useCallback(async () => {
    if (!audioEnabled || state.complete || !prompt) return;

    const run = ++audioRunRef.current;

    setSpeaking(true);
    setAudioError("");

    try {
      await speakLearningText(prompt.speak, "wendy");

      if (run !== audioRunRef.current) return;

      for (const sound of prompt.sounds || []) {
        if (run !== audioRunRef.current) return;
        await playPhoneme(sound);
      }
    } catch (error) {
      if (mountedRef.current && run === audioRunRef.current) {
        setAudioError(
          error.message || "Wendy could not play the audio."
        );
      }
    } finally {
      if (mountedRef.current && run === audioRunRef.current) {
        setSpeaking(false);
      }
    }
  }, [audioEnabled, state.complete, prompt]);

  useEffect(() => {
    const key = `${wordId}-${state.step}-${audioEnabled}`;

    if (
      audioEnabled &&
      !state.complete &&
      spokenKeyRef.current !== key
    ) {
      spokenKeyRef.current = key;
      speakPrompt();
    }
  }, [
    audioEnabled,
    wordId,
    state.step,
    state.complete,
    speakPrompt,
  ]);

  const recordComplete = async () => {
    try {
      const current = {
        ...EMPTY_PROGRESS,
        ...(await getProgress()),
      };

      const alreadyComplete =
        current.completedLessons.includes(wordId);

      await saveProgress({
        ...current,
        stars: current.stars + (alreadyComplete ? 0 : 1),
        completedLessons: [
          ...new Set([...current.completedLessons, wordId]),
        ],
        wordsLearned: [
          ...new Set([
            ...(current.wordsLearned || []),
            wordId.toLowerCase(),
          ]),
        ],
      });
    } catch (error) {
      console.warn("Could not save lesson progress:", error);
    }
  };

  const submit = async (value) => {
    const response = String(value ?? input).trim();

    if (
      !response ||
      submittingRef.current ||
      state.complete ||
      !lesson
    ) {
      return;
    }

    submittingRef.current = true;
    audioRunRef.current += 1;

    stopLearningAudio();
    setSpeaking(false);
    setBusy(true);
    setMicError("");

    try {
      const result = await answerLesson({
        lesson_id: wordId,
        step: state.step,
        response,
      });

      if (!mountedRef.current) return;

      const next = {
        step: result.step,
        complete: Boolean(result.complete),
      };

      const stepChanged =
        next.step !== state.step || next.complete;

      setState(next);

      localStorage.setItem(
        STORAGE_PREFIX + wordId,
        JSON.stringify(next)
      );

      setFeedback(result.message);

      if (stepChanged) {
        spokenKeyRef.current = "";
      }

      if (result.complete && result.correct !== false) {
        await recordComplete();
      }

      if (audioEnabled && !stepChanged) {
        const run = ++audioRunRef.current;
        setSpeaking(true);

        try {
          await speakLearningText(result.message, "wendy");
        } catch (error) {
          if (mountedRef.current) {
            setAudioError(error.message);
          }
        } finally {
          if (mountedRef.current && run === audioRunRef.current) {
            setSpeaking(false);
          }
        }
      }
    } catch (error) {
      if (mountedRef.current) {
        setFeedback(
          error.message || "Wendy could not check your answer."
        );
      }
    } finally {
      submittingRef.current = false;

      if (mountedRef.current) {
        setBusy(false);
        setInput("");
      }
    }
  };

  submitRef.current = submit;

  const startAudio = () => {
    warmVoices();
    setAudioEnabled(true);
    setAudioError("");
    spokenKeyRef.current = "";
    setFeedback("Wendy is ready to teach you!");
  };

  const stopListening = () => {
    try {
      recognitionRef.current?.stop();
    } catch (error) {
      console.warn("Microphone stop:", error);
    }
  };

  const listen = () => {
    if (recognitionRef.current) {
      stopListening();
      return;
    }

    if (busy || submittingRef.current) return;

    audioRunRef.current += 1;
    stopLearningAudio();
    setSpeaking(false);
    setMicError("");
    setHeardText("");

    const Engine =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition;

    if (!Engine) {
      setMicError(
        "Speech recognition isn't supported. Type your answer."
      );
      return;
    }

    const recognition = new Engine();

    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    let finished = false;
    let finalText = "";
    let hadError = false;

    const clearTimer = () => {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    };

    const finish = () => {
      if (finished) return;
      finished = true;

      clearTimer();
      recognitionRef.current = null;

      if (!mountedRef.current) return;

      setListening(false);

      if (finalText && !hadError) {
        setHeardText(finalText);
        setInput(finalText);
        setFeedback(`I heard: ${finalText}`);
        submitRef.current?.(finalText);
      } else if (!hadError) {
        setFeedback(
          "No speech was recognized. Please try again."
        );
      }
    };

    recognition.onstart = () => {
      console.log("[Wendy Mic] Started");
      setListening(true);
      setFeedback("Listening... Speak clearly.");
    };

    recognition.onspeechstart = () => {
      console.log("[Wendy Mic] Speech detected");
    };

    recognition.onresult = (event) => {
      const finals = [];
      const interims = [];

      for (let i = 0; i < event.results.length; i++) {
        const text = event.results[i][0]?.transcript || "";

        if (event.results[i].isFinal) {
          finals.push(text);
        } else {
          interims.push(text);
        }
      }

      finalText = finals.join(" ").trim();

      const combined = [
        finalText,
        interims.join(" ").trim(),
      ].filter(Boolean).join(" ");

      console.log("[Wendy Mic] Heard:", combined);

      if (mountedRef.current) {
        setHeardText(combined);
        setInput(combined);
      }

      if (finalText) {
        try {
          recognition.stop();
        } catch {
          finish();
        }
      }
    };

    recognition.onerror = (event) => {
      if (event.error === "aborted") return;

      hadError = true;

      console.error(
        "[Wendy Mic] Error:",
        event.error
      );

      const messages = {
        "not-allowed": "Microphone permission was blocked.",
        "no-speech": "No speech was heard. Try again.",
        network: "Chrome's speech service could not connect.",
        "audio-capture": "Chrome could not access your microphone.",
      };

      setMicError(
        messages[event.error] ||
        `Microphone error: ${event.error}`
      );
    };

    recognition.onend = finish;
    recognitionRef.current = recognition;

    try {
      recognition.start();

      timerRef.current = setTimeout(() => {
        if (!finished) {
          setMicError(
            "Listening took too long. Please try again."
          );
          recognition.stop();
        }
      }, 20000);
    } catch (error) {
      recognitionRef.current = null;
      clearTimer();
      setListening(false);
      setMicError("Microphone could not start.");
    }
  };

  const restart = () => {
    recognitionRef.current?.abort();
    recognitionRef.current = null;
    clearTimeout(timerRef.current);

    audioRunRef.current += 1;
    stopLearningAudio();

    const reset = { step: 0, complete: false };

    setState(reset);
    setInput("");
    setFeedback("Lesson restarted!");
    setMicError("");
    setHeardText("");
    setSpeaking(false);
    setListening(false);

    spokenKeyRef.current = "";

    localStorage.setItem(
      STORAGE_PREFIX + wordId,
      JSON.stringify(reset)
    );
  };

  if (!wendy || !lesson) {
    return <p>Wendy's lesson is unavailable.</p>;
  }

  return (
    <section className="stage-shell">
      <div className="stage-character">
        <DoodleCanvas
          doodle={wendy}
          state={
            speaking
              ? COMPANION_STATES.SPEAKING
              : listening
              ? COMPANION_STATES.LISTENING
              : feedback
              ? COMPANION_STATES.POINTING
              : COMPANION_STATES.IDLE
          }
        />
      </div>

      <div className="lesson-board">
        <p className="eyebrow">Wendy — Learning Buddy</p>

        <h1>
          {state.complete
            ? `${lesson.word} complete!`
            : `${lesson.word}: step ${state.step + 1} of ${SUPPORTED_STEPS}`}
        </h1>

        <div className="board-word">{lesson.word}</div>

        <p>
          {state.complete
            ? "Wonderful effort! You finished this word!"
            : prompt.display}
        </p>

        {!audioEnabled && (
          <button className="start-audio" onClick={startAudio}>
            <Headphones size={18} />
            Start Learning
          </button>
        )}

        {audioEnabled && (
          <p className="audio-ready">
            Audio on · Wendy reads the lesson aloud
          </p>
        )}

        {!state.complete && (
          <div className="lesson-input">
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") submit();
              }}
              placeholder="Type your answer"
              aria-label="Lesson answer"
            />

            <button
              onClick={() => submit()}
              disabled={busy || listening}
            >
              {busy ? "Checking..." : "Send"}
            </button>

            <button onClick={listen} disabled={busy}>
              <Mic size={18} />
              {listening ? "Stop listening" : "Tap to talk"}
            </button>
          </div>
        )}

        <div className="lesson-tools">
          <button
            onClick={speakPrompt}
            disabled={!audioEnabled || speaking || state.complete}
          >
            <Volume2 size={17} />
            Repeat
          </button>

          {!state.complete && (
            <button
              onClick={() => submit("hint")}
              disabled={busy}
            >
              Help
            </button>
          )}

          <button onClick={restart}>
            <RotateCcw size={17} />
            Restart
          </button>
        </div>

        {heardText && (
          <p className="lesson-feedback">
            Recognized: {heardText}
          </p>
        )}

        {micError && (
          <p className="audio-error" role="alert">
            Microphone: {micError}
          </p>
        )}

        {audioError && (
          <p className="audio-error" role="alert">
            Audio: {audioError}
          </p>
        )}

        {feedback && (
          <p className="lesson-feedback" role="status">
            {feedback}
          </p>
        )}
      </div>
    </section>
  );
}

export function LearnPage() {
  const [level, setLevel] = useState(1);
  const [wordId, setWordId] = useState("cat");

  const words = getTeachingWords(level);

  const chooseLevel = (nextLevel) => {
    const nextWords = getTeachingWords(nextLevel);

    setLevel(nextLevel);

    if (nextWords.length > 0) {
      setWordId(nextWords[0].word.toLowerCase());
    }
  };

  return (
    <Shell>
      <section className="hub-card">
        <p className="eyebrow">
          Wendy — Your Learning Buddy
        </p>
        <h2>Choose what we will learn today!</h2>
        <p>
          Let's discover letters, sounds and words together.
          Take your time — every small step matters!
        </p>

        <div className="lesson-tabs">
          {teachingLevels.map((item) => (
            <button
              key={item.id}
              className={level === item.id ? "active" : ""}
              onClick={() => chooseLevel(item.id)}
            >
              Level {item.id} — {item.title}
            </button>
          ))}
        </div>

        <p>
          {teachingLevels.find((item) => item.id === level)?.description}
        </p>

        <div className="lesson-tabs">
          {words.map((item) => (
            <button
              key={item.word}
              className={
                wordId === item.word.toLowerCase()
                  ? "active"
                  : ""
              }
              onClick={() =>
                setWordId(item.word.toLowerCase())
              }
            >
              {item.word}
            </button>
          ))}
        </div>
      </section>

      <WendyLesson key={wordId} wordId={wordId} />
    </Shell>
  );
}

export function PracticePage() {
  return (
    <Shell>
      <BobPractice />
    </Shell>
  );
}

export function GamesPage() {
  const [progress, update] = useProgress();

  const record = (id, level) => {
    const key = `${id}-level-${level}`;

    if (progress.completedGames.includes(key)) return;

    update({
      stars: progress.stars + 1,
      completedGames: [
        ...progress.completedGames,
        key,
      ],
      level: Math.max(progress.level || 1, level),
    });
  };

  return (
    <Shell>
      <PhonicsGameSuite onProgress={record} />
    </Shell>
  );
}

export function ReadingPage() {
  const [enabled, setEnabled] = useState(false);
  const [error, setError] = useState("");

  const read = async () => {
    setEnabled(true);
    setError("");

    try {
      await speakLearningText(
        "A cat sat in the sun. The cat had fun.",
        "wendy"
      );
    } catch (error) {
      setError(error.message);
    }
  };

  return (
    <Shell>
      <section className="hub-card reading-card">
        <p className="eyebrow">Reading activity</p>
        <h1>A sunny cat</h1>

        <p className="reading-line">A cat sat in the sun.</p>
        <p className="reading-line">The cat had fun.</p>

        <button onClick={read}>
          <Volume2 size={18} />
          {enabled ? "Read again" : "Start reading audio"}
        </button>

        {error && <p className="audio-error">{error}</p>}

        <p>Point to each word. Take all the time you need.</p>
      </section>
    </Shell>
  );
}

export function ProgressPage() {
  const [progress] = useProgress();

  return (
    <Shell>
      <section className="hub-card">
        <p className="eyebrow">Learning progress</p>
        <h1>Every small step matters</h1>

        <div className="progress-cards">
          <article>
            <b>{progress.stars}</b>
            <span>Stars earned</span>
          </article>

          <article>
            <b>{progress.completedLessons.length}</b>
            <span>Lessons completed</span>
          </article>

          <article>
            <b>{progress.completedGames.length}</b>
            <span>Game levels completed</span>
          </article>

          <article>
            <b>{progress.wordsLearned?.length || 0}</b>
            <span>Words learned</span>
          </article>
        </div>
      </section>
    </Shell>
  );
}

export function SettingsPage() {
  const [large, setLarge] = useState(
    () => localStorage.getItem("lwm-large-type") === "true"
  );

  const [reduced, setReduced] = useState(
    () => localStorage.getItem("lwm-reduced-motion") === "true"
  );

  useEffect(() => {
    document.body.classList.toggle("large-type", large);
    localStorage.setItem("lwm-large-type", String(large));
  }, [large]);

  useEffect(() => {
    document.body.classList.toggle("reduced-motion", reduced);
    localStorage.setItem(
      "lwm-reduced-motion",
      String(reduced)
    );
  }, [reduced]);

  return (
    <Shell>
      <section className="hub-card">
        <p className="eyebrow">Accessibility settings</p>
        <h1>Make LearnWithMe comfortable</h1>

        <label className="setting-row">
          <input
            type="checkbox"
            checked={large}
            onChange={(event) =>
              setLarge(event.target.checked)
            }
          />
          Use larger text
        </label>

        <label className="setting-row">
          <input
            type="checkbox"
            checked={reduced}
            onChange={(event) =>
              setReduced(event.target.checked)
            }
          />
          Reduce movement
        </label>
      </section>
    </Shell>
  );
}
