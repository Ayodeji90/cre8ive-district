from fastapi import FastAPI

app = FastAPI(title="Cre8ive District Website Agent", version="0.1.0")


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "website-agent"}
