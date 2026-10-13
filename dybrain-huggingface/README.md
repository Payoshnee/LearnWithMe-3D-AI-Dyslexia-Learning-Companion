---
title: DyBrain Shared Ollama
emoji: 🧠
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# DyBrain shared model service

This standalone Hugging Face Docker Space runs one `qwen2.5vl:3b` Ollama model for DyslexiaLearn, Closira, and PANDHARKAWDA-AROGYA.

## Required Space secret

Add `DYBRAIN_API_KEYS` in **Space Settings → Variables and secrets**. Its value is a comma-separated list of three newly generated project tokens. Never commit the tokens.

Generate each token locally with:

```sh
openssl rand -hex 32
```

The public health endpoint is `/api/dybrain/health`. Authenticated Ollama-compatible endpoints are `/api/tags`, `/api/ps`, `/api/chat`, and `/api/generate`. Send a project token as `Authorization: Bearer TOKEN`.

## Deploy this folder to the Space

```sh
git subtree split --prefix dybrain-huggingface -b dybrain-space
git push space dybrain-space:main
git branch -D dybrain-space
```

The Space uses its own Git history, so if the regular push is rejected, update a Space worktree and commit there instead of force-pushing.
