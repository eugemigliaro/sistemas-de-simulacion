#include <cstddef>
#include <cstdint>
#include <vector>

#include "test_support.hpp"
#include "tp2/neighbors.hpp"
#include "tp2/simulation.hpp"

namespace {

tp2::Particle particle(std::size_t id, double x, double y) {
    return tp2::Particle{
        .id = id,
        .position = {.x = x, .y = y},
        .angle = 0.0,
    };
}

void expect_matches(const tp2::System& system, double cutoff, std::size_t m) {
    const auto brute = tp2::brute_force_neighbors(system, cutoff);
    const auto cim = tp2::cell_index_neighbors(system, cutoff, m);
    EXPECT_TRUE(cim.neighbors == brute.neighbors);
    EXPECT_TRUE(cim.pair_count == brute.pair_count);
    EXPECT_TRUE(tp2::is_valid_neighbor_list(cim.neighbors));
}

void test_periodic_neighbors() {
    const tp2::System system{
        .side = 10.0,
        .particles = {
            particle(1, 0.2, 0.2),
            particle(2, 9.8, 0.2),
            particle(3, 5.0, 5.0),
        },
    };
    const auto result = tp2::cell_index_neighbors(system, 0.5, 9);
    EXPECT_TRUE(result.neighbors[0] == std::vector<std::size_t>{1});
    EXPECT_TRUE(result.neighbors[1] == std::vector<std::size_t>{0});
    EXPECT_TRUE(result.neighbors[2].empty());
    expect_matches(system, 0.5, 9);
}

void test_small_periodic_grids_and_validation() {
    const tp2::System system{
        .side = 10.0,
        .particles = {
            particle(1, 0.1, 0.1),
            particle(2, 9.9, 0.1),
            particle(3, 0.1, 9.9),
            particle(4, 9.9, 9.9),
        },
    };
    expect_matches(system, 0.5, 1);
    expect_matches(system, 0.5, 2);
    EXPECT_TRUE(tp2::maximum_valid_cells_per_side(system, 1.0) == 9);
    EXPECT_INVALID_ARGUMENT(tp2::cell_index_neighbors(system, 1.0, 10));
}

void test_generated_systems_match_brute_force() {
    constexpr std::uint64_t seeds[]{0, 1, 42, 20260821};
    constexpr std::size_t cell_counts[]{1, 2, 5, 9};
    for (std::uint64_t seed : seeds) {
        const tp2::System system = tp2::generate_system(
            tp2::InitializationConfig{
                .particle_count = 200,
                .side = 10.0,
                .seed = seed,
            }
        );
        for (std::size_t cells_per_side : cell_counts) {
            expect_matches(system, 1.0, cells_per_side);
        }
        const auto brute = tp2::brute_force_neighbors(system, 1.0);
        const auto cim = tp2::cell_index_neighbors(system, 1.0, 9);
        EXPECT_TRUE(cim.distance_evaluations < brute.distance_evaluations);
    }
}

}  // namespace

int main() {
    test_periodic_neighbors();
    test_small_periodic_grids_and_validation();
    test_generated_systems_match_brute_force();
    return test::finish("Neighbor tests");
}
