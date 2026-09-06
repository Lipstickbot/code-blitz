from pathlib import Path
import shutil
import sys

from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.database import AsyncSessionLocal
from app.services.judge_languages import JUDGE_LANGUAGES
from app.services.rate_limiter import rate_limiter_health


router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
async def health():
    return {
        "service": "BlitzCode API",
        "status": "ok",
    }


@router.get("/ready")
async def readiness():
    database = await _check_database()
    runtimes = _check_judge_runtimes()
    rate_limiter = rate_limiter_health()
    ready = (
        database["ok"]
        and runtimes["python"]["ok"]
        and runtimes["javascript"]["ok"]
        and runtimes["typescript"]["ok"]
        and rate_limiter["ok"]
    )

    return {
        "service": "BlitzCode API",
        "status": "ok" if ready else "degraded",
        "database": database,
        "judge": runtimes,
        "judge_languages": JUDGE_LANGUAGES,
        "rate_limiter": rate_limiter,
    }


async def _check_database() -> dict:
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("select 1"))
        return {"ok": True}
    except SQLAlchemyError as error:
        return {"ok": False, "error": str(error.__class__.__name__)}


def _check_judge_runtimes() -> dict:
    executor = settings.judge_executor.lower()
    docker_ok = _binary_exists(settings.judge_docker_binary) if executor == "docker" else True
    return {
        "executor": {
            "mode": executor,
            "ok": docker_ok,
            "docker_binary": settings.judge_docker_binary if executor == "docker" else None,
        },
        "python": {
            "ok": docker_ok if executor == "docker" else bool(sys.executable),
            "binary": settings.judge_python_image if executor == "docker" else sys.executable,
        },
        "javascript": {
            "ok": docker_ok if executor == "docker" else _binary_exists(settings.node_binary),
            "binary": settings.judge_node_image if executor == "docker" else settings.node_binary,
        },
        "typescript": {
            "ok": docker_ok if executor == "docker" else _binary_exists(settings.node_binary),
            "binary": settings.judge_node_image if executor == "docker" else settings.node_binary,
            "mode": "ts-light",
        },
    }


def _binary_exists(binary: str) -> bool:
    if not binary:
        return False
    if Path(binary).exists():
        return True
    return shutil.which(binary) is not None
