import os
import unittest
import uuid


RUN_INTEGRATION = os.getenv("RUN_DB_INTEGRATION_TESTS") == "1"


@unittest.skipUnless(RUN_INTEGRATION, "Set RUN_DB_INTEGRATION_TESTS=1 to run database integration tests.")
class MatchmakingApiIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        try:
            from httpx import ASGITransport, AsyncClient
            from sqlalchemy import delete, select

            from app.auth import create_access_token, hash_password
            from app.database import AsyncSessionLocal, Base, engine
            from app.main import app
            from app.models import (
                FriendRoom,
                Match,
                MatchEvent,
                MatchParticipant,
                MatchTask,
                MatchmakingQueue,
                Problem,
                RatingEvent,
                Submission,
                SubmissionCaseResult,
                TestCase,
                User,
                UserProblemHistory,
                UserStats,
            )
        except Exception as error:
            self.skipTest(f"Backend dependencies are not available: {error}")

        self.AsyncClient = AsyncClient
        self.ASGITransport = ASGITransport
        self.app = app
        self.AsyncSessionLocal = AsyncSessionLocal
        self.Base = Base
        self.engine = engine
        self.create_access_token = create_access_token
        self.hash_password = hash_password
        self.delete = delete
        self.select = select

        self.Match = Match
        self.FriendRoom = FriendRoom
        self.MatchEvent = MatchEvent
        self.MatchParticipant = MatchParticipant
        self.MatchTask = MatchTask
        self.MatchmakingQueue = MatchmakingQueue
        self.Problem = Problem
        self.RatingEvent = RatingEvent
        self.Submission = Submission
        self.SubmissionCaseResult = SubmissionCaseResult
        self.TestCase = TestCase
        self.User = User
        self.UserProblemHistory = UserProblemHistory
        self.UserStats = UserStats

        self.prefix = f"mm_{uuid.uuid4().hex}"
        self.user_ids: list[str] = []
        self.problem_ids: list[str] = []
        self.match_ids: list[str] = []

        async with self.engine.begin() as conn:
            await conn.run_sync(self.Base.metadata.create_all)

        await self._create_problem_bank()

    async def asyncTearDown(self):
        try:
            async with self.AsyncSessionLocal() as db:
                queue_ids = await db.execute(
                    self.select(self.MatchmakingQueue.matched_match_id).where(
                        self.MatchmakingQueue.user_id.in_(self.user_ids)
                    )
                )
                for match_id in queue_ids.scalars().all():
                    if match_id:
                        self.match_ids.append(match_id)
                self.match_ids = list(dict.fromkeys(self.match_ids))

                if self.user_ids:
                    await db.execute(self.delete(self.MatchmakingQueue).where(self.MatchmakingQueue.user_id.in_(self.user_ids)))

                if self.match_ids:
                    await db.execute(self.delete(self.FriendRoom).where(self.FriendRoom.match_id.in_(self.match_ids)))
                    await db.execute(
                        self.delete(self.SubmissionCaseResult).where(
                            self.SubmissionCaseResult.submission_id.in_(
                                self.select(self.Submission.id).where(self.Submission.match_id.in_(self.match_ids))
                            )
                        )
                    )
                    await db.execute(self.delete(self.Submission).where(self.Submission.match_id.in_(self.match_ids)))
                    await db.execute(self.delete(self.RatingEvent).where(self.RatingEvent.match_id.in_(self.match_ids)))
                    await db.execute(self.delete(self.MatchEvent).where(self.MatchEvent.match_id.in_(self.match_ids)))
                    await db.execute(self.delete(self.MatchTask).where(self.MatchTask.match_id.in_(self.match_ids)))
                    await db.execute(
                        self.delete(self.MatchParticipant).where(self.MatchParticipant.match_id.in_(self.match_ids))
                    )
                    await db.execute(self.delete(self.Match).where(self.Match.id.in_(self.match_ids)))

                if self.user_ids:
                    await db.execute(self.delete(self.UserProblemHistory).where(self.UserProblemHistory.user_id.in_(self.user_ids)))
                    await db.execute(self.delete(self.UserStats).where(self.UserStats.user_id.in_(self.user_ids)))
                    await db.execute(self.delete(self.User).where(self.User.id.in_(self.user_ids)))

                if self.problem_ids:
                    await db.execute(self.delete(self.TestCase).where(self.TestCase.problem_id.in_(self.problem_ids)))
                    await db.execute(self.delete(self.Problem).where(self.Problem.id.in_(self.problem_ids)))

                await db.commit()
        finally:
            await self.engine.dispose()

    async def test_queue_pair_creates_match_and_active_match_restores(self):
        left_id, left_token = await self._create_user("left", 1200)
        right_id, right_token = await self._create_user("right", 1250)

        first_join = await self._post("/api/matchmaking/join", left_token)
        self.assertEqual(first_join.status_code, 200, first_join.text)
        self.assertEqual(first_join.json()["status"], "searching")

        second_join = await self._post("/api/matchmaking/join", right_token)
        self.assertEqual(second_join.status_code, 200, second_join.text)
        matched_payload = second_join.json()
        self.assertEqual(matched_payload["status"], "matched")
        match_id = matched_payload["match_id"]
        self.assertIsNotNone(match_id)
        self.match_ids.append(match_id)

        active_response = await self._get("/api/matches/active", left_token)
        self.assertEqual(active_response.status_code, 200, active_response.text)
        active = active_response.json()
        self.assertEqual(active["id"], match_id)
        self.assertEqual(active["status"], "active")
        self.assertEqual(active["duration_seconds"], 1800)
        self.assertEqual(len(active["participants"]), 2)
        self.assertEqual(len(active["tasks"]), 6)
        self.assertEqual([task["difficulty"] for task in active["tasks"]], ["easy", "easy", "medium", "easy", "medium", "hard"])

        status_response = await self._get("/api/matchmaking/status", right_token)
        self.assertEqual(status_response.status_code, 200, status_response.text)
        self.assertEqual(status_response.json()["status"], "matched")
        self.assertEqual(status_response.json()["match_id"], match_id)

        async with self.AsyncSessionLocal() as db:
            participants = (
                await db.execute(
                    self.select(self.MatchParticipant).where(self.MatchParticipant.match_id == match_id)
                )
            ).scalars().all()
        self.assertEqual({item.user_id for item in participants}, {left_id, right_id})

    async def test_far_rating_stays_searching_then_can_cancel(self):
        low_id, low_token = await self._create_user("low", 900)
        high_id, high_token = await self._create_user("high", 1800)

        low_join = await self._post("/api/matchmaking/join", low_token)
        self.assertEqual(low_join.status_code, 200, low_join.text)
        self.assertEqual(low_join.json()["status"], "searching")

        high_join = await self._post("/api/matchmaking/join", high_token)
        self.assertEqual(high_join.status_code, 200, high_join.text)
        self.assertEqual(high_join.json()["status"], "searching")

        low_cancel = await self._post("/api/matchmaking/cancel", low_token)
        self.assertEqual(low_cancel.status_code, 200, low_cancel.text)
        self.assertTrue(low_cancel.json()["cancelled"])

        async with self.AsyncSessionLocal() as db:
            rows = (
                await db.execute(
                    self.select(self.MatchmakingQueue).where(self.MatchmakingQueue.user_id.in_([low_id, high_id]))
                )
            ).scalars().all()
        self.assertEqual({row.user_id: row.status for row in rows}[low_id], "cancelled")
        self.assertEqual({row.user_id: row.status for row in rows}[high_id], "searching")

    async def test_friend_room_invite_accepts_into_active_match(self):
        creator_id, creator_token = await self._create_user("creator", 1180)
        invited_id, invited_token = await self._create_user("invited", 1190)
        invited_username = f"{self.prefix}_invited"

        create_response = await self._post(
            "/api/matchmaking/rooms",
            creator_token,
            json={"opponent_username": invited_username},
        )
        self.assertEqual(create_response.status_code, 200, create_response.text)
        room_payload = create_response.json()
        self.assertEqual(room_payload["status"], "pending")
        self.assertEqual(room_payload["creator_user_id"], creator_id)
        self.assertEqual(room_payload["invited_user_id"], invited_id)
        self.match_ids.append(room_payload["match_id"])

        invites_response = await self._get("/api/matchmaking/rooms/invites", invited_token)
        self.assertEqual(invites_response.status_code, 200, invites_response.text)
        self.assertIn(room_payload["id"], [room["id"] for room in invites_response.json()])

        accept_response = await self._post(f"/api/matchmaking/rooms/{room_payload['id']}/accept", invited_token)
        self.assertEqual(accept_response.status_code, 200, accept_response.text)
        accepted = accept_response.json()
        self.assertEqual(accepted["status"], "accepted")

        active_response = await self._get("/api/matches/active", creator_token)
        self.assertEqual(active_response.status_code, 200, active_response.text)
        active = active_response.json()
        self.assertEqual(active["id"], room_payload["match_id"])
        self.assertEqual(active["mode"], "friend")
        self.assertEqual(active["status"], "active")
        self.assertEqual(len(active["participants"]), 2)
        self.assertEqual(len(active["tasks"]), 6)

    async def test_friend_room_can_be_cancelled_before_accept(self):
        _, creator_token = await self._create_user("cancel_creator", 1180)
        _, invited_token = await self._create_user("cancel_invited", 1190)

        create_response = await self._post(
            "/api/matchmaking/rooms",
            creator_token,
            json={"opponent_username": f"{self.prefix}_cancel_invited"},
        )
        self.assertEqual(create_response.status_code, 200, create_response.text)
        room_payload = create_response.json()
        self.match_ids.append(room_payload["match_id"])

        cancel_response = await self._post(f"/api/matchmaking/rooms/{room_payload['id']}/cancel", creator_token)
        self.assertEqual(cancel_response.status_code, 200, cancel_response.text)
        self.assertEqual(cancel_response.json()["status"], "cancelled")

        accept_response = await self._post(f"/api/matchmaking/rooms/{room_payload['id']}/accept", invited_token)
        self.assertEqual(accept_response.status_code, 400, accept_response.text)

    async def _create_user(self, suffix: str, rating: int) -> tuple[str, str]:
        async with self.AsyncSessionLocal() as db:
            user = self.User(
                email=f"{self.prefix}_{suffix}@example.com",
                username=f"{self.prefix}_{suffix}",
                password_hash=self.hash_password("CodeRunner123"),
                rating=rating,
            )
            user.stats = self.UserStats(rating=rating)
            db.add(user)
            await db.commit()
            await db.refresh(user)
            self.user_ids.append(user.id)
            return user.id, self.create_access_token(user.id)

    async def _create_problem_bank(self) -> None:
        layout = ["easy", "easy", "medium", "easy", "medium", "hard"]
        async with self.AsyncSessionLocal() as db:
            for index, difficulty in enumerate(layout):
                problem = self.Problem(
                    slug=f"{self.prefix}_problem_{index}",
                    title=f"Matchmaking Problem {index}",
                    description="Temporary problem for matchmaking integration tests.",
                    statement="Temporary problem for matchmaking integration tests.",
                    difficulty=difficulty,
                    status="active",
                    concept_group=f"{self.prefix}_concept_{index}",
                    tags=["integration", difficulty],
                    starter_code_js="function solve() {\n  return true;\n}",
                    speed_score=10 - index,
                    time_limit_ms=1000,
                    memory_limit_mb=256,
                )
                problem.test_cases = [
                    self.TestCase(
                        position=1,
                        input="[]",
                        expected_output="true",
                        input_json=[],
                        expected_json=True,
                        is_sample=True,
                        is_hidden=False,
                    )
                ]
                db.add(problem)
                await db.flush()
                self.problem_ids.append(problem.id)
            await db.commit()

    async def _post(self, path: str, token: str, json=None):
        transport = self.ASGITransport(app=self.app)
        async with self.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.post(path, headers={"Authorization": f"Bearer {token}"}, json=json)

    async def _get(self, path: str, token: str):
        transport = self.ASGITransport(app=self.app)
        async with self.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.get(path, headers={"Authorization": f"Bearer {token}"})


if __name__ == "__main__":
    unittest.main()
