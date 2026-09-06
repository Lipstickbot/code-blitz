import sys
import unittest
from pathlib import Path
from types import SimpleNamespace


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.services.env_validation import InvalidProductionConfig, assert_valid_startup_config, production_config_errors  # noqa: E402


def make_settings(**overrides):
    values = {
        "environment": "development",
        "jwt_secret": "change-me-in-production",
        "auto_create_tables": True,
        "run_test_limit": 5,
        "submit_test_limit": 50,
        "min_judge_timeout_seconds": 1,
        "max_judge_timeout_seconds": 5,
        "node_binary": "node",
        "judge_executor": "local",
        "judge_docker_binary": "docker",
        "judge_python_image": "python:3.12-alpine",
        "judge_node_image": "node:22-alpine",
        "rate_limiter_backend": "auto",
        "redis_url": "redis://localhost:6379/0",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class EnvironmentValidationTests(unittest.TestCase):
    def test_development_allows_local_defaults(self):
        errors = production_config_errors(make_settings())

        self.assertEqual(errors, [])

    def test_production_rejects_unsafe_defaults(self):
        settings = make_settings(environment="production")

        errors = production_config_errors(settings)

        self.assertIn("JWT_SECRET must be changed and contain at least 32 characters", errors)
        self.assertIn("AUTO_CREATE_TABLES must be false in production; use Alembic migrations instead", errors)
        self.assertIn("JUDGE_EXECUTOR must be docker in production/staging", errors)
        self.assertIn("RATE_LIMITER_BACKEND must be redis in production/staging", errors)

    def test_staging_uses_production_safety_rules(self):
        settings = make_settings(environment="staging")

        errors = production_config_errors(settings)

        self.assertIn("JWT_SECRET must be changed and contain at least 32 characters", errors)
        self.assertIn("JUDGE_EXECUTOR must be docker in production/staging", errors)

    def test_production_accepts_safe_minimum_config(self):
        settings = make_settings(
            environment="production",
            jwt_secret="a-real-production-secret-with-32-chars",
            auto_create_tables=False,
            judge_executor="docker",
            rate_limiter_backend="redis",
            redis_url="redis://redis.prod.local:6379/0",
        )

        assert_valid_startup_config(settings)

    def test_production_raises_one_clear_error_message(self):
        settings = make_settings(environment="production", node_binary="")

        with self.assertRaises(InvalidProductionConfig) as raised:
            assert_valid_startup_config(settings)

        self.assertIn("NODE_BINARY must not be empty", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
