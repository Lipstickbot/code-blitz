import unittest

try:
    from app.models import Problem
    from app.services.anti_cheat import (
        build_speed_signal,
        code_fingerprint,
        normalize_code_for_similarity,
        suspicious_speed_threshold_seconds,
    )
    BACKEND_DEPS_READY = True
except Exception as error:
    BACKEND_DEPS_READY = False
    BACKEND_DEPS_ERROR = error


@unittest.skipUnless(BACKEND_DEPS_READY, "Backend dependencies are not available.")
class AntiCheatTests(unittest.TestCase):
    def test_code_fingerprint_ignores_whitespace_and_comments(self):
        first = "function solve(nums) {\n  // scan values\n  return nums.length;\n}"
        second = "function solve(nums){return nums.length;}"

        self.assertEqual(normalize_code_for_similarity(first), normalize_code_for_similarity(second))
        self.assertEqual(code_fingerprint(first), code_fingerprint(second))

    def test_speed_threshold_uses_difficulty_floor(self):
        problem = Problem(title="Fast", description="x", difficulty="hard", estimated_seconds=200)

        self.assertEqual(suspicious_speed_threshold_seconds(problem), 90)

    def test_fast_accept_builds_signal(self):
        problem = Problem(title="Fast", description="x", difficulty="medium", estimated_seconds=600)

        signal = build_speed_signal(problem, accepted_after_seconds=10)

        self.assertIsNotNone(signal)
        self.assertEqual(signal.signal_type, "very_fast_accept")
        self.assertEqual(signal.severity, "high")

    def test_normal_accept_does_not_build_signal(self):
        problem = Problem(title="Normal", description="x", difficulty="easy", estimated_seconds=120)

        self.assertIsNone(build_speed_signal(problem, accepted_after_seconds=60))


if __name__ == "__main__":
    unittest.main()
