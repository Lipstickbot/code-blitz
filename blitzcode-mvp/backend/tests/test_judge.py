import sys
import types
import unittest
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

NODE_BINARY = Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies" / "node" / "bin" / "node.exe"

config_stub = types.ModuleType("app.config")
config_stub.settings = types.SimpleNamespace(
    node_binary=str(NODE_BINARY) if NODE_BINARY.exists() else "node",
    judge_executor="local",
    judge_docker_binary="docker",
    judge_python_image="python:3.12-alpine",
    judge_node_image="node:22-alpine",
    judge_docker_memory="128m",
    judge_docker_cpus="0.5",
    judge_docker_pids_limit=128,
)
sys.modules.setdefault("app.config", config_stub)

models_stub = types.ModuleType("app.models")


class TestCase:
    pass


models_stub.TestCase = TestCase
sys.modules.setdefault("app.models", models_stub)

from app.services import judge  # noqa: E402


def make_case(position, args, expected, hidden=True):
    test_case = TestCase()
    test_case.id = f"case-{position}"
    test_case.position = position
    test_case.input = ""
    test_case.expected_output = ""
    test_case.input_json = args
    test_case.expected_json = expected
    test_case.is_sample = not hidden
    test_case.is_hidden = hidden
    return test_case


class PythonJudgeTests(unittest.TestCase):
    def test_python_solution_accepts_many_cases(self):
        cases = [make_case(index + 1, [index], index + 1) for index in range(50)]

        result = judge.evaluate(
            "def solve(value):\n    return value + 1\n",
            "python",
            cases,
            timeout_seconds=2,
        )

        self.assertEqual(result.status, "accepted")
        self.assertEqual(result.passed_count, 50)
        self.assertEqual(result.total_count, 50)
        self.assertEqual(len(result.case_results), 50)

    def test_python_wrong_answer_keeps_expected_and_actual(self):
        result = judge.evaluate(
            "def solve(value):\n    return value\n",
            "python",
            [make_case(1, [4], 5)],
            timeout_seconds=2,
        )

        self.assertEqual(result.status, "wrong_answer")
        self.assertEqual(result.passed_count, 0)
        self.assertEqual(result.case_results[0].actual, 4)
        self.assertEqual(result.case_results[0].expected, 5)

    def test_python_runtime_error_is_reported_per_case(self):
        result = judge.evaluate(
            "def solve(value):\n    return value / 0\n",
            "python",
            [make_case(1, [4], 5)],
            timeout_seconds=2,
        )

        self.assertEqual(result.status, "runtime_error")
        self.assertEqual(result.case_results[0].status, "runtime_error")
        self.assertIn("division by zero", result.case_results[0].error_message)

    def test_missing_solve_is_compile_error(self):
        result = judge.evaluate(
            "def helper(value):\n    return value\n",
            "python",
            [make_case(1, [4], 5)],
            timeout_seconds=2,
        )

        self.assertEqual(result.status, "compile_error")
        self.assertIn("solve", result.error_message)

    def test_docker_command_is_isolated(self):
        runtime = judge._runtime_for_language("python")
        command, container_name = judge._docker_command(runtime)

        self.assertTrue(container_name.startswith("code-blitz-judge-"))
        self.assertIn("--network", command)
        self.assertIn("none", command)
        self.assertIn("--memory", command)
        self.assertIn("128m", command)
        self.assertIn("--cpus", command)
        self.assertIn("0.5", command)
        self.assertIn("--pids-limit", command)
        self.assertIn("128", command)
        self.assertIn("--read-only", command)
        self.assertIn("python:3.12-alpine", command)


@unittest.skipUnless(NODE_BINARY.exists(), "Bundled Node.js runtime is not available")
class JavaScriptJudgeTests(unittest.TestCase):
    def test_javascript_solution_accepts_many_cases(self):
        cases = [make_case(index + 1, [[index, index + 1]], index * 2 + 1) for index in range(50)]

        result = judge.evaluate(
            "function solve(nums) {\n  return nums[0] + nums[1];\n}\n",
            "javascript",
            cases,
            timeout_seconds=2,
        )

        self.assertEqual(result.status, "accepted")
        self.assertEqual(result.passed_count, 50)
        self.assertEqual(result.total_count, 50)

    def test_typescript_solution_accepts_basic_annotations(self):
        result = judge.evaluate(
            "function solve(nums: number[]): number {\n  const first: number = nums[0];\n  return first + nums[1];\n}\n",
            "typescript",
            [make_case(1, [[2, 5]], 7)],
            timeout_seconds=2,
        )

        self.assertEqual(result.status, "accepted")
        self.assertEqual(result.passed_count, 1)


if __name__ == "__main__":
    unittest.main()
