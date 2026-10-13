# DyslexiaLearn Feature Set

## Core Idea

DyslexiaLearn is a voice-first AI learning companion for children with dyslexia. A child talks to a 3D doodle, the backend understands the intent with local AI/RAG, and the doodle responds with speech, animation, and a dynamic teaching board.

## Main Features

- Voice-first learning stage with a 3D AI doodle companion.
- Four selectable doodles: Nova, Luna, Bob, and Leo.
- Doodle selection screen with 3D preview and voice preview.
- Animated companion states: walking, greeting, hearing, listening, processing, speaking, pointing, and idle.
- Browser-independent speech output through backend TTS audio.
- Piper-ready local TTS architecture for deployable offline voice generation.
- FastAPI backend replacing the previous Spring Boot direction.
- React/Vite frontend with full-page companion stage.
- Local Ollama LLM integration for tutor responses.
- RAG-ready backend using stored lesson chunks and learner memory.
- Dynamic intent routing from user speech.
- Dynamic teaching board generated from backend responses.
- Pronunciation help flow with syllable board.
- Pronunciation attempt detection so repeating the word gives feedback instead of restarting the lesson.
- Voice quiz flow with spoken option handling.
- Stats/progress request flow with a dynamic progress board.
- Learner memory for practiced words, quiz results, retrieved context, and focus areas.
- Chrome-native speech-to-text using `SpeechRecognition`/`webkitSpeechRecognition`.
- Text fallback input when browser speech recognition is unavailable.
- Keep-listening mode for hands-free conversational practice.
- Day/night theme toggle.
- Background video on non-stage pages.

## Voice AI Flow

```text
Child speaks
→ Chrome converts microphone speech to text
→ FastAPI /api/v1/companion/voice-turn
→ local intent detection + shared DyBrain Ollama/RAG response
→ backend returns response text, doodle actions, and board data
→ FastAPI /api/v1/companion/speech generates audio with Piper
→ frontend plays one controlled audio stream
→ doodle animates and points to the board
```

## Supported Intents

- General question or learning help.
- Pronunciation request, such as "help me pronounce elephant".
- Pronunciation attempt, such as saying the current board word.
- Quiz request, such as "quiz me".
- Quiz answer, such as "option two" or "number two".
- Stats request, such as "how am I doing?".
- Translation/help intent foundation for multilingual expansion.

## Resume Highlight

Voice-first multimodal dyslexia tutor with a local LLM/RAG backend, dynamic teaching boards, deployable TTS audio generation, learner memory, and animated 3D companion state control.
