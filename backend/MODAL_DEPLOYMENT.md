# Modal deployment

This is an actual Modal ASGI entry point: `modal_app.py`.

1. Install the CLI: `pip install modal`, then run `modal setup`.
2. Create a secret without committing it: `modal secret create learnwithme-secrets SESSION_SECRET=<long-random-value> DATABASE_URL=<managed-postgres-url>`.
3. From `backend`, run `modal deploy modal_app.py`.
4. Set Vercel's `VITE_API_BASE_URL` to the resulting HTTPS URL.

The function uses `scaledown_window=120`, so it scales to zero after idle time. Modal cold starts are expected. This service does not start local Ollama or provision a GPU. Its core authentication and deterministic learning APIs can use CPU scale-to-zero; optional AI conversation needs a separately configured provider. Modal allowances and prices change, so review the current dashboard, add a spending limit, and monitor usage before enabling any paid inference.
