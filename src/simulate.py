"""
Monte Carlo verification: spin the machine millions of times and confirm
the measured RTP converges to the exact value from analytical.py. This is
the Law of Large Numbers in practice, and it's also how you catch bugs
that only show up in aggregate (e.g. a mistyped paytable entry).
"""

import numpy as np
import pandas as pd

from config import REEL_SIZES, REELS, BET_PER_SPIN, get_payout


def _build_payout_table() -> np.ndarray:
    """Precompute payout[i, j, k] once so simulation is a single vectorized lookup."""
    table = np.zeros(REEL_SIZES, dtype=np.int64)
    for i in range(REEL_SIZES[0]):
        for j in range(REEL_SIZES[1]):
            for k in range(REEL_SIZES[2]):
                table[i, j, k] = get_payout(REELS[0][i], REELS[1][j], REELS[2][k])
    return table


def run_simulation(n_spins: int = 1_000_000, seed: int = 42, track_every: int = 10_000):
    rng = np.random.default_rng(seed)
    payout_table = _build_payout_table()

    stops = rng.integers([0, 0, 0], REEL_SIZES, size=(n_spins, 3))
    wins = payout_table[stops[:, 0], stops[:, 1], stops[:, 2]]

    cum_return = np.cumsum(wins)
    cum_bet = np.arange(1, n_spins + 1) * BET_PER_SPIN
    checkpoints = np.arange(track_every, n_spins + 1, track_every)
    rtp_tracker = pd.DataFrame({
        "spin": checkpoints,
        "rtp": cum_return[checkpoints - 1] / cum_bet[checkpoints - 1],
    })

    sim_rtp = wins.sum() / (n_spins * BET_PER_SPIN)
    hit_freq = float(np.mean(wins > 0))
    avg_win = float(wins[wins > 0].mean())

    return {
        "sim_rtp": sim_rtp,
        "hit_frequency": hit_freq,
        "avg_win": avg_win,
        "rtp_tracker": rtp_tracker,
        "wins": wins,
    }


def analyse_volatility(wins: np.ndarray, n_sessions: int = 10_000, session_spins: int = 500,
                        start_balance: int = 500, seed: int = 7):
    """
    Volatility = std dev of return per spin. Session simulation shows what
    that actually feels like for a player over a realistic length of play.
    """
    rng = np.random.default_rng(seed)
    sd = float(np.std(wins))

    if sd < 2:
        label = "LOW — frequent small wins, steady balance"
    elif sd < 5:
        label = "MEDIUM"
    else:
        label = "HIGH — rare big wins, balance swings a lot"

    sampled = rng.choice(wins, size=(n_sessions, session_spins))
    ending_balance = start_balance - session_spins * BET_PER_SPIN + sampled.sum(axis=1)

    return {
        "std_dev": sd,
        "volatility_label": label,
        "ending_balance": ending_balance,
        "median_balance": float(np.median(ending_balance)),
        "pct_profitable": float(np.mean(ending_balance > start_balance)),
    }
