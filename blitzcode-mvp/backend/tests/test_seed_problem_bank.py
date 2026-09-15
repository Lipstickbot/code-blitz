import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SEED_FILE = ROOT / "db" / "seed_problems.json"


class SeedProblemBankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.problems = json.loads(SEED_FILE.read_text(encoding="utf-8"))

    def test_problem_bank_has_expected_size_and_unique_slugs(self):
        slugs = [problem["slug"] for problem in self.problems]

        self.assertGreaterEqual(len(self.problems), 100)
        self.assertEqual(len(slugs), len(set(slugs)))

    def test_each_difficulty_has_enough_match_choices(self):
        counts = Counter(problem["difficulty"] for problem in self.problems)

        self.assertGreaterEqual(counts["easy"], 30)
        self.assertGreaterEqual(counts["medium"], 25)
        self.assertGreaterEqual(counts["hard"], 20)

    def test_each_problem_has_sample_and_hidden_cases(self):
        missing = []
        for problem in self.problems:
            cases = problem.get("cases", [])
            has_sample = any(not case.get("hidden", False) for case in cases)
            has_hidden = any(case.get("hidden", False) for case in cases)
            if not has_sample or not has_hidden:
                missing.append(problem["slug"])

        self.assertEqual(missing, [])

    def test_each_problem_has_required_seed_shape(self):
        allowed_difficulties = {"easy", "medium", "hard"}
        broken = []
        for problem in self.problems:
            cases = problem.get("cases", [])
            if (
                not problem.get("slug")
                or not problem.get("title")
                or problem.get("difficulty") not in allowed_difficulties
                or not problem.get("statement")
                or not problem.get("tags")
                or not problem.get("concept_group")
                or not isinstance(problem.get("estimated_seconds"), int)
                or not isinstance(problem.get("speed_score"), int)
                or not problem.get("starter_code_js", "").startswith("function solve")
                or len(cases) < 5
                or any("input" not in case or "expected" not in case for case in cases)
            ):
                broken.append(problem.get("slug", "<missing slug>"))

        self.assertEqual(broken, [])


if __name__ == "__main__":
    unittest.main()
