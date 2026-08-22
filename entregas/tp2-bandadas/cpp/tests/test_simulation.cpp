#include <cmath>
#include <cstdint>
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

void test_voter_can_copy_self_or_neighbor() {
    bool copied_self = false;
    bool copied_neighbor = false;
    for (std::uint64_t seed = 0; seed < 100; ++seed) {
        tp2::System system{
            .side = 10.0,
            .particles = {
                particle(1, 5.0, 5.0, 0.0),
                particle(2, 5.2, 5.0, std::numbers::pi_v<double> / 2.0),
            },
        };
        const auto neighbors = tp2::brute_force_neighbors(system, 1.0).neighbors;
        const tp2::DynamicsConfig config{
            .model = tp2::AlignmentModel::Voter,
            .cutoff = 1.0,
            .speed = 0.03,
            .time_step = 1.0,
            .eta = 0.0,
        };
        std::mt19937_64 generator{seed};
        tp2::advance(system, neighbors, config, generator);
        copied_self = copied_self || std::abs(system.particles[0].angle) < 1e-12;
        copied_neighbor = copied_neighbor || std::abs(
            system.particles[0].angle - std::numbers::pi_v<double> / 2.0
        ) < 1e-12;
    }
    EXPECT_TRUE(copied_self);
    EXPECT_TRUE(copied_neighbor);
}

void test_noise_uses_normalized_eta_amplitude() {
    constexpr double eta = 0.25;
    constexpr double amplitude = eta * std::numbers::pi_v<double>;
    bool saw_positive = false;
    bool saw_negative = false;
    for (std::uint64_t seed = 0; seed < 100; ++seed) {
        tp2::System system{
            .side = 10.0,
            .particles = {particle(1, 5.0, 5.0, 0.0)},
        };
        const tp2::NeighborList neighbors(1);
        const tp2::DynamicsConfig config{
            .model = tp2::AlignmentModel::Vicsek,
            .cutoff = 1.0,
            .speed = 0.03,
            .time_step = 1.0,
            .eta = eta,
        };
        std::mt19937_64 generator{seed};
        tp2::advance(system, neighbors, config, generator);
        const double angle = system.particles[0].angle;
        EXPECT_TRUE(angle >= -amplitude && angle <= amplitude);
        saw_positive = saw_positive || angle > 0.0;
        saw_negative = saw_negative || angle < 0.0;
    }
    EXPECT_TRUE(saw_positive);
    EXPECT_TRUE(saw_negative);
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
    test_voter_can_copy_self_or_neighbor();
    test_noise_uses_normalized_eta_amplitude();
    test_generation_is_reproducible();
    return test::finish("Simulation tests");
}
