from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models import Problem, ProblemReview, TestCase, User, UserProblemHistory
from app.schemas import (
    AdminProblemOut,
    ProblemDetailOut,
    ProblemIn,
    ProblemOut,
    ProblemReviewIn,
    ProblemReviewOut,
    ProblemSolutionOut,
    ProblemUpdateIn,
    TestCaseIn,
    TestCaseOut,
)
from app.services.problem_quality import ProblemQualityError, validate_problem_quality
from app.services.problem_review import ProblemReviewError, validate_problem_review

router = APIRouter(prefix="/api/problems", tags=["problems"])
admin_router = APIRouter(prefix="/api/admin/problems", tags=["admin"])


def _make_slug(title: str) -> str:
    return title.lower().strip().replace(" ", "-").replace("_", "-").replace("/", "-")


async def _ensure_slug_available(db: AsyncSession, slug: str, current_problem_id: str | None = None) -> None:
    result = await db.execute(select(Problem).where(Problem.slug == slug))
    existing = result.scalar_one_or_none()
    if existing and existing.id != current_problem_id:
        raise HTTPException(status_code=400, detail="Problem slug already exists")


def _validate_problem_or_400(problem: Problem | ProblemIn, test_cases: list[TestCase | TestCaseIn]) -> None:
    try:
        validate_problem_quality(
            status=problem.status,
            difficulty=problem.difficulty,
            title=problem.title,
            description=problem.description,
            statement=problem.statement,
            starter_code_js=problem.starter_code_js,
            estimated_seconds=problem.estimated_seconds,
            speed_score=problem.speed_score,
            time_limit_ms=problem.time_limit_ms,
            memory_limit_mb=problem.memory_limit_mb,
            test_cases=test_cases,
        )
    except ProblemQualityError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


def _validate_review_or_400(payload: ProblemReviewIn) -> None:
    try:
        validate_problem_review(payload.status, payload.notes, payload.checklist)
    except ProblemReviewError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("", response_model=list[ProblemOut])
async def list_problems(
    difficulty: str | None = None,
    tag: str | None = None,
    status: str = "active",
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    query = select(Problem).where(Problem.status == status)
    if difficulty:
        query = query.where(Problem.difficulty == difficulty)
    if tag:
        query = query.where(Problem.tags.any(tag))
    result = await db.execute(
        query.order_by(desc(Problem.created_at), Problem.title)
        .offset(offset)
        .limit(limit)
    )
    return list(result.scalars().all())


@router.get("/{problem_id}", response_model=ProblemDetailOut)
async def get_problem(problem_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Problem).where(Problem.id == problem_id))
    problem = result.scalar_one_or_none()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    samples = await _list_test_cases(db, problem.id, samples_only=True)
    return ProblemDetailOut(
        id=problem.id,
        slug=problem.slug,
        title=problem.title,
        description=problem.description,
        statement=problem.statement,
        difficulty=problem.difficulty,
        status=problem.status,
        concept_group=problem.concept_group,
        tags=problem.tags,
        starter_code_js=problem.starter_code_js,
        estimated_seconds=problem.estimated_seconds,
        speed_score=problem.speed_score,
        sample_tests=samples,
    )


@router.get("/{problem_id}/solution", response_model=ProblemSolutionOut)
async def get_problem_solution(
    problem_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    problem = await _get_problem_or_404(db, problem_id)
    history_result = await db.execute(
        select(UserProblemHistory).where(
            UserProblemHistory.user_id == current_user.id,
            UserProblemHistory.problem_id == problem_id,
            UserProblemHistory.solved_count > 0,
        )
    )
    if not history_result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Solve this problem before viewing the editorial")
    return ProblemSolutionOut(
        problem_id=problem.id,
        title=problem.title,
        solution_notes=problem.solution_notes,
    )


def _require_admin(user: User) -> None:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")


async def _get_problem_or_404(db: AsyncSession, problem_id: str) -> Problem:
    result = await db.execute(select(Problem).where(Problem.id == problem_id))
    problem = result.scalar_one_or_none()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem


async def _list_test_cases(db: AsyncSession, problem_id: str, samples_only: bool = False) -> list[TestCase]:
    query = select(TestCase).where(TestCase.problem_id == problem_id)
    if samples_only:
        query = query.where(TestCase.is_sample == True)  # noqa: E712
    result = await db.execute(query.order_by(TestCase.position))
    return list(result.scalars().all())


def _make_test_case(problem_id: str, payload: TestCaseIn, position: int) -> TestCase:
    return TestCase(
        problem_id=problem_id,
        position=payload.position or position,
        input=payload.input,
        expected_output=payload.expected_output,
        input_json=payload.input_json,
        expected_json=payload.expected_json,
        is_sample=payload.is_sample,
        is_hidden=payload.is_hidden,
        explanation=payload.explanation,
    )


@admin_router.get("", response_model=list[AdminProblemOut])
async def list_admin_problems(
    status: str = "active",
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    result = await db.execute(
        select(Problem)
        .where(Problem.status == status)
        .order_by(desc(Problem.created_at), Problem.title)
        .offset(offset)
        .limit(limit)
    )
    return list(result.scalars().all())


@admin_router.post("", response_model=AdminProblemOut)
async def create_problem(
    payload: ProblemIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    slug = payload.slug or _make_slug(payload.title)
    _validate_problem_or_400(payload, payload.test_cases)
    await _ensure_slug_available(db, slug)

    problem = Problem(
        slug=slug,
        title=payload.title,
        description=payload.description,
        statement=payload.statement or payload.description,
        difficulty=payload.difficulty,
        status=payload.status,
        concept_group=payload.concept_group,
        tags=payload.tags,
        starter_code_js=payload.starter_code_js,
        solution_notes=payload.solution_notes,
        estimated_seconds=payload.estimated_seconds,
        speed_score=payload.speed_score,
        time_limit_ms=payload.time_limit_ms,
        memory_limit_mb=payload.memory_limit_mb,
        created_by=current_user.id,
    )
    problem.test_cases = [
        TestCase(
            position=tc.position or index + 1,
            input=tc.input,
            expected_output=tc.expected_output,
            input_json=tc.input_json,
            expected_json=tc.expected_json,
            is_sample=tc.is_sample,
            is_hidden=tc.is_hidden,
            explanation=tc.explanation,
        )
        for index, tc in enumerate(payload.test_cases)
    ]
    db.add(problem)
    await db.commit()
    await db.refresh(problem)
    return problem


@admin_router.patch("/{problem_id}", response_model=AdminProblemOut)
async def update_problem(
    problem_id: str,
    payload: ProblemUpdateIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    problem = await _get_problem_or_404(db, problem_id)

    updates = payload.model_dump(exclude_unset=True)
    if "slug" in updates:
        next_slug = updates["slug"] or problem.slug
        await _ensure_slug_available(db, next_slug, current_problem_id=problem.id)
        problem.slug = next_slug
    if "title" in updates:
        problem.title = updates["title"]
        if not problem.slug:
            next_slug = _make_slug(problem.title)
            await _ensure_slug_available(db, next_slug, current_problem_id=problem.id)
            problem.slug = next_slug
    if "description" in updates:
        problem.description = updates["description"]
        if "statement" not in updates:
            problem.statement = updates["description"]
    for field in [
        "statement",
        "difficulty",
        "status",
        "concept_group",
        "tags",
        "starter_code_js",
        "solution_notes",
        "estimated_seconds",
        "speed_score",
        "time_limit_ms",
        "memory_limit_mb",
    ]:
        if field in updates:
            setattr(problem, field, updates[field])

    test_cases = await _list_test_cases(db, problem.id)
    _validate_problem_or_400(problem, test_cases)
    await db.commit()
    await db.refresh(problem)
    return problem


@admin_router.get("/{problem_id}/reviews", response_model=list[ProblemReviewOut])
async def list_problem_reviews(
    problem_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    await _get_problem_or_404(db, problem_id)
    result = await db.execute(
        select(ProblemReview)
        .where(ProblemReview.problem_id == problem_id)
        .order_by(desc(ProblemReview.created_at))
    )
    return list(result.scalars().all())


@admin_router.post("/{problem_id}/reviews", response_model=ProblemReviewOut)
async def create_problem_review(
    problem_id: str,
    payload: ProblemReviewIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    await _get_problem_or_404(db, problem_id)
    _validate_review_or_400(payload)

    review = ProblemReview(
        problem_id=problem_id,
        reviewer_user_id=current_user.id,
        status=payload.status.strip().lower(),
        notes=payload.notes.strip(),
        checklist=payload.checklist,
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review


@admin_router.get("/{problem_id}/tests", response_model=list[TestCaseOut])
async def list_problem_tests(
    problem_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    await _get_problem_or_404(db, problem_id)
    return await _list_test_cases(db, problem_id)


@admin_router.post("/{problem_id}/tests", response_model=TestCaseOut)
async def create_problem_test(
    problem_id: str,
    payload: TestCaseIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    problem = await _get_problem_or_404(db, problem_id)
    existing = await _list_test_cases(db, problem_id)
    test_case = _make_test_case(problem_id, payload, len(existing) + 1)
    _validate_problem_or_400(problem, [*existing, test_case])
    db.add(test_case)
    await db.commit()
    await db.refresh(test_case)
    return test_case


@admin_router.put("/{problem_id}/tests", response_model=list[TestCaseOut])
async def replace_problem_tests(
    problem_id: str,
    payload: list[TestCaseIn],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    problem = await _get_problem_or_404(db, problem_id)
    existing = await _list_test_cases(db, problem_id)
    for test_case in existing:
        await db.delete(test_case)
    next_cases = [
        _make_test_case(problem_id, item, index + 1)
        for index, item in enumerate(payload)
    ]
    _validate_problem_or_400(problem, next_cases)
    db.add_all(next_cases)
    await db.commit()
    return await _list_test_cases(db, problem_id)


@admin_router.patch("/{problem_id}/tests/{test_case_id}", response_model=TestCaseOut)
async def update_problem_test(
    problem_id: str,
    test_case_id: str,
    payload: TestCaseIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    problem = await _get_problem_or_404(db, problem_id)
    test_case = await db.get(TestCase, test_case_id)
    if not test_case or test_case.problem_id != problem_id:
        raise HTTPException(status_code=404, detail="Test case not found")

    existing = await _list_test_cases(db, problem_id)
    next_case = _make_test_case(problem_id, payload, test_case.position)
    next_case.id = test_case.id
    _validate_problem_or_400(
        problem,
        [next_case if item.id == test_case.id else item for item in existing],
    )

    test_case.position = payload.position or test_case.position
    test_case.input = payload.input
    test_case.expected_output = payload.expected_output
    test_case.input_json = payload.input_json
    test_case.expected_json = payload.expected_json
    test_case.is_sample = payload.is_sample
    test_case.is_hidden = payload.is_hidden
    test_case.explanation = payload.explanation
    await db.commit()
    await db.refresh(test_case)
    return test_case


@admin_router.delete("/{problem_id}/tests/{test_case_id}")
async def delete_problem_test(
    problem_id: str,
    test_case_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    problem = await _get_problem_or_404(db, problem_id)
    test_case = await db.get(TestCase, test_case_id)
    if not test_case or test_case.problem_id != problem_id:
        raise HTTPException(status_code=404, detail="Test case not found")
    existing = await _list_test_cases(db, problem_id)
    _validate_problem_or_400(
        problem,
        [item for item in existing if item.id != test_case.id],
    )
    await db.delete(test_case)
    await db.commit()
    return {"deleted": True}


@admin_router.delete("/{problem_id}")
async def delete_problem(
    problem_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    result = await db.execute(select(Problem).where(Problem.id == problem_id))
    problem = result.scalar_one_or_none()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    await db.delete(problem)
    await db.commit()
    return {"deleted": True}
