import unittest

try:
    from app.routers.admin import _acceptance_rate, _calibration_recommendation
    BACKEND_DEPS_READY = True
except Exception as error:
    BACKEND_DEPS_READY = False
    BACKEND_DEPS_ERROR = error


@unittest.skipUnless(BACKEND_DEPS_READY, "Backend dependencies are not available.")
class ProblemCalibrationTests(unittest.TestCase):
    def test_acceptance_rate_is_percentage(self):
        self.assertEqual(_acceptance_rate(4, 3), 75.0)
        self.assertEqual(_acceptance_rate(0, 0), 0.0)

    def test_easy_task_with_low_acceptance_needs_review(self):
        recommendation = _calibration_recommendation("easy", 30, 6)

        self.assertIn("too hard", recommendation)

    def test_hard_task_with_high_acceptance_needs_review(self):
        recommendation = _calibration_recommendation("hard", 30, 24)

        self.assertIn("too easy", recommendation)

    def test_small_sample_needs_more_data(self):
        recommendation = _calibration_recommendation("medium", 4, 4)

        self.assertEqual(recommendation, "need more data")


if __name__ == "__main__":
    unittest.main()
