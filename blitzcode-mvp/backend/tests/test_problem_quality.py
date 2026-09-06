import sys
import unittest
from pathlib import Path
from types import SimpleNamespace


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.services.problem_quality import ProblemQualityError, problem_quality_errors, validate_problem_quality  # noqa: E402


def test_case(sample=False, hidden=True):
    return SimpleNamespace(is_sample=sample, is_hidden=hidden)


def valid_problem(**overrides):
    values = {
        "status": "active",
        "difficulty": "easy",
        "title": "Two Sum",
        "description": "Return indices of two numbers that add up to target.",
        "statement": "Given an array of integers, return the indices of two numbers that add up to target.",
        "starter_code_js": "function solve(nums, target) {\n  return [];\n}",
        "estimated_seconds": 300,
        "speed_score": 8,
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
        "test_cases": [test_case(sample=True, hidden=False), test_case(hidden=True)],
    }
    values.update(overrides)
    return values


class ProblemQualityTests(unittest.TestCase):
    def test_active_problem_accepts_valid_payload(self):
        validate_problem_quality(**valid_problem())

    def test_draft_problem_can_exist_without_tests(self):
        errors = problem_quality_errors(**valid_problem(status="draft", test_cases=[]))

        self.assertEqual(errors, [])

    def test_active_problem_requires_sample_and_hidden_tests(self):
        errors = problem_quality_errors(**valid_problem(test_cases=[test_case(sample=True, hidden=False)]))

        self.assertIn("active problem must have at least one hidden test", errors)

    def test_rejects_unknown_status_and_difficulty(self):
        errors = problem_quality_errors(**valid_problem(status="published", difficulty="nightmare"))

        self.assertIn("status must be draft, active or archived", errors)
        self.assertIn("difficulty must be easy, medium or hard", errors)

    def test_rejects_bad_limits_and_missing_solve(self):
        errors = problem_quality_errors(
            **valid_problem(
                starter_code_js="function answer() { return null; }",
                estimated_seconds=10,
                speed_score=30,
                time_limit_ms=50,
                memory_limit_mb=8,
            )
        )

        self.assertIn("starter_code_js must define or mention solve(...)", errors)
        self.assertIn("estimated_seconds must be between 30 and 3600", errors)
        self.assertIn("speed_score must be between 1 and 20", errors)
        self.assertIn("time_limit_ms must be between 100 and 10000", errors)
        self.assertIn("memory_limit_mb must be between 16 and 1024", errors)

    def test_validate_raises_combined_error(self):
        with self.assertRaises(ProblemQualityError) as raised:
            validate_problem_quality(**valid_problem(status="active", test_cases=[]))

        self.assertIn("active problem must have test cases", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
