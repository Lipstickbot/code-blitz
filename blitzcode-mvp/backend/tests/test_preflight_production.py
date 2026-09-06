import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from scripts import preflight_production  # noqa: E402


class ProductionPreflightTests(unittest.TestCase):
    def test_load_env_reads_key_value_file(self):
        env = load_fake_env(
            "ENVIRONMENT=production\n"
            "JWT_SECRET='quoted-secret'\n"
            "AUTO_CREATE_TABLES=false\n"
        )

        self.assertEqual(env["ENVIRONMENT"], "production")
        self.assertEqual(env["JWT_SECRET"], "quoted-secret")
        self.assertEqual(env["AUTO_CREATE_TABLES"], "false")

    def test_main_passes_safe_minimum_config(self):
        with fake_env_file(
                "ENVIRONMENT=production\n"
                "DATABASE_URL=postgresql+asyncpg://user:password@db.prod.local:5432/app\n"
                "REDIS_URL=redis://redis.prod.local:6379/0\n"
                "RATE_LIMITER_BACKEND=redis\n"
                "JWT_SECRET=a-real-production-secret-with-32-chars\n"
                "AUTO_CREATE_TABLES=false\n"
                "JUDGE_EXECUTOR=docker\n"
                "JUDGE_DOCKER_BINARY=docker\n"
                "JUDGE_PYTHON_IMAGE=python:3.12-alpine\n"
                "JUDGE_NODE_IMAGE=node:22-alpine\n"
                f"NODE_BINARY={sys.executable}\n",
        ):
            with redirect_stdout(StringIO()):
                exit_code = preflight_production.main(["--env-file", "fake.env"])

        self.assertEqual(exit_code, 0)

    def test_main_fails_unsafe_config(self):
        with fake_env_file(
                "ENVIRONMENT=production\n"
                "DATABASE_URL=\n"
                "JWT_SECRET=change-me-in-production\n"
                "AUTO_CREATE_TABLES=true\n"
                "NODE_BINARY=definitely-missing-node\n",
        ):
            with redirect_stdout(StringIO()):
                exit_code = preflight_production.main(["--env-file", "fake.env"])

        self.assertEqual(exit_code, 1)

    def test_invalid_numeric_values_fail_cleanly(self):
        with fake_env_file(
                "ENVIRONMENT=production\n"
                "DATABASE_URL=postgresql+asyncpg://user:password@db.prod.local:5432/app\n"
                "REDIS_URL=redis://redis.prod.local:6379/0\n"
                "RATE_LIMITER_BACKEND=redis\n"
                "JWT_SECRET=a-real-production-secret-with-32-chars\n"
                "AUTO_CREATE_TABLES=false\n"
                "RUN_TEST_LIMIT=bad\n"
                "SUBMIT_TEST_LIMIT=bad\n"
                "MIN_JUDGE_TIMEOUT_SECONDS=bad\n"
                "MAX_JUDGE_TIMEOUT_SECONDS=bad\n"
                "JUDGE_EXECUTOR=docker\n"
                "JUDGE_DOCKER_BINARY=docker\n"
                "JUDGE_PYTHON_IMAGE=python:3.12-alpine\n"
                "JUDGE_NODE_IMAGE=node:22-alpine\n"
                f"NODE_BINARY={sys.executable}\n",
        ):
            with redirect_stdout(StringIO()):
                exit_code = preflight_production.main(["--env-file", "fake.env"])

        self.assertEqual(exit_code, 1)


def load_fake_env(content: str):
    with fake_env_file(content):
        return preflight_production.load_env(Path("fake.env"))


def fake_env_file(content: str):
    original_exists = Path.exists
    original_read_text = Path.read_text

    def exists(path: Path):
        if str(path) == "fake.env":
            return True
        return original_exists(path)

    def read_text(path: Path, *args, **kwargs):
        if str(path) == "fake.env":
            return content
        return original_read_text(path, *args, **kwargs)

    return patch.multiple(Path, exists=exists, read_text=read_text)


if __name__ == "__main__":
    unittest.main()
