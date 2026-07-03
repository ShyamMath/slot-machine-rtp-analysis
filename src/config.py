"""
Game design for a 3-reel, single-payline slot machine.

A reel strip is a list of symbols. Spinning picks one random stop per
reel; how many times a symbol appears on a strip controls how often it
lands. That's the entire mechanism behind RTP tuning in a real machine.
"""

SYMBOLS = ("SEVEN", "BAR", "BELL", "CHERRY", "LEMON")

# stops per symbol, per reel (20 stops per reel)
REEL_1 = ["SEVEN"] * 1 + ["BAR"] * 2 + ["BELL"] * 3 + ["CHERRY"] * 5 + ["LEMON"] * 9
REEL_2 = ["SEVEN"] * 1 + ["BAR"] * 2 + ["BELL"] * 4 + ["CHERRY"] * 4 + ["LEMON"] * 9
REEL_3 = ["SEVEN"] * 1 + ["BAR"] * 2 + ["BELL"] * 3 + ["CHERRY"] * 5 + ["LEMON"] * 9
REELS = [REEL_1, REEL_2, REEL_3]
REEL_SIZES = [len(r) for r in REELS]

for i, reel in enumerate(REELS, 1):
    assert len(reel) == 20, f"Reel {i} has {len(reel)} stops, expected 20"

TOTAL_COMBINATIONS = REEL_SIZES[0] * REEL_SIZES[1] * REEL_SIZES[2]  # 8,000

# One payline. Payout is a multiplier of the 1-coin bet.
PAYTABLE = {
    ("SEVEN",  "SEVEN",  "SEVEN"):  321,   # jackpot
    ("BAR",    "BAR",    "BAR"):     80,
    ("BELL",   "BELL",   "BELL"):    32,
    ("CHERRY", "CHERRY", "CHERRY"):  16,
    ("CHERRY", "CHERRY", "LEMON"):    8,
    ("CHERRY", "CHERRY", "BAR"):      8,
    ("CHERRY", "CHERRY", "BELL"):     8,
    ("CHERRY", "CHERRY", "SEVEN"):    8,
    ("CHERRY", "LEMON",  "LEMON"):    3,
    ("CHERRY", "BAR",    "BAR"):      3,
    ("CHERRY", "BELL",   "BELL"):     3,
}

BET_PER_SPIN = 1  # 1 coin, 1 payline


def get_payout(s1: str, s2: str, s3: str) -> int:
    """Payout multiplier for a 3-symbol combination, 0 if it doesn't win."""
    return PAYTABLE.get((s1, s2, s3), 0)
