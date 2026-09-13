import unittest

from app.services.tournament_rules import is_valid_tournament_size


class TournamentRulesTest(unittest.TestCase):
    def test_power_of_two_sizes_up_to_32_are_valid(self):
        for player_count in [2, 4, 8, 16, 32]:
            with self.subTest(player_count=player_count):
                self.assertTrue(is_valid_tournament_size(player_count))

    def test_odd_or_non_bracket_sizes_are_rejected(self):
        for player_count in [1, 3, 6, 10, 12, 24, 33]:
            with self.subTest(player_count=player_count):
                self.assertFalse(is_valid_tournament_size(player_count))


if __name__ == "__main__":
    unittest.main()
