#include <vector>

#include "test_support.hpp"
#include "tp3/geometry.hpp"

namespace {

constexpr double tolerance = 1e-12;

tp3::Obstacle obstacle(std::size_t id, double x, double y, double radius) {
    return tp3::Obstacle{.id = id, .center = {.x = x, .y = y}, .radius = radius};
}

tp3::Particle particle(std::size_t id, double x, double y) {
    return tp3::Particle{
        .id = id,
        .position = {.x = x, .y = y},
        .velocity = {},
        .radius = tp3::default_particle_radius,
        .mass = tp3::default_particle_mass,
        .state = tp3::ParticleState::Fresh,
        .collision_count = 0,
    };
}

void test_vector_algebra() {
    const tp3::Vec2 left{.x = 3.0, .y = -4.0};
    const tp3::Vec2 right{.x = 1.0, .y = 2.0};

    EXPECT_NEAR(dot(left, right), -5.0, tolerance);
    EXPECT_NEAR(tp3::norm(left), 5.0, tolerance);
    EXPECT_NEAR(tp3::norm_squared(left), 25.0, tolerance);
    EXPECT_TRUE((left + right) == (tp3::Vec2{.x = 4.0, .y = -2.0}));
    EXPECT_TRUE((left - right) == (tp3::Vec2{.x = 2.0, .y = -6.0}));
    EXPECT_TRUE((2.0 * right) == (tp3::Vec2{.x = 2.0, .y = 4.0}));
}

// Con W = 0.68 y d = 0.20 el arco ocupa y en [0.24, 0.44] [TP03, p. 2].
void test_goal_span() {
    const tp3::Table table{};

    EXPECT_NEAR(tp3::goal_lower_bound(table), 0.24, tolerance);
    EXPECT_NEAR(tp3::goal_upper_bound(table), 0.44, tolerance);

    EXPECT_TRUE(tp3::is_on_goal(table, 0.34));
    EXPECT_TRUE(tp3::is_on_goal(table, 0.2401));
    EXPECT_TRUE(tp3::is_on_goal(table, 0.4399));
    EXPECT_FALSE(tp3::is_on_goal(table, 0.2399));
    EXPECT_FALSE(tp3::is_on_goal(table, 0.4401));
    EXPECT_FALSE(tp3::is_on_goal(table, 0.0));

    // El criterio coincide exactamente con las cotas expuestas. El borde
    // nominal (0.24) no es representable en doble precision y cae afuera;
    // es un caso de medida nula y no afecta la estadistica de goles.
    EXPECT_TRUE(tp3::is_on_goal(table, tp3::goal_lower_bound(table)));
    EXPECT_TRUE(tp3::is_on_goal(table, tp3::goal_upper_bound(table)));
}

void test_containment() {
    const tp3::Table table{};
    const double radius = tp3::default_particle_radius;

    EXPECT_TRUE(tp3::contains(table, {.x = 0.6, .y = 0.34}, radius));
    EXPECT_TRUE(tp3::contains(table, {.x = radius, .y = radius}, radius));
    EXPECT_FALSE(tp3::contains(table, {.x = 0.0, .y = 0.34}, radius));
    EXPECT_FALSE(tp3::contains(table, {.x = 1.20, .y = 0.34}, radius));
    EXPECT_FALSE(tp3::contains(table, {.x = 0.6, .y = 0.68}, radius));
}

// El caso tangente no cuenta como solapamiento.
void test_disc_overlap() {
    EXPECT_TRUE(tp3::discs_overlap({.x = 0.0, .y = 0.0}, 1.0, {.x = 1.5, .y = 0.0}, 1.0));
    EXPECT_FALSE(tp3::discs_overlap({.x = 0.0, .y = 0.0}, 1.0, {.x = 2.0, .y = 0.0}, 1.0));
    EXPECT_FALSE(tp3::discs_overlap({.x = 0.0, .y = 0.0}, 1.0, {.x = 2.5, .y = 0.0}, 1.0));
}

void test_obstacle_validation_accepts_valid_configuration() {
    const tp3::Table table{};
    const std::vector<tp3::Obstacle> obstacles{
        obstacle(0, 0.30, 0.34, 0.05),
        obstacle(1, 0.60, 0.20, 0.05),
        obstacle(2, 0.90, 0.34, 0.05),
    };

    tp3::validate_obstacles(table, obstacles, tp3::default_particle_radius);
    EXPECT_TRUE(true);
}

// La mesa vacía es un caso legítimo: el punto 1.1 simula el sistema sin
// obstáculos y los puntos 1.2 y 1.3 la usan como referencia [TP03, p. 3].
void test_obstacle_validation_accepts_empty_table() {
    tp3::validate_obstacles(tp3::Table{}, {}, tp3::default_particle_radius);
    EXPECT_TRUE(true);
}

// La restricción K > 0 pertenece a la configuración de competencia, no al
// motor [TP03, p. 3].
void test_competition_validation_requires_obstacles() {
    const tp3::Table table{};
    const double radius = tp3::default_particle_radius;

    EXPECT_INVALID_ARGUMENT(
        tp3::validate_competition_obstacles(table, {}, radius)
    );
    tp3::validate_competition_obstacles(
        table,
        {obstacle(0, 0.60, 0.34, 0.05)},
        radius
    );
    // Las restricciones geométricas siguen aplicando.
    EXPECT_INVALID_ARGUMENT(
        tp3::validate_competition_obstacles(
            table,
            {obstacle(0, 0.60, 0.34, 0.01)},
            radius
        )
    );
}

void test_obstacle_validation_rejects_violations() {
    const tp3::Table table{};
    const double radius = tp3::default_particle_radius;

    // Rk >= r.
    EXPECT_INVALID_ARGUMENT(
        tp3::validate_obstacles(table, {obstacle(0, 0.60, 0.34, 0.01)}, radius)
    );
    // Íntegramente dentro del dominio.
    EXPECT_INVALID_ARGUMENT(
        tp3::validate_obstacles(table, {obstacle(0, 0.02, 0.34, 0.05)}, radius)
    );
    EXPECT_INVALID_ARGUMENT(
        tp3::validate_obstacles(table, {obstacle(0, 0.60, 0.66, 0.05)}, radius)
    );
    // Sin solaparse entre sí.
    EXPECT_INVALID_ARGUMENT(
        tp3::validate_obstacles(
            table,
            {obstacle(0, 0.60, 0.34, 0.05), obstacle(1, 0.64, 0.34, 0.05)},
            radius
        )
    );
}

void test_free_placement() {
    const tp3::Table table{};
    const double radius = tp3::default_particle_radius;
    const std::vector<tp3::Obstacle> obstacles{obstacle(0, 0.60, 0.34, 0.05)};
    const std::vector<tp3::Particle> placed{particle(0, 0.30, 0.34)};

    EXPECT_TRUE(tp3::is_free_placement(table, obstacles, placed, {.x = 0.90, .y = 0.34}, radius));
    // Sobre el obstáculo.
    EXPECT_FALSE(tp3::is_free_placement(table, obstacles, placed, {.x = 0.62, .y = 0.34}, radius));
    // Sobre una partícula ya ubicada.
    EXPECT_FALSE(tp3::is_free_placement(table, obstacles, placed, {.x = 0.32, .y = 0.34}, radius));
    // Fuera del dominio.
    EXPECT_FALSE(tp3::is_free_placement(table, obstacles, placed, {.x = 0.005, .y = 0.34}, radius));
}

}  // namespace

int main() {
    test_vector_algebra();
    test_goal_span();
    test_containment();
    test_disc_overlap();
    test_obstacle_validation_accepts_valid_configuration();
    test_obstacle_validation_accepts_empty_table();
    test_competition_validation_requires_obstacles();
    test_obstacle_validation_rejects_violations();
    test_free_placement();
    return test::finish("test_geometry");
}
