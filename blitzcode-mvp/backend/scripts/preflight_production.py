import argparse
import os
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.services.env_validation import production_config_errors  # noqa: E402


DEFAULTS = {
    "ENVIRONMENT": "development",
    "DATABASE_URL": "",
    "JWT_SECRET": "",
    "AUTO_CREATE_TABLES": "true",
    "RUN_TEST_LIMIT": "5",
    "SUBMIT_TEST_LIMIT": "50",
    "MIN_JUDGE_TIMEOUT_SECONDS": "1",
    "MAX_JUDGE_TIMEOUT_SECONDS": "5",
    "NODE_BINARY": "node",
    "JUDGE_EXECUTOR": "docker",
    "JUDGE_DOCKER_BINARY": "docker",
    "JUDGE_PYTHON_IMAGE": "python:3.12-alpine",
    "JUDGE_NODE_IMAGE": "node:22-alpine",
    "RATE_LIMITER_BACKEND": "redis",
    "REDIS_URL": "",
    "REDIS_SOCKET_TIMEOUT_SECONDS": "0.35",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Code Blitz production settings before deploy.")
    parser.add_argument("--env-file", default=".env.production.example", help="Path to an env file to validate.")
    args = parser.parse_args(argv)

    env = load_env(Path(args.env_file))
    settings = make_settings(env)
    errors = production_config_errors(settings)
    errors.extend(runtime_errors(settings))
    errors.extend(required_value_errors(settings))

    if errors:
        print("Production preflight failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Production preflight passed.")
    print(f"- ENVIRONMENT={settings.environment}")
    print("- AUTO_CREATE_TABLES=false")
    print(f"- NODE_BINARY={settings.node_binary}")
    return 0


def load_env(path: Path) -> dict[str, str]:
    env = dict(DEFAULTS)
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            env[key.strip()] = value.strip().strip('"').strip("'")

    for key in DEFAULTS:
        if key in os.environ:
            env[key] = os.environ[key]
    return env


def make_settings(env: dict[str, str]) -> SimpleNamespace:
    return SimpleNamespace(
        environment=env["ENVIRONMENT"],
        database_url=env["DATABASE_URL"],
        jwt_secret=env["JWT_SECRET"],
        auto_create_tables=parse_bool(env["AUTO_CREATE_TABLES"]),
        run_test_limit=parse_int(env["RUN_TEST_LIMIT"]),
        submit_test_limit=parse_int(env["SUBMIT_TEST_LIMIT"]),
        min_judge_timeout_seconds=parse_float(env["MIN_JUDGE_TIMEOUT_SECONDS"]),
        max_judge_timeout_seconds=parse_float(env["MAX_JUDGE_TIMEOUT_SECONDS"]),
        node_binary=env["NODE_BINARY"],
        judge_executor=env["JUDGE_EXECUTOR"],
        judge_docker_binary=env["JUDGE_DOCKER_BINARY"],
        judge_python_image=env["JUDGE_PYTHON_IMAGE"],
        judge_node_image=env["JUDGE_NODE_IMAGE"],
        rate_limiter_backend=env["RATE_LIMITER_BACKEND"],
        redis_url=env["REDIS_URL"],
        redis_socket_timeout_seconds=parse_float(env["REDIS_SOCKET_TIMEOUT_SECONDS"]),
    )


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def parse_int(value: str) -> int:
    try:
        return int(value)
    except ValueError:
        return 0


def parse_float(value: str) -> float:
    try:
        return float(value)
    except ValueError:
        return 0


def runtime_errors(settings: SimpleNamespace) -> list[str]:
    if settings.judge_executor.lower() == "docker":
        if Path(settings.judge_docker_binary).exists() or shutil.which(settings.judge_docker_binary):
            return []
        return [f"JUDGE_DOCKER_BINARY was not found: {settings.judge_docker_binary}"]
    if Path(settings.node_binary).exists() or shutil.which(settings.node_binary):
        return []
    return [f"NODE_BINARY was not found: {settings.node_binary}"]


def required_value_errors(settings: SimpleNamespace) -> list[str]:
    errors: list[str] = []
    if not settings.database_url.strip():
        errors.append("DATABASE_URL must not be empty")
    elif "replace-" in settings.database_url.lower() or "example.com" in settings.database_url.lower():
        errors.append("DATABASE_URL must point to a real database")
    if settings.judge_executor.lower() != "docker":
        errors.append("JUDGE_EXECUTOR must be docker in production/staging")
    if not settings.judge_docker_binary.strip():
        errors.append("JUDGE_DOCKER_BINARY must not be empty")
    if not settings.judge_python_image.strip():
        errors.append("JUDGE_PYTHON_IMAGE must not be empty")
    if not settings.judge_node_image.strip():
        errors.append("JUDGE_NODE_IMAGE must not be empty")
    if settings.rate_limiter_backend.lower() != "redis":
        errors.append("RATE_LIMITER_BACKEND must be redis in production/staging")
    if not settings.redis_url.strip():
        errors.append("REDIS_URL must not be empty")
    elif "replace-" in settings.redis_url.lower() or "example.com" in settings.redis_url.lower():
        errors.append("REDIS_URL must point to a real Redis instance")
    return errors


if __name__ == "__main__":
    raise SystemExit(main())
