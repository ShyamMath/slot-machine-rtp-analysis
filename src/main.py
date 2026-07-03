"""
Run the full model: exact RTP, Monte Carlo verification, volatility, charts.

    python src/main.py
"""

import os
import pandas as pd

from config import REELS, TOTAL_COMBINATIONS, BET_PER_SPIN
from analytical import calculate_exact_rtp
from simulate import run_simulation, analyse_volatility
from plotting import plot_results

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outputs")
os.makedirs(OUT, exist_ok=True)


def main():
    print("3-REEL SLOT MACHINE — GAME MATH MODEL\n")

    # 1. Exact math
    exact = calculate_exact_rtp()
    print(f"Theoretical RTP    : {exact['rtp']:.4%}")
    print(f"House edge         : {1 - exact['rtp']:.4%}")
    print(f"Hit frequency      : {exact['hit_frequency']:.2%} "
          f"(1 in {1 / exact['hit_frequency']:.1f} spins)")

    # 2. Simulation
    n_spins = 1_000_000
    sim = run_simulation(n_spins=n_spins)
    print(f"\nSimulated RTP ({n_spins:,} spins) : {sim['sim_rtp']:.4%}")
    diff = abs(exact["rtp"] - sim["sim_rtp"])
    print(f"Math vs simulation gap             : {diff:.4%} "
          f"({'OK' if diff < 0.005 else 'CHECK REEL CONFIG'})")

    # 3. Volatility + player sessions
    vol = analyse_volatility(sim["wins"])
    print(f"\nVolatility (std dev) : {vol['std_dev']:.2f} — {vol['volatility_label']}")
    print(f"Sessions ending in profit (10,000 x 500 spins) : {vol['pct_profitable']:.1%}")

    # 4. Save outputs
    exact["paytable_df"].to_csv(os.path.join(OUT, "paytable_analysis.csv"), index=False)
    sim["rtp_tracker"].to_csv(os.path.join(OUT, "rtp_convergence.csv"), index=False)

    summary = pd.DataFrame([{
        "theoretical_rtp": f"{exact['rtp']:.4%}",
        "simulated_rtp": f"{sim['sim_rtp']:.4%}",
        "house_edge": f"{1 - exact['rtp']:.4%}",
        "hit_frequency": f"{exact['hit_frequency']:.4%}",
        "volatility_sd": f"{vol['std_dev']:.4f}",
        "total_combinations": TOTAL_COMBINATIONS,
    }])
    summary.to_csv(os.path.join(OUT, "summary.csv"), index=False)

    plot_results(
        exact["rtp"], exact["hit_frequency"], exact["paytable_df"],
        sim["rtp_tracker"], sim["sim_rtp"], vol["ending_balance"],
        start_balance=500, out_path=os.path.join(OUT, "slot_analysis.png"),
    )

    print("\nOutputs written to outputs/: slot_analysis.png, paytable_analysis.csv, "
          "rtp_convergence.csv, summary.csv")


if __name__ == "__main__":
    main()
