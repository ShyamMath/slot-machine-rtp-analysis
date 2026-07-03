import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

BG, SURF, BORDER = "#0D0F14", "#141720", "#1E2330"
ACCENT, ACCENT2, WARN = "#00D4A1", "#5B6CFF", "#FF6B4A"
TEXT, DIM = "#E8EBF5", "#7A8299"


def plot_results(rtp_exact, hit_freq, paytable_df, rtp_tracker, sim_rtp,
                  ending_balance, start_balance, out_path):
    plt.rcParams.update({
        "text.color": TEXT, "axes.labelcolor": DIM, "xtick.color": DIM,
        "ytick.color": DIM, "axes.facecolor": SURF, "figure.facecolor": BG,
        "axes.edgecolor": BORDER, "grid.color": BORDER, "axes.titlecolor": TEXT,
    })

    fig = plt.figure(figsize=(16, 13), facecolor=BG)
    gs = gridspec.GridSpec(2, 2, hspace=0.42, wspace=0.35,
                            top=0.92, bottom=0.07, left=0.08, right=0.97)

    # RTP convergence
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(rtp_tracker["spin"] / 1e6, rtp_tracker["rtp"] * 100,
              color=ACCENT, lw=1.5, label="Simulated RTP")
    ax1.axhline(rtp_exact * 100, color=WARN, lw=1.5, ls="--",
                label=f"Theoretical RTP = {rtp_exact:.2%}")
    ax1.set_title("RTP Convergence — Law of Large Numbers", fontsize=12, pad=10)
    ax1.set_xlabel("Spins (millions)")
    ax1.set_ylabel("RTP %")
    ax1.legend(fontsize=9, framealpha=0.2)
    ax1.grid(True, alpha=0.25)

    # Paytable contribution
    ax2 = fig.add_subplot(gs[1, 0])
    top = paytable_df.sort_values("rtp_contribution").tail(8)
    bars = ax2.barh(top["combination"], top["rtp_contribution"] * 100, color=ACCENT2, height=0.5)
    for bar, v in zip(bars, top["rtp_contribution"] * 100):
        ax2.text(v + 0.05, bar.get_y() + bar.get_height() / 2, f"{v:.2f}%",
                  va="center", fontsize=8, color=TEXT)
    ax2.set_title("RTP Contribution by Combination", fontsize=11, pad=10)
    ax2.set_xlabel("Contribution to RTP %")
    ax2.grid(True, axis="x", alpha=0.2)

    # Player session outcomes
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.hist(ending_balance, bins=60, color=ACCENT, alpha=0.8, edgecolor=BORDER, linewidth=0.3)
    ax3.axvline(start_balance, color=WARN, lw=1.5, ls="--", label="Starting balance")
    ax3.axvline(np.median(ending_balance), color=ACCENT2, lw=1.5, ls="--",
                label=f"Median = {np.median(ending_balance):.0f}")
    ax3.set_title("Player Session Outcomes\n(10,000 sessions × 500 spins)", fontsize=11, pad=10)
    ax3.set_xlabel("Ending balance (coins)")
    ax3.set_ylabel("Sessions")
    ax3.legend(fontsize=9, framealpha=0.2)
    ax3.grid(True, alpha=0.2)

    fig.suptitle(
        f"3-Reel Slot · Theoretical RTP {rtp_exact:.2%} · Hit Frequency {hit_freq:.2%} "
        f"· Simulated RTP {sim_rtp:.2%}",
        fontsize=12, color=TEXT, fontweight="bold"
    )

    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=BG)
    plt.close()
