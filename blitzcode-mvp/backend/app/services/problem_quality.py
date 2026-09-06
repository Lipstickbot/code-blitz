from typing import Any


ALLOWED_DIFFICULTIES = {"easy", "medium", "hard"}
ALLOWED_STATUSES = {"draft", "active", "archived"}


class ProblemQualityError(ValueError):
    pass


def validate_problem_quality(
    *,
    status: str,
    difficulty: str,
    title: str,
    description: str,
    statement: str | None,
    starter_code_js: str | None,
    estimated_seconds: int,
    speed_score: int,
    time_limit_ms: int,
    memory_limit_mb: int,
    test_cases: list[Any],
) -> None:
    errors = problem_quality_errors(
        status=status,
        difficulty=difficulty,
        title=title,
        description=description,
        statement=statement,
        starter_code_js=starter_code_js,
        estimated_seconds=estimated_seconds,
        speed_score=speed_score,
        time_limit_ms=time_limit_ms,
        memory_limit_mb=memory_limit_mb,
        test_cases=test_cases,
    )
    if errors:
        raise ProblemQualityError("; ".join(errors))


def problem_quality_errors(
    *,
    status: str,
    difficulty: str,
    title: str,
    description: str,
    statement: str | None,
    starter_code_js: str | None,
    estimated_seconds: int,
    speed_score: int,
    time_limit_ms: int,
    memory_limit_mb: int,
    test_cases: list[Any],
) -> list[str]:
    errors: list[str] = []
    normalized_status = (status or "").strip().lower()
    normalized_difficulty = (difficulty or "").strip().lower()

    if normalized_status not in ALLOWED_STATUSES:
        errors.append("status must be draft, active or archived")
    if normalized_difficulty not in ALLOWED_DIFFICULTIES:
        errors.append("difficulty must be easy, medium or hard")
    if not title.strip():
        errors.append("title must not be empty")
    if not description.strip():
        errors.append("description must not be empty")
    if normalized_status == "active" and len((statement or description).strip()) < 40:
        errors.append("active problem statement must contain at least 40 characters")
    if starter_code_js is not None and "solve" not in starter_code_js:
        errors.append("starter_code_js must define or mention solve(...)")
    if estimated_seconds < 30 or estimated_seconds > 3600:
        errors.append("estimated_seconds must be between 30 and 3600")
    if speed_score < 1 or speed_score > 20:
        errors.append("speed_score must be between 1 and 20")
    if time_limit_ms < 100 or time_limit_ms > 10000:
        errors.append("time_limit_ms must be between 100 and 10000")
    if memory_limit_mb < 16 or memory_limit_mb > 1024:
        errors.append("memory_limit_mb must be between 16 and 1024")

    if normalized_status == "active":
        errors.extend(_active_test_errors(test_cases))

    return errors


def _active_test_errors(test_cases: list[Any]) -> list[str]:
    if not test_cases:
        return ["active problem must have test cases"]
    if not any(bool(getattr(test_case, "is_sample", False)) for test_case in test_cases):
        return ["active problem must have at least one sample test"]
    if not any(bool(getattr(test_case, "is_hidden", False)) for test_case in test_cases):
        return ["active problem must have at least one hidden test"]
    return []
