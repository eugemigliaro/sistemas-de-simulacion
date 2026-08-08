#include "tp1/benchmark.hpp"

#include <chrono>
#include <iomanip>
#include <limits>
#include <ostream>
#include <stdexcept>

#include "tp1/neighbors.hpp"

namespace tp1 {
namespace {

NeighborSearchResult search_for_m(
    const ParticleSystem& system,
    double cutoff,
    std::size_t cells_per_side
) {
    if (cells_per_side == 1) {
        return brute_force_neighbors(system, cutoff);
    }
    return cell_index_neighbors(system, cutoff, cells_per_side);
}

void require_same_neighbors(
    const NeighborSearchResult& actual,
    const NeighborSearchResult& expected
) {
    if (actual.pair_count != expected.pair_count
        || actual.neighbors != expected.neighbors) {
        throw std::runtime_error{
            "Cell Index Method result differs from brute force"
        };
    }
}

std::string_view boundary_name(BoundaryCondition boundary) {
    switch (boundary) {
        case BoundaryCondition::Walls:
            return "walls";
        case BoundaryCondition::Periodic:
            return "periodic";
    }
    throw std::invalid_argument{"unknown boundary condition"};
}

}  // namespace

std::string_view benchmark_method_name(BenchmarkMethod method) noexcept {
    switch (method) {
        case BenchmarkMethod::BruteForce:
            return "brute_force";
        case BenchmarkMethod::CellIndex:
            return "cim";
    }
    return "unknown";
}

std::vector<BenchmarkMeasurement> benchmark_m(
    const ParticleSystem& system,
    double cutoff,
    std::size_t repetitions
) {
    if (repetitions == 0) {
        throw std::invalid_argument{"repetitions must be positive"};
    }

    const NeighborSearchResult oracle = brute_force_neighbors(system, cutoff);
    const std::size_t maximum_m = maximum_valid_cells_per_side(
        system,
        cutoff
    );
    if (maximum_m
        > std::numeric_limits<std::size_t>::max() / repetitions) {
        throw std::invalid_argument{"too many benchmark measurements"};
    }

    std::vector<BenchmarkMeasurement> measurements{};
    measurements.reserve(maximum_m * repetitions);

    for (std::size_t cells_per_side = 1;
         cells_per_side <= maximum_m;
         ++cells_per_side) {
        const BenchmarkMethod method = cells_per_side == 1
            ? BenchmarkMethod::BruteForce
            : BenchmarkMethod::CellIndex;

        const NeighborSearchResult validation = search_for_m(
            system,
            cutoff,
            cells_per_side
        );
        require_same_neighbors(validation, oracle);

        const NeighborSearchResult warmup = search_for_m(
            system,
            cutoff,
            cells_per_side
        );
        require_same_neighbors(warmup, oracle);

        for (std::size_t repetition = 1;
             repetition <= repetitions;
             ++repetition) {
            const auto start = std::chrono::steady_clock::now();
            const NeighborSearchResult result = search_for_m(
                system,
                cutoff,
                cells_per_side
            );
            const auto end = std::chrono::steady_clock::now();
            const auto elapsed =
                std::chrono::duration_cast<std::chrono::nanoseconds>(
                    end - start
                );

            require_same_neighbors(result, oracle);
            measurements.push_back(BenchmarkMeasurement{
                .method = method,
                .cells_per_side = cells_per_side,
                .repetition = repetition,
                .time_ns = elapsed.count(),
                .neighbor_pairs = result.pair_count,
                .distance_evaluations = result.distance_evaluations,
            });
        }
    }
    return measurements;
}

void write_benchmark_csv(
    std::ostream& output,
    std::uint64_t seed,
    const ParticleSystem& system,
    double cutoff,
    const std::vector<BenchmarkMeasurement>& measurements
) {
    output << "seed,boundary,method,N,L,M,rc,repetition,time_ns,"
              "neighbor_pairs,distance_evaluations\n"
           << std::setprecision(std::numeric_limits<double>::max_digits10);

    for (const BenchmarkMeasurement& measurement : measurements) {
        output << seed << ','
               << boundary_name(system.domain.boundary) << ','
               << benchmark_method_name(measurement.method) << ','
               << system.particles.size() << ','
               << system.domain.side << ','
               << measurement.cells_per_side << ','
               << cutoff << ','
               << measurement.repetition << ','
               << measurement.time_ns << ','
               << measurement.neighbor_pairs << ','
               << measurement.distance_evaluations << '\n';
    }
    if (!output) {
        throw std::runtime_error{"could not write benchmark data"};
    }
}

}  // namespace tp1
