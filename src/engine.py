"""
engine.py
---------
The core slot machine logic: spin the reels, check paylines for wins,
check scatters, and calculate the total payout for one spin.

This file is intentionally separate from config.py so the GAME RULES
(how a spin works) are kept apart from the GAME DESIGN (what the reels
and paytable actually contain). In a real studio, designers tweak
config.py constantly while engine.py rarely changes.
"""

import numpy as np
from config import REELS, PAYLINES, PAYTABLE, SCATTER_PAYS, BET_PER_LINE


def spin_reels(rng: np.random.RandomState) -> dict:
    """
    Spin all 5 reels and return what's visible.

    Returns a dictionary like:
        {1: ["CHERRY", "BAR", "LEMON"],   <- reel 1, rows 0/1/2
         2: ["BELL", "CHERRY", "WILD"],   <- reel 2, rows 0/1/2
         ...}

    How it works: each reel strip is a list of 64 symbols. We pick a random
    "stop position" on the strip, then read 3 symbols starting from there
    (wrapping around to the start if we go past the end of the strip).
    This mimics a real spinning reel landing at a random point.
    """
    grid = {}
    for reel_num in range(1, 6):
        strip = REELS[reel_num]
        stop_position = rng.randint(0, len(strip))
        visible_symbols = [
            strip[(stop_position + row) % len(strip)]
            for row in range(3)
        ]
        grid[reel_num] = visible_symbols
    return grid


def evaluate_payline(grid: dict, payline: list) -> int:
    """
    Check ONE payline for a win and return the payout (in bet multiples).

    Logic:
      1. Read the symbol at each reel along this payline's path.
      2. Find the first "real" symbol (skip past WILDs at the start,
         since a WILD by itself doesn't tell us what we're matching).
      3. Count how many symbols in a row (starting from reel 1) match
         that symbol OR are WILD.
      4. If we got 3, 4, or 5 in a row, look up the payout.

    Example: payline reads [CHERRY, WILD, CHERRY, BAR, LEMON]
      -> first real symbol = CHERRY
      -> CHERRY, WILD(counts as CHERRY), CHERRY = 3 match, then BAR breaks it
      -> Result: 3x CHERRY win
    """
    sequence = [grid[reel + 1][row] for reel, row in enumerate(payline)]

    # Find the first non-wild symbol to know what we're matching against
    anchor_symbol = None
    for symbol in sequence:
        if symbol != "WILD":
            anchor_symbol = symbol
            break

    # If the whole line is wilds, treat WILD itself as the matching symbol
    if anchor_symbol is None:
        anchor_symbol = "WILD"

    # SCATTER and BLANK symbols don't pay on paylines (scatter is handled separately)
    if anchor_symbol in ("SCATTER", "BLANK"):
        return 0

    # Count consecutive matches starting from reel 1
    match_count = 0
    for symbol in sequence:
        if symbol == anchor_symbol or symbol == "WILD":
            match_count += 1
        else:
            break  # the chain is broken, stop counting

    # Look up payout — minimum 3 matches required to win anything
    if anchor_symbol in PAYTABLE and match_count >= 3:
        capped = min(match_count, 5)
        return PAYTABLE[anchor_symbol][capped]

    return 0


def count_scatters(grid: dict) -> int:
    """Count how many SCATTER symbols appear anywhere on the grid (any reel, any row)."""
    return sum(grid[reel].count("SCATTER") for reel in range(1, 6))


def play_one_spin(rng: np.random.RandomState) -> dict:
    """
    Play exactly one spin and return full details:
      - the grid that landed
      - win amount from paylines
      - win amount from scatters
      - total win

    Returns a dict so callers can inspect exactly what happened,
    which is useful for debugging and for showing example spins.
    """
    grid = spin_reels(rng)

    payline_win = sum(
        evaluate_payline(grid, payline) * BET_PER_LINE
        for payline in PAYLINES
    )

    scatter_count = count_scatters(grid)
    scatter_win = 0
    if scatter_count >= 3:
        capped = min(scatter_count, 5)
        scatter_win = SCATTER_PAYS.get(capped, 0) * BET_PER_LINE

    return {
        "grid": grid,
        "payline_win": payline_win,
        "scatter_count": scatter_count,
        "scatter_win": scatter_win,
        "total_win": payline_win + scatter_win,
    }


def print_grid(grid: dict):
    """Pretty-print a 5x3 grid to the console, for demo purposes."""
    for row in range(3):
        line = " | ".join(f"{grid[reel][row]:<8}" for reel in range(1, 6))
        print(f"  {line}")
