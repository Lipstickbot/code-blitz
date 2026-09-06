from typing import Any


ALLOWED_REVIEW_STATUSES = {"approved", "needs_changes", "comment"}


class ProblemReviewError(ValueError):
    pass


def validate_problem_review(status: str, notes: str, checklist: dict[str, Any] | None = None) -> None:
    errors = problem_review_errors(status, notes, checklist)
    if errors:
        raise ProblemReviewError("; ".join(errors))


def problem_review_errors(status: str, notes: str, checklist: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    normalized_status = (status or "").strip().lower()
    normalized_notes = (notes or "").strip()

    if normalized_status not in ALLOWED_REVIEW_STATUSES:
        errors.append("review status must be approved, needs_changes or comment")
    if normalized_status == "needs_changes" and not normalized_notes:
        errors.append("needs_changes review must include notes")
    if checklist is not None and not isinstance(checklist, dict):
        errors.append("checklist must be an object")

    return errors
