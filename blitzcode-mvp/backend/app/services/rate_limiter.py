from collections import defaultdict, deque
from dataclasses import dataclass
from time import monotonic, time
from uuid import uuid4

from app.config import settings

try:
    from redis import Redis
    from redis.exceptions import RedisError
except ImportError:  # pragma: no cover - optional dependency guard
    Redis = None
    RedisError = Exception


@dataclass
class RateLimitResult:
    allowed: bool
    retry_after_seconds: int = 0
    backend: str = "memory"


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str, limit: int, window_seconds: int) -> RateLimitResult:
        now = monotonic()
        window_start = now - window_seconds
        hits = self._hits[key]

        while hits and hits[0] <= window_start:
            hits.popleft()

        if len(hits) >= limit:
            retry_after = max(1, int(hits[0] + window_seconds - now))
            return RateLimitResult(allowed=False, retry_after_seconds=retry_after, backend="memory")

        hits.append(now)
        return RateLimitResult(allowed=True, backend="memory")


class RedisRateLimiter:
    def __init__(self, prefix: str = "rate") -> None:
        if Redis is None:
            raise RuntimeError("redis package is not installed")
        self.prefix = prefix
        self.client = Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=settings.redis_socket_timeout_seconds,
            socket_timeout=settings.redis_socket_timeout_seconds,
        )

    def check(self, key: str, limit: int, window_seconds: int) -> RateLimitResult:
        now = time()
        window_start = now - window_seconds
        redis_key = f"{self.prefix}:{key}"
        member = f"{now:.6f}:{uuid4().hex}"

        pipe = self.client.pipeline()
        pipe.zremrangebyscore(redis_key, 0, window_start)
        pipe.zcard(redis_key)
        pipe.zrange(redis_key, 0, 0, withscores=True)
        _, count, oldest = pipe.execute()

        if int(count) >= limit:
            oldest_score = float(oldest[0][1]) if oldest else now
            retry_after = max(1, int(oldest_score + window_seconds - now))
            return RateLimitResult(allowed=False, retry_after_seconds=retry_after, backend="redis")

        pipe = self.client.pipeline()
        pipe.zadd(redis_key, {member: now})
        pipe.expire(redis_key, window_seconds + 5)
        pipe.execute()
        return RateLimitResult(allowed=True, backend="redis")

    def ping(self) -> bool:
        return bool(self.client.ping())


class ResilientRateLimiter:
    def __init__(self, name: str) -> None:
        self.name = name
        self.memory = InMemoryRateLimiter()
        self.redis: RedisRateLimiter | None = None
        self._redis_disabled = False

    def check(self, key: str, limit: int, window_seconds: int) -> RateLimitResult:
        if self._should_use_redis():
            try:
                return self._redis().check(f"{self.name}:{key}", limit, window_seconds)
            except RedisError:
                if self._redis_required():
                    raise
                self._redis_disabled = True

        return self.memory.check(f"{self.name}:{key}", limit, window_seconds)

    def health(self) -> dict:
        if not self._should_use_redis():
            return {"backend": "memory", "ok": True}
        try:
            return {"backend": "redis", "ok": self._redis().ping()}
        except Exception as error:  # pragma: no cover - defensive readiness path
            if not self._redis_required():
                self._redis_disabled = True
                return {
                    "backend": "memory",
                    "ok": True,
                    "fallback_reason": error.__class__.__name__,
                }
            return {"backend": "redis", "ok": False, "error": error.__class__.__name__}

    def _redis(self) -> RedisRateLimiter:
        if self.redis is None:
            self.redis = RedisRateLimiter()
        return self.redis

    def _redis_required(self) -> bool:
        return settings.rate_limiter_backend.lower() == "redis"

    def _should_use_redis(self) -> bool:
        backend = settings.rate_limiter_backend.lower()
        if backend == "memory":
            return False
        if self._redis_disabled and backend == "auto":
            return False
        return backend in {"auto", "redis"}


def rate_limiter_health() -> dict:
    checks = {
        "auth": auth_rate_limiter.health(),
        "submissions": submission_rate_limiter.health(),
        "matchmaking": matchmaking_rate_limiter.health(),
    }
    return {
        "ok": all(item["ok"] for item in checks.values()),
        "limiters": checks,
    }


submission_rate_limiter = ResilientRateLimiter("submissions")
auth_rate_limiter = ResilientRateLimiter("auth")
matchmaking_rate_limiter = ResilientRateLimiter("matchmaking")
