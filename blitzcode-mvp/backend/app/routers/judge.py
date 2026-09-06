from fastapi import APIRouter

from app.schemas import JudgeLanguageOut
from app.services.judge_languages import JUDGE_LANGUAGES


router = APIRouter(prefix="/api/judge", tags=["judge"])


@router.get("/languages", response_model=list[JudgeLanguageOut])
async def list_judge_languages():
    return JUDGE_LANGUAGES
