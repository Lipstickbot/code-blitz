import unittest

from app.services.judge_languages import JUDGE_LANGUAGES, executable_language_ids


class JudgeLanguageMatrixTests(unittest.TestCase):
    def test_dynamic_languages_are_executable(self):
        self.assertEqual(executable_language_ids(), {"javascript", "typescript", "python"})

    def test_planned_compiled_languages_are_visible(self):
        planned = {item["id"] for item in JUDGE_LANGUAGES if item["status"] == "planned"}

        self.assertGreaterEqual(planned, {"cpp", "java", "go", "rust"})

    def test_language_ids_are_unique(self):
        ids = [item["id"] for item in JUDGE_LANGUAGES]

        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
