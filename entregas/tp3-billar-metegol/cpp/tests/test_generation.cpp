#include <cmath>
#include <stdexcept>
#include <vector>

#include "test_support.hpp"
#include "tp3/generation.hpp"
#include "tp3/geometry.hpp"

namespace {

constexpr double tolerance = 1e-12;

tp3::InitializationConfig config(std::size_t count, std::uint64_t seed) {
    return tp3::InitializationConfig{
        .particle_count = count,
        .table = {},
        .particle_radius = tp3::default_particle_radius,
        .particle_mass = tp3::default_particle_mass,
        .initial_speed = tp3::default_initial_speed,
        .seed = seed,
        .max_placement_attempts = 10000,
    };
}

tp3::Obstacle obstacle(std::size_t id, double x, double y, double radius) {
    return tp3::Obstacle{.id = id, .center = {.x = x, .y = y}, .radius = radius};
}

void expect_well_formed(const tp3::System& system, std::size_t expected_count) {
    EXPECT_TRUE(system.particles.size() == expected_count);
    EXPECT_NEAR(system.time, 0.0, tolerance);

    for (std::size_t index = 0; index < system.particles.size(); ++index) {
        const tp3::Particle& particle = system.particles[index];

        EXPECT_TRUE(particle.id == index);
        EXPECT_TRUE(tp3::is_valid(particle));
        // Todas nacen frescas [TP03, p. 2].
        EXPECT_TRUE(particle.state == tp3::ParticleState::Fresh);
        EXPECT_TRUE(particle.collision_count == 0);
        // Rapidez inicial v0 = 1 m/s para todas.
        EXPECT_NEAR(tp3::norm(particle.velocity), tp3::default_initial_speed, 1e-12);
        // Integramente dentro del dominio.
        EXPECT_TRUE(tp3::contains(system.table, particle.position, particle.radius));

        // Sin solaparse con ninguna anterior.
        for (std::size_t other = 0; other < index; ++other) {
            EXPECT_FALSE(tp3::discs_overlap(
                particle.position,
                particle.radius,
                system.particles[other].position,
                system.particles[other].radius
            ));
        }
        // Sin solaparse con los obstaculos.
        for (const tp3::Obstacle& fixed : system.obstacles) {
            EXPECT_FALSE(tp3::discs_overlap(
                particle.position,
                particle.radius,
                fixed.center,
                fixed.radius
            ));
        }
    }
}

void test_empty_table() {
    const tp3::System system = tp3::generate_system(config(100, 1), {});
    expect_well_formed(system, 100);
    EXPECT_TRUE(system.obstacles.empty());
}

void test_with_obstacles() {
    const std::vector<tp3::Obstacle> obstacles{
        obstacle(0, 0.30, 0.34, 0.06),
        obstacle(1, 0.60, 0.34, 0.06),
        obstacle(2, 0.90, 0.34, 0.06),
    };
    const tp3::System system = tp3::generate_system(config(100, 7), obstacles);
    expect_well_formed(system, 100);
    EXPECT_TRUE(system.obstacles.size() == 3);
}

// Misma semilla, misma condicion inicial; semillas distintas, distinta.
void test_reproducibility() {
    const tp3::System first = tp3::generate_system(config(20, 42), {});
    const tp3::System second = tp3::generate_system(config(20, 42), {});
    const tp3::System third = tp3::generate_system(config(20, 43), {});

    EXPECT_TRUE(first == second);
    EXPECT_FALSE(first == third);
}

void test_zero_particles_is_allowed() {
    const tp3::System system = tp3::generate_system(config(0, 1), {});
    EXPECT_TRUE(system.particles.empty());
}

// La restriccion (ii) del punto 1.2 exige radios que permitan generar las N
// particulas; una configuracion que no lo permite falla de forma explicita en
// lugar de reintentar para siempre o bajar N en silencio [TP03, p. 3].
void test_impossible_configuration_fails_loudly() {
    // Caso 1: mesa vacia pero demasiadas particulas. El area de 2000 discos
    // es 1.92 m2 contra una mesa de 0.816 m2, asi que no hay empaquetamiento
    // posible.
    tp3::InitializationConfig too_many = config(2000, 1);
    too_many.max_placement_attempts = 200;
    EXPECT_THROWS(std::runtime_error, tp3::generate_system(too_many, {}));

    // Caso 2: el obstaculo deja unos 0.37 m2 de area libre para los centros,
    // insuficiente para 400 particulas. Es la restriccion (ii) del punto 1.2.
    tp3::InitializationConfig crowded = config(400, 1);
    crowded.max_placement_attempts = 200;
    const std::vector<tp3::Obstacle> obstacles{obstacle(0, 0.60, 0.34, 0.33)};
    EXPECT_THROWS(std::runtime_error, tp3::generate_system(crowded, obstacles));
}

// Contracara del caso anterior: un obstaculo grande sigue permitiendo generar
// las 100 particulas del TP, y la generacion debe lograrlo.
void test_large_obstacle_still_allows_the_tp_configuration() {
    const std::vector<tp3::Obstacle> obstacles{obstacle(0, 0.60, 0.34, 0.33)};
    const tp3::System system = tp3::generate_system(config(100, 3), obstacles);
    expect_well_formed(system, 100);
}

void test_invalid_arguments_are_rejected() {
    tp3::InitializationConfig invalid = config(10, 1);
    invalid.max_placement_attempts = 0;
    EXPECT_INVALID_ARGUMENT(tp3::generate_system(invalid, {}));

    tp3::InitializationConfig negative_radius = config(10, 1);
    negative_radius.particle_radius = -1.0;
    EXPECT_INVALID_ARGUMENT(tp3::generate_system(negative_radius, {}));

    tp3::InitializationConfig negative_mass = config(10, 1);
    negative_mass.particle_mass = 0.0;
    EXPECT_INVALID_ARGUMENT(tp3::generate_system(negative_mass, {}));

    // Los obstaculos invalidos se rechazan antes de sortear nada.
    EXPECT_INVALID_ARGUMENT(
        tp3::generate_system(config(10, 1), {obstacle(0, 0.60, 0.34, 0.001)})
    );
}

}  // namespace

int main() {
    test_empty_table();
    test_with_obstacles();
    test_reproducibility();
    test_zero_particles_is_allowed();
    test_impossible_configuration_fails_loudly();
    test_large_obstacle_still_allows_the_tp_configuration();
    test_invalid_arguments_are_rejected();
    return test::finish("test_generation");
}
