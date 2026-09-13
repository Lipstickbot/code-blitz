from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routers import (
    admin,
    auth,
    blitz,
    health,
    judge,
    leaderboard,
    learning,
    matchmaking,
    matches,
    problems,
    profile,
    submissions,
    tournaments,
)
from app.services.env_validation import assert_valid_startup_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    assert_valid_startup_config(settings)
    # MVP: create tables directly from models on startup.
    # Replace with Alembic migrations once the schema stabilizes.
    if settings.auto_create_tables:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="BlitzCode API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(health.router)
app.include_router(judge.router)
app.include_router(problems.router)
app.include_router(problems.admin_router)
app.include_router(submissions.router)
app.include_router(blitz.router)
app.include_router(leaderboard.router)
app.include_router(learning.router)
app.include_router(matchmaking.router)
app.include_router(matches.router)
app.include_router(profile.router)
app.include_router(tournaments.router)


@app.get("/")
async def root():
    return {"service": "BlitzCode API", "status": "ok"}
