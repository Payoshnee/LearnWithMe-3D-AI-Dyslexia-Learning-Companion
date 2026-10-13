FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DYBRAIN_MODEL=qwen2.5vl:3b

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl zstd \
    && curl -fsSL https://ollama.com/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY app.py start.sh ./
RUN chmod +x ./start.sh
RUN ollama serve >/tmp/ollama-build.log 2>&1 & server_pid=$!; \
    until curl --silent --fail http://127.0.0.1:11434/api/tags >/dev/null 2>&1; do sleep 1; done; \
    ollama pull "$DYBRAIN_MODEL"; \
    kill "$server_pid"

EXPOSE 7860
CMD ["./start.sh"]
