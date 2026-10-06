from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import init_db
from app.routes.auth import router as auth_router
from app.routes.pages import router as pages_router
from app.routes.planners import router as planners_router
from app.routes.session import router as session_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    settings.database_file.parent.mkdir(parents=True, exist_ok=True)
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    init_db()
    yield


app = FastAPI(
    title="PocketSmart AI",
    description="Budget-aware AI recommendation assistant for home, party and jewelry planning.",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(pages_router)
app.include_router(auth_router)
app.include_router(planners_router)
app.include_router(session_router)

# Initialize persistence for CLI/test clients as well as ASGI lifespan startup.
init_db()


@app.get("/startup")
def startup():
    settings = get_settings()
    return {
        "status": "ready",
        "app": settings.app_name,
        "gemini_configured": bool(settings.gemini_api_key),
        "gemini_model": settings.gemini_model,
    }


@app.get("/health")
def health():
    return {"status": "ok"}
