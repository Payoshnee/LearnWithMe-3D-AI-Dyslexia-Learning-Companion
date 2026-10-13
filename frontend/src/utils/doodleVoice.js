import { requestSpeechAudio } from "../services/companionApi.js";

let activeAudio = null;
let activeAudioUrl = "";
let activeSpeechRequest = null;

export function stopDoodleSpeech() {
  window.speechSynthesis?.cancel();

  if (activeSpeechRequest) {
    activeSpeechRequest.abort();
    activeSpeechRequest = null;
  }

  if (activeAudio) {
    activeAudio.pause();
    activeAudio.src = "";
    activeAudio = null;
  }

  if (activeAudioUrl) {
    URL.revokeObjectURL(activeAudioUrl);
    activeAudioUrl = "";
  }
}

function speakWithBrowser(text, voiceProfile = {}) {
  if (!("speechSynthesis" in window) || !("SpeechSynthesisUtterance" in window)) {
    return Promise.resolve(false);
  }

  return new Promise((resolve) => {
    const utterance = new SpeechSynthesisUtterance(text);
    const voices = window.speechSynthesis.getVoices();
    const preferredNames = voiceProfile.preferredNames || [];
    utterance.voice = preferredNames
      .map((name) => voices.find((voice) => voice.name.includes(name)))
      .find(Boolean) || voices.find((voice) => voice.lang?.startsWith("en")) || null;
    utterance.rate = Math.min(1.5, Math.max(0.5, voiceProfile.rate || 0.86));
    utterance.pitch = Math.min(2, Math.max(0, voiceProfile.pitch || 1));
    utterance.onend = () => resolve(true);
    utterance.onerror = () => resolve(false);
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
  });
}

function playAudioBlob(blob) {
  return new Promise((resolve) => {
    stopDoodleSpeech();
    activeAudioUrl = URL.createObjectURL(blob);
    activeAudio = new Audio(activeAudioUrl);

    activeAudio.onended = () => {
      stopDoodleSpeech();
      resolve(true);
    };
    activeAudio.onerror = () => {
      stopDoodleSpeech();
      resolve(false);
    };

    activeAudio.play().catch(() => {
      stopDoodleSpeech();
      resolve(false);
    });
  });
}

export async function speakAsDoodle(text, voiceProfile = {}, doodle = null) {
  stopDoodleSpeech();
  const request = new AbortController();
  activeSpeechRequest = request;

  try {
    const audioBlob = await requestSpeechAudio({
      text,
      doodleId: doodle?.id || voiceProfile.doodleId || "nova",
      voiceName: voiceProfile.ttsVoice,
      rate: voiceProfile.rate || 0.86,
    }, { signal: request.signal });
    if (request.signal.aborted) return false;
    activeSpeechRequest = null;
    const played = await playAudioBlob(audioBlob);
    if (played) {
      return true;
    }
  } catch (error) {
    if (error?.name === "AbortError") return false;
    console.error("Doodle Piper speech failed; using browser fallback:", error);
  }

  if (activeSpeechRequest === request) activeSpeechRequest = null;
  return speakWithBrowser(text, voiceProfile);
}
