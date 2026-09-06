from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AntiCheatSignal, Problem, Submission


MIN_FAST_ACCEPT_SECONDS = {
    "easy": 20,
    "medium": 45,
    "hard": 90,
}


@dataclass(frozen=True)
class SignalDraft:
    signal_type: str
    severity: str
    payload: dict


def normalize_code_for_similarity(code: str) -> str:
    without_line_comments = re.sub(r"//.*", "", code)
    without_hash_comments = re.sub(r"#.*", "", without_line_comments)
    return re.sub(r"\s+", "", without_hash_comments).strip().lower()


def code_fingerprint(code: str) -> str:
    normalized = normalize_code_for_similarity(code)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def suspicious_speed_threshold_seconds(problem: Problem) -> int:
    difficulty_floor = MIN_FAST_ACCEPT_SECONDS.get(problem.difficulty, 30)
    estimated_floor = int((problem.estimated_seconds or 300) * 0.12)
    return max(difficulty_floor, estimated_floor)


def build_speed_signal(problem: Problem, accepted_after_seconds: int) -> SignalDraft | None:
    threshold = suspicious_speed_threshold_seconds(problem)
    if accepted_after_seconds >= threshold:
        return None
    severity = "high" if accepted_after_seconds < max(5, threshold // 3) else "medium"
    return SignalDraft(
        signal_type="very_fast_accept",
        severity=severity,
        payload={
            "accepted_after_seconds": accepted_after_seconds,
            "threshold_seconds": threshold,
            "difficulty": problem.difficulty,
            "estimated_seconds": problem.estimated_seconds,
        },
    )


async def record_submission_signals(
    db: AsyncSession,
    *,
    submission: Submission,
    problem: Problem,
    match_started_at: datetime | None = None,
) -> list[AntiCheatSignal]:
    if submission.kind != "submit" or submission.status != "accepted":
        return []

    drafts: list[SignalDraft] = []
    if match_started_at:
        accepted_after_seconds = max(0, int((datetime.utcnow() - match_started_at).total_seconds()))
        speed_signal = build_speed_signal(problem, accepted_after_seconds)
        if speed_signal:
            drafts.append(speed_signal)

    repeated_signal = await _build_repeated_code_signal(db, submission)
    if repeated_signal:
        drafts.append(repeated_signal)

    first_sweep_signal = await _build_first_submit_sweep_signal(db, submission)
    if first_sweep_signal:
        drafts.append(first_sweep_signal)

    signals = [
        AntiCheatSignal(
            user_id=submission.user_id,
            submission_id=submission.id,
            match_id=submission.match_id,
            problem_id=submission.problem_id,
            signal_type=draft.signal_type,
            severity=draft.severity,
            payload=draft.payload,
        )
        for draft in drafts
    ]
    db.add_all(signals)
    return signals


async def _build_repeated_code_signal(db: AsyncSession, submission: Submission) -> SignalDraft | None:
    current_hash = code_fingerprint(submission.code)
    result = await db.execute(
        select(Submission)
        .where(
            Submission.id != submission.id,
            Submission.problem_id == submission.problem_id,
            Submission.kind == "submit",
            Submission.status == "accepted",
        )
        .order_by(Submission.created_at.desc())
        .limit(50)
    )
    matches = [
        row
        for row in result.scalars().all()
        if row.user_id != submission.user_id and code_fingerprint(row.code) == current_hash
    ]
    if not matches:
        return None
    return SignalDraft(
        signal_type="repeated_exact_code",
        severity="medium",
        payload={
            "matching_submission_ids": [item.id for item in matches[:5]],
            "fingerprint": current_hash,
        },
    )


async def _build_first_submit_sweep_signal(db: AsyncSession, submission: Submission) -> SignalDraft | None:
    if not submission.user_id or submission.total_count < 20:
        return None
    result = await db.execute(
        select(Submission.id)
        .where(
            Submission.id != submission.id,
            Submission.user_id == submission.user_id,
            Submission.problem_id == submission.problem_id,
        )
        .limit(1)
    )
    if result.scalar_one_or_none():
        return None
    return SignalDraft(
        signal_type="first_submit_hidden_sweep",
        severity="low",
        payload={
            "passed_count": submission.passed_count,
            "total_count": submission.total_count,
            "note": "Accepted all hidden tests without earlier recorded attempts.",
        },
    )
