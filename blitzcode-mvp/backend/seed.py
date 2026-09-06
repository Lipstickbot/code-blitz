"""
Seed the backend database from the shared Code Blitz problem bank.

Run from `blitzcode-mvp/backend`:
  python seed.py
"""
import asyncio
import json
from pathlib import Path

from sqlalchemy import select

from app.database import AsyncSessionLocal, Base, engine
from app.models import Course, CourseLesson, CoursePracticeProblem, Problem, TestCase


ROOT = Path(__file__).resolve().parents[2]
SEED_FILE = ROOT / "db" / "seed_problems.json"
COURSE_SEED_FILE = ROOT / "db" / "seed_courses.json"


def format_case_value(value) -> str:
    return json.dumps(value, ensure_ascii=False)


def make_slug(title: str) -> str:
    return (
        title.lower()
        .replace(" ", "-")
        .replace("/", "-")
        .replace("_", "-")
    )


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    problems = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    courses = json.loads(COURSE_SEED_FILE.read_text(encoding="utf-8"))

    async with AsyncSessionLocal() as db:
        inserted = 0
        for item in problems:
            slug = item.get("slug") or make_slug(item["title"])
            existing = await db.execute(select(Problem).where(Problem.slug == slug))
            if existing.scalar_one_or_none():
                continue

            problem = Problem(
                slug=slug,
                title=item["title"],
                description=item["statement"],
                statement=item["statement"],
                difficulty=item["difficulty"],
                status="active",
                concept_group=item.get("concept_group", "general"),
                tags=item.get("tags", []),
                starter_code_js=item.get("starter_code_js", "function solve() {\n  return null;\n}"),
                estimated_seconds=item.get("estimated_seconds", 300),
                speed_score=item.get("speed_score", 5),
                time_limit_ms=2000,
                memory_limit_mb=256,
            )
            problem.test_cases = [
                TestCase(
                    position=index + 1,
                    input=format_case_value(case["input"]),
                    expected_output=format_case_value(case["expected"]),
                    input_json=case["input"],
                    expected_json=case["expected"],
                    is_sample=not case.get("hidden", False),
                    is_hidden=case.get("hidden", False),
                )
                for index, case in enumerate(item.get("cases", []))
            ]
            db.add(problem)
            inserted += 1

        seed_course_slugs = {item["slug"] for item in courses}
        archived_courses = 0
        existing_courses = (await db.execute(select(Course))).scalars().all()
        for existing_course in existing_courses:
            if existing_course.slug not in seed_course_slugs and existing_course.status != "archived":
                existing_course.status = "archived"
                archived_courses += 1

        inserted_courses = 0
        inserted_practice_links = 0
        for item in courses:
            existing = await db.execute(select(Course).where(Course.slug == item["slug"]))
            course = existing.scalar_one_or_none()
            lessons = item.get("lessons", [])
            if course:
                course.title = item["title"]
                course.summary = item["summary"]
                course.level = item.get("level", "beginner")
                course.access_type = item.get("access_type", "free")
                course.price_cents = item.get("price_cents", 0)
                course.currency = item.get("currency", "USD")
                course.status = item.get("status", "published")
                course.tags = item.get("tags", [])
            else:
                course = Course(
                    slug=item["slug"],
                    title=item["title"],
                    summary=item["summary"],
                    level=item.get("level", "beginner"),
                    access_type=item.get("access_type", "free"),
                    price_cents=item.get("price_cents", 0),
                    currency=item.get("currency", "USD"),
                    status=item.get("status", "published"),
                    tags=item.get("tags", []),
                )
                db.add(course)
                inserted_courses += 1
            await db.flush()
            existing_lessons = {
                lesson.position: lesson
                for lesson in (
                    await db.execute(select(CourseLesson).where(CourseLesson.course_id == course.id))
                ).scalars().all()
            }
            for lesson in lessons:
                course_lesson = existing_lessons.get(lesson["position"])
                if not course_lesson:
                    course_lesson = CourseLesson(course_id=course.id, position=lesson["position"])
                    db.add(course_lesson)
                course_lesson.title = lesson["title"]
                course_lesson.summary = lesson.get("summary", "")
                course_lesson.content = lesson.get("content", "")
                course_lesson.checklist = lesson.get("checklist", [])
                course_lesson.kind = lesson.get("kind", "lesson")
                course_lesson.duration_minutes = lesson.get("duration_minutes", 10)
                course_lesson.is_preview = lesson.get("is_preview", item.get("access_type") == "free")
            for position, problem_slug in enumerate(item.get("practice_slugs", []), start=1):
                problem = await db.scalar(select(Problem).where(Problem.slug == problem_slug))
                existing_link = None
                if problem:
                    existing_link = await db.scalar(
                        select(CoursePracticeProblem).where(
                            CoursePracticeProblem.course_id == course.id,
                            CoursePracticeProblem.problem_id == problem.id,
                        )
                    )
                if problem and not existing_link:
                    db.add(
                        CoursePracticeProblem(
                            course_id=course.id,
                            problem_id=problem.id,
                            position=position,
                        )
                    )
                    inserted_practice_links += 1

        await db.commit()

    print(f"Seeded {inserted} new problems from {SEED_FILE}.")
    print(f"Seeded {inserted_courses} new courses from {COURSE_SEED_FILE}.")
    print(f"Archived {archived_courses} courses missing from the current seed.")
    print(f"Seeded {inserted_practice_links} new course practice links.")


if __name__ == "__main__":
    asyncio.run(seed())
