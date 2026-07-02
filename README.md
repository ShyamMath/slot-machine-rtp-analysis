# Slot Machine — Game Math Model

A complete mathematical model for a 3-reel, 5-payline slot machine. Built as a portfolio project for Game Mathematician roles in the iGaming industry.

---

## What this project covers

The two things every Game Mathematician must be able to do:

1. **Prove the RTP mathematically** — enumerate every possible outcome, multiply by its probability, sum them up. No guessing. Exact numbers.

2. **Verify with simulation** — run 1,000,000 random spins and confirm the simulated RTP converges to the theoretical one. This is the Law of Large Numbers in practice.

---

## Game design

**Reel configuration** — 3 reels, 20 stops each (8,000 total combinations)

| Symbol | Reel 1 | Reel 2 | Reel 3 |
|--------|--------|--------|--------|
| SEVEN  | 1      | 1      | 1      |
| BAR    | 2      | 2      | 2      |
| BELL   | 3      | 4      | 3      |
| CHERRY | 5      | 4      | 5      |
| LEMON  | 9      | 9      | 9      |

The number of stops per symbol is how you control RTP. More stops = higher probability = more impact on RTP. LEMON has 9 stops but pays nothing — it's the blank equivalent.

**Paytable**

| Combination | Payout | Probability | RTP Contribution |
|---|---|---|---|
| SEVEN \| SEVEN \| SEVEN | 321x | 1/8000 | 4.01% |
| BAR \| BAR \| BAR | 80x | 8/8000 | 8.00% |
| BELL \| BELL \| BELL | 32x | 36/8000 | 14.40% |
| CHERRY \| CHERRY \| CHERRY | 16x | 100/8000 | 20.00% |
| CHERRY \| CHERRY \| any | 8x | various | 28.75% |
| CHERRY \| any \| any | 3x | various | 19.44% |

---

## Results

| Metric | Value |
|---|---|
| **Theoretical RTP** | **94.60%** |
| Simulated RTP (1M spins) | 94.42% |
| Math vs simulation gap | 0.18% ✓ |
| House edge | 5.40% |
| Hit frequency | 11.63% (1 in 9 spins) |
| Volatility (std dev) | 5.46 — HIGH |
| Sessions ending in profit | 31.9% |

The 0.18% gap between theoretical and simulated RTP is entirely expected — it's random variance that disappears further toward infinity. At 10M spins it would be ~0.05%.

---

## Key concepts explained

**RTP (Return to Player)**
If RTP = 94.6%, a player betting R$1,000 over a long session gets back ~R$946 on average. The casino keeps ~R$54. This is an average over millions of spins, not a guarantee per session.

**House edge**
100% - RTP = 5.4%. This is the casino's profit margin per coin wagered.

**Hit frequency**
11.63% means roughly 1 in every 9 spins produces any win. Between wins, a player goes through ~8 losing spins on average.

**Volatility**
This game has HIGH volatility (std dev 5.46). That means player balances swing a lot during play. In 10,000 simulated sessions of 500 spins, only 31.9% ended in profit. The rest lost — but some wins were very large (jackpot 321x). High volatility games are more exciting but riskier for players.

**Law of large numbers**
The RTP convergence chart shows the simulated RTP starting wild (sometimes 200%, sometimes 20%) in the first few thousand spins, then steadily settling toward 94.6% as spins accumulate. This is why casinos make money — individual players experience high variance, but the casino's aggregate result is predictable.

---

## How to run

```bash
# Install dependencies
pip install pandas numpy matplotlib

# Run the model
python src/slot_math.py
```

Outputs go to `outputs/`.

---

## Project structure

```
slot-math-model/
├── src/
│   └── slot_math.py          ← full model: math + simulation + charts
├── outputs/
│   ├── slot_analysis.png     ← RTP convergence + paytable + session chart
│   ├── paytable_analysis.csv ← each winning combo, probability, RTP contribution
│   ├── rtp_convergence.csv   ← RTP tracked every 10,000 spins
│   └── summary.csv           ← key metrics
└── README.md
```

---

## Things I would extend with more time

- **Multi-payline evaluation** — check all 5 paylines per spin independently (increases hit frequency)
- **Wild symbols** — wilds substitute for any symbol; requires updating the combo evaluation logic
- **Bonus trigger math** — scatter symbols triggering free spins; track bonus contribution to overall RTP separately
- **Player session risk modelling** — ruin probability: given a starting bankroll of X coins, what's the probability of going broke before N spins?
- **Math sheet** — formal Excel-style document with variance, 95th percentile outcomes, max win cap — standard deliverable in the industry

---

## Tech stack

Python 3 · NumPy · pandas · matplotlib · itertools
