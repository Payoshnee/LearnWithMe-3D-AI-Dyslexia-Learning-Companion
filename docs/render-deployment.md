# Deploy the DyslexiaLearn backend on Render

The repository root contains `render.yaml`, which creates:

- `dyslexialearn-api`: the FastAPI backend on Render's free Python runtime.

The Blueprint does not create a Render database. The backend uses an external Neon PostgreSQL database supplied through `DATABASE_URL`.

## Deploy

1. Open <https://dashboard.render.com/blueprints> and select **New Blueprint Instance**.
2. Connect the GitHub repository `Payoshnee/DyslexiaLearn`.
3. Keep the Blueprint path as `render.yaml` and deploy it.
4. When Render requests `DATABASE_URL`, paste the Neon pooled PostgreSQL connection string. Keep `sslmode=require` in the URL.
5. When Render requests `OLLAMA_API_KEY`, enter only the token assigned to DyslexiaLearn from the Hugging Face `DYBRAIN_API_KEYS` secret.
6. Wait until `/health` reports HTTP 200.

Do not add `DYBRAIN_API_KEYS` to Render. That comma-separated master list belongs only in the Hugging Face Space. Render receives one project token through `OLLAMA_API_KEY`.

The Neon value should have this shape and must be stored as a Render secret:

```text
postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require
```

Do not commit the real connection string or database password.

## Connect Vercel

After Render assigns the backend URL, set this Vercel production variable:

```env
VITE_API_BASE_URL=https://YOUR-RENDER-SERVICE.onrender.com
```

Redeploy the Vercel frontend after changing the variable. If the Vercel production domain changes, update `FRONTEND_ALLOWED_ORIGINS` in Render.

## Verify

```sh
curl https://YOUR-RENDER-SERVICE.onrender.com/health
curl https://YOUR-RENDER-SERVICE.onrender.com/api/v1/companion/system
```

The first endpoint should return `"Server is running!"`. The second should report that `qwen2.5vl:3b` is connected.

Render free web services spin down while idle and can take time to wake. Neon persists the application database independently from the Render web service.
