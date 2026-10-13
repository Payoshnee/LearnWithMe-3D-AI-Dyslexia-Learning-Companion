# RAG Implementation Plan (Ollama Integration)

Retrieval-Augmented Generation (RAG) allows an AI model to read your specific documents, textbooks, or custom content and use that information to generate accurate, context-aware answers. This is perfect for a learning platform to create personalized, grounded educational experiences without hallucinating facts.

## Proposed Architecture: Python + Java Hybrid

Using Python for the RAG/AI logic and Java for the main backend is an **excellent and highly recommended idea**. In fact, this is the industry standard for enterprise applications. Python has the richest AI ecosystem (LangChain, LlamaIndex), while Java is incredibly robust for business logic.

1. **AI Microservice (Python):** We will build a lightweight API using **FastAPI** and **LangChain** (or LlamaIndex). This service will handle document chunking, embedding generation, vector database search, and talking to Ollama.
2. **Main Backend (Java Spring Boot):** Your existing Java backend will remain the core. It handles user authentication, database management, and serves the React frontend. When an AI feature is requested, Java simply makes a fast HTTP REST call to the Python microservice.
3. **AI Engine:** [Ollama](https://ollama.com) (Running locally).
4. **Vector Database:** **ChromaDB** or **FAISS** (running within the Python service), OR we can still use **PostgreSQL pgvector**. For simplicity in Python, ChromaDB is often preferred.

## Proposed Features for DyslexiaLearn

1. **Personalized AI Tutor:** An interactive assistant that retrieves educational materials and explains them using simple vocabulary, short sentences, and engaging analogies tailored for dyslexic students.
2. **Dynamic Story & Quiz Generator:** The AI can retrieve specific paragraphs from a story and instantly generate multiple-choice reading comprehension quizzes based *only* on that text.
3. **"Read it to me" Summarizer:** Students can upload or select a long, complex text. The RAG pipeline retrieves the core concepts and the AI rewrites it into a dyslexia-friendly format (bullet points, spaced out text).
4. **Contextual Synonym Finder:** If a student struggles with a specific word in a story, the AI analyzes the exact sentence using RAG and provides a simpler synonym or emoji-based explanation that fits perfectly in that context.
5. **Socratic Concept Checker:** Instead of just giving answers, the AI Tutor uses the Socratic method—asking the child gentle, guided questions to help them figure out the answer themselves, which builds confidence.
6. **Visual Vocabulary Builder:** The AI scans uploaded documents, identifies traditionally difficult words for dyslexic readers, and automatically generates simple phonetic spellings and visual analogies before the student even starts reading.

## Hardware Requirements & Model Recommendations

Running Ollama locally depends heavily on the system's RAM and VRAM (GPU Memory).

### 🟢 Low-End PC (Minimum Requirements)
* **Hardware:** 8GB RAM, CPU-only (No dedicated GPU) or basic integrated graphics.
* **Best Models:**
  * `phi3` (3.8B parameters) - Microsoft's highly capable small model. Extremely fast and surprisingly smart for its size.
  * `qwen2:1.5b` - Great balance of speed and intelligence for low RAM.

### 🟡 Medium PC (Recommended Baseline)
* **Hardware:** 16GB RAM, Dedicated GPU with 6GB - 8GB VRAM (e.g., RTX 3060 / 4060 or Mac M1/M2/M3 with 16GB Unified Memory).
* **Best Models:**
  * `llama3:8b` (8B parameters) - Meta's incredibly smart model. Excellent reasoning, instruction following, and perfect for the AI Tutor.
  * `nomic-embed-text` - Required model for generating the vector embeddings.

### 🔴 High-End PC / Server
* **Hardware:** 32GB - 64GB+ RAM, Dedicated GPU with 16GB - 24GB+ VRAM (e.g., RTX 3090, 4090, Mac Studio).
* **Best Models:**
  * `llama3:70b` (Requires ~40GB RAM to run quantized) - State-of-the-art reasoning.
  * `mixtral:8x7b` (Requires ~26GB RAM) - Extremely fast and accurate Mixture of Experts model.

## Implementation Steps (How we will build it)

### Step 1: Integrated FastAPI AI Backend
- Keep the AI/RAG/voice pipeline inside the main `backend/app` FastAPI service.
- Use the existing `/api/v1/companion/*` endpoints for voice turns, transcription, speech, pronunciation, quiz, stats, and memory.
- Use the shared DyBrain Ollama service for LLM responses and embeddings, PostgreSQL/pgvector for durable retrieval, Chrome's native speech recognition for STT, and Piper for TTS.

### Step 2: Backend Integration
- Route frontend requests directly to the FastAPI companion API.
- Keep rule-based pronunciation, quiz, and stats flows fast, and call the LLM only when open-ended tutoring or unknown words need reasoning.
- Store learner memory and retrieved context through the same backend so there is no separate AI microservice to run.

### Step 3: Frontend (React)
- Create a beautiful, child-friendly AI Chat interface.
- Render the AI's response with clear, spaced-out typography.

## Open Questions for Approval

> [!IMPORTANT]
> 1. Do you approve this hybrid architecture (Python FastAPI for AI, Java Spring Boot for core backend)?
> 2. Which hardware tier (Low/Medium/High) will you primarily be running this on?
