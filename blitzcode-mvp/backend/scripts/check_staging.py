import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from preflight_production import load_env, make_settings, production_config_errors, required_value_errors


BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parents[1]

REQUIRED_FILES = [
    BACKEND_ROOT / "Dockerfile",
    BACKEND_ROOT / "docker-compose.staging.yml",
    BACKEND_ROOT / "Caddyfile.staging",
    BACKEND_ROOT / "scripts" / "deploy_staging.sh",
    REPO_ROOT / "index.html",
    REPO_ROOT / "app.js",
    REPO_ROOT / "styles.css",
    REPO_ROOT / "config.js",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check whether the staging deployment target is configured.")
    parser.add_argument("--env-file", default=".env.staging", help="Staging env file to validate.")
    parser.add_argument("--with-docker", action="store_true", help="Also run docker compose config validation.")
    args = parser.parse_args(argv)

    env_path = Path(args.env_file)
    env = load_env(env_path)
    settings = make_settings(env)

    errors = []
    errors.extend(required_file_errors())
    errors.extend(staging_env_errors(env_path, env))
    errors.extend(production_config_errors(settings))
    errors.extend(required_value_errors(settings))

    if args.with_docker:
        errors.extend(docker_errors(env_path))

    if errors:
        print("Staging readiness failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Staging readiness passed.")
    print(f"- domain: {env['STAGING_DOMAIN']}")
    print("- reverse proxy: Caddy")
    print("- rate limiter: Redis")
    print("- judge executor: Docker")
    return 0


def required_file_errors() -> list[str]:
    return [f"Required file is missing: {path}" for path in REQUIRED_FILES if not path.exists()]


def staging_env_errors(env_path: Path, env: dict[str, str]) -> list[str]:
    errors: list[str] = []
    if not env_path.exists():
        errors.append(f"Env file is missing: {env_path}")

    domain = env.get("STAGING_DOMAIN", "").strip()
    if not domain:
        errors.append("STAGING_DOMAIN must not be empty")
    elif domain == "staging.example.com" or "example.com" in domain:
        errors.append("STAGING_DOMAIN must be changed to a real staging domain")

    acme_email = env.get("ACME_EMAIL", "").strip()
    if not acme_email or "@" not in acme_email:
        errors.append("ACME_EMAIL must be a valid email")
    elif acme_email == "admin@example.com" or "example.com" in acme_email:
        errors.append("ACME_EMAIL must be changed to a real email")

    postgres_password = env.get("POSTGRES_PASSWORD", "").strip()
    if not postgres_password:
        errors.append("POSTGRES_PASSWORD must not be empty")
    elif postgres_password.startswith("replace-") or len(postgres_password) < 16:
        errors.append("POSTGRES_PASSWORD must be changed and contain at least 16 characters")

    cors = env.get("CORS_ORIGINS", "").strip()
    if domain and cors:
        try:
            origins = json.loads(cors)
        except json.JSONDecodeError:
            errors.append("CORS_ORIGINS must be valid JSON, for example [\"https://staging.your-domain.com\"]")
        else:
            expected_origin = f"https://{domain}"
            if expected_origin not in origins:
                errors.append(f"CORS_ORIGINS must include {expected_origin}")

    return errors


def docker_errors(env_path: Path) -> list[str]:
    if not shutil.which("docker"):
        return ["docker binary was not found"]

    command = [
        "docker",
        "compose",
        "--env-file",
        str(env_path),
        "-f",
        "docker-compose.staging.yml",
        "config",
        "--quiet",
    ]
    compose_env = {**os.environ, "BLITZCODE_ENV_FILE": str(env_path)}
    completed = subprocess.run(command, cwd=BACKEND_ROOT, env=compose_env, capture_output=True, text=True, check=False)
    if completed.returncode == 0:
        return []
    message = completed.stderr.strip() or completed.stdout.strip() or "docker compose config failed"
    return [message]


if __name__ == "__main__":
    raise SystemExit(main())
