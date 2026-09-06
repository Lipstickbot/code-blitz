import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SEED_FILE = ROOT / "db" / "seed_courses.json"
PROBLEM_SEED_FILE = ROOT / "db" / "seed_problems.json"


class SeedCourseCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.courses = json.loads(SEED_FILE.read_text(encoding="utf-8"))
        cls.problem_slugs = {
            problem["slug"]
            for problem in json.loads(PROBLEM_SEED_FILE.read_text(encoding="utf-8"))
        }

    def test_course_catalog_has_single_free_intro_track(self):
        access_types = {course["access_type"] for course in self.courses}

        self.assertEqual(len(self.courses), 1)
        self.assertEqual(access_types, {"free"})
        self.assertEqual(self.courses[0]["price_cents"], 0)

    def test_course_slugs_are_unique(self):
        slugs = [course["slug"] for course in self.courses]

        self.assertEqual(len(slugs), len(set(slugs)))

    def test_each_course_has_required_shape_and_lessons(self):
        broken = []
        for course in self.courses:
            lessons = course.get("lessons", [])
            if (
                not course.get("slug")
                or not course.get("title")
                or course.get("access_type") not in {"free", "premium"}
                or course.get("level") not in {"beginner", "intermediate", "advanced"}
                or not isinstance(course.get("price_cents"), int)
                or course["price_cents"] < 0
                or len(lessons) < 3
                or len(course.get("practice_slugs", [])) < 3
                or [lesson.get("position") for lesson in lessons] != list(range(1, len(lessons) + 1))
                or any(not lesson.get("content") for lesson in lessons)
                or any(len(lesson.get("checklist", [])) < 3 for lesson in lessons)
            ):
                broken.append(course.get("slug", "<missing slug>"))

        self.assertEqual(broken, [])

    def test_practice_slugs_point_to_real_seed_problems(self):
        missing = []
        duplicated = []
        for course in self.courses:
            practice_slugs = course.get("practice_slugs", [])
            if len(practice_slugs) != len(set(practice_slugs)):
                duplicated.append(course["slug"])
            missing.extend(slug for slug in practice_slugs if slug not in self.problem_slugs)

        self.assertEqual(duplicated, [])
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
