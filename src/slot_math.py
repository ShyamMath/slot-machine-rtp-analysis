"""
slot_math.py
------------
Mathematical model for a 3-reel, 5-payline slot machine.

This script does two things:
  1. EXACT RTP — calculates the theoretical return to player mathematically
                 by enumerating every possible outcome and its probability.
  2. SIMULATION — runs 1,000,000 random spins to verify the math is correct.

Key terms (you need to know these for interviews):
  RTP  (Return to Player) — % of all wagered money paid back over time.
                            e.g. 96% RTP means for every R$100 bet,
                            R$96 is returned on average.
  House Edge — 100% - RTP. The casino's profit margin.
  Hit Frequency — % of spins that produce any win.
  Volatility — how "swingy" the game is. High volatility = rare but big wins.
               Low volatility = frequent but small wins.
  Paytable — the list of winning symbol combinations and their payouts.

Run:
    python src/slot_math.py
"""

import os
import itertools
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from collections import defaultdict

np.random.seed(42)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../outputs")
os.makedirs(OUT, exist_ok=True)


# =============================================================
# 1. REEL STRIPS
# =============================================================
# Each reel is a list of symbols. The slot picks one random position
# per reel per spin. The number of times a symbol appears on a reel
# directly controls how often it lands — this is how RTP is tuned.
#
# Symbol counts (out of 20 stops per reel):
#   SEVEN  — 1 stop  → rarest, biggest payout
#   BAR    — 2 stops
#   BELL   — 3 stops
#   CHERRY — 5 stops
#   LEMON  — 9 stops → most common, no payout (blank equivalent)

REEL_1 = (
    ["SEVEN"]  * 1 +
    ["BAR"]    * 2 +
    ["BELL"]   * 3 +
    ["CHERRY"] * 5 +
    ["LEMON"]  * 9
)  # 20 stops total

REEL_2 = (
    ["SEVEN"]  * 1 +
    ["BAR"]    * 2 +
    ["BELL"]   * 4 +
    ["CHERRY"] * 4 +
    ["LEMON"]  * 9
)  # 20 stops total

REEL_3 = (
    ["SEVEN"]  * 1 +
    ["BAR"]    * 2 +
    ["BELL"]   * 3 +
    ["CHERRY"] * 5 +
    ["LEMON"]  * 9
)  # 20 stops total

REELS = [REEL_1, REEL_2, REEL_3]
REEL_SIZES = [len(r) for r in REELS]
TOTAL_COMBINATIONS = REEL_SIZES[0] * REEL_SIZES[1] * REEL_SIZES[2]  # 20^3 = 8,000


# =============================================================
# 2. PAYTABLE
# =============================================================
# Payout is expressed as a MULTIPLIER of the bet.
# e.g. ("SEVEN","SEVEN","SEVEN") pays 200x the bet.
# This is for a single payline. We have 5 paylines so total
# payout per spin = line_win * 5 (one coin per line).

PAYTABLE = {
    ("SEVEN",  "SEVEN",  "SEVEN"):  321,   # jackpot
    ("BAR",    "BAR",    "BAR"):     80,
    ("BELL",   "BELL",   "BELL"):    32,
    ("CHERRY", "CHERRY", "CHERRY"):  16,
    ("CHERRY", "CHERRY", "LEMON"):   8,   # partial cherry pays
    ("CHERRY", "CHERRY", "BAR"):     8,
    ("CHERRY", "CHERRY", "BELL"):    8,
    ("CHERRY", "CHERRY", "SEVEN"):   8,
    ("CHERRY", "LEMON",  "LEMON"):   3,
    ("CHERRY", "BAR",    "BAR"):     3,
    ("CHERRY", "BELL",   "BELL"):    3,
}

def get_payout(s1, s2, s3):
    """Look up the payout multiplier for a 3-symbol combination."""
    return PAYTABLE.get((s1, s2, s3), 0)


# =============================================================
# 3. EXACT RTP CALCULATION (Mathematical)
# =============================================================
def calculate_exact_rtp():
    """
    Enumerate every single possible spin outcome (8,000 combinations)
    and calculate the exact theoretical RTP.

    Formula:
      RTP = SUM( probability_of_outcome * payout_of_outcome )
      where probability = 1 / total_combinations for each outcome.

    This is the "math sheet" approach — what game studios do before
    building a game. The simulation later just verifies this number.
    """
    print("\n" + "=" * 55)
    print("  EXACT RTP CALCULATION")
    print("=" * 55)

    total_payout  = 0       # sum of all payouts across all outcomes
    hit_count     = 0       # how many outcomes produce a win
    win_breakdown = defaultdict(lambda: {"count": 0, "total_payout": 0})

    # Loop through every possible (reel1_pos, reel2_pos, reel3_pos)
    for i, j, k in itertools.product(
        range(REEL_SIZES[0]),
        range(REEL_SIZES[1]),
        range(REEL_SIZES[2])
    ):
        s1 = REEL_1[i]
        s2 = REEL_2[j]
        s3 = REEL_3[k]

        payout = get_payout(s1, s2, s3)
        total_payout += payout

        if payout > 0:
            hit_count += 1
            combo = f"{s1} | {s2} | {s3}"
            win_breakdown[combo]["count"]        += 1
            win_breakdown[combo]["total_payout"] += payout

    # RTP: total payout across all combos / total bet across all combos
    # Each combo costs 1 coin (1 payline × 1 coin)
    rtp           = total_payout / TOTAL_COMBINATIONS
    hit_frequency = hit_count   / TOTAL_COMBINATIONS

    print(f"\n  Total combinations : {TOTAL_COMBINATIONS:,}")
    print(f"  Winning combos     : {hit_count:,}")
    print(f"  Hit frequency      : {hit_frequency:.2%}  (1 in {1/hit_frequency:.0f} spins)")
    print(f"\n  Theoretical RTP    : {rtp:.4%}")
    print(f"  House edge         : {1 - rtp:.4%}")

    # Contribution of each symbol combo to total RTP
    print("\n  Paytable contribution to RTP:")
    print(f"  {'Combination':<35} {'Count':>6}  {'Payout':>7}  {'RTP Contrib':>10}")
    print(f"  {'-'*35} {'-'*6}  {'-'*7}  {'-'*10}")

    rows = []
    for combo, data in sorted(win_breakdown.items(),
                               key=lambda x: -x[1]["total_payout"]):
        contrib = data["total_payout"] / TOTAL_COMBINATIONS
        prob    = data["count"] / TOTAL_COMBINATIONS
        rows.append({
            "combination":    combo,
            "count":          data["count"],
            "payout_per_hit": data["total_payout"] // data["count"],
            "probability":    prob,
            "rtp_contribution": contrib,
        })
        print(f"  {combo:<35} {data['count']:>6}  "
              f"{data['total_payout']//data['count']:>6}x  {contrib:>10.4%}")

    return rtp, hit_frequency, pd.DataFrame(rows)


# =============================================================
# 4. MONTE CARLO SIMULATION
# =============================================================
def run_simulation(n_spins=1_000_000, bet_per_spin=1):
    """
    Simulate n_spins random spins and track results.

    bet_per_spin = 5 coins (1 coin × 5 paylines).
    Each payline is evaluated independently.

    Why simulate if we have exact math?
      - Verifies the math is correct
      - Shows how RTP converges over many spins (law of large numbers)
      - Produces win distribution data for volatility analysis
      - Shows realistic player session outcomes

    Law of large numbers: the more spins, the closer simulated RTP
    gets to the theoretical RTP. At 1M spins it should be within ~0.1%.
    """
    print("\n" + "=" * 55)
    print(f"  MONTE CARLO SIMULATION  ({n_spins:,} spins)")
    print("=" * 55)

    total_bet    = 0
    total_return = 0
    wins         = []
    rtp_tracker  = []   # track RTP convergence every 10K spins

    # Pre-generate all random stops for speed
    stops = np.column_stack([
        np.random.randint(0, REEL_SIZES[0], n_spins),
        np.random.randint(0, REEL_SIZES[1], n_spins),
        np.random.randint(0, REEL_SIZES[2], n_spins),
    ])

    for spin_idx in range(n_spins):
        i, j, k = stops[spin_idx]
        s1 = REEL_1[i]
        s2 = REEL_2[j]
        s3 = REEL_3[k]

        payout     = get_payout(s1, s2, s3)
        spin_win   = payout          # win in coins (per payline)
        spin_bet   = bet_per_spin    # 5 coins per spin (5 paylines)

        total_bet    += spin_bet
        total_return += spin_win
        wins.append(spin_win)

        # Track RTP every 10,000 spins for convergence chart
        if (spin_idx + 1) % 10_000 == 0:
            rtp_tracker.append({
                "spin": spin_idx + 1,
                "rtp":  total_return / total_bet
            })

    sim_rtp       = total_return / total_bet
    hit_freq      = np.mean([w > 0 for w in wins])
    avg_win       = np.mean([w for w in wins if w > 0])
    win_arr       = np.array(wins)

    print(f"\n  Spins simulated    : {n_spins:,}")
    print(f"  Total bet          : {total_bet:,} coins")
    print(f"  Total returned     : {total_return:,} coins")
    print(f"\n  Simulated RTP      : {sim_rtp:.4%}")
    print(f"  Hit frequency      : {hit_freq:.2%}")
    print(f"  Avg win (on wins)  : {avg_win:.2f}x")
    print(f"\n  Win distribution:")
    for mult in sorted(set(PAYTABLE.values()), reverse=True):
        count = np.sum(win_arr == mult)
        print(f"    {mult:>4}x payout  →  {count:>7,} times  "
              f"({count/n_spins:.3%} of spins)")

    return sim_rtp, pd.DataFrame(rtp_tracker), win_arr


# =============================================================
# 5. VOLATILITY ANALYSIS
# =============================================================
def analyse_volatility(win_arr, bet_per_spin=1, session_spins=500):
    """
    Volatility tells you how much a player's balance swings during play.

    Standard Deviation of return per spin is the core volatility metric.
    High SD = balance swings a lot (exciting but risky).
    Low SD  = balance stays steadier (less exciting but safer).

    We also simulate 10,000 player sessions of 500 spins each to show
    the realistic range of outcomes a player might experience.
    """
    print("\n" + "=" * 55)
    print("  VOLATILITY ANALYSIS")
    print("=" * 55)

    returns_per_spin = win_arr / bet_per_spin   # normalise to 1-coin bet

    sd          = np.std(returns_per_spin)
    variance    = np.var(returns_per_spin)
    skewness    = pd.Series(returns_per_spin).skew()

    print(f"\n  Std deviation (volatility) : {sd:.4f}")
    print(f"  Variance                   : {variance:.4f}")
    print(f"  Skewness                   : {skewness:.4f}  "
          f"({'right-skewed — rare big wins' if skewness > 0 else 'left-skewed'})")

    # Classify volatility
    if sd < 1.5:
        label = "LOW  — frequent small wins, steady balance"
    elif sd < 3.0:
        label = "MEDIUM"
    else:
        label = "HIGH — rare big wins, balance swings a lot"
    print(f"  Volatility classification  : {label}")

    # Simulate player sessions
    n_sessions    = 10_000
    start_balance = 500     # coins
    session_results = []

    for _ in range(n_sessions):
        balance = start_balance
        spins   = np.random.choice(win_arr, session_spins)
        bets    = bet_per_spin * session_spins
        balance = start_balance - bets + spins.sum()
        session_results.append(balance)

    session_arr = np.array(session_results)
    print(f"\n  Player session analysis ({session_spins} spins, starting {start_balance} coins):")
    print(f"    Median ending balance : {np.median(session_arr):.0f} coins")
    print(f"    Best session          : {np.max(session_arr):.0f} coins")
    print(f"    Worst session         : {np.min(session_arr):.0f} coins")
    print(f"    % sessions profitable : {np.mean(session_arr > start_balance):.1%}")

    return sd, session_arr


# =============================================================
# 6. PLOTS
# =============================================================
def plot_all(rtp_exact, hit_freq, paytable_df, rtp_tracker_df,
             win_arr, session_arr, sim_rtp):

    BG     = "#0D0F14"
    SURF   = "#141720"
    BORDER = "#1E2330"
    ACCENT = "#00D4A1"
    ACC2   = "#5B6CFF"
    WARN   = "#FF6B4A"
    TEXT   = "#E8EBF5"
    DIM    = "#7A8299"

    plt.rcParams.update({
        "text.color":       TEXT,
        "axes.labelcolor":  DIM,
        "xtick.color":      DIM,
        "ytick.color":      DIM,
        "axes.facecolor":   SURF,
        "figure.facecolor": BG,
        "axes.edgecolor":   BORDER,
        "grid.color":       BORDER,
        "axes.titlecolor":  TEXT,
    })

    fig = plt.figure(figsize=(16, 13), facecolor=BG)
    gs  = gridspec.GridSpec(2, 2, hspace=0.42, wspace=0.35,
                            top=0.92, bottom=0.07, left=0.08, right=0.97)

    # ── Panel 1: RTP Convergence ─────────────────────────────
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(rtp_tracker_df["spin"] / 1e6,
             rtp_tracker_df["rtp"] * 100,
             color=ACCENT, lw=1.5, label="Simulated RTP")
    ax1.axhline(rtp_exact * 100, color=WARN, lw=1.5,
                ls="--", label=f"Theoretical RTP = {rtp_exact:.2%}")
    ax1.axhline(sim_rtp * 100, color=ACC2, lw=1,
                ls=":", alpha=0.7, label=f"Final simulated RTP = {sim_rtp:.4%}")
    ax1.fill_between(rtp_tracker_df["spin"] / 1e6,
                     rtp_exact * 100 - 1, rtp_exact * 100 + 1,
                     color=WARN, alpha=0.07)
    ax1.set_title("RTP Convergence  –  Law of Large Numbers", fontsize=12, pad=10)
    ax1.set_xlabel("Spins (millions)", fontsize=10)
    ax1.set_ylabel("RTP %", fontsize=10)
    ax1.legend(fontsize=9, framealpha=0.2)
    ax1.grid(True, alpha=0.25)

    # ── Panel 2: Paytable RTP Contribution ───────────────────
    ax2 = fig.add_subplot(gs[1, 0])
    top = paytable_df.sort_values("rtp_contribution", ascending=True).tail(8)
    bars = ax2.barh(top["combination"], top["rtp_contribution"] * 100,
                    color=ACC2, height=0.5)
    for bar, v in zip(bars, top["rtp_contribution"] * 100):
        ax2.text(v + 0.05, bar.get_y() + bar.get_height()/2,
                 f"{v:.2f}%", va="center", fontsize=8, color=TEXT)
    ax2.set_title("RTP Contribution by Symbol Combination", fontsize=11, pad=10)
    ax2.set_xlabel("Contribution to total RTP %", fontsize=9)
    ax2.grid(True, axis="x", alpha=0.2)

    # ── Panel 3: Player Session Outcomes ─────────────────────
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.hist(session_arr, bins=60, color=ACCENT, alpha=0.8,
             edgecolor=BORDER, linewidth=0.3)
    ax3.axvline(100, color=WARN, lw=1.5, ls="--", label="Starting balance")
    ax3.axvline(np.median(session_arr), color=ACC2, lw=1.5,
                ls="--", label=f"Median = {np.median(session_arr):.0f}")
    ax3.set_title("Player Session Outcomes\n(10,000 sessions × 500 spins)", fontsize=11, pad=10)
    ax3.set_xlabel("Ending balance (coins)", fontsize=9)
    ax3.set_ylabel("Number of sessions", fontsize=9)
    ax3.legend(fontsize=9, framealpha=0.2)
    ax3.grid(True, alpha=0.2)

    fig.suptitle(
        f"3-Reel Slot  ·  Theoretical RTP {rtp_exact:.2%}  "
        f"·  Hit Frequency {hit_freq:.2%}  ·  1,000,000 Spin Simulation",
        fontsize=12, color=TEXT, fontweight="bold"
    )

    out = os.path.join(OUT, "slot_analysis.png")
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close()
    print(f"\n  Chart saved → {out}")


# =============================================================
# 7. MAIN
# =============================================================
def main():
    print("\n" + "=" * 55)
    print("  3-REEL SLOT MACHINE  –  GAME MATH MODEL")
    print("=" * 55)

    print("\nReel configuration:")
    for i, reel in enumerate(REELS, 1):
        counts = {s: reel.count(s) for s in set(reel)}
        print(f"  Reel {i} ({len(reel)} stops): {counts}")

    # Step 1: Exact math
    rtp_exact, hit_freq, paytable_df = calculate_exact_rtp()

    # Step 2: Simulation
    sim_rtp, rtp_tracker_df, win_arr = run_simulation(n_spins=1_000_000)

    # Step 3: Verify math vs simulation agree
    diff = abs(rtp_exact - sim_rtp)
    print(f"\n  Math vs Simulation difference: {diff:.4%}  "
          f"({'✓ Good agreement' if diff < 0.005 else '✗ Check reel config'})")

    # Step 4: Volatility
    sd, session_arr = analyse_volatility(win_arr)

    # Step 5: Save outputs
    paytable_df.to_csv(os.path.join(OUT, "paytable_analysis.csv"), index=False)
    rtp_tracker_df.to_csv(os.path.join(OUT, "rtp_convergence.csv"), index=False)

    summary = {
        "theoretical_rtp":  f"{rtp_exact:.4%}",
        "simulated_rtp":    f"{sim_rtp:.4%}",
        "house_edge":       f"{1 - rtp_exact:.4%}",
        "hit_frequency":    f"{hit_freq:.4%}",
        "volatility_sd":    f"{sd:.4f}",
        "total_combos":     TOTAL_COMBINATIONS,
    }
    pd.DataFrame([summary]).to_csv(os.path.join(OUT, "summary.csv"), index=False)

    # Step 6: Plot
    plot_all(rtp_exact, hit_freq, paytable_df,
             rtp_tracker_df, win_arr, session_arr, sim_rtp)

    print("\n── Output Files ──")
    for f in ["slot_analysis.png", "paytable_analysis.csv",
              "rtp_convergence.csv", "summary.csv"]:
        print(f"  outputs/{f}")

    print("\n── Summary ──")
    for k, v in summary.items():
        print(f"  {k:<22} {v}")

    print("\nDone.")


if __name__ == "__main__":
    main()
