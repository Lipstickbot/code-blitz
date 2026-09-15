VALID_TOURNAMENT_SIZES = {2, 4, 8, 16, 32}
MAX_TOURNAMENT_PLAYERS = 32


def is_valid_tournament_size(player_count: int) -> bool:
    return player_count in VALID_TOURNAMENT_SIZES


def tournament_round_count(player_count: int) -> int:
    if not is_valid_tournament_size(player_count):
        raise ValueError("Tournament size must be 2, 4, 8, 16, or 32")
    rounds = 0
    while player_count > 1:
        rounds += 1
        player_count //= 2
    return rounds


def tournament_round_name(round_number: int, total_rounds: int) -> str:
    distance_to_final = total_rounds - round_number
    if distance_to_final == 0:
        return "Final"
    if distance_to_final == 1:
        return "Semifinal"
    if distance_to_final == 2:
        return "Quarterfinal"
    return f"Round {round_number}"


def first_round_seed_pairs(player_count: int) -> list[tuple[int, int]]:
    """Pair strong seeds against lower seeds while keeping a full bracket tree."""
    if not is_valid_tournament_size(player_count):
        raise ValueError("Tournament size must be 2, 4, 8, 16, or 32")
    return [(seed, player_count + 1 - seed) for seed in range(1, player_count // 2 + 1)]
