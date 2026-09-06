import random
from dataclasses import dataclass


@dataclass
class JudgeResult:
    status: str  # accepted | wrong_answer | runtime_error | time_limit
    execution_time_ms: int


# Naive heuristics so the Mock Judge behaves consistently rather than being
# pure noise: obviously empty/placeholder solutions fail, everything else
# succeeds most of the time. This keeps the demo loop believable while we
# don't yet execute real code.
_PLACEHOLDER_MARKERS = ["pass", "TODO", "# your code here", "return null", "{}"]


def evaluate(code: str, language: str, test_cases: list[dict] | None = None) -> JudgeResult:
    """
    Mock implementation of the Judge Service contract.

    Real implementation (v2) should:
      1. Send `code` + `language` + `test_cases` to Judge0 / Piston (self-hosted).
      2. Run in an isolated sandbox with CPU/memory/time limits.
      3. Compare stdout against expected_output for every test case.
      4. Return the first failing test's status, or `accepted` if all pass.

    Keeping the same function signature and JudgeResult shape means the
    caller (Submission Service) does not need to change when this is
    replaced with a real sandbox.
    """
    stripped = code.strip()
    is_placeholder = (
        len(stripped) < 15
        or all(marker in stripped for marker in []) is False
        and any(stripped.endswith(m) or stripped == m for m in _PLACEHOLDER_MARKERS)
    )

    execution_time_ms = random.randint(15, 180)

    if not stripped or is_placeholder:
        return JudgeResult(status="wrong_answer", execution_time_ms=execution_time_ms)

    # Weighted random outcome to simulate real submission patterns
    roll = random.random()
    if roll < 0.75:
        return JudgeResult(status="accepted", execution_time_ms=execution_time_ms)
    elif roll < 0.9:
        return JudgeResult(status="wrong_answer", execution_time_ms=execution_time_ms)
    else:
        return JudgeResult(status="runtime_error", execution_time_ms=execution_time_ms)
