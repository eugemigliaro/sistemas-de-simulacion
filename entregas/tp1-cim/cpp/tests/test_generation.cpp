#include <cstddef>

#include "tp1/generation.hpp"
#include "tp1/geometry.hpp"
#include "test_support.hpp"

namespace {

tp1::GenerationConfig config_for(tp1::BoundaryCondition boundary) {
    return tp1::GenerationConfig{
        .particle_count = 80,
        .domain = {.side = 20.0, .boundary = boundary},
        .min_radius = 0.23,
        .max_radius = 0.26,
        .property = 1.0,
        .seed = 20260807,
        .max_attempts_per_particle = 100'000,
    };
}

void expect_same_system(
    const tp1::ParticleSystem& first,
    const tp1::ParticleSystem& second
) {
    EXPECT_TRUE(first.domain.side == second.domain.side);
    EXPECT_TRUE(first.domain.boundary == second.domain.boundary);
    EXPECT_TRUE(first.time == second.time);
    EXPECT_TRUE(first.particles.size() == second.particles.size());

    for (std::size_t index = 0; index < first.particles.size(); ++index) {
        const tp1::Particle& left = first.particles[index];
        const tp1::Particle& right = second.particles[index];
        EXPECT_TRUE(left.id == right.id);
        EXPECT_TRUE(left.position.x == right.position.x);
        EXPECT_TRUE(left.position.y == right.position.y);
        EXPECT_TRUE(left.velocity.x == right.velocity.x);
        EXPECT_TRUE(left.velocity.y == right.velocity.y);
        EXPECT_TRUE(left.radius == right.radius);
        EXPECT_TRUE(left.property == right.property);
    }
}

void test_generation(tp1::BoundaryCondition boundary) {
    const tp1::GenerationConfig config = config_for(boundary);
    const tp1::ParticleSystem first = tp1::generate_system(config);
    const tp1::ParticleSystem second = tp1::generate_system(config);

    EXPECT_TRUE(first.particles.size() == config.particle_count);
    EXPECT_FALSE(tp1::has_overlaps(first));
    expect_same_system(first, second);

    for (std::size_t index = 0; index < first.particles.size(); ++index) {
        const tp1::Particle& particle = first.particles[index];
        EXPECT_TRUE(particle.id == index + 1);
        EXPECT_TRUE(particle.radius >= config.min_radius);
        EXPECT_TRUE(particle.radius <= config.max_radius);
        EXPECT_TRUE(particle.property == config.property);
        EXPECT_TRUE(particle.velocity.x == 0.0);
        EXPECT_TRUE(particle.velocity.y == 0.0);
        EXPECT_TRUE(tp1::is_inside_domain(particle, first.domain));
    }

    tp1::GenerationConfig other_seed = config;
    ++other_seed.seed;
    const tp1::ParticleSystem different = tp1::generate_system(other_seed);
    EXPECT_FALSE(
        first.particles.front().position.x
        == different.particles.front().position.x
    );
}

void test_invalid_configuration() {
    tp1::GenerationConfig config = config_for(tp1::BoundaryCondition::Walls);
    EXPECT_TRUE(tp1::is_valid(config));

    config.particle_count = 0;
    EXPECT_FALSE(tp1::is_valid(config));
    EXPECT_INVALID_ARGUMENT(tp1::generate_system(config));

    config = config_for(tp1::BoundaryCondition::Walls);
    config.min_radius = -0.1;
    EXPECT_FALSE(tp1::is_valid(config));

    config = config_for(tp1::BoundaryCondition::Walls);
    config.max_radius = config.domain.side;
    EXPECT_FALSE(tp1::is_valid(config));

    config = config_for(tp1::BoundaryCondition::Walls);
    config.max_attempts_per_particle = 0;
    EXPECT_FALSE(tp1::is_valid(config));
}

void test_impossible_placement_fails() {
    const tp1::GenerationConfig config{
        .particle_count = 2,
        .domain = {
            .side = 1.0,
            .boundary = tp1::BoundaryCondition::Walls,
        },
        .min_radius = 0.5,
        .max_radius = 0.5,
        .property = 1.0,
        .seed = 1,
        .max_attempts_per_particle = 3,
    };
    EXPECT_RUNTIME_ERROR(tp1::generate_system(config));
}

}  // namespace

int main() {
    test_generation(tp1::BoundaryCondition::Walls);
    test_generation(tp1::BoundaryCondition::Periodic);
    test_invalid_configuration();
    test_impossible_placement_fails();
    return test::finish("Generation tests");
}
