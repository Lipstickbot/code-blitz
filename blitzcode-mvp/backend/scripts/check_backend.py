import argparse
import py_compile
import subprocess
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run backend checks used by local development and CI.")
    parser.add_argument("--with-preflight", action="store_true", help="Also run production preflight with safe test values.")
    args = parser.parse_args(argv)

    commands = [
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
    ]
    for command in commands:
        print(f"$ {' '.join(command)}", flush=True)
        completed = subprocess.run(command, cwd=BACKEND_ROOT, check=False)
        if completed.returncode != 0:
            return completed.returncode
    if args.with_preflight:
        exit_code = run_preflight()
        if exit_code != 0:
            return exit_code
    return compile_python_files()


def compile_python_files() -> int:
    for path in python_files():
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as error:
            print(error.msg)
            return 1
    return 0


def run_preflight() -> int:
    env_file = BACKEND_ROOT / ".env.production.preflight"
    env_file.write_text(
        "\n".join(
            [
                "ENVIRONMENT=production",
                "DATABASE_URL=postgresql+asyncpg://user:password@db.prod.local:5432/blitzcode",
                "JWT_SECRET=a-real-production-secret-with-32-chars",
                "AUTO_CREATE_TABLES=false",
                "RUN_TEST_LIMIT=5",
                "SUBMIT_TEST_LIMIT=50",
                "MIN_JUDGE_TIMEOUT_SECONDS=1",
                "MAX_JUDGE_TIMEOUT_SECONDS=5",
                "JUDGE_EXECUTOR=docker",
                "JUDGE_DOCKER_BINARY=docker",
                "JUDGE_PYTHON_IMAGE=python:3.12-alpine",
                "JUDGE_NODE_IMAGE=node:22-alpine",
                f"NODE_BINARY={sys.executable}",
                "RATE_LIMITER_BACKEND=redis",
                "REDIS_URL=redis://redis.prod.local:6379/0",
                "",
            ]
        ),
        encoding="utf-8",
    )
    command = [sys.executable, "scripts/preflight_production.py", "--env-file", str(env_file)]
    try:
        print(f"$ {' '.join(command)}", flush=True)
        completed = subprocess.run(command, cwd=BACKEND_ROOT, check=False)
        return completed.returncode
    finally:
        env_file.unlink(missing_ok=True)


def python_files() -> list[Path]:
    roots = [BACKEND_ROOT / "app", BACKEND_ROOT / "scripts", BACKEND_ROOT / "migrations", BACKEND_ROOT / "tests"]
    files: list[Path] = []
    for root in roots:
        for path in root.rglob("*.py"):
            if "__pycache__" in path.parts or any(part.startswith("tmp") for part in path.parts):
                continue
            files.append(path)
    return sorted(files)


if __name__ == "__main__":
    raise SystemExit(main())
