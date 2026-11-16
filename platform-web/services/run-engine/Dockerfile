FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

COPY src/ src/

EXPOSE 8002

CMD ["uvicorn", "run_engine.api.app:app", "--host", "0.0.0.0", "--port", "8002"]
