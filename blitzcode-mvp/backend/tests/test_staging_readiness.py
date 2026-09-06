import sys
import unittest
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))
sys.path.insert(0, str(BACKEND_ROOT / "scripts"))

from scripts import check_staging  # noqa: E402


def staging_env(**overrides):
    values = {
        "STAGING_DOMAIN": "staging.codeblitz.test",
        "ACME_EMAIL": "admin@codeblitz.test",
        "POSTGRES_PASSWORD": "staging-password-32-characters",
        "CORS_ORIGINS": '["https://staging.codeblitz.test"]',
    }
    values.update(overrides)
    return values


class StagingReadinessTests(unittest.TestCase):
    def test_rejects_placeholder_domain_email_and_password(self):
        errors = check_staging.staging_env_errors(
            Path(".env.staging.example"),
            staging_env(
                STAGING_DOMAIN="staging.example.com",
                ACME_EMAIL="admin@example.com",
                POSTGRES_PASSWORD="replace-staging-db-password",
            ),
        )

        self.assertIn("STAGING_DOMAIN must be changed to a real staging domain", errors)
        self.assertIn("ACME_EMAIL must be changed to a real email", errors)
        self.assertIn("POSTGRES_PASSWORD must be changed and contain at least 16 characters", errors)

    def test_accepts_matching_cors_origin(self):
        errors = check_staging.staging_env_errors(Path(".env.staging.example"), staging_env())

        self.assertEqual(errors, [])

    def test_rejects_cors_without_staging_origin(self):
        errors = check_staging.staging_env_errors(
            Path(".env.staging.example"),
            staging_env(CORS_ORIGINS='["https://other.codeblitz.test"]'),
        )

        self.assertIn("CORS_ORIGINS must include https://staging.codeblitz.test", errors)


if __name__ == "__main__":
    unittest.main()
