#include <sstream>
#include <string>

#include "tp1/generation.hpp"
#include "tp1/io.hpp"
#include "test_support.hpp"

namespace {

tp1::ParticleSystem read(
    const std::string& static_data,
    const std::string& dynamic_data,
    tp1::BoundaryCondition boundary = tp1::BoundaryCondition::Walls
) {
    std::istringstream static_input{static_data};
    std::istringstream dynamic_input{dynamic_data};
    return tp1::read_system(static_input, dynamic_input, boundary);
}

void test_round_trip() {
    const tp1::GenerationConfig config{
        .particle_count = 25,
        .domain = {
            .side = 10.0,
            .boundary = tp1::BoundaryCondition::Periodic,
        },
        .min_radius = 0.23,
        .max_radius = 0.26,
        .property = 7.5,
        .seed = 42,
        .max_attempts_per_particle = 10'000,
    };
    tp1::ParticleSystem original = tp1::generate_system(config);
    original.time = 12.5;
    original.particles.front().velocity = {.x = -1.25, .y = 2.5};

    std::ostringstream static_output{};
    std::ostringstream dynamic_output{};
    tp1::write_static(static_output, original);
    tp1::write_dynamic(dynamic_output, original);

    const tp1::ParticleSystem restored = read(
        static_output.str(),
        dynamic_output.str(),
        tp1::BoundaryCondition::Periodic
    );

    EXPECT_TRUE(restored.domain.side == original.domain.side);
    EXPECT_TRUE(restored.domain.boundary == original.domain.boundary);
    EXPECT_TRUE(restored.time == original.time);
    EXPECT_TRUE(restored.particles.size() == original.particles.size());
    for (std::size_t index = 0; index < original.particles.size(); ++index) {
        const tp1::Particle& expected = original.particles[index];
        const tp1::Particle& actual = restored.particles[index];
        EXPECT_TRUE(actual.id == expected.id);
        EXPECT_TRUE(actual.position.x == expected.position.x);
        EXPECT_TRUE(actual.position.y == expected.position.y);
        EXPECT_TRUE(actual.velocity.x == expected.velocity.x);
        EXPECT_TRUE(actual.velocity.y == expected.velocity.y);
        EXPECT_TRUE(actual.radius == expected.radius);
        EXPECT_TRUE(actual.property == expected.property);
    }
}

void test_two_column_dynamic_format() {
    const tp1::ParticleSystem system = read(
        "2\n10\n0.5 1\n0.25 2\n",
        "3.5\n1 1\n9.5 9.5\n"
    );

    EXPECT_TRUE(system.particles.size() == 2);
    EXPECT_TRUE(system.time == 3.5);
    EXPECT_TRUE(system.particles[0].velocity.x == 0.0);
    EXPECT_TRUE(system.particles[0].velocity.y == 0.0);
    EXPECT_TRUE(system.particles[1].property == 2.0);
}

void test_invalid_inputs() {
    EXPECT_INVALID_ARGUMENT(read(
        "0\n10\n",
        "0\n"
    ));
    EXPECT_INVALID_ARGUMENT(read(
        "1.5\n10\n0.5 1\n",
        "0\n1 1\n"
    ));
    EXPECT_INVALID_ARGUMENT(read(
        "184467440737095516160\n10\n",
        "0\n"
    ));
    EXPECT_INVALID_ARGUMENT(read(
        "1\n10\n0.5 1\n",
        "0\n1 1 0\n"
    ));
    EXPECT_INVALID_ARGUMENT(read(
        "1\n10\n0 1\n",
        "0\n1 1\n"
    ));
    EXPECT_INVALID_ARGUMENT(read(
        "1\n10\n0.5 1\nextra\n",
        "0\n1 1\n"
    ));
    EXPECT_INVALID_ARGUMENT(read(
        "1\n10\n0.5 1\n",
        "0\n0.25 1\n"
    ));
    EXPECT_INVALID_ARGUMENT(read(
        "2\n10\n0.5 1\n0.5 1\n",
        "0\n1 1\n"
    ));
}

void test_invalid_output_system() {
    const tp1::ParticleSystem invalid{};
    std::ostringstream output{};
    EXPECT_INVALID_ARGUMENT(tp1::write_static(output, invalid));
    EXPECT_INVALID_ARGUMENT(tp1::write_dynamic(output, invalid));
}

}  // namespace

int main() {
    test_round_trip();
    test_two_column_dynamic_format();
    test_invalid_inputs();
    test_invalid_output_system();
    return test::finish("I/O tests");
}
