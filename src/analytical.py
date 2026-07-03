"""
Exact RTP via exhaustive enumeration — the "math sheet" method studios
use for regulatory certification. Every one of the 8,000 possible spins
is equally likely (1/8,000), so:

    RTP = sum(payout_of_outcome) / total_outcomes

No sampling, no error bars — this is the ground truth that simulate.py
is checked against.
"""

import itertools
from collections import defaultdict

import pandas as pd

from config import REELS, REEL_SIZES, TOTAL_COMBINATIONS, get_payout


def calculate_exact_rtp():
    total_payout = 0
    hit_count = 0
    breakdown = defaultdict(lambda: {"count": 0, "payout_per_hit": 0})

    for i, j, k in itertools.product(*(range(n) for n in REEL_SIZES)):
        s1, s2, s3 = REELS[0][i], REELS[1][j], REELS[2][k]
        payout = get_payout(s1, s2, s3)
        total_payout += payout

        if payout > 0:
            hit_count += 1
            combo = f"{s1} | {s2} | {s3}"
            breakdown[combo]["count"] += 1
            breakdown[combo]["payout_per_hit"] = payout

    rtp = total_payout / TOTAL_COMBINATIONS
    hit_frequency = hit_count / TOTAL_COMBINATIONS

    rows = [
        {
            "combination": combo,
            "count": d["count"],
            "payout_per_hit": d["payout_per_hit"],
            "probability": d["count"] / TOTAL_COMBINATIONS,
            "rtp_contribution": d["count"] * d["payout_per_hit"] / TOTAL_COMBINATIONS,
        }
        for combo, d in breakdown.items()
    ]
    paytable_df = pd.DataFrame(rows).sort_values("rtp_contribution", ascending=False)

    return {
        "rtp": rtp,
        "hit_frequency": hit_frequency,
        "hit_count": hit_count,
        "paytable_df": paytable_df,
    }
