
/**
 * LearnWithMe — Fast Learning Audio
 *
 * Wendy: Learning Buddy
 * Bob: Practice Buddy
 *
 * Browser speech first for low latency.
 * Backend speech is a fallback.
 * Existing phoneme recordings are preserved.
 */

import { requestSpeechAudio } from "../services/companionApi.js";

const PHONEMES = new Set([
  "a", "b", "c", "d", "e", "f", "g", "h",
  "i", "k", "l", "m", "n", "o", "p",
  "r", "s", "t", "u", "w",
]);

let currentAudio = null;
let currentUrl = "";
let currentRequest = null;
let currentCancel = null;
let speechToken = 0;

const VOICE_PROFILES = {
  wendy: {
    rate: 0.88,
    pitch: 1.08,
    preferred: [
      "Microsoft Aria",
      "Microsoft Jenny",
      "Google UK English Female",
      "Samantha",
    ],
  },

  bob: {
    rate: 0.94,
    pitch: 0.94,
    preferred: [
      "Microsoft Ryan",
      "Microsoft Guy",
      "Google UK English Male",
      "Daniel",
    ],
  },
};

export const normalizeAnswer = (value) =>
  String(value ?? "")
    .toLowerCase()
    .replace(/[\/\\[\](){}*]/g, "")
    .replace(/[^a-z]/g, "");

function getProfile(name) {
  return VOICE_PROFILES[name] || VOICE_PROFILES.wendy;
}

function getBrowserVoices() {
  if (!("speechSynthesis" in window)) return [];

  return window.speechSynthesis.getVoices();
}

function selectVoice(profileName) {
  const voices = getBrowserVoices();
  const profile = getProfile(profileName);

  const englishVoices = voices.filter((voice) =>
    /^en(?:-|$)/i.test(voice.lang || "")
  );

  for (const preferredName of profile.preferred) {
    const voice = englishVoices.find((item) =>
      item.name.toLowerCase().includes(
        preferredName.toLowerCase()
      )
    );

    if (voice) return voice;
  }

  return (
    englishVoices.find((voice) => voice.default) ||
    englishVoices[0] ||
    null
  );
}

/**
 * Stop all current speech or phoneme playback.
 */
export function stopLearningAudio() {
  speechToken += 1;

  const cancel = currentCancel;
  currentCancel = null;

  if ("speechSynthesis" in window) {
    window.speechSynthesis.cancel();
  }

  if (currentRequest) {
    currentRequest.abort();
    currentRequest = null;
  }

  if (currentAudio) {
    currentAudio.pause();
    currentAudio.removeAttribute("src");
    currentAudio = null;
  }

  if (currentUrl) {
    URL.revokeObjectURL(currentUrl);
    currentUrl = "";
  }

  cancel?.();
}

/**
 * Play an audio file.
 */
function playUrl(src, token) {
  return new Promise((resolve, reject) => {
    if (token !== speechToken) {
      resolve("cancelled");
      return;
    }

    const audio = new Audio(src);
    currentAudio = audio;

    let settled = false;

    const cleanup = () => {
      audio.onended = null;
      audio.onerror = null;

      if (currentAudio === audio) {
        currentAudio = null;
      }

      if (currentCancel === cancel) {
        currentCancel = null;
      }
    };

    const finish = (result, error = null) => {
      if (settled) return;
      settled = true;

      cleanup();

      if (error) reject(error);
      else resolve(result);
    };

    const cancel = () => {
      audio.pause();
      finish("cancelled");
    };

    currentCancel = cancel;

    audio.onended = () => finish("played");

    audio.onerror = () => {
      finish(
        "error",
        new Error("Audio recording could not be played.")
      );
    };

    audio.play().catch(() => {
      if (token !== speechToken) {
        finish("cancelled");
        return;
      }

      finish(
        "error",
        new Error(
          "Audio playback was blocked. Press Start Learning again."
        )
      );
    });
  });
}

/**
 * Speak using Chrome or Windows browser voices.
 */
function browserSpeak(text, profileName, token) {
  if (
    !("speechSynthesis" in window) ||
    !("SpeechSynthesisUtterance" in window)
  ) {
    return Promise.reject(
      new Error("Browser speech is unavailable.")
    );
  }

  return new Promise((resolve, reject) => {
    if (token !== speechToken) {
      resolve("cancelled");
      return;
    }

    const synth = window.speechSynthesis;
    const profile = getProfile(profileName);

    const utterance = new SpeechSynthesisUtterance(text);

    utterance.lang = "en-US";
    utterance.rate = profile.rate;
    utterance.pitch = profile.pitch;
    utterance.volume = 1;

    const selectedVoice = selectVoice(profileName);

    if (selectedVoice) {
      utterance.voice = selectedVoice;
      utterance.lang = selectedVoice.lang;
    }

    let settled = false;

    const cleanup = () => {
      utterance.onend = null;
      utterance.onerror = null;

      if (currentCancel === cancel) {
        currentCancel = null;
      }
    };

    const finish = (result, error = null) => {
      if (settled) return;
      settled = true;

      cleanup();

      if (error) reject(error);
      else resolve(result);
    };

    const cancel = () => finish("cancelled");

    currentCancel = cancel;

    utterance.onend = () => {
      finish(
        token === speechToken ? "browser" : "cancelled"
      );
    };

    utterance.onerror = (event) => {
      if (
        token !== speechToken ||
        ["interrupted", "canceled", "cancelled"].includes(
          event.error
        )
      ) {
        finish("cancelled");
        return;
      }

      finish(
        "error",
        new Error("Browser speech could not play.")
      );
    };

    try {
      synth.speak(utterance);
    } catch (error) {
      finish("error", error);
    }
  });
}

/**
 * Backend TTS fallback.
 */
async function serverSpeak(text, profileName, token) {
  const controller = new AbortController();
  currentRequest = controller;

  const profile = getProfile(profileName);

  try {
    const blob = await requestSpeechAudio(
      {
        text,
        doodleId: profileName,
        rate: profile.rate,
      },
      { signal: controller.signal }
    );

    if (
      controller.signal.aborted ||
      token !== speechToken
    ) {
      return "cancelled";
    }

    currentRequest = null;
    currentUrl = URL.createObjectURL(blob);

    return await playUrl(currentUrl, token);
  } finally {
    if (currentRequest === controller) {
      currentRequest = null;
    }
  }
}

/**
 * Main speaking function.
 *
 * Browser speech is attempted immediately.
 * Backend speech is only used if browser
 * synthesis fails.
 */
export async function speakLearningText(
  text,
  profileName = "wendy"
) {
  stopLearningAudio();

  const token = speechToken;
  const content = String(text ?? "").trim();

  if (!content) return "empty";

  try {
    const result = await browserSpeak(
      content,
      profileName,
      token
    );

    if (token !== speechToken) return "cancelled";

    return result;
  } catch (browserError) {
    if (token !== speechToken) return "cancelled";

    console.warn(
      "[LearnWithMe Audio] Browser voice unavailable:",
      browserError.message
    );
  }

  try {
    return await serverSpeak(
      content,
      profileName,
      token
    );
  } catch (serverError) {
    if (token !== speechToken) return "cancelled";

    console.error(
      "[LearnWithMe Audio] Speech failed:",
      serverError
    );

    throw new Error(
      "Wendy or Bob could not speak. Check your audio settings."
    );
  }
}

/**
 * Play existing checked phoneme recordings.
 *
 * This still stops previous audio intentionally,
 * so simultaneous narration will not overlap.
 */
export async function playPhoneme(symbol) {
  const key = normalizeAnswer(symbol);

  const recording = key === "k" ? "c" : key;

  if (!PHONEMES.has(key)) {
    throw new Error(
      `No phoneme recording is available for ${key}.`
    );
  }

  stopLearningAudio();

  const token = speechToken;

  try {
    const result = await playUrl(
      `/audio/phonemes/${recording}.m4a`,
      token
    );

    return result === "played"
      ? "recording"
      : result;
  } catch (error) {
    console.warn(
      `[LearnWithMe Audio] Phoneme ${key} failed:`,
      error.message
    );

    throw error;
  }
}

/**
 * Load available voices.
 */
export function warmVoices() {
  if (!("speechSynthesis" in window)) return [];

  return window.speechSynthesis.getVoices();
}
