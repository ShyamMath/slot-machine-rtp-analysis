"""
simulate.py
-----------
Runs millions of simulated spins to verify the actual RTP (Return to Player)
of the game design in config.py, and produces summary statistics and charts.

WHY SIMULATION INSTEAD OF JUST MATH?
You technically COULD calculate exact RTP by working out every possible
combination of symbols across 5 reels (64^5 = over 1 billion combinations)
and summing up the expected payout. That's called "exhaustive enumeration"
and real studios do use it for final certification. But for design and
testing purposes, Monte Carlo simulation (spinning millions of times and
averaging the results) gets you within a fraction of a percent of the true
answer and is much faster to set up and iterate on.

The Law of Large Numbers guarantees that the more spins we simulate,
the closer our measured RTP gets to the true mathematical RTP.

Run:
    python src/simulate.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from engine import play_one_spin
from config import TOTAL_BET_PER_SPIN, PAYTABLE, SCATTER_PAYS

OUT_DIR = os.path.join(os.path.dirname(__file__), "../outputs")
os.makedirs(OUT_DIR, exist_ok=True)

# Colour palette (kept consistent with the rest of the portfolio)
ACCENT, ACCENT2, WARN = "#00D4A1", "#5B6CFF", "#FF6B4A"
TEXT, DIM, BG, SURF, BORDER = "#E8EBF5", "#7A8299", "#0D0F14", "#141720", "#1E2330"


def run_simulation(n_spins: int, seed: int = 2024) -> pd.DataFrame:
    """
    Spin the machine n_spins times and record the result of every spin.

    Returns a DataFrame with one row per spin — this lets us calculate
    not just the average RTP, but also volatility (how spread out the
    wins are) and the win distribution (what % of spins win nothing,
    a little, or a lot).
    """
    rng = np.random.RandomState(seed)
    records = []

    for i in range(n_spins):
        result = play_one_spin(rng)
        records.append({
            "spin": i + 1,
            "total_win": result["total_win"],
            "scatter_count": result["scatter_count"],
        })

    return pd.DataFrame(records)


def summarise(df: pd.DataFrame) -> dict:
    """
    Calculate the key metrics a game mathematician reports on:

    RTP (Return to Player) — the % of all money wagered that gets paid
        back to players over the long run. Regulators require this to
        be disclosed, and it must be mathematically provable, not guessed.

    Hit Frequency — what % of spins result in ANY win (even a small one).
        This affects how "fun" a game feels even when RTP is identical —
        a high hit-frequency game feels more rewarding even at the same RTP.

    Volatility (standard deviation of win size) — how spread out the wins
        are. Low volatility = frequent small wins. High volatility = rare
        but large wins. This is a design choice, not a bug — different
        player segments prefer different volatility levels.

    Max win — the single biggest payout observed (useful for checking the
        game doesn't have some integer/formula bug producing impossible wins).
    """
    total_spins = len(df)
    total_wagered = total_spins * TOTAL_BET_PER_SPIN
    total_won = df["total_win"].sum()

    rtp = total_won / total_wagered * 100
    hit_freq = (df["total_win"] > 0).mean() * 100
    volatility = df["total_win"].std()
    max_win = df["total_win"].max()

    return {
        "total_spins": total_spins,
        "total_wagered": total_wagered,
        "total_won": int(total_won),
        "rtp_pct": round(rtp, 3),
        "hit_frequency_pct": round(hit_freq, 2),
        "volatility": round(volatility, 2),
        "max_win_multiplier": int(max_win / TOTAL_BET_PER_SPIN) if max_win else 0,
        "max_win_amount": int(max_win),
    }


def rtp_convergence_check(seeds=(1, 7, 42, 99, 2024), n_spins=500_000):
    """
    Run the simulation multiple times with DIFFERENT random seeds.

    Why this matters: if you only run the simulation once, you can't tell
    if your measured RTP (e.g. 96.1%) is the TRUE RTP or just luck from
    that particular random sequence. Running it 5 times with different
    seeds shows how much the result varies — if all 5 runs land close to
    each other, you can be confident the design is stable.
    """
    results = []
    for seed in seeds:
        df = run_simulation(n_spins, seed=seed)
        s = summarise(df)
        results.append({"seed": seed, "rtp_pct": s["rtp_pct"]})

    return pd.DataFrame(results)


def plot_results(df: pd.DataFrame, summary: dict, convergence_df: pd.DataFrame):
    """
    3-panel chart:
      1. RTP converging toward true value as more spins are simulated
      2. Win size distribution (histogram, log scale because of rare big wins)
      3. RTP stability across different random seeds
    """
    plt.rcParams.update({
        "text.color": TEXT, "axes.labelcolor": DIM, "xtick.color": DIM,
        "ytick.color": DIM, "axes.facecolor": SURF, "figure.facecolor": BG,
        "axes.edgecolor": BORDER, "grid.color": BORDER, "axes.titlecolor": TEXT,
    })

    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5), facecolor=BG)

    # ── Panel 1: RTP convergence over spin count ─────────────
    running_rtp = (
        df["total_win"].cumsum() /
        (df["spin"] * TOTAL_BET_PER_SPIN)
    ) * 100

    ax1 = axes[0]
    # Subsample for plotting speed (every 1000th point is enough to see the curve)
    step = max(1, len(df) // 5000)
    ax1.plot(df["spin"][::step], running_rtp[::step], color=ACCENT, lw=1.3)
    ax1.axhline(96, color=DIM, ls="--", lw=1, alpha=0.5, label="96% target")
    ax1.set_title("RTP Convergence\n(measured RTP stabilises as spins increase)", fontsize=10)
    ax1.set_xlabel("Number of spins simulated")
    ax1.set_ylabel("Running RTP %")
    ax1.legend(fontsize=8)
    ax1.grid(alpha=0.3)

    # ── Panel 2: Win distribution histogram ───────────────────
    ax2 = axes[1]
    wins = df[df["total_win"] > 0]["total_win"]
    ax2.hist(wins, bins=50, color=ACCENT2, alpha=0.85, log=True)
    ax2.set_title("Win Size Distribution\n(log scale — most wins are small, big wins are rare)", fontsize=10)
    ax2.set_xlabel("Win amount (credits)")
    ax2.set_ylabel("Frequency (log scale)")
    ax2.grid(alpha=0.3)

    # ── Panel 3: RTP stability across random seeds ────────────
    ax3 = axes[2]
    bar_colors = [ACCENT if abs(r - 96) < 1 else WARN for r in convergence_df["rtp_pct"]]
    ax3.bar(convergence_df["seed"].astype(str), convergence_df["rtp_pct"],
            color=bar_colors, width=0.5)
    ax3.axhline(96, color=DIM, ls="--", lw=1, alpha=0.6)
    for i, v in enumerate(convergence_df["rtp_pct"]):
        ax3.text(i, v + 0.05, f"{v:.2f}%", ha="center", fontsize=9, color=TEXT)
    ax3.set_title("RTP Stability Across 5 Random Seeds\n(500K spins each — confirms result isn't just luck)", fontsize=10)
    ax3.set_ylabel("RTP %")
    ax3.set_ylim(min(convergence_df["rtp_pct"]) - 1, max(convergence_df["rtp_pct"]) + 1)
    ax3.grid(alpha=0.3, axis="y")

    fig.suptitle(
        f"Slot Machine RTP Verification  ·  {summary['total_spins']:,} spins simulated  ·  "
        f"Measured RTP = {summary['rtp_pct']}%",
        fontsize=13, color=TEXT, fontweight="bold"
    )
    plt.tight_layout(rect=[0, 0, 1, 0.93])

    out_path = os.path.join(OUT_DIR, "rtp_simulation.png")
    plt.savefig(out_path, dpi=150, facecolor=BG, bbox_inches="tight")
    plt.close()
    print(f"\nChart saved -> {out_path}")


def main():
    print("=" * 55)
    print("  Slot Machine RTP Simulation")
    print("=" * 55)

    N_SPINS = 3_000_000
    print(f"\nSimulating {N_SPINS:,} spins...")
    df = run_simulation(N_SPINS, seed=2024)
    summary = summarise(df)

    print("\n── Results ──")
    print(f"  Total spins simulated : {summary['total_spins']:,}")
    print(f"  Total wagered         : {summary['total_wagered']:,} credits")
    print(f"  Total paid out        : {summary['total_won']:,} credits")
    print(f"  RTP                   : {summary['rtp_pct']}%")
    print(f"  Hit frequency         : {summary['hit_frequency_pct']}%  (spins with any win)")
    print(f"  Volatility (std dev)  : {summary['volatility']}")
    print(f"  Max single win        : {summary['max_win_amount']:,} credits "
          f"({summary['max_win_multiplier']}x total bet)")

    print("\n── Checking RTP stability across different random seeds ──")
    print("   (running 5 independent simulations of 500K spins each)")
    convergence_df = rtp_convergence_check()
    print(convergence_df.to_string(index=False))
    print(f"\n   Range across seeds: {convergence_df['rtp_pct'].min():.2f}% – "
          f"{convergence_df['rtp_pct'].max():.2f}%")
    print("   A tight range here means the design is stable, not a fluke.")

    # Save outputs
    summary_df = pd.DataFrame([summary])
    summary_df.to_csv(os.path.join(OUT_DIR, "rtp_summary.csv"), index=False)
    convergence_df.to_csv(os.path.join(OUT_DIR, "rtp_seed_stability.csv"), index=False)

    plot_results(df, summary, convergence_df)

    print("\n── Output files ──")
    print("  outputs/rtp_summary.csv")
    print("  outputs/rtp_seed_stability.csv")
    print("  outputs/rtp_simulation.png")
    print("\nDone.")


if __name__ == "__main__":
    main()
