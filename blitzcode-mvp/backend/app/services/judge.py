import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from app.config import settings
from app.models import TestCase
from app.services.judge_languages import executable_language_ids


@dataclass
class JudgeCaseResult:
    position: int
    status: str
    actual: Any = None
    expected: Any = None
    runtime_ms: int | None = None
    error_message: str | None = None
    test_case_id: str | None = None


@dataclass
class JudgeResult:
    status: str
    passed_count: int
    total_count: int
    runtime_ms: int
    case_results: list[JudgeCaseResult]
    error_message: str | None = None


def evaluate(code: str, language: str, test_cases: list[TestCase], timeout_seconds: float = 2.0) -> JudgeResult:
    normalized_language = language.lower()
    runtime = _runtime_for_language(normalized_language)
    if runtime is None:
        return JudgeResult(
            status="runtime_error",
            passed_count=0,
            total_count=len(test_cases),
            runtime_ms=0,
            case_results=[],
            error_message="JavaScript, TypeScript and Python judges are implemented in this backend step.",
        )

    payload = {
        "code": _prepare_code_for_language(code, normalized_language),
        "cases": [_serialize_case(test_case) for test_case in test_cases],
    }
    started = time.perf_counter()
    docker_container_name: str | None = None

    if _use_docker_executor():
        command, docker_container_name = _docker_command(runtime)
        missing_runtime_message = f"Docker judge runtime is required. Checked binary: {_setting('judge_docker_binary', 'docker')}"
    else:
        command = runtime.local_command
        missing_runtime_message = runtime.missing_runtime_message

    try:
        completed = subprocess.run(
            command,
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        _cleanup_docker_container(docker_container_name)
        runtime_ms = int((time.perf_counter() - started) * 1000)
        return JudgeResult(
            status="time_limit",
            passed_count=0,
            total_count=len(test_cases),
            runtime_ms=runtime_ms,
            case_results=[
                JudgeCaseResult(
                    position=test_case.position,
                    status="time_limit",
                    expected=_expected_value(test_case),
                    runtime_ms=runtime_ms,
                    test_case_id=test_case.id,
                )
                for test_case in test_cases
            ],
            error_message="Time limit exceeded.",
        )
    except FileNotFoundError:
        _cleanup_docker_container(docker_container_name)
        return JudgeResult(
            status="runtime_error",
            passed_count=0,
            total_count=len(test_cases),
            runtime_ms=0,
            case_results=[],
            error_message=missing_runtime_message,
        )

    _cleanup_docker_container(docker_container_name)
    runtime_ms = int((time.perf_counter() - started) * 1000)
    if completed.returncode != 0:
        return JudgeResult(
            status="runtime_error",
            passed_count=0,
            total_count=len(test_cases),
            runtime_ms=runtime_ms,
            case_results=[],
            error_message=completed.stderr.strip() or completed.stdout.strip() or "Judge process failed.",
        )

    try:
        output = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return JudgeResult(
            status="runtime_error",
            passed_count=0,
            total_count=len(test_cases),
            runtime_ms=runtime_ms,
            case_results=[],
            error_message="Judge returned invalid JSON.",
        )

    if output.get("compile_error"):
        return JudgeResult(
            status="compile_error",
            passed_count=0,
            total_count=len(test_cases),
            runtime_ms=runtime_ms,
            case_results=[],
            error_message=output["compile_error"],
        )

    case_results = [
        JudgeCaseResult(
            position=item["position"],
            status="accepted" if item["passed"] else item.get("status", "wrong_answer"),
            actual=item.get("actual"),
            expected=item.get("expected"),
            runtime_ms=item.get("runtime_ms"),
            error_message=item.get("error_message"),
            test_case_id=item.get("test_case_id"),
        )
        for item in output.get("cases", [])
    ]
    passed_count = sum(1 for item in case_results if item.status == "accepted")
    total_count = len(test_cases)
    status = "accepted" if total_count > 0 and passed_count == total_count else "wrong_answer"
    if any(item.status == "runtime_error" for item in case_results):
        status = "runtime_error"

    return JudgeResult(
        status=status,
        passed_count=passed_count,
        total_count=total_count,
        runtime_ms=runtime_ms,
        case_results=case_results,
    )


def _serialize_case(test_case: TestCase) -> dict[str, Any]:
    return {
        "id": test_case.id,
        "position": test_case.position,
        "args": _input_args(test_case),
        "expected": _expected_value(test_case),
    }


def _input_args(test_case: TestCase) -> list[Any]:
    if test_case.input_json is not None:
        return test_case.input_json if isinstance(test_case.input_json, list) else [test_case.input_json]
    return json.loads(f"[{test_case.input}]")


def _expected_value(test_case: TestCase) -> Any:
    if test_case.expected_json is not None:
        return test_case.expected_json
    return json.loads(test_case.expected_output)


@dataclass(frozen=True)
class JudgeRuntime:
    local_command: list[str]
    docker_image: str
    docker_command: list[str]
    missing_runtime_message: str


def _runtime_for_language(language: str) -> JudgeRuntime | None:
    if language not in executable_language_ids() and language not in {"js", "ts", "py", "python3"}:
        return None
    if language in {"javascript", "js", "typescript", "ts"}:
        return JudgeRuntime(
            local_command=[_setting("node_binary", "node"), "-e", JS_RUNNER],
            docker_image=_setting("judge_node_image", "node:22-alpine"),
            docker_command=["node", "-e", JS_RUNNER],
            missing_runtime_message=f"Node.js is required for JavaScript judging. Checked binary: {_setting('node_binary', 'node')}",
        )
    if language in {"python", "py", "python3"}:
        return JudgeRuntime(
            local_command=[sys.executable, "-c", PYTHON_RUNNER],
            docker_image=_setting("judge_python_image", "python:3.12-alpine"),
            docker_command=["python", "-c", PYTHON_RUNNER],
            missing_runtime_message="Python is required for Python judging.",
        )
    return None


def _prepare_code_for_language(code: str, language: str) -> str:
    if language in {"typescript", "ts"}:
        return _strip_typescript_for_runner(code)
    return code


def _strip_typescript_for_runner(code: str) -> str:
    stripped = re.sub(r"^\s*interface\s+\w+\s*\{[^}]*\}\s*", "", code, flags=re.MULTILINE | re.DOTALL)
    stripped = re.sub(r"^\s*type\s+\w+\s*=\s*[^;]+;\s*", "", stripped, flags=re.MULTILINE)
    stripped = re.sub(r"\)\s*:\s*[A-Za-z_$][A-Za-z0-9_$<>\[\]\|&?,\s]*(?=\s*\{)", ")", stripped)
    stripped = re.sub(r"([,(]\s*[A-Za-z_$][A-Za-z0-9_$]*)\s*:\s*[A-Za-z_$][A-Za-z0-9_$<>\[\]\|&?,\s]*(?=\s*[,)=])", r"\1", stripped)
    stripped = re.sub(r"\b(const|let|var)\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*:\s*[A-Za-z_$][A-Za-z0-9_$<>\[\]\|&?,\s]*(?=\s*=)", r"\1 \2", stripped)
    stripped = re.sub(r"\s+as\s+[A-Za-z_$][A-Za-z0-9_$<>\[\]\|&?,\s]*", "", stripped)
    return stripped


def _use_docker_executor() -> bool:
    return _setting("judge_executor", "local").lower() == "docker"


def _docker_command(runtime: JudgeRuntime) -> tuple[list[str], str]:
    container_name = f"code-blitz-judge-{uuid4().hex}"
    command = [
        _setting("judge_docker_binary", "docker"),
        "run",
        "--rm",
        "-i",
        "--name",
        container_name,
        "--network",
        "none",
        "--memory",
        _setting("judge_docker_memory", "128m"),
        "--cpus",
        _setting("judge_docker_cpus", "0.5"),
        "--pids-limit",
        str(_setting("judge_docker_pids_limit", 128)),
        "--read-only",
        "--tmpfs",
        "/tmp:rw,noexec,nosuid,size=16m",
        runtime.docker_image,
        *runtime.docker_command,
    ]
    return command, container_name


def _cleanup_docker_container(container_name: str | None) -> None:
    if not container_name:
        return
    try:
        subprocess.run(
            [_setting("judge_docker_binary", "docker"), "rm", "-f", container_name],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass


def _setting(name: str, default: Any) -> Any:
    return getattr(settings, name, default)


JS_RUNNER = r"""
const fs = require("fs");
const payload = JSON.parse(fs.readFileSync(0, "utf8"));

function deepEqual(a, b) {
  if (Object.is(a, b)) return true;
  if (Array.isArray(a) || Array.isArray(b)) {
    if (!Array.isArray(a) || !Array.isArray(b) || a.length !== b.length) return false;
    for (let i = 0; i < a.length; i++) {
      if (!deepEqual(a[i], b[i])) return false;
    }
    return true;
  }
  if (a && b && typeof a === "object" && typeof b === "object") {
    const aKeys = Object.keys(a).sort();
    const bKeys = Object.keys(b).sort();
    if (!deepEqual(aKeys, bKeys)) return false;
    for (const key of aKeys) {
      if (!deepEqual(a[key], b[key])) return false;
    }
    return true;
  }
  return false;
}

let solve;
try {
  solve = Function('"use strict";\n' + payload.code + '\n; return typeof solve === "function" ? solve : null;')();
} catch (error) {
  console.log(JSON.stringify({ compile_error: error.message || String(error) }));
  process.exit(0);
}

if (typeof solve !== "function") {
  console.log(JSON.stringify({ compile_error: "Function solve(...) was not found." }));
  process.exit(0);
}

const results = [];
for (const testCase of payload.cases) {
  const started = Date.now();
  try {
    const args = JSON.parse(JSON.stringify(testCase.args));
    const actual = solve(...args);
    const passed = deepEqual(actual, testCase.expected);
    results.push({
      test_case_id: testCase.id,
      position: testCase.position,
      passed,
      status: passed ? "accepted" : "wrong_answer",
      actual,
      expected: testCase.expected,
      runtime_ms: Date.now() - started
    });
  } catch (error) {
    results.push({
      test_case_id: testCase.id,
      position: testCase.position,
      passed: false,
      status: "runtime_error",
      expected: testCase.expected,
      runtime_ms: Date.now() - started,
      error_message: error.message || String(error)
    });
  }
}

console.log(JSON.stringify({ cases: results }));
"""


PYTHON_RUNNER = r"""
import copy
import json
import sys
import time
import traceback

payload = json.loads(sys.stdin.read())

namespace = {}
try:
    exec(compile(payload["code"], "solution.py", "exec"), namespace)
except Exception as error:
    print(json.dumps({"compile_error": str(error)}))
    sys.exit(0)

solve = namespace.get("solve")
if not callable(solve):
    print(json.dumps({"compile_error": "Function solve(...) was not found."}))
    sys.exit(0)

results = []
for test_case in payload["cases"]:
    started = time.perf_counter()
    try:
        args = copy.deepcopy(test_case["args"])
        actual = solve(*args)
        passed = actual == test_case["expected"]
        results.append({
            "test_case_id": test_case["id"],
            "position": test_case["position"],
            "passed": passed,
            "status": "accepted" if passed else "wrong_answer",
            "actual": actual,
            "expected": test_case["expected"],
            "runtime_ms": int((time.perf_counter() - started) * 1000),
        })
    except Exception as error:
        results.append({
            "test_case_id": test_case["id"],
            "position": test_case["position"],
            "passed": False,
            "status": "runtime_error",
            "expected": test_case["expected"],
            "runtime_ms": int((time.perf_counter() - started) * 1000),
            "error_message": str(error),
        })

print(json.dumps({"cases": results}, ensure_ascii=False))
"""
