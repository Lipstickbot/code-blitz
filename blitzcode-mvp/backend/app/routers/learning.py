from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user_optional
from app.database import get_db
from app.models import (
    Course,
    CourseEnrollment,
    CourseLesson,
    CourseLessonProgress,
    CoursePracticeProblem,
    Problem,
    User,
    UserProblemHistory,
)
from app.schemas import (
    CourseDetailOut,
    CourseEnrollmentOut,
    CourseLessonCompleteOut,
    CourseLessonOut,
    CourseOut,
    CoursePracticeProblemOut,
    CourseRecommendationOut,
)


router = APIRouter(prefix="/api/learning", tags=["learning"])


@router.get("/courses", response_model=list[CourseOut])
async def list_courses(
    access_type: str | None = None,
    level: str | None = None,
    status: str = "published",
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    query = select(Course).where(Course.status == status)
    if access_type:
        query = query.where(Course.access_type == access_type)
    if level:
        query = query.where(Course.level == level)
    result = await db.execute(query.order_by(Course.access_type, Course.level, Course.title).limit(limit))
    return [await _course_out(db, course, current_user) for course in result.scalars().all()]


@router.get("/courses/{course_ref}", response_model=CourseDetailOut)
async def get_course(
    course_ref: str,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    course = await _get_course_or_404(db, course_ref)
    lessons = (
        await db.execute(
            select(CourseLesson)
            .where(CourseLesson.course_id == course.id)
            .order_by(CourseLesson.position)
        )
    ).scalars().all()
    base = await _course_out(db, course, current_user)
    completed_ids = await _completed_lesson_ids(db, course.id, current_user)
    practice_rows = (
        await db.execute(
            select(CoursePracticeProblem, Problem)
            .join(Problem, Problem.id == CoursePracticeProblem.problem_id)
            .where(CoursePracticeProblem.course_id == course.id)
            .order_by(CoursePracticeProblem.position)
        )
    ).all()
    return CourseDetailOut(
        **base.model_dump(),
        lessons=[
            CourseLessonOut(
                id=lesson.id,
                position=lesson.position,
                title=lesson.title,
                summary=lesson.summary,
                content=lesson.content,
                checklist=lesson.checklist or [],
                kind=lesson.kind,
                duration_minutes=lesson.duration_minutes,
                is_preview=lesson.is_preview,
                completed=lesson.id in completed_ids,
            )
            for lesson in lessons
        ],
        practice_problems=[
            CoursePracticeProblemOut(
                id=problem.id,
                slug=problem.slug,
                title=problem.title,
                difficulty=problem.difficulty,
                tags=problem.tags,
                position=link.position,
            )
            for link, problem in practice_rows
        ],
    )


@router.get("/recommendations", response_model=list[CourseRecommendationOut])
async def recommend_courses(
    limit: int = Query(default=3, ge=1, le=6),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    courses = (
        await db.execute(
            select(Course)
            .where(Course.status == "published")
            .order_by(Course.access_type, Course.level, Course.title)
        )
    ).scalars().all()
    weak_tags, solved_tags = await _learning_profile_tags(db, current_user)

    scored: list[tuple[int, str, Course]] = []
    for course in courses:
        score, reason = _score_course_recommendation(course, weak_tags, solved_tags, current_user is not None)
        scored.append((score, reason, course))

    scored.sort(key=lambda item: (-item[0], item[2].access_type != "free", item[2].level, item[2].title))
    recommendations: list[CourseRecommendationOut] = []
    for score, reason, course in scored[:limit]:
        course_out = await _course_out(db, course, current_user)
        recommendations.append(
            CourseRecommendationOut(
                **course_out.model_dump(),
                score=score,
                reason=reason,
            )
        )
    return recommendations


@router.post("/courses/{course_ref}/enroll", response_model=CourseEnrollmentOut)
async def enroll_course(
    course_ref: str,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Login is required to enroll")
    course = await _get_course_or_404(db, course_ref)
    if course.access_type != "free":
        raise HTTPException(status_code=402, detail="Premium checkout is not connected yet")

    existing = await db.execute(
        select(CourseEnrollment).where(
            CourseEnrollment.course_id == course.id,
            CourseEnrollment.user_id == current_user.id,
        )
    )
    enrollment = existing.scalar_one_or_none()
    if not enrollment:
        enrollment = CourseEnrollment(
            course_id=course.id,
            user_id=current_user.id,
            status="active",
            source="free",
            progress_percent=0,
        )
        db.add(enrollment)
        await db.commit()
        await db.refresh(enrollment)

    return CourseEnrollmentOut(
        course_id=course.id,
        status=enrollment.status,
        progress_percent=enrollment.progress_percent,
    )


@router.post("/courses/{course_ref}/lessons/{lesson_id}/complete", response_model=CourseLessonCompleteOut)
async def complete_lesson(
    course_ref: str,
    lesson_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Login is required to track lesson progress")

    course = await _get_course_or_404(db, course_ref)
    lesson = await db.scalar(
        select(CourseLesson).where(CourseLesson.id == lesson_id, CourseLesson.course_id == course.id)
    )
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    enrollment = await _get_enrollment(db, course.id, current_user.id)
    if not enrollment:
        if course.access_type != "free":
            raise HTTPException(status_code=402, detail="Premium checkout is not connected yet")
        enrollment = CourseEnrollment(
            course_id=course.id,
            user_id=current_user.id,
            status="active",
            source="free",
            progress_percent=0,
        )
        db.add(enrollment)
        await db.flush()

    existing_progress = await db.scalar(
        select(CourseLessonProgress).where(
            CourseLessonProgress.user_id == current_user.id,
            CourseLessonProgress.lesson_id == lesson.id,
        )
    )
    if not existing_progress:
        db.add(
            CourseLessonProgress(
                user_id=current_user.id,
                course_id=course.id,
                lesson_id=lesson.id,
            )
        )
        await db.flush()

    lesson_count = int(await db.scalar(select(func.count(CourseLesson.id)).where(CourseLesson.course_id == course.id)) or 0)
    completed_lessons = int(
        await db.scalar(
            select(func.count(CourseLessonProgress.id)).where(
                CourseLessonProgress.user_id == current_user.id,
                CourseLessonProgress.course_id == course.id,
            )
        )
        or 0
    )
    enrollment.progress_percent = 100 if lesson_count == 0 else round((completed_lessons / lesson_count) * 100)
    await db.commit()

    return CourseLessonCompleteOut(
        course_id=course.id,
        lesson_id=lesson.id,
        progress_percent=enrollment.progress_percent,
        completed_lessons=completed_lessons,
        lesson_count=lesson_count,
    )


async def _get_course_or_404(db: AsyncSession, course_ref: str) -> Course:
    try:
        UUID(course_ref)
        query = select(Course).where(Course.id == course_ref)
    except ValueError:
        query = select(Course).where(Course.slug == course_ref)
    result = await db.execute(query)
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


async def _get_enrollment(db: AsyncSession, course_id: str, user_id: str) -> CourseEnrollment | None:
    return await db.scalar(
        select(CourseEnrollment).where(
            CourseEnrollment.course_id == course_id,
            CourseEnrollment.user_id == user_id,
        )
    )


async def _completed_lesson_ids(db: AsyncSession, course_id: str, user: User | None) -> set[str]:
    if not user:
        return set()
    result = await db.execute(
        select(CourseLessonProgress.lesson_id).where(
            CourseLessonProgress.course_id == course_id,
            CourseLessonProgress.user_id == user.id,
        )
    )
    return set(result.scalars().all())


async def _learning_profile_tags(db: AsyncSession, user: User | None) -> tuple[dict[str, int], set[str]]:
    if not user:
        return {}, set()

    rows = (
        await db.execute(
            select(UserProblemHistory, Problem)
            .join(Problem, Problem.id == UserProblemHistory.problem_id)
            .where(UserProblemHistory.user_id == user.id)
        )
    ).all()

    weak_tags: dict[str, int] = {}
    solved_tags: set[str] = set()
    for history, problem in rows:
        tags = set(problem.tags or [])
        if problem.concept_group:
            tags.add(problem.concept_group)
        if history.solved_count > 0:
            solved_tags.update(tags)
        if history.failed_count > 0:
            weight = 3 if history.solved_count == 0 else 1
            for tag in tags:
                weak_tags[tag] = weak_tags.get(tag, 0) + weight + min(history.failed_count, 3)
    return weak_tags, solved_tags


def _score_course_recommendation(
    course: Course,
    weak_tags: dict[str, int],
    solved_tags: set[str],
    authenticated: bool,
) -> tuple[int, str]:
    course_tags = set(course.tags or [])
    score = 0

    if course.access_type == "free":
        score += 3
    if course.level == "beginner":
        score += 2
    if not authenticated:
        return score, "Start here before ranked learning history exists."

    matched_weak_tags = sorted(course_tags.intersection(weak_tags), key=lambda tag: (-weak_tags[tag], tag))
    matched_solved_tags = sorted(course_tags.intersection(solved_tags))
    score += sum(weak_tags[tag] for tag in matched_weak_tags)
    score += min(len(matched_solved_tags), 2)

    if matched_weak_tags:
        return score, f"Recommended because your recent attempts touch {', '.join(matched_weak_tags[:3])}."
    if matched_solved_tags:
        return score, f"Good next step after solved work in {', '.join(matched_solved_tags[:3])}."
    if course.access_type == "free":
        return score, "Free course with a clean path into arena practice."
    return score, "Premium path reserved for deeper pattern training."


async def _course_out(db: AsyncSession, course: Course, user: User | None) -> CourseOut:
    lesson_count = await db.scalar(select(func.count(CourseLesson.id)).where(CourseLesson.course_id == course.id))
    enrollment = None
    if user:
        enrollment = await _get_enrollment(db, course.id, user.id)
    return CourseOut(
        id=course.id,
        slug=course.slug,
        title=course.title,
        summary=course.summary,
        level=course.level,
        access_type=course.access_type,
        price_cents=course.price_cents,
        currency=course.currency,
        status=course.status,
        tags=course.tags,
        lesson_count=int(lesson_count or 0),
        enrolled=bool(enrollment),
        progress_percent=enrollment.progress_percent if enrollment else 0,
    )
