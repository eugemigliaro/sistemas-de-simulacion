#include <numbers>
#include <random>

#include "test_support.hpp"
#include "tp2/neighbors.hpp"
#include "tp2/simulation.hpp"

namespace {

tp2::Particle particle(std::size_t id, double x, double y, double angle) {
    return tp2::Particle{
        .id = id,
        .position = {.x = x, .y = y},
        .angle = angle,
    };
}

void test_vicsek_is_synchronous_and_moves_with_old_angle() {
    tp2::System system{
        .side = 10.0,
        .particles = {
            particle(1, 5.0, 5.0, 0.0),
            particle(2, 5.2, 5.0, std::numbers::pi_v<double> / 2.0),
        },
    };
    const auto neighbors = tp2::brute_force_neighbors(system, 1.0).neighbors;
    const tp2::DynamicsConfig config{
        .model = tp2::AlignmentModel::Vicsek,
        .cutoff = 1.0,
        .speed = 0.03,
        .time_step = 1.0,
        .eta = 0.0,
    };
    std::mt19937_64 generator{7};
    tp2::advance(system, neighbors, config, generator);

    EXPECT_NEAR(system.particles[0].position.x, 5.03, 1e-12);
    EXPECT_NEAR(system.particles[0].position.y, 5.0, 1e-12);
    EXPECT_NEAR(system.particles[1].position.x, 5.2, 1e-12);
    EXPECT_NEAR(system.particles[1].position.y, 5.03, 1e-12);
    EXPECT_NEAR(
        system.particles[0].angle,
        std::numbers::pi_v<double> / 4.0,
        1e-12
    );
    EXPECT_NEAR(
        system.particles[1].angle,
        std::numbers::pi_v<double> / 4.0,
        1e-12
    );
}

void test_voter_includes_self_for_isolated_particle() {
    tp2::System system{
        .side = 10.0,
        .particles = {
            particle(1, 9.99, 4.0, std::numbers::pi_v<double> / 6.0),
        },
    };
    const tp2::NeighborList neighbors(1);
    const tp2::DynamicsConfig config{
        .model = tp2::AlignmentModel::Voter,
        .cutoff = 1.0,
        .speed = 0.03,
        .time_step = 1.0,
        .eta = 0.0,
    };
    std::mt19937_64 generator{42};
    tp2::advance(system, neighbors, config, generator);
    EXPECT_NEAR(
        system.particles[0].angle,
        std::numbers::pi_v<double> / 6.0,
        1e-12
    );
}

void test_generation_is_reproducible() {
    const tp2::InitializationConfig config{
        .particle_count = 20,
        .side = 10.0,
        .seed = 1234,
    };
    EXPECT_TRUE(tp2::generate_system(config) == tp2::generate_system(config));
}

}  // namespace

int main() {
    test_vicsek_is_synchronous_and_moves_with_old_angle();
    test_voter_includes_self_for_isolated_particle();
    test_generation_is_reproducible();
    return test::finish("Simulation tests");
}
