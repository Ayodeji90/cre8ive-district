FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src

RUN --mount=type=cache,target=/root/.cache/pip pip install .

EXPOSE 8000

CMD ["uvicorn", "website_agent.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
