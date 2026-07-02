"""
config.py
---------
This file holds the actual game design: reel strips, paylines, and paytable.

Think of a "reel strip" as a physical wheel with symbols printed on it.
When you spin, the wheel stops at a random position, and you see whichever
3 symbols land in the window. The MORE times a symbol appears on the strip,
the more LIKELY it is to show up. This is how real slot machines control odds
without needing "fake" probabilities — the probability is built directly into
how many times each symbol physically appears on the wheel.

Each reel strip below has exactly 64 symbol slots. 64 was chosen because
it's a clean power of 2, which historically maps well to physical reel
mechanisms and random number generators, though modern slots can use
any strip length.
"""

# ---------------------------------------------------------------
# REEL STRIPS
# ---------------------------------------------------------------
# Each dictionary says "this symbol appears N times on this reel".
# Reels 1 and 5 are slightly more generous (more wilds/scatters) —
# a common design trick to make near-misses on the edges feel more frequent,
# which keeps players engaged even on losing spins.

REEL_DESIGNS = {
    1: {"CHERRY": 16, "LEMON": 16, "BELL": 12, "BAR": 8, "STAR": 5, "WILD": 3, "SCATTER": 4},
    2: {"CHERRY": 15, "LEMON": 15, "BELL": 11, "BAR": 8, "STAR": 5, "WILD": 3, "SCATTER": 4, "BLANK": 3},
    3: {"CHERRY": 15, "LEMON": 15, "BELL": 11, "BAR": 7, "STAR": 4, "WILD": 3, "SCATTER": 4, "BLANK": 5},
    4: {"CHERRY": 15, "LEMON": 15, "BELL": 11, "BAR": 8, "STAR": 5, "WILD": 3, "SCATTER": 4, "BLANK": 3},
    5: {"CHERRY": 16, "LEMON": 16, "BELL": 12, "BAR": 8, "STAR": 5, "WILD": 3, "SCATTER": 4},
}

# Sanity check: every reel strip must sum to exactly 64 symbols.
# If this fails, the reel design is broken and probabilities won't make sense.
for reel_num, design in REEL_DESIGNS.items():
    total = sum(design.values())
    assert total == 64, f"Reel {reel_num} has {total} symbols, expected 64"


def build_strip(design: dict) -> list:
    """
    Turn a {symbol: count} dictionary into an actual list of symbols.
    Example: {"CHERRY": 2, "BAR": 1} -> ["CHERRY", "CHERRY", "BAR"]
    """
    strip = []
    for symbol, count in design.items():
        strip.extend([symbol] * count)
    return strip


# Pre-build all 5 reel strips once, so we don't rebuild them on every spin
REELS = {reel_num: build_strip(design) for reel_num, design in REEL_DESIGNS.items()}


# ---------------------------------------------------------------
# PAYLINES
# ---------------------------------------------------------------
# A payline is a specific path across the 5x3 grid that we check for matches.
# Row numbering: 0 = top row, 1 = middle row, 2 = bottom row.
# Each payline is a list of 5 numbers — one row-position per reel.
#
# Example: [1,1,1,1,1] means "check the middle row straight across".
# Example: [0,1,2,1,0] means "top, middle, bottom, middle, top" (a V shape).

PAYLINES = [
    [1, 1, 1, 1, 1],   # 1.  Straight middle
    [0, 0, 0, 0, 0],   # 2.  Straight top
    [2, 2, 2, 2, 2],   # 3.  Straight bottom
    [0, 1, 2, 1, 0],   # 4.  V shape
    [2, 1, 0, 1, 2],   # 5.  Inverted V
    [0, 0, 1, 2, 2],   # 6.  Diagonal down
    [2, 2, 1, 0, 0],   # 7.  Diagonal up
    [1, 0, 0, 0, 1],   # 8.
    [1, 2, 2, 2, 1],   # 9.
    [0, 1, 1, 1, 0],   # 10.
    [2, 1, 1, 1, 2],   # 11.
    [1, 0, 1, 0, 1],   # 12. Zigzag
    [1, 2, 1, 2, 1],   # 13. Zigzag
    [0, 1, 0, 1, 0],   # 14.
    [2, 1, 2, 1, 2],   # 15.
    [0, 2, 0, 2, 0],   # 16.
    [2, 0, 2, 0, 2],   # 17.
    [1, 1, 0, 1, 1],   # 18.
    [1, 1, 2, 1, 1],   # 19.
    [0, 2, 1, 2, 0],   # 20.
]

assert len(PAYLINES) == 20
for p in PAYLINES:
    assert len(p) == 5
    assert all(row in (0, 1, 2) for row in p)


# ---------------------------------------------------------------
# PAYTABLE
# ---------------------------------------------------------------
# How much each symbol pays, depending on how many in a row you get
# (3, 4, or 5 matching symbols starting from reel 1).
# Payout is a MULTIPLIER of the bet placed on that single line.
#
# Design principle: symbols that appear MORE often on the reels pay LESS,
# and rare symbols pay MORE. This keeps the math balanced — a symbol that's
# easy to land but pays huge would break the RTP target.
#
# These exact numbers were reached through iterative testing (see
# src/calibrate_rtp.py) until the simulated RTP landed near our 96% target.

PAYTABLE = {
    "CHERRY":  {3: 3,   4: 13,  5: 30},
    "LEMON":   {3: 3,   4: 13,  5: 30},
    "BELL":    {3: 9,   4: 30,  5: 95},
    "BAR":     {3: 25,  4: 95,  5: 300},
    "STAR":    {3: 50,  4: 190, 5: 600},
    "WILD":    {3: 95,  4: 300, 5: 1500},
}

# SCATTER doesn't need to land on a payline — it pays based on how many
# appear ANYWHERE on the grid (any reel, any row). This is standard in
# real slots and usually also triggers a bonus round (free spins).
SCATTER_PAYS = {3: 3, 4: 13, 5: 60}

# WILD substitutes for any symbol except SCATTER, the same way a Joker
# would in a card game — it completes whatever combination it's part of.


# ---------------------------------------------------------------
# BET STRUCTURE
# ---------------------------------------------------------------
BET_PER_LINE = 1          # cost of activating ONE payline
NUM_LINES = len(PAYLINES) # 20
TOTAL_BET_PER_SPIN = BET_PER_LINE * NUM_LINES   # 20
