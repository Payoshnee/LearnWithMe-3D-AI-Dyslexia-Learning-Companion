"""Modal deployment entry point. Run: modal deploy modal_app.py

The web endpoint scales to zero when idle. It intentionally does not launch
Ollama or a GPU; deterministic lessons remain available, and optional AI uses
the configured remote/local provider only when one is reachable.
"""
import modal

image = modal.Image.debian_slim(python_version="3.12").pip_install_from_requirements("requirements.txt")
app = modal.App("learnwithme-backend")
secrets = [modal.Secret.from_name("learnwithme-secrets", required_keys=["SESSION_SECRET"])]

@app.function(image=image, secrets=secrets, timeout=60, scaledown_window=120)
@modal.asgi_app()
def fastapi_app():
    from app.main import app as api
    return api
