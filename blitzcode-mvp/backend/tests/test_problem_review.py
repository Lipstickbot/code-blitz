import sys
import unittest
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.services.problem_review import ProblemReviewError, problem_review_errors, validate_problem_review  # noqa: E402


class ProblemReviewTests(unittest.TestCase):
    def test_approved_review_can_have_empty_notes(self):
        errors = problem_review_errors("approved", "", {"examples": True})

        self.assertEqual(errors, [])

    def test_needs_changes_requires_notes(self):
        errors = problem_review_errors("needs_changes", "")

        self.assertIn("needs_changes review must include notes", errors)

    def test_unknown_status_is_rejected(self):
        errors = problem_review_errors("done", "looks fine")

        self.assertIn("review status must be approved, needs_changes or comment", errors)

    def test_checklist_must_be_object(self):
        errors = problem_review_errors("comment", "note", ["not", "object"])

        self.assertIn("checklist must be an object", errors)

    def test_validate_raises_combined_error(self):
        with self.assertRaises(ProblemReviewError) as raised:
            validate_problem_review("needs_changes", "", ["not", "object"])

        message = str(raised.exception)
        self.assertIn("needs_changes review must include notes", message)
        self.assertIn("checklist must be an object", message)


if __name__ == "__main__":
    unittest.main()
