DEFAULT_JWT_SECRET = "change-me-in-production"
PRODUCTION_ENVIRONMENTS = {"prod", "production", "staging"}


class InvalidProductionConfig(RuntimeError):
    pass


def production_config_errors(settings) -> list[str]:
    errors: list[str] = []
    environment = str(getattr(settings, "environment", "development")).lower()
    if environment not in PRODUCTION_ENVIRONMENTS:
        return errors

    jwt_secret = str(getattr(settings, "jwt_secret", ""))
    if jwt_secret == DEFAULT_JWT_SECRET or jwt_secret.lower().startswith("replace-") or len(jwt_secret) < 32:
        errors.append("JWT_SECRET must be changed and contain at least 32 characters")

    if bool(getattr(settings, "auto_create_tables", True)):
        errors.append("AUTO_CREATE_TABLES must be false in production; use Alembic migrations instead")

    if int(getattr(settings, "run_test_limit", 0)) <= 0:
        errors.append("RUN_TEST_LIMIT must be greater than 0")

    if int(getattr(settings, "submit_test_limit", 0)) <= 0:
        errors.append("SUBMIT_TEST_LIMIT must be greater than 0")

    if float(getattr(settings, "min_judge_timeout_seconds", 0)) <= 0:
        errors.append("MIN_JUDGE_TIMEOUT_SECONDS must be greater than 0")

    min_timeout = float(getattr(settings, "min_judge_timeout_seconds", 0))
    max_timeout = float(getattr(settings, "max_judge_timeout_seconds", 0))
    if max_timeout < min_timeout:
        errors.append("MAX_JUDGE_TIMEOUT_SECONDS must be greater than or equal to MIN_JUDGE_TIMEOUT_SECONDS")

    if not str(getattr(settings, "node_binary", "")).strip():
        errors.append("NODE_BINARY must not be empty")

    judge_executor = str(getattr(settings, "judge_executor", "")).lower()
    if judge_executor != "docker":
        errors.append("JUDGE_EXECUTOR must be docker in production/staging")

    if not str(getattr(settings, "judge_docker_binary", "")).strip():
        errors.append("JUDGE_DOCKER_BINARY must not be empty")

    if not str(getattr(settings, "judge_python_image", "")).strip():
        errors.append("JUDGE_PYTHON_IMAGE must not be empty")

    if not str(getattr(settings, "judge_node_image", "")).strip():
        errors.append("JUDGE_NODE_IMAGE must not be empty")

    rate_limiter_backend = str(getattr(settings, "rate_limiter_backend", "")).lower()
    if rate_limiter_backend != "redis":
        errors.append("RATE_LIMITER_BACKEND must be redis in production/staging")

    redis_url = str(getattr(settings, "redis_url", "")).strip()
    if not redis_url:
        errors.append("REDIS_URL must not be empty")
    elif "replace-" in redis_url.lower() or "example.com" in redis_url.lower():
        errors.append("REDIS_URL must point to a real Redis instance")

    return errors


def assert_valid_startup_config(settings) -> None:
    errors = production_config_errors(settings)
    if errors:
        raise InvalidProductionConfig("; ".join(errors))
