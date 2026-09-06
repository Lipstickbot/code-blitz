from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://blitzcode:blitzcode@localhost:5432/blitzcode"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days
    auto_create_tables: bool = True
    max_submission_code_bytes: int = 64_000
    submission_rate_limit_count: int = 30
    submission_rate_limit_window_seconds: int = 60
    auth_rate_limit_count: int = 10
    auth_rate_limit_window_seconds: int = 60
    matchmaking_rate_limit_count: int = 40
    matchmaking_rate_limit_window_seconds: int = 60
    rate_limiter_backend: str = "auto"
    redis_url: str = "redis://localhost:6379/0"
    redis_socket_timeout_seconds: float = 0.35
    min_judge_timeout_seconds: float = 1.0
    max_judge_timeout_seconds: float = 5.0
    judge_executor: str = "local"
    judge_docker_binary: str = "docker"
    judge_python_image: str = "python:3.12-alpine"
    judge_node_image: str = "node:22-alpine"
    judge_docker_memory: str = "128m"
    judge_docker_cpus: str = "0.5"
    judge_docker_pids_limit: int = 128
    run_test_limit: int = 5
    submit_test_limit: int = 50
    node_binary: str = "node"
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:51337",
        "http://127.0.0.1:51337",
    ]
    cors_origin_regex: str = r"https?://(localhost|127\.0\.0\.1):\d+"

    class Config:
        env_file = ".env"


settings = Settings()
