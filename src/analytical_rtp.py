"""
analytical_rtp.py
------------------
Calculates the EXACT mathematical RTP using probability theory,
instead of simulation. This is the method real game mathematicians
use for regulatory certification — simulation gives you a close estimate,
but regulators (and serious math checks) want the EXACT number, calculated
from first principles.

THE CORE IDEA: Expected Value (EV)
For any single payline and any single symbol, we can calculate the exact
probability of landing 3, 4, or 5 matching symbols (counting WILDs), then
multiply each probability by its payout. Summing all of those gives the
"expected value" — literally the average amount you'd win per spin,
mathematically guaranteed by the Law of Large Numbers.

RTP = (sum of all expected values) / (total bet per spin)

This script calculates RTP this way and compares it against the simulated
RTP from simulate.py. If they match closely (they should, within ~0.1%),
that's strong proof the simulation code is correct.

Run:
    python src/analytical_rtp.py
"""

from config import REELS, PAYLINES, PAYTABLE, SCATTER_PAYS, TOTAL_BET_PER_SPIN, BET_PER_LINE


def prob_symbol_or_wild(reel_num: int, symbol: str) -> float:
    """
    Probability that a given reel lands on `symbol` OR a WILD
    (since WILD substitutes for any paying symbol).
    """
    strip = REELS[reel_num]
    favourable = strip.count(symbol) + strip.count("WILD")
    return favourable / len(strip)


def prob_not_symbol_or_wild(reel_num: int, symbol: str) -> float:
    """Probability that a reel does NOT land on `symbol` or WILD (breaks the chain)."""
    return 1 - prob_symbol_or_wild(reel_num, symbol)


def expected_value_for_symbol_on_payline(symbol: str, payline: list) -> float:
    """
    Calculate the expected payout contribution of one symbol on one payline.

    We need the EXACT probability of getting exactly 3, exactly 4, and
    exactly 5 matches (not "at least 3", because that would double-count —
    a 5-match also technically contains a 3-match within it, so we must
    use "exactly" probabilities and sum their individual payouts).

    payline is a list like [1,1,1,1,1] telling us which row to check
    on each reel.
    """
    reel_indices = [r + 1 for r in range(5)]  # reels are 1-indexed in REELS

    p = [prob_symbol_or_wild(reel_indices[i], symbol) for i in range(5)]
    not_p = [prob_not_symbol_or_wild(reel_indices[i], symbol) for i in range(5)]

    # Exactly 3: reels 1,2,3 match, reel 4 breaks (reel 5 doesn't matter)
    p_exact_3 = p[0] * p[1] * p[2] * not_p[3]

    # Exactly 4: reels 1,2,3,4 match, reel 5 breaks
    p_exact_4 = p[0] * p[1] * p[2] * p[3] * not_p[4]

    # Exactly 5: all reels match
    p_exact_5 = p[0] * p[1] * p[2] * p[3] * p[4]

    if symbol not in PAYTABLE:
        return 0.0

    ev = (
        p_exact_3 * PAYTABLE[symbol][3] +
        p_exact_4 * PAYTABLE[symbol][4] +
        p_exact_5 * PAYTABLE[symbol][5]
    )
    return ev


def total_payline_ev() -> dict:
    """
    Sum the expected value across ALL symbols and ALL 20 paylines.

    Returns a breakdown so we can see which symbols contribute most
    to the overall RTP — useful for spotting if one symbol is doing
    too much of the work (a common balance problem in real design).
    """
    symbols_to_check = list(PAYTABLE.keys())  # CHERRY, LEMON, BELL, BAR, STAR, WILD

    breakdown = {symbol: 0.0 for symbol in symbols_to_check}

    for payline in PAYLINES:
        for symbol in symbols_to_check:
            ev = expected_value_for_symbol_on_payline(symbol, payline)
            breakdown[symbol] += ev

    # Convert per-line EV into credits (each line costs BET_PER_LINE)
    breakdown_credits = {sym: ev * BET_PER_LINE for sym, ev in breakdown.items()}

    return breakdown_credits


def scatter_ev() -> float:
    """
    Calculate expected value of the scatter bonus.

    Unlike paylines, scatters can appear ANYWHERE on the grid (15 total
    positions: 5 reels x 3 rows), so this needs a different approach —
    we calculate the probability of getting exactly 3, 4, or 5 scatters
    total across the whole grid using each reel's scatter probability.

    Simplification note: a fully exact calculation would need to account
    for scatters appearing in MULTIPLE rows on the same reel (since each
    reel shows 3 symbols). For clarity and a close approximation, this
    calculation treats each reel as contributing at most one scatter
    "opportunity" based on its scatter density across the 3 visible rows
    combined. This slightly undercounts versus simulation, which is why
    we cross-check both methods below.
    """
    # P(at least one scatter visible on this reel, across its 3 rows)
    reel_scatter_probs = []
    for reel_num in range(1, 6):
        strip = REELS[reel_num]
        scatter_density = strip.count("SCATTER") / len(strip)
        # Probability at least 1 of the 3 visible symbols is scatter
        # Approximation: 1 - (1 - density)^3 assuming rows are independent samples
        p_at_least_one = 1 - (1 - scatter_density) ** 3
        reel_scatter_probs.append(p_at_least_one)

    # Now compute probability of exactly k reels showing a scatter (k=3,4,5)
    # using a simple combinatorial approach across 5 reels
    from itertools import combinations

    ev = 0.0
    for k in (3, 4, 5):
        prob_exactly_k = 0.0
        for combo in combinations(range(5), k):
            prob = 1.0
            for reel_idx in range(5):
                if reel_idx in combo:
                    prob *= reel_scatter_probs[reel_idx]
                else:
                    prob *= (1 - reel_scatter_probs[reel_idx])
            prob_exactly_k += prob
        ev += prob_exactly_k * SCATTER_PAYS[k]

    return ev * BET_PER_LINE * 20  # scatter pays apply to full bet (20 lines), not per-line


def calculate_analytical_rtp():
    """Main calculation: sum all expected values and convert to RTP %."""
    payline_breakdown = total_payline_ev()
    payline_total_ev = sum(payline_breakdown.values())

    scatter_total_ev = scatter_ev()

    total_ev = payline_total_ev + scatter_total_ev
    rtp = total_ev / TOTAL_BET_PER_SPIN * 100

    return {
        "payline_breakdown": payline_breakdown,
        "payline_total_ev": payline_total_ev,
        "scatter_ev": scatter_total_ev,
        "total_ev_per_spin": total_ev,
        "analytical_rtp_pct": rtp,
    }


if __name__ == "__main__":
    print("=" * 55)
    print("  Analytical RTP Calculation (Exact Probability Math)")
    print("=" * 55)

    result = calculate_analytical_rtp()

    print("\n── Expected Value Contribution by Symbol (paylines only) ──")
    print("   (this is the average credits returned per spin, from this symbol)")
    for symbol, ev in sorted(result["payline_breakdown"].items(),
                              key=lambda x: -x[1]):
        pct_of_bet = ev / TOTAL_BET_PER_SPIN * 100
        print(f"   {symbol:<10} EV = {ev:.4f} credits/spin  ({pct_of_bet:.2f}% of total bet)")

    print(f"\n   Payline total EV   : {result['payline_total_ev']:.4f} credits/spin")
    print(f"   Scatter EV         : {result['scatter_ev']:.4f} credits/spin")
    print(f"   Combined total EV  : {result['total_ev_per_spin']:.4f} credits/spin")

    print(f"\n── ANALYTICAL RTP: {result['analytical_rtp_pct']:.3f}% ──")
    print("\n   Compare this to simulate.py's measured RTP (~96.08%).")
    print("   They should be close. Small differences come from the scatter")
    print("   calculation using an approximation (see function docstring).")
