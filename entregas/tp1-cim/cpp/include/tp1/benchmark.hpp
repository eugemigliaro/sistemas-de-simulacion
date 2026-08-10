#pragma once

#include <cstddef>
#include <cstdint>
#include <iosfwd>
#include <string_view>
#include <vector>

#include "tp1/model.hpp"
#include "tp1/generation.hpp"

namespace tp1 {

enum class BenchmarkMethod {
    BruteForce,
    CellIndex,
};

struct BenchmarkMeasurement {
    BenchmarkMethod method{BenchmarkMethod::BruteForce};
    std::size_t cells_per_side{};
    std::size_t repetition{};
    std::int64_t time_ns{};
    std::size_t neighbor_pairs{};
    std::size_t distance_evaluations{};
};

struct SeededBenchmarkMeasurement {
    std::uint64_t seed{};
    BenchmarkMeasurement measurement{};
};

[[nodiscard]] std::string_view benchmark_method_name(
    BenchmarkMethod method
) noexcept;

[[nodiscard]] std::vector<BenchmarkMeasurement> benchmark_m(
    const ParticleSystem& system,
    double cutoff,
    std::size_t repetitions
);

[[nodiscard]] std::vector<BenchmarkMeasurement> benchmark_n(
    const ParticleSystem& system,
    double cutoff,
    std::size_t cells_per_side,
    std::size_t repetitions
);

[[nodiscard]] std::vector<SeededBenchmarkMeasurement> benchmark_random_m(
    GenerationConfig config,
    double cutoff,
    std::size_t repetitions
);

[[nodiscard]] std::vector<SeededBenchmarkMeasurement> benchmark_random_n(
    GenerationConfig config,
    double cutoff,
    std::size_t cells_per_side,
    std::size_t repetitions
);

void write_benchmark_csv(
    std::ostream& output,
    std::uint64_t seed,
    const ParticleSystem& system,
    double cutoff,
    const std::vector<BenchmarkMeasurement>& measurements
);

void write_seeded_benchmark_csv(
    std::ostream& output,
    const GenerationConfig& config,
    double cutoff,
    const std::vector<SeededBenchmarkMeasurement>& measurements
);

}  // namespace tp1
