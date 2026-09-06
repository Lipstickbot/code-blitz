import unittest

try:
    from app.services.bot_match import bot_accept_schedule_seconds, resolve_bot_strategy
    BACKEND_DEPS_READY = True
except Exception as error:
    BACKEND_DEPS_READY = False
    BACKEND_DEPS_ERROR = error


@unittest.skipUnless(BACKEND_DEPS_READY, "Backend dependencies are not available.")
class BotMatchTests(unittest.TestCase):
    def test_bot_schedule_has_one_time_per_task(self):
        schedule = bot_accept_schedule_seconds(1800, 6)

        self.assertEqual(len(schedule), 6)
        self.assertEqual(schedule, sorted(schedule))

    def test_bot_schedule_stays_inside_match_duration(self):
        schedule = bot_accept_schedule_seconds(120, 6)

        self.assertTrue(all(0 < second < 120 for second in schedule))

    def test_auto_strategy_follows_player_rating(self):
        self.assertEqual(resolve_bot_strategy("auto", 900).level, "easy")
        self.assertEqual(resolve_bot_strategy("auto", 1200).level, "normal")
        self.assertEqual(resolve_bot_strategy("auto", 1600).level, "hard")

    def test_hard_bot_solves_earlier_than_easy_bot(self):
        easy = bot_accept_schedule_seconds(1800, 6, resolve_bot_strategy("easy"))
        hard = bot_accept_schedule_seconds(1800, 6, resolve_bot_strategy("hard"))

        self.assertLess(hard[-1], easy[-1])


if __name__ == "__main__":
    unittest.main()
