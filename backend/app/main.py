from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import attempts_router, problems_router
from .config import settings
from .database import Base, engine
from .seed import seed


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Create database tables and seed problems on startup."""
    Base.metadata.create_all(bind=engine)
    seed()
    yield


app = FastAPI(
    title="LLD Practice Platform",
    description="A practice platform for Low-Level Design problems with AI-assisted feedback.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(problems_router)
app.include_router(attempts_router)


@app.get("/api/health")
def health_check():
    """Simple health check endpoint."""
    return {
        "status": "ok",
        "llm_enabled": settings.llm_enabled,
        "llm_model": settings.LLM_MODEL if settings.llm_enabled else None,
    }
