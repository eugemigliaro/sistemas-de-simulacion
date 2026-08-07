#include <cstddef>
#include <limits>
#include <sstream>

#include "tp1/io.hpp"
#include "tp1/neighbors.hpp"
#include "test_support.hpp"

namespace {

tp1::Particle particle(
    std::size_t id,
    double x,
    double y,
    double radius = 0.25
) {
    return tp1::Particle{
        .id = id,
        .position = {.x = x, .y = y},
        .velocity = {},
        .radius = radius,
        .property = 1.0,
    };
}

tp1::ParticleSystem wall_system() {
    return tp1::ParticleSystem{
        .domain = {
            .side = 10.0,
            .boundary = tp1::BoundaryCondition::Walls,
        },
        .time = 0.0,
        .particles = {
            particle(1, 1.0, 1.0),
            particle(2, 1.5, 1.0),
            particle(3, 3.0, 1.0),
            particle(4, 8.0, 8.0),
        },
    };
}

void test_wall_search_and_strict_cutoff() {
    const tp1::ParticleSystem system = wall_system();
    const tp1::NeighborSearchResult exact =
        tp1::brute_force_neighbors(system, 1.0);

    EXPECT_TRUE(exact.neighbors.size() == 4);
    EXPECT_TRUE(exact.neighbors[0] == std::vector<std::size_t>{2});
    EXPECT_TRUE(exact.neighbors[1] == std::vector<std::size_t>{1});
    EXPECT_TRUE(exact.neighbors[2].empty());
    EXPECT_TRUE(exact.neighbors[3].empty());
    EXPECT_TRUE(exact.pair_count == 1);
    EXPECT_TRUE(exact.distance_evaluations == 6);
    EXPECT_TRUE(tp1::is_valid_neighbor_list(exact.neighbors));
    EXPECT_TRUE(tp1::count_neighbor_pairs(exact.neighbors) == 1);

    const tp1::NeighborSearchResult above =
        tp1::brute_force_neighbors(system, 1.000001);
    EXPECT_TRUE(above.neighbors[1] == std::vector<std::size_t>({1, 3}));
    EXPECT_TRUE(above.neighbors[2] == std::vector<std::size_t>{2});
    EXPECT_TRUE(above.pair_count == 2);
}

void test_periodic_search() {
    const tp1::ParticleSystem periodic{
        .domain = {
            .side = 10.0,
            .boundary = tp1::BoundaryCondition::Periodic,
        },
        .time = 0.0,
        .particles = {
            particle(1, 0.2, 5.0, 0.2),
            particle(2, 9.6, 5.0, 0.2),
            particle(3, 5.0, 5.0, 0.2),
        },
    };
    const tp1::NeighborSearchResult periodic_result =
        tp1::brute_force_neighbors(periodic, 0.25);
    EXPECT_TRUE(periodic_result.neighbors[0] == std::vector<std::size_t>{2});
    EXPECT_TRUE(periodic_result.neighbors[1] == std::vector<std::size_t>{1});
    EXPECT_TRUE(periodic_result.neighbors[2].empty());

    tp1::ParticleSystem walls = periodic;
    walls.domain.boundary = tp1::BoundaryCondition::Walls;
    walls.particles[0].position.x = 0.25;
    const tp1::NeighborSearchResult wall_result =
        tp1::brute_force_neighbors(walls, 0.25);
    EXPECT_TRUE(wall_result.pair_count == 0);
}

void test_sorted_symmetric_output() {
    const tp1::NeighborList neighbors{
        {2},
        {1, 3},
        {2},
        {},
    };
    EXPECT_TRUE(tp1::is_valid_neighbor_list(neighbors));
    EXPECT_TRUE(tp1::count_neighbor_pairs(neighbors) == 2);

    std::ostringstream output{};
    tp1::write_neighbors(output, neighbors);
    EXPECT_TRUE(output.str() == "1,2\n2,1,3\n3,2\n4\n");

    EXPECT_FALSE(tp1::is_valid_neighbor_list({{2}, {}}));
    EXPECT_FALSE(tp1::is_valid_neighbor_list({{2, 2}, {1}}));
    EXPECT_FALSE(tp1::is_valid_neighbor_list({{1}}));
    EXPECT_FALSE(tp1::is_valid_neighbor_list({{3}, {}}));
    EXPECT_INVALID_ARGUMENT(tp1::count_neighbor_pairs({{2}, {}}));

    std::ostringstream invalid_output{};
    EXPECT_INVALID_ARGUMENT(tp1::write_neighbors(
        invalid_output,
        tp1::NeighborList{{2}, {}}
    ));
}

void test_invalid_search_inputs() {
    const tp1::ParticleSystem valid = wall_system();
    EXPECT_INVALID_ARGUMENT(tp1::brute_force_neighbors(valid, -0.1));
    EXPECT_INVALID_ARGUMENT(tp1::brute_force_neighbors(
        valid,
        std::numeric_limits<double>::infinity()
    ));

    tp1::ParticleSystem invalid = valid;
    invalid.particles[1].id = 1;
    EXPECT_INVALID_ARGUMENT(tp1::brute_force_neighbors(invalid, 1.0));

    invalid = valid;
    invalid.particles[0].position.x = 0.0;
    EXPECT_INVALID_ARGUMENT(tp1::brute_force_neighbors(invalid, 1.0));
}

}  // namespace

int main() {
    test_wall_search_and_strict_cutoff();
    test_periodic_search();
    test_sorted_symmetric_output();
    test_invalid_search_inputs();
    return test::finish("Neighbor tests");
}
