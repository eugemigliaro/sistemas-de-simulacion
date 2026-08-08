#include <algorithm>
#include <cstddef>
#include <sstream>
#include <string>

#include "tp1/benchmark.hpp"
#include "tp1/generation.hpp"
#include "tp1/neighbors.hpp"
#include "test_support.hpp"

namespace {

tp1::ParticleSystem generated_system() {
    return tp1::generate_system(tp1::GenerationConfig{
        .particle_count = 40,
        .domain = {
            .side = 10.0,
            .boundary = tp1::BoundaryCondition::Walls,
        },
        .min_radius = 0.2,
        .max_radius = 0.2,
        .property = 1.0,
        .seed = 42,
        .max_attempts_per_particle = 100'000,
    });
}

void test_maximum_valid_m() {
    const tp1::ParticleSystem generated = generated_system();
    EXPECT_TRUE(tp1::maximum_valid_cells_per_side(generated, 0.5) == 11);

    const tp1::ParticleSystem exact_limit{
        .domain = {
            .side = 10.0,
            .boundary = tp1::BoundaryCondition::Walls,
        },
        .time = 0.0,
        .particles = {
            tp1::Particle{
                .id = 1,
                .position = {.x = 1.0, .y = 1.0},
                .velocity = {},
                .radius = 0.5,
                .property = 1.0,
            },
            tp1::Particle{
                .id = 2,
                .position = {.x = 4.0, .y = 4.0},
                .velocity = {},
                .radius = 0.5,
                .property = 1.0,
            },
        },
    };
    EXPECT_TRUE(
        tp1::maximum_valid_cells_per_side(exact_limit, 1.0) == 4
    );

    tp1::ParticleSystem short_periodic = exact_limit;
    short_periodic.domain = {
        .side = 1.0,
        .boundary = tp1::BoundaryCondition::Periodic,
    };
    short_periodic.particles[0].position = {.x = 0.1, .y = 0.1};
    short_periodic.particles[1].position = {.x = 0.8, .y = 0.8};
    EXPECT_TRUE(
        tp1::maximum_valid_cells_per_side(short_periodic, 1.0) == 1
    );
}

void test_benchmark_measurements() {
    const tp1::ParticleSystem system = generated_system();
    const std::size_t maximum_m = tp1::maximum_valid_cells_per_side(
        system,
        0.5
    );
    const std::vector<tp1::BenchmarkMeasurement> measurements =
        tp1::benchmark_m(system, 0.5, 2);

    EXPECT_TRUE(measurements.size() == maximum_m * 2);
    const std::size_t expected_pairs = measurements.front().neighbor_pairs;

    for (std::size_t index = 0; index < measurements.size(); ++index) {
        const tp1::BenchmarkMeasurement& measurement = measurements[index];
        const std::size_t expected_m = index / 2 + 1;
        const std::size_t expected_repetition = index % 2 + 1;

        EXPECT_TRUE(measurement.cells_per_side == expected_m);
        EXPECT_TRUE(measurement.repetition == expected_repetition);
        EXPECT_TRUE(measurement.time_ns >= 0);
        EXPECT_TRUE(measurement.neighbor_pairs == expected_pairs);
        EXPECT_TRUE(measurement.method == (
            expected_m == 1
                ? tp1::BenchmarkMethod::BruteForce
                : tp1::BenchmarkMethod::CellIndex
        ));
    }

    EXPECT_TRUE(
        measurements.front().distance_evaluations
        == system.particles.size() * (system.particles.size() - 1) / 2
    );
    EXPECT_TRUE(
        measurements.back().distance_evaluations
        < measurements.front().distance_evaluations
    );
}

void test_csv_output() {
    const tp1::ParticleSystem system = generated_system();
    const std::vector<tp1::BenchmarkMeasurement> measurements =
        tp1::benchmark_m(system, 0.5, 2);
    std::ostringstream output{};
    tp1::write_benchmark_csv(output, 42, system, 0.5, measurements);

    const std::string csv = output.str();
    EXPECT_TRUE(csv.starts_with(
        "seed,boundary,method,N,L,M,rc,repetition,time_ns,"
        "neighbor_pairs,distance_evaluations\n"
    ));
    EXPECT_TRUE(
        static_cast<std::size_t>(std::count(csv.begin(), csv.end(), '\n'))
        == measurements.size() + 1
    );
    EXPECT_TRUE(csv.find("42,walls,brute_force,40,10,1,0.5,1,")
                != std::string::npos);
    EXPECT_TRUE(csv.find("42,walls,cim,40,10,2,0.5,1,")
                != std::string::npos);
}

void test_invalid_benchmark() {
    const tp1::ParticleSystem system = generated_system();
    EXPECT_INVALID_ARGUMENT(tp1::benchmark_m(system, 0.5, 0));
    EXPECT_INVALID_ARGUMENT(tp1::maximum_valid_cells_per_side(system, -1.0));
}

}  // namespace

int main() {
    test_maximum_valid_m();
    test_benchmark_measurements();
    test_csv_output();
    test_invalid_benchmark();
    return test::finish("Benchmark tests");
}
