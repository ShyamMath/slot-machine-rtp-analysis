// slot_sim.cpp
// C++ port of the Monte Carlo simulation core from src/simulate.py.
// Same reels, same paytable, same math — kept in C++ for the
// performance-critical spin loop. Python (src/) stays the source of
// truth for design, exact-RTP proof, and reporting.
//
// Build:  g++ -O3 -std=c++17 -o slot_sim slot_sim.cpp
// Run:    ./slot_sim [n_spins]

#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <random>
#include <string>
#include <vector>

enum Symbol : int { SEVEN = 0, BAR, BELL, CHERRY, LEMON, N_SYMBOLS };

// Same reel strips as config.py (20 stops each).
std::vector<int> build_reel(int seven, int bar, int bell, int cherry, int lemon) {
    std::vector<int> reel;
    reel.insert(reel.end(), seven, SEVEN);
    reel.insert(reel.end(), bar, BAR);
    reel.insert(reel.end(), bell, BELL);
    reel.insert(reel.end(), cherry, CHERRY);
    reel.insert(reel.end(), lemon, LEMON);
    return reel;
}

const std::vector<int> REEL_1 = build_reel(1, 2, 3, 5, 9);
const std::vector<int> REEL_2 = build_reel(1, 2, 4, 4, 9);
const std::vector<int> REEL_3 = build_reel(1, 2, 3, 5, 9);

// Same paytable as config.py, keyed by (s1, s2, s3).
int get_payout(int s1, int s2, int s3) {
    if (s1 == SEVEN && s2 == SEVEN && s3 == SEVEN) return 321;
    if (s1 == BAR && s2 == BAR && s3 == BAR) return 80;
    if (s1 == BELL && s2 == BELL && s3 == BELL) return 32;
    if (s1 == CHERRY && s2 == CHERRY && s3 == CHERRY) return 16;
    if (s1 == CHERRY && s2 == CHERRY) return 8;                       // CC*, any 3rd symbol
    if (s1 == CHERRY && s2 == LEMON && s3 == LEMON) return 3;
    if (s1 == CHERRY && s2 == BAR && s3 == BAR) return 3;
    if (s1 == CHERRY && s2 == BELL && s3 == BELL) return 3;
    return 0;
}

int main(int argc, char** argv) {
    const long long n_spins = (argc > 1) ? std::stoll(argv[1]) : 10'000'000;
    const int seed = 42;

    std::mt19937_64 rng(seed);
    std::uniform_int_distribution<int> d1(0, static_cast<int>(REEL_1.size()) - 1);
    std::uniform_int_distribution<int> d2(0, static_cast<int>(REEL_2.size()) - 1);
    std::uniform_int_distribution<int> d3(0, static_cast<int>(REEL_3.size()) - 1);

    long long total_payout = 0;
    long long hit_count = 0;

    auto start = std::chrono::high_resolution_clock::now();
    for (long long n = 0; n < n_spins; ++n) {
        int s1 = REEL_1[d1(rng)];
        int s2 = REEL_2[d2(rng)];
        int s3 = REEL_3[d3(rng)];
        int payout = get_payout(s1, s2, s3);
        total_payout += payout;
        hit_count += (payout > 0);
    }
    auto end = std::chrono::high_resolution_clock::now();
    double seconds = std::chrono::duration<double>(end - start).count();

    double rtp = static_cast<double>(total_payout) / static_cast<double>(n_spins);
    double hit_freq = static_cast<double>(hit_count) / static_cast<double>(n_spins);

    std::cout << "Spins simulated : " << n_spins << "\n";
    std::cout << "Simulated RTP   : " << rtp * 100 << "%\n";
    std::cout << "Hit frequency   : " << hit_freq * 100 << "%\n";
    std::cout << "Elapsed         : " << seconds << " s\n";
    std::cout << "Spins/sec       : " << static_cast<long long>(n_spins / seconds) << "\n";

    std::ofstream out("../outputs/cpp_simulation_summary.csv");
    out << "n_spins,simulated_rtp,hit_frequency,elapsed_seconds,spins_per_second\n";
    out << n_spins << "," << rtp << "," << hit_freq << "," << seconds << ","
        << static_cast<long long>(n_spins / seconds) << "\n";

    return 0;
}
