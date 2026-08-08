#include <array>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <vector>

#include "tp1/generation.hpp"
#include "tp1/neighbors.hpp"
#include "test_support.hpp"

namespace {

tp1::Particle particle(
    std::size_t id,
    double x,
    double y,
    double radius = 0.2
) {
    return tp1::Particle{
        .id = id,
        .position = {.x = x, .y = y},
        .velocity = {},
        .radius = radius,
        .property = 1.0,
    };
}

void expect_matches_brute_force(
    const tp1::ParticleSystem& system,
    double cutoff,
    std::size_t cells_per_side
) {
    const tp1::NeighborSearchResult brute =
        tp1::brute_force_neighbors(system, cutoff);
    const tp1::NeighborSearchResult cell_index =
        tp1::cell_index_neighbors(system, cutoff, cells_per_side);

    EXPECT_TRUE(cell_index.neighbors == brute.neighbors);
    EXPECT_TRUE(cell_index.pair_count == brute.pair_count);
    EXPECT_TRUE(tp1::is_valid_neighbor_list(cell_index.neighbors));
    EXPECT_TRUE(
        cell_index.distance_evaluations <= brute.distance_evaluations
    );
}

void test_same_and_adjacent_cells_with_walls() {
    const tp1::ParticleSystem system{
        .domain = {
            .side = 12.0,
            .boundary = tp1::BoundaryCondition::Walls,
        },
        .time = 0.0,
        .particles = {
            particle(1, 2.8, 2.8),
            particle(2, 3.2, 2.8),
            particle(3, 2.8, 3.2),
            particle(4, 3.2, 3.2),
            particle(5, 10.0, 10.0),
        },
    };

    const tp1::NeighborSearchResult result =
        tp1::cell_index_neighbors(system, 0.5, 4);

    EXPECT_TRUE(result.neighbors[0] == std::vector<std::size_t>({2, 3, 4}));
    EXPECT_TRUE(result.neighbors[1] == std::vector<std::size_t>({1, 3, 4}));
    EXPECT_TRUE(result.neighbors[2] == std::vector<std::size_t>({1, 2, 4}));
    EXPECT_TRUE(result.neighbors[3] == std::vector<std::size_t>({1, 2, 3}));
    EXPECT_TRUE(result.neighbors[4].empty());
    EXPECT_TRUE(result.pair_count == 6);
    expect_matches_brute_force(system, 0.5, 4);
}

void test_strict_cutoff_across_cells() {
    const tp1::ParticleSystem system{
        .domain = {
            .side = 10.0,
            .boundary = tp1::BoundaryCondition::Walls,
        },
        .time = 0.0,
        .particles = {
            particle(1, 2.9, 5.0, 0.25),
            particle(2, 3.9, 5.0, 0.25),
        },
    };

    const tp1::NeighborSearchResult exact =
        tp1::cell_index_neighbors(system, 0.5, 3);
    EXPECT_TRUE(exact.neighbors[0].empty());
    EXPECT_TRUE(exact.neighbors[1].empty());

    const tp1::NeighborSearchResult above =
        tp1::cell_index_neighbors(system, 0.500001, 3);
    EXPECT_TRUE(above.neighbors[0] == std::vector<std::size_t>{2});
    EXPECT_TRUE(above.neighbors[1] == std::vector<std::size_t>{1});
}

void test_periodic_small_grids_without_duplicate_pairs() {
    const tp1::ParticleSystem system{
        .domain = {
            .side = 10.0,
            .boundary = tp1::BoundaryCondition::Periodic,
        },
        .time = 0.0,
        .particles = {
            particle(1, 0.2, 0.2),
            particle(2, 9.8, 0.2),
            particle(3, 0.2, 9.8),
            particle(4, 9.8, 9.8),
        },
    };

    const tp1::NeighborSearchResult one_cell =
        tp1::cell_index_neighbors(system, 0.5, 1);
    EXPECT_TRUE(one_cell.distance_evaluations == 6);
    EXPECT_TRUE(one_cell.pair_count == 6);
    expect_matches_brute_force(system, 0.5, 1);

    const tp1::NeighborSearchResult four_cells =
        tp1::cell_index_neighbors(system, 0.5, 2);
    EXPECT_TRUE(four_cells.distance_evaluations == 6);
    EXPECT_TRUE(four_cells.pair_count == 6);
    expect_matches_brute_force(system, 0.5, 2);
}

void test_cell_count_validation() {
    const tp1::ParticleSystem system{
        .domain = {
            .side = 10.0,
            .boundary = tp1::BoundaryCondition::Walls,
        },
        .time = 0.0,
        .particles = {
            particle(1, 1.0, 1.0, 0.5),
            particle(2, 4.0, 4.0, 0.5),
        },
    };

    expect_matches_brute_force(system, 1.0, 4);
    EXPECT_INVALID_ARGUMENT(tp1::cell_index_neighbors(system, 1.0, 0));
    EXPECT_INVALID_ARGUMENT(tp1::cell_index_neighbors(system, 1.0, 5));
    EXPECT_INVALID_ARGUMENT(tp1::cell_index_neighbors(system, 1.0, 6));
    EXPECT_INVALID_ARGUMENT(tp1::cell_index_neighbors(system, -0.1, 1));
    EXPECT_INVALID_ARGUMENT(tp1::cell_index_neighbors(
        system,
        std::numeric_limits<double>::infinity(),
        1
    ));

    tp1::ParticleSystem short_periodic = system;
    short_periodic.domain = {
        .side = 1.0,
        .boundary = tp1::BoundaryCondition::Periodic,
    };
    short_periodic.particles = {
        particle(1, 0.1, 0.1, 0.2),
        particle(2, 0.8, 0.8, 0.2),
    };
    expect_matches_brute_force(short_periodic, 0.8, 1);
}

void test_generated_systems_match_brute_force() {
    constexpr std::array<tp1::BoundaryCondition, 2> boundaries{
        tp1::BoundaryCondition::Walls,
        tp1::BoundaryCondition::Periodic,
    };
    constexpr std::array<std::uint64_t, 4> seeds{
        0,
        1,
        42,
        20'260'807,
    };
    constexpr std::array<std::size_t, 5> cell_counts{1, 2, 5, 10, 13};

    for (tp1::BoundaryCondition boundary : boundaries) {
        for (std::uint64_t seed : seeds) {
            const tp1::GenerationConfig config{
                .particle_count = 120,
                .domain = {.side = 20.0, .boundary = boundary},
                .min_radius = 0.23,
                .max_radius = 0.26,
                .property = 1.0,
                .seed = seed,
                .max_attempts_per_particle = 100'000,
            };
            const tp1::ParticleSystem system = tp1::generate_system(config);

            for (std::size_t cells_per_side : cell_counts) {
                expect_matches_brute_force(system, 1.0, cells_per_side);
            }

            const tp1::NeighborSearchResult brute =
                tp1::brute_force_neighbors(system, 1.0);
            const tp1::NeighborSearchResult fine_grid =
                tp1::cell_index_neighbors(system, 1.0, 13);
            EXPECT_TRUE(
                fine_grid.distance_evaluations
                < brute.distance_evaluations
            );
        }
    }
}

}  // namespace

int main() {
    test_same_and_adjacent_cells_with_walls();
    test_strict_cutoff_across_cells();
    test_periodic_small_grids_without_duplicate_pairs();
    test_cell_count_validation();
    test_generated_systems_match_brute_force();
    return test::finish("Cell index tests");
}
