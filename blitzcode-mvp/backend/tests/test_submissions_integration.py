import os
import unittest
import uuid


RUN_INTEGRATION = os.getenv("RUN_DB_INTEGRATION_TESTS") == "1"


@unittest.skipUnless(RUN_INTEGRATION, "Set RUN_DB_INTEGRATION_TESTS=1 to run database integration tests.")
class SubmissionsApiIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        try:
            from httpx import ASGITransport, AsyncClient
            from sqlalchemy import delete, func, select

            from app.database import AsyncSessionLocal, Base, engine
            from app.main import app
            from app.models import Problem, Submission, SubmissionCaseResult, TestCase
        except Exception as error:
            self.skipTest(f"Backend dependencies are not available: {error}")

        self.AsyncClient = AsyncClient
        self.ASGITransport = ASGITransport
        self.app = app
        self.AsyncSessionLocal = AsyncSessionLocal
        self.Base = Base
        self.engine = engine
        self.Problem = Problem
        self.TestCase = TestCase
        self.Submission = Submission
        self.SubmissionCaseResult = SubmissionCaseResult
        self.delete = delete
        self.func = func
        self.select = select
        self.slug = f"integration-sum-{uuid.uuid4().hex}"
        self.problem_id = None

        async with self.engine.begin() as conn:
            await conn.run_sync(self.Base.metadata.create_all)

        await self._create_problem()

    async def asyncTearDown(self):
        try:
            if not self.problem_id:
                return
            async with self.AsyncSessionLocal() as db:
                submission_ids = await db.execute(
                    self.select(self.Submission.id).where(self.Submission.problem_id == self.problem_id)
                )
                ids = list(submission_ids.scalars().all())
                if ids:
                    await db.execute(
                        self.delete(self.SubmissionCaseResult).where(
                            self.SubmissionCaseResult.submission_id.in_(ids)
                        )
                    )
                    await db.execute(self.delete(self.Submission).where(self.Submission.id.in_(ids)))
                await db.execute(self.delete(self.TestCase).where(self.TestCase.problem_id == self.problem_id))
                await db.execute(self.delete(self.Problem).where(self.Problem.id == self.problem_id))
                await db.commit()
        finally:
            await self.engine.dispose()

    async def test_run_checks_first_five_sample_cases(self):
        response = await self._post_submission(kind="run", code="function solve(a, b) { return a + b; }")

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["status"], "accepted")
        self.assertEqual(payload["passed_count"], 5)
        self.assertEqual(payload["total_count"], 5)
        self.assertEqual(len(payload["case_results"]), 5)

    async def test_submit_checks_hidden_cases_and_persists_results(self):
        response = await self._post_submission(kind="submit", code="function solve(a, b) { return a + b; }")

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["status"], "accepted")
        self.assertEqual(payload["passed_count"], 50)
        self.assertEqual(payload["total_count"], 50)

        async with self.AsyncSessionLocal() as db:
            submission_count = await db.scalar(
                self.select(self.func.count()).select_from(self.Submission).where(
                    self.Submission.problem_id == self.problem_id
                )
            )
        self.assertEqual(submission_count, 1)

    async def test_submit_returns_wrong_answer_for_real_failed_code(self):
        response = await self._post_submission(kind="submit", code="function solve(a, b) { return 0; }")

        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["status"], "wrong_answer")
        self.assertLess(payload["passed_count"], payload["total_count"])
        self.assertTrue(any(case["status"] == "wrong_answer" for case in payload["case_results"]))
        self.assertTrue(all("expected" not in case and "actual" not in case for case in payload["case_results"]))

    async def test_run_returns_console_output_for_sample_cases(self):
        response = await self._post_submission(
            kind="run", code="function solve(a, b) { console.log('sum', a + b); return a + b; }"
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["case_results"][0]["stdout"], "sum 1")

    async def _create_problem(self):
        async with self.AsyncSessionLocal() as db:
            problem = self.Problem(
                slug=self.slug,
                title="Integration Sum",
                description="Return the sum of two input numbers.",
                statement="Return the sum of two input numbers.",
                difficulty="easy",
                status="active",
                concept_group="math",
                tags=["math", "integration"],
                starter_code_js="function solve(a, b) {\n  return a + b;\n}",
                time_limit_ms=1000,
                memory_limit_mb=256,
            )
            cases = []
            for index in range(5):
                cases.append(
                    self.TestCase(
                        position=index + 1,
                        input=f"[{index}, {index + 1}]",
                        expected_output=str(index + index + 1),
                        input_json=[index, index + 1],
                        expected_json=index + index + 1,
                        is_sample=True,
                        is_hidden=False,
                    )
                )
            for index in range(50):
                left = index + 10
                right = index * 2
                cases.append(
                    self.TestCase(
                        position=index + 6,
                        input=f"[{left}, {right}]",
                        expected_output=str(left + right),
                        input_json=[left, right],
                        expected_json=left + right,
                        is_sample=False,
                        is_hidden=True,
                    )
                )
            problem.test_cases = cases
            db.add(problem)
            await db.commit()
            await db.refresh(problem)
            self.problem_id = problem.id

    async def _post_submission(self, *, kind: str, code: str):
        transport = self.ASGITransport(app=self.app)
        async with self.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post(
                "/api/submissions",
                json={
                    "problem_id": self.problem_id,
                    "language": "javascript",
                    "code": code,
                    "kind": kind,
                },
            )


if __name__ == "__main__":
    unittest.main()
