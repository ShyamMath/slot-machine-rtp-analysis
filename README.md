# Slot Machine — Game Math Model

A complete mathematical model for a 3-reel, single-payline slot machine. Built
as a portfolio project for Game Mathematician roles in the iGaming industry.

## What this project covers

The two things every Game Mathematician must prove:

1. **Exact RTP** — enumerate all 8,000 possible outcomes and their
   probabilities. No sampling, no error bars.
2. **Simulated RTP** — run 1,000,000 random spins and confirm it converges
   to the theoretical value (Law of Large Numbers).

The simulation core is also ported to **C++** to show the same math running
at production-loop speed — see [Python vs C++](#python-vs-c).

## Game design

3 reels, 20 stops each (8,000 total combinations), 1 payline.

| Symbol | Reel 1 | Reel 2 | Reel 3 |
|---|---|---|---|
| SEVEN  | 1 | 1 | 1 |
| BAR    | 2 | 2 | 2 |
| BELL   | 3 | 4 | 3 |
| CHERRY | 5 | 4 | 5 |
| LEMON  | 9 | 9 | 9 |

More stops on a symbol = higher probability = more RTP impact. LEMON is the
blank equivalent: common, pays nothing.

**Paytable** (multiplier of a 1-coin bet)

| Combination | Payout | Probability | RTP Contribution |
|---|---|---|---|
| SEVEN · SEVEN · SEVEN | 321x | 1/8,000 | 4.01% |
| BAR · BAR · BAR | 80x | 8/8,000 | 8.00% |
| BELL · BELL · BELL | 32x | 36/8,000 | 14.40% |
| CHERRY · CHERRY · CHERRY | 16x | 100/8,000 | 20.00% |
| CHERRY · CHERRY · (other) | 8x | various | 28.75% |
| CHERRY · (other) · (other) | 3x | various | 19.44% |

## Results

| Metric | Value |
|---|---|
| Theoretical RTP | **94.60%** |
| Simulated RTP (1M spins) | 94.42% |
| Math vs simulation gap | 0.18% ✓ |
| House edge | 5.40% |
| Hit frequency | 11.62% (1 in ~8.6 spins) |
| Volatility (std dev) | 5.35 — HIGH |
| Sessions ending in profit (10,000 × 500 spins) | 32.2% |

The gap between theoretical and simulated RTP is expected variance — it
shrinks as spin count grows (~0.05% at 10M spins).

## Key concepts

- **RTP** — % of wagered money returned to players over the long run. At
  94.6% RTP, a player betting 1,000 coins gets back ~946 on average.
- **House edge** — `100% − RTP`. The operator's margin per coin wagered.
- **Hit frequency** — % of spins that produce any win.
- **Volatility** — how much balances swing during play. High volatility =
  rare, large wins; low volatility = frequent, small wins.
- **Law of Large Numbers** — simulated RTP is noisy over the first few
  thousand spins, then settles toward the theoretical value as spins
  accumulate. This is why the house edge is reliable in aggregate even
  though any single player's result is unpredictable.

## Python vs C++

`simulate.py`'s spin loop is fully vectorized with NumPy; `cpp/slot_sim.cpp`
is the same reels, same paytable, same RNG approach, compiled. Benchmarked
at 10,000,000 spins on this machine:

| Implementation | Time | Spins/sec | RTP |
|---|---|---|---|
| Python (NumPy, vectorized) | 3.06 s | ~3.3M/s | 94.72% |
| C++ (`-O3`) | 0.25 s | ~40.6M/s | 94.58% |

This mirrors how studios actually split the work: **Python for design,
analysis, and reporting** (fast to iterate on, easy to read), **C++ for the
simulation core** when a model needs to run inside the production game
engine or be stress-tested at very high spin counts.

## How to run

**Python — full model, exact math, charts, CSVs:**
```bash
pip install numpy pandas matplotlib
python src/main.py
```
Outputs go to `outputs/`.

**C++ — simulation core only, for speed:**
```bash
cd cpp
g++ -O3 -std=c++17 -o slot_sim slot_sim.cpp
./slot_sim 10000000        # spin count is optional, defaults to 10M
```
Writes `outputs/cpp_simulation_summary.csv`.

## Project structure

```
slot-machine-math/
├── src/
│   ├── config.py       # reel strips, paytable — the game design
│   ├── analytical.py   # exact RTP via full enumeration
│   ├── simulate.py      # Monte Carlo verification + volatility/session risk
│   ├── plotting.py      # results chart
│   └── main.py          # runs everything, saves outputs
├── cpp/
│   └── slot_sim.cpp     # C++ port of the simulation core, for speed
├── outputs/
│   ├── slot_analysis.png
│   ├── paytable_analysis.csv
│   ├── rtp_convergence.csv
│   ├── summary.csv
│   └── cpp_simulation_summary.csv
└── README.md
```

## Things I'd extend with more time

- **Multi-payline evaluation** — check several paylines per spin independently
- **Wild symbols** — substitute for any symbol, requires updating combo evaluation
- **Bonus trigger math** — scatters triggering free spins, tracked separately in RTP
- **Ruin probability** — given a starting bankroll, probability of going broke before N spins
- **Formal math sheet** — Excel-style deliverable with variance, percentile outcomes, win cap — the standard regulatory submission format

## Tech stack

Python 3 · NumPy · pandas · matplotlib · C++17
