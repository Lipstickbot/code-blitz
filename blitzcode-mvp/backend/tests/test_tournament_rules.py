import unittest

from app.services.tournament_rules import (
    first_round_seed_pairs,
    is_valid_tournament_size,
    tournament_round_count,
    tournament_round_name,
)


class TournamentRulesTest(unittest.TestCase):
    def test_power_of_two_sizes_up_to_32_are_valid(self):
        for player_count in [2, 4, 8, 16, 32]:
            with self.subTest(player_count=player_count):
                self.assertTrue(is_valid_tournament_size(player_count))

    def test_odd_or_non_bracket_sizes_are_rejected(self):
        for player_count in [1, 3, 6, 10, 12, 24, 33]:
            with self.subTest(player_count=player_count):
                self.assertFalse(is_valid_tournament_size(player_count))

    def test_round_names_describe_full_path_to_final(self):
        total_rounds = tournament_round_count(8)

        self.assertEqual(total_rounds, 3)
        self.assertEqual(tournament_round_name(1, total_rounds), "Quarterfinal")
        self.assertEqual(tournament_round_name(2, total_rounds), "Semifinal")
        self.assertEqual(tournament_round_name(3, total_rounds), "Final")

    def test_first_round_pairs_high_seed_against_low_seed(self):
        self.assertEqual(first_round_seed_pairs(8), [(1, 8), (2, 7), (3, 6), (4, 5)])


if __name__ == "__main__":
    unittest.main()
