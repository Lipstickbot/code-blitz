VALID_TOURNAMENT_SIZES = {2, 4, 8, 16, 32}
MAX_TOURNAMENT_PLAYERS = 32


def is_valid_tournament_size(player_count: int) -> bool:
    return player_count in VALID_TOURNAMENT_SIZES
