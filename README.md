# Slot Machine RTP Model

Math model for a 3-reel, single-payline slot machine: exact RTP proof, Monte Carlo verification, and a C++ port of the simulation core.

## Game design

3 reels, 20 stops each, 8,000 total combinations, 1 payline.

| Symbol | Reel 1 | Reel 2 | Reel 3 |
|---|---|---|---|
| SEVEN  | 1 | 1 | 1 |
| BAR    | 2 | 2 | 2 |
| BELL   | 3 | 4 | 3 |
| CHERRY | 5 | 4 | 5 |
| LEMON  | 9 | 9 | 9 |

More stops = higher probability = more RTP impact. LEMON pays nothing (blank equivalent).

**Paytable** (multiplier of a 1-coin bet)

| Combination | Payout | Probability | RTP Contribution |
|---|---|---|---|
| SEVEN . SEVEN . SEVEN | 321x | 1/8,000 | 4.01% |
| BAR . BAR . BAR | 80x | 8/8,000 | 8.00% |
| BELL . BELL . BELL | 32x | 36/8,000 | 14.40% |
| CHERRY . CHERRY . CHERRY | 16x | 100/8,000 | 20.00% |
| CHERRY . CHERRY . other | 8x | various | 28.75% |
| CHERRY . other . other | 3x | various | 19.44% |

## Results

| Metric | Value |
|---|---|
| Theoretical RTP | 94.60% |
| Simulated RTP (1M spins) | 94.42% |
| Math vs simulation gap | 0.18% |
| House edge | 5.40% |
| Hit frequency | 11.62% (1 in ~8.6 spins) |
| Volatility (std dev) | 5.35, high |
| Sessions ending in profit (10,000 x 500 spins) | 32.2% |

Gap between theoretical and simulated RTP shrinks with spin count (~0.05% at 10M spins).

## Python vs C++

Same reels, same paytable, both implementations. Benchmarked at 10,000,000 spins:

| Implementation | Time | Spins/sec | RTP |
|---|---|---|---|
| Python (NumPy, vectorized) | 3.06 s | 3.3M/s | 94.72% |
| C++ (-O3) | 0.25 s | 40.6M/s | 94.58% |

Python handles design, exact-RTP proof, and reporting. C++ is the spin loop, for when a model needs to run at production speed or be stress-tested at high spin counts.

## Run

Python (full model, exact math, charts, CSVs):
```bash
pip install numpy pandas matplotlib
python src/main.py
```

C++ (simulation core only):
```bash
cd cpp
g++ -O3 -std=c++17 -o slot_sim slot_sim.cpp
./slot_sim 10000000
```

## Structureb · C++17
